import pandas as pd
import matplotlib.pyplot as plt
from time_series_input import TS_input
from utility_functions import annual_factor, colors_stacked_bar, adjust_legend, extract_case_details, figure_subfolder
from pyomo.common.timing import TicTocTimer
import itertools
from sizing_cases import Sync_WDM, Sync_WD, Sync_W, SizingResults
from scheduling_opti_functions import build_schedule_model, rebuild_schedule_model, extract_results, solve_schedule_model, calc_LCOMeOH
import os.path

def scheduling_optimization(CASE, CAPgen_ins, ratio_wind_solar, CAPEXgen, CAPEXgrid, Annual_land_lease_costs, SizingCases_list):
    timer = TicTocTimer()
    timer.tic(msg=None)

    SizingCases_list = SizingCases_list # select which SizingCases to apply for the search for the optimal design

    DE = CASE.de
    NU = CASE.nu
    CMP = CASE.cmp
    YEAR = CASE.year
    minCAP = CASE.minCAP
    switch_capex_max_cap_scaling = CASE.switch_capex_max_cap_scaling
    switch_capex_max_cap_scaling_equal_sizes = CASE.switch_capex_max_cap_scaling_equal_sizes

    df_wind, df_solar = TS_input()
    df = df_wind
    df['CFgen'] = ratio_wind_solar * df_wind['CFgen'] + (1 - ratio_wind_solar) * df_solar['CFgen']

    df['CAPgen'] = CAPgen_ins * df['CFgen']
    CAPgen = df['CAPgen'].values

    for SC in SizingCases_list:

        S_days_of_storage_product = list(itertools.product(*[SC.S_days_of_storage_alternatives[k] for k in SC.S_days_of_storage_alternatives.keys()]))

        S_days_of_storage_CGH2 = []
        S_days_of_storage_CO2tank = []
        S_days_of_storage_BAT = []
        S_days_of_storage_TES = []
        for i in range(len(S_days_of_storage_product)):
            S_days_of_storage_CGH2.append(S_days_of_storage_product[i][0])
            S_days_of_storage_CO2tank.append(S_days_of_storage_product[i][1])
            S_days_of_storage_BAT.append(S_days_of_storage_product[i][2])
            S_days_of_storage_TES.append(S_days_of_storage_product[i][3])

        SC.S_days_of_storage['CGH2'] = S_days_of_storage_CGH2
        SC.S_days_of_storage['CO2tank'] = S_days_of_storage_CO2tank
        SC.S_days_of_storage['BAT'] = S_days_of_storage_BAT
        SC.S_days_of_storage['TES'] = S_days_of_storage_TES

    number_of_runs_sizing = 0
    for SC in SizingCases_list:
        number_of_runs_sizing = number_of_runs_sizing + len(SC.rel_CAP_ins['WEL']) * len(SC.S_days_of_storage['CGH2'])
    print('Number of runs in one sizing screening = ' + str(number_of_runs_sizing) + ' + 1 (initial fully flexible)')

    # fully flexible case
    max_CAP = 1e8
    CAP_ins_flex = {'WEL': max_CAP,  # [kmol/h]
                   'DAC': max_CAP,
                   'MTS': max_CAP,
                   'HP_amb': max_CAP,  # [kWh/h]
                   'HP_int': 0,
                   "BAT_in": 0,  # ATB NREL - typical 4h battery duration
                   "BAT_out": 0,
                   "CGH2_in": 0,
                   "CGH2_out": 0,
                   "TES_in": 0,
                   "TES_out": 0,
                   "CO2tank_in": 0,
                   "CO2tank_out": 0,
                   "Curt": CAPgen_ins}

    S_ins_flex ={'CGH2': 0,
                 'CO2tank': 0,
                 'BAT': 0,
                 'TES': 0}

    minCAP_flex = {key: 0 for key in CAP_ins_flex.keys()}
    minCAP_flex['MTS'] = 0

    rampLimit = {key: 1 for key in CAP_ins_flex.keys()}
    rampLimit_slow_processes = 0.3
    rampLimit['MTS'] = rampLimit_slow_processes
    rampLimit['DAC'] = rampLimit_slow_processes
    rampLimit['HP_int'] = rampLimit_slow_processes
    rampLimit['HP_amb'] = rampLimit_slow_processes

    # solve unrestricted fully flexible model, no storages
    m, opt, DT_equations, DT_write_model = build_schedule_model(DE, CAPgen, CAP_ins_flex, S_ins_flex, minCAP_flex, rampLimit, timer)

    Production_annual_t, CAP_ins_flex_actual, S_ins_flex_actual, solver_status = solve_schedule_model(m, opt, 0)
    LCOMeOH_flex, dLCOMeOH_all_flex = calc_LCOMeOH(DE, ratio_wind_solar, Production_annual_t, CAP_ins_flex_actual, S_ins_flex_actual, NU, YEAR, CMP, CAPEXgen, CAPEXgrid, Annual_land_lease_costs, switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes, 0)

    DT_solve_init = timer.toc(msg=None)

    print('Run # ' + str(0) + '/' + str(number_of_runs_sizing) +
          ',    Case: ' + CASE.name +
          ',    Sizing case: ' + 'Flex' +
          ',    CAPgen (MW) = ' + str(round(CAPgen_ins / 1000, 0)) +
          ',    ratio WS = ' + str(ratio_wind_solar) +
          ',    Built eq. (s) = ' + str(round(DT_equations, 2)) +
          ',    Wrote model (s) = ' + str(round(DT_write_model, 2)) +
          ',    Init. solve (s) = ' + str(round(DT_solve_init, 2)))

    DT_resolve = []
    DT_rebuild = []
    CAP_ins_list_IN = [CAP_ins_flex]
    CAP_ins_list_OUT = [CAP_ins_flex_actual]
    S_ins_list_IN = [S_ins_flex]
    S_ins_list_OUT = [S_ins_flex_actual]
    minCAP_list_IN = [minCAP_flex]
    solver_status_list = [solver_status]
    rel_CAP_ins_list = [CAP_ins_flex]
    S_days_of_storage_list = [0]

    Production_annual_t_list = [Production_annual_t]
    LCOMeOH_list = [LCOMeOH_flex]
    dLCOMeOH_all_list = [dLCOMeOH_all_flex]
    counter = 0

    for SC in SizingCases_list:
        for i in range(len(SC.rel_CAP_ins['MTS'])):
            for j in range(len(SC.S_days_of_storage['CGH2'])):

                CAP_ins_list_IN.append(CAP_ins_list_OUT[counter].copy())
                CAP_ins_list_OUT.append(CAP_ins_list_OUT[counter].copy())
                minCAP_list_IN.append(minCAP_list_IN[counter].copy())

                CAP_ins_list_IN[counter+1]['Curt'] = CAPgen_ins
                minCAP_list_IN[counter+1] = minCAP


                rel_CAP_ins_in_new = {}
                for k in SC.rel_CAP_ins.keys():
                    CAP_ins_list_IN[counter+1][k] = CAP_ins_flex_actual[k] * SC.rel_CAP_ins[k][i]
                    rel_CAP_ins_in_new[k] = SC.rel_CAP_ins[k][i]

                rel_CAP_ins_list.append(rel_CAP_ins_in_new)

                BAT_supporting_DAC = 1
                if SC.rel_CAP_ins['WEL'][i] == SC.rel_CAP_ins['DAC'][i]:
                    BAT_supporting_DAC = 0

                S_flow_requirement_h =  {'CGH2': -1 * DE['MTS'].calc_flows(CAP_ins_list_IN[counter+1]['MTS'])['H2'], # selecting the flows to be covered by the storage (kmol/h or kWh/h) based on the installed capacities of the other processes
                                        'CO2tank': -1 * DE['MTS'].calc_flows(CAP_ins_list_IN[counter+1]['MTS'])['CO2'],
                                        'BAT': -1 * (DE['MTS'].calc_flows(CAP_ins_list_IN[counter+1]['MTS'])['e']
                                                     + DE['DAC'].calc_flows(CAP_ins_list_IN[counter+1]['DAC'])['e'] * BAT_supporting_DAC
                                                     + DE['HP_amb'].calc_flows(CAP_ins_list_IN[counter+1]['HP_amb'])['e'] * BAT_supporting_DAC),
                                        'TES': -1 * DE['MTS'].calc_flows(CAP_ins_list_IN[counter+1]['MTS'])['q100']}

                S_in_new = {}
                S_days_of_storage_in_new = {}
                for k in SC.S_days_of_storage.keys():
                    S_in_new[k] = S_flow_requirement_h[k] * 24*SC.S_days_of_storage[k][j]
                    S_days_of_storage_in_new[k] = SC.S_days_of_storage[k][j]

                S_days_of_storage_list.append(S_days_of_storage_in_new)
                S_ins_list_IN.append(S_in_new)
                S_ins_list_OUT.append(S_ins_list_IN[counter+1])

                # setting charging and discharging process capacities
                CAP_ins_list_IN[counter + 1]["BAT_in"] = S_ins_list_IN[counter+1]['BAT'] / 4  # ATB NREL - typical 4h battery duration
                CAP_ins_list_IN[counter + 1]["BAT_out"] = S_ins_list_IN[counter+1]['BAT'] / 4
                CAP_ins_list_IN[counter + 1]["CGH2_in"] = CAP_ins_list_IN[counter + 1]['WEL']
                CAP_ins_list_IN[counter + 1]["CGH2_out"] = CAP_ins_list_IN[counter + 1]['MTS'] * 3.1
                CAP_ins_list_IN[counter + 1]["TES_in"] = S_ins_list_IN[counter+1]['TES'] * 0.1
                CAP_ins_list_IN[counter + 1]["TES_out"] = S_ins_list_IN[counter+1]['TES'] * 0.1
                CAP_ins_list_IN[counter + 1]["CO2tank_in"] = CAP_ins_list_IN[counter + 1]['DAC']
                CAP_ins_list_IN[counter + 1]["CO2tank_out"] = CAP_ins_list_IN[counter + 1]['DAC']

                m, opt = rebuild_schedule_model(m, opt, CAP_ins_list_IN[counter], CAP_ins_list_IN[counter+1], S_ins_list_IN[counter], S_ins_list_IN[counter+1], minCAP_list_IN[counter], minCAP_list_IN[counter+1])
                DT_rebuild.append(timer.toc(msg=None))

                Production_annual_t, CAP_ins_actual, S_ins_actual, solver_status = solve_schedule_model(m, opt, 0)
                LCOMeOH, dLCOMeOH_all = calc_LCOMeOH(DE, ratio_wind_solar, Production_annual_t, CAP_ins_actual, S_ins_actual, NU, YEAR, CMP, CAPEXgen, CAPEXgrid, Annual_land_lease_costs, switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes, 0)

                CAP_ins_list_OUT[counter+1] = CAP_ins_actual
                S_ins_list_OUT[counter+1] = S_ins_actual
                Production_annual_t_list.append(Production_annual_t)
                LCOMeOH_list.append(LCOMeOH)
                dLCOMeOH_all_list.append(dLCOMeOH_all)
                solver_status_list.append(solver_status)

                DT_resolve.append(timer.toc(msg=None))
                counter = counter + 1
                print('Run # ' + str(counter) + '/' + str(number_of_runs_sizing) +
                      ',  Case: ' + CASE.name +
                      ',  Size case: ' + SC.name +
                      ',  r-WS = ' + str(ratio_wind_solar) +
                      ',  CAPgen(MW) = ' + str(int(round(CAPgen_ins/1000, 0))) +
                      ',  relCAP-M-W-D = ' + str(SC.rel_CAP_ins['MTS'][i]) + ', ' + str(SC.rel_CAP_ins['WEL'][i]) + ', ' + str(SC.rel_CAP_ins['DAC'][i]) +
                      ',  daysS-B-H-C-T = ' + str(SC.S_days_of_storage['BAT'][j]) + ', ' + str(SC.S_days_of_storage['CGH2'][j]) + ', ' + str(SC.S_days_of_storage['CO2tank'][j]) + ', ' + str(SC.S_days_of_storage['TES'][j]) +
                      ',  LCOMeOH = ' + str(int(round(LCOMeOH, 0))) +
                      ',  Reb.(s) = ' + str(round(DT_rebuild[-1], 1)) +
                      ',  Res.(s) = ' + str(round(DT_resolve[-1], 1)))


    DT_total = DT_equations + DT_write_model + sum(DT_rebuild) + DT_solve_init + sum(DT_resolve)

    print('Elapsed time one sizing screening = ', round(DT_total,1))

    df_LCOMeOH_stacked_bar_list = []
    for i in range(len(dLCOMeOH_all_list)):
        df_LCOMeOH_stacked_bar_list.append(pd.DataFrame(dLCOMeOH_all_list[i], index=[i]))

    df_LCOMeOH_stacked_bar = pd.concat(df_LCOMeOH_stacked_bar_list, axis=0)


    # Set general plot settings
    plt.rcParams.update({
        'font.size': 16,  # Font size for text
        'font.family': 'serif',  # Font family (serif is commonly used in publications)
        'axes.labelsize': 16,  # Font size for axis labels
        'axes.titlesize': 16,  # Font size for plot titles
        'xtick.labelsize': 15,  # Font size for x-axis tick labels
        'ytick.labelsize': 15,  # Font size for y-axis tick labels
        'legend.fontsize': 13,  # Font size for legend
        'axes.linewidth': 0.8,  # Width of axes lines
        'lines.linewidth': 1.0,  # Width of plot lines
        'lines.markersize': 4,  # Size of markers
        'grid.linewidth': 0.5,  # Width of grid lines
        'grid.alpha': 0.7,  # Transparency of grid lines
    })

    plotting_sizing = 0
    if plotting_sizing == 1:
        fig, ax = plt.subplots(figsize=(18, 6), dpi=600)
        df_LCOMeOH_stacked_bar.plot(kind='bar', stacked=True, ax=ax, color=colors_stacked_bar())
        SizingCases_string = ''
        for i in SizingCases_list:
            SizingCases_string = SizingCases_string + i.name + ', '
        ax.set_title(extract_case_details(CASE.name)  + ' ' + str(int(round(CAPgen_ins/1000, 0)/10)*10) + ' MW, ' + ' Sizing Cases: ' + SizingCases_string, fontsize=18)
        #plt.title('CASE: ' + CASE.name + '     SIZING CASES: ' + SizingCases_string + '\n CAPgen (MW) = ' + str(round(CAPgen_ins/1000, 0)) + '     ratio WS = ' + str(ratio_wind_solar))
        plt.xlabel('Sizing runs', fontsize=18)
        plt.ylabel('LCOMeOH (USD/t)', fontsize=18)
        plt.ylim([0, 3500])
        ax.set_xticklabels([])
        solver_status_list_short = []
        for i in range(len(solver_status_list)):
            if solver_status_list[i] == 'ok':
                solver_status_list_short.append('1')
            else:
                solver_status_list_short.append('0')
            ax.text(i, +50, solver_status_list_short[i], ha='center', va='top', fontsize=7, color='white')

        #plt.legend(bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)
        legend_text_replacements = {'indir_OPEX': 'OPEX$_{indir}$',
                                    'indir_CAPEX': 'CAPEX$_{indir}$',
                                    'CO2tank': 'CO$_{2,tank}$',
                                    'CGH2': 'H$_{2,CG}$',
                                    'WEL replace': 'WEL$_{replace}$',
                                    'HP_amb': 'HP$_{amb}$',
                                    'DACsorb': 'DAC$_{sorb}$'}
        filt_handles, filt_labels = adjust_legend(ax, ['TES', 'HP_int'], legend_text_replacements)
        ax.legend(filt_handles, filt_labels, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
                  reverse=True, frameon=False, fontsize=16)
        plt.tight_layout()
        SizingCases_string = SizingCases_string.replace(', ', '_')
        fig_name = 'fig_SIZING_' + CASE.name + '_cases_' + SizingCases_string + str(int(round(CAPgen_ins/1000, 0)/10)*10) + '_MW.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()

    if any(value > 0 for value in minCAP.values()):     # if there is a minCAP design in the case, we cannot count the fully flexible run as one of the ones we select the optimal design from
        LCOMeOH_selected = min(LCOMeOH_list[1:])        # and since the infeasible runs have been assigned an unrealistically high value, any feasible design abiding by the minCAP limitations, should be selected
    else:
        LCOMeOH_selected = min(LCOMeOH_list)

    min_index = LCOMeOH_list.index(LCOMeOH_selected)
    Production_annual_t_selected = Production_annual_t_list[min_index]
    CAP_ins_selected = CAP_ins_list_OUT[min_index]
    S_ins_selected = S_ins_list_OUT[min_index]
    df_LCOMeOH_stacked_bar_selected = df_LCOMeOH_stacked_bar.loc[[min_index]]
    rel_CAP_ins_selected = rel_CAP_ins_list[min_index]
    S_days_of_storage_selected = S_days_of_storage_list[min_index]

    print('minimum LCOMeOH within sizing screening = ', round(LCOMeOH_selected,1))

    Results = SizingResults(name='Sizing results')
    Results.SizingCases_run = SizingCases_list
    Results.CAPgen_ins = CAPgen_ins
    Results.ratio_wind_solar = ratio_wind_solar
    Results.LCOMeOH_list = LCOMeOH_list
    Results.Production_annual_t_list = Production_annual_t_list
    Results.CAP_ins_list_OUT = CAP_ins_list_OUT
    Results.S_ins_list_OUT = S_ins_list_OUT
    Results.df_LCOMeOH_stacked_bar = df_LCOMeOH_stacked_bar

    Results.LCOMeOH_selected = LCOMeOH_selected
    Results.Production_annual_t_selected = Production_annual_t_selected
    Results.CAP_ins_selected = CAP_ins_selected
    Results.S_ins_selected = S_ins_selected
    Results.df_LCOMeOH_stacked_bar_selected = df_LCOMeOH_stacked_bar_selected

    Results.rel_CAP_ins_selected = rel_CAP_ins_selected
    Results.S_days_of_storage_selected = S_days_of_storage_selected

    return Results


x=1