import os.path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
from pickle import load, dump
from utility_functions import colors_stacked_bar, figure_subfolder, adjust_legend, extract_case_details, res_subfolder
from scheduling_opti_functions import build_schedule_model, rebuild_schedule_model, extract_results, solve_schedule_model, calc_LCOMeOH
from time_series_input import TS_input
from pyomo.common.timing import TicTocTimer

plotting_schedule = 0

CS_psm_years = load(open(os.path.join(res_subfolder(), 'CS_YEARS_p1s1m1_maxPgrid_6000__2025-02-21_16-13-03.pkl'), 'rb'))
CS_plm_years = load(open(os.path.join(res_subfolder(), 'CS_YEARS_p1l1m1_maxPgrid_6000__2025-02-21_16-13-03.pkl'), 'rb'))

CS_psm_years_maxCAPscale = load(open(os.path.join(res_subfolder(), 'CS_YEARS_p1s1m1_maxCAPscale_maxPgrid_6000__2025-02-21_16-13-03.pkl'), 'rb'))
CS_plm_years_maxCAPscale = load(open(os.path.join(res_subfolder(), 'CS_YEARS_p1l1m1_maxCAPscale_maxPgrid_6000__2025-02-21_16-13-03.pkl'), 'rb'))

CS_plm_years_minCAP_DACL_25 = load(open(os.path.join(res_subfolder(), 'CS_YEARS_minCAP_DACL_25_p1l1m1_maxPgrid_6000__2025-02-21_18-05-21.pkl'), 'rb'))
CS_plm_years_minCAP_DACL_50 = load(open(os.path.join(res_subfolder(), 'CS_YEARS_minCAP_DACL_50_p1l1m1_maxPgrid_6000__2025-02-21_18-05-21.pkl'), 'rb'))

CS_psm_years_minCAP_MTS_25 = load(open(os.path.join(res_subfolder(), 'CS_YEARS_minCAP_MTS_25_p1s1m1_maxPgrid_6000__2025-02-21_18-05-21.pkl'), 'rb'))
CS_psm_years_minCAP_MTS_50 = load(open(os.path.join(res_subfolder(), 'CS_YEARS_minCAP_MTS_50_p1s1m1_maxPgrid_6000__2025-02-21_18-05-21.pkl'), 'rb'))

GC_2020_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GC_2020_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
GC_2030_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GC_2030_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
GC_2050_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GC_2050_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))

# CaseStudies_to_extract = [CS_psm_years, CS_psm_years_minCAP_MTS_25, CS_psm_years_minCAP_MTS_50]
CaseStudies_to_extract = [CS_psm_years, CS_psm_years_minCAP_MTS_25, CS_psm_years_minCAP_MTS_50, CS_plm_years_minCAP_DACL_25, CS_plm_years_minCAP_DACL_50]

# Set general plot settings
blue_MPI = np.array((51 / 255, 165 / 255, 195 / 255))
red_MPI = np.array((120 / 255, 0 / 255, 75 / 255))
green_MPI = np.array((0 / 255, 118 / 255, 117 / 255))
yellow_MPI = np.array((236 / 255, 233 / 255, 212 / 255))
colors_MPI = [blue_MPI, green_MPI, red_MPI]

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
    'savefig.dpi': 600,  # DPI for saving the figure
    'savefig.format': 'pdf',  # Format for saving the figure
    'savefig.bbox': 'tight',  # Ensures the plot is tightly cropped when saved
})
colors_bar = colors_stacked_bar()
ylim_list = [2000, 1250, 1000]
legend_text_replacements = {'indir_OPEX':'OPEX$_{indir}$',
                            'indir_CAPEX':'CAPEX$_{indir}$',
                            'CO2tank':'CO$_{2,tank}$',
                            'CGH2':'H$_{2,CG}$',
                            'WEL replace':'WEL$_{replace}$',
                            'HP_amb':'HP$_{amb}$',
                            'DACsorb':'DAC$_{sorb}$'}

# summary table - different size plants considered

summary_table_cases = [CS_psm_years, CS_psm_years_maxCAPscale, CS_plm_years_minCAP_DACL_25]

prod_capacity_to_cover = 1800 # kt MeOH/a
Nplants = np.array([90, 9, 3, 1])
prod_cap_to_cover_vector = 1800 / Nplants * 0.95

cap_picks = [0, 1, 3, 9] # which plant capacity to be picked (0 - 14) ordered

df_summary_table = pd.DataFrame()
years =  [0, 2]
cols = ["_0","_1","_3","_9"]
index_list = []
for year in years:
    for TC in summary_table_cases:
        data_LCOMeOH = [{'LCOMeOH' + cols[i]: int(round(TC.cases[year].res['LCOMeOH_selected'][cap_picks[i]], 0)) for i in range(len(cap_picks))}]
        data_prod = {'Prod' + cols[i]: round(TC.cases[year].res['production_MeOH'][cap_picks[i]]/1000,1) for i in range(len(cap_picks))}

        data_LCOMeOH[0].update(data_prod)

        index_list.append(TC.cases[year].name)
        # Iterate through the data and append rows
        for row in data_LCOMeOH:
            df_summary_table = pd.concat([df_summary_table, pd.DataFrame([row])], ignore_index=True)

        df_summary_table.index = index_list
x=1









for CS in CaseStudies_to_extract:
    counter = 0
    for C in CS.cases:

        fig, ax = plt.subplots(figsize=(8, 6), dpi=600)
        C.res['dLCOMeOH'].plot(kind='bar', stacked=True, ax=ax, color=colors_bar)
        xticklabels = np.array([round(elem/10, 0)*10 for elem in C.res['CAPgen_ins_array'] / 1000])
        ax.set_xticklabels(xticklabels.astype(int), rotation=45, ha='right', rotation_mode='anchor')
        ax.set_title(extract_case_details(C.name), y=0.93)
        ax.set_xlabel('Grid output capacity (MW)')
        ax.set_ylabel('LCOMeOH (USD/t)')
        plt.ylim(0, ylim_list[counter])
        filt_handles, filt_labels = adjust_legend(ax, ['TES', 'HP_int'], legend_text_replacements)
        ax.legend(filt_handles, filt_labels, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True, frameon=False)
        plt.tight_layout()
        fig_name = 'fig_CAPgen_'+ C.name + '_maxPgrid_' + str(int(max(C.res['CAPgen_ins_array']/1000))) + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=600)
        C.res['dLCOMeOH'].plot(kind='bar', stacked=True, ax=ax, color=colors_bar)
        xticklabels = np.array([round(elem / 10000, 0) * 10000 for elem in C.res['production_MeOH']])/1000
        ax.set_xticklabels(xticklabels.astype(int), rotation=45, ha='right', rotation_mode='anchor')
        ax.set_title(extract_case_details(C.name), y=0.93)
        plt.xlabel('Produced MeOH (kt/a)')
        plt.ylabel('LCOMeOH (USD/t)')
        plt.ylim(0,  ylim_list[counter])
        filt_handles, filt_labels = adjust_legend(ax, ['TES', 'HP_int'], legend_text_replacements)
        ax.legend(filt_handles, filt_labels, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,reverse=True, frameon=False)
        plt.tight_layout()
        fig_name = 'fig_prod_' + C.name + '_maxPgrid_' + str(int(max(C.res['CAPgen_ins_array']/1000))) + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()



        # Installed capacities plot

        cap_sel = 0                 # select for which capacity to plot (ordered)
        cap_grid_MW = round(C.res['CAPgen_ins_array'][cap_sel]/1000  /10, 0)*10

        # Group 1: Keys for the first subplot
        CAPins_energy_keys = ['HP_amb']
        CAPins_energy_data_MW = {key: C.res['CAP_ins_selected'][cap_sel][key]/1000 for key in CAPins_energy_keys}

        # Group 2: Keys for the second subplot
        CAPins_mass_keys = ['DAC', 'WEL', 'MTS']
        CAPins_mass_data = {key: C.res['CAP_ins_selected'][cap_sel][key] for key in CAPins_mass_keys}

        Sins_mass_keys = ['CGH2', 'CO2tank']
        Sins_mass_data_1000kmol = {key: C.res['S_ins_selected'][cap_sel][key]/1000 for key in Sins_mass_keys}

        Sins_energy_keys = ['BAT']
        Sins_energy_data_MW = {key: C.res['S_ins_selected'][cap_sel][key]/1000 for key in Sins_energy_keys}

        width_ratios = [len(CAPins_mass_data), len(Sins_mass_data_1000kmol), len(Sins_energy_data_MW)]
        fig = plt.figure(figsize=(10, 5), dpi=600)

        gs = GridSpec(1, 3, width_ratios=width_ratios, figure=fig)

        fig.suptitle(extract_case_details(C.name) + ', ' + str(int(cap_grid_MW)) + ' MW', fontsize = 18, y=0.93)

        # Plot the first group
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(CAPins_mass_data.keys(), CAPins_mass_data.values(), color=blue_MPI)
        ax1.set_title('kmol/h', fontsize=14)
        ax1.set_ylim([0, 400 * (cap_grid_MW/50)])
        ax1.set_ylabel('Installed capacity', fontsize = 18, labelpad=10)
        ax1.tick_params(axis='x', rotation=45)

        # ax2 = fig.add_subplot(gs[0, 1])
        # ax2.bar(CAPins_energy_data.keys(), CAPins_energy_data.values()/1000, color=blue_MPI)
        # ax2.set_ylabel('MW')
        # ax2.tick_params(axis='x', rotation=45)

        ax3 = fig.add_subplot(gs[0, 1])
        ax3.bar(Sins_mass_data_1000kmol.keys(), Sins_mass_data_1000kmol.values(), color=blue_MPI)
        ax3.set_title('Mmol', fontsize=14)
        ax3.set_ylim([0, 30 * (cap_grid_MW/50)])
        ax3.tick_params(axis='x', rotation=45)

        ax4 = fig.add_subplot(gs[0, 2])
        ax4.bar(Sins_energy_data_MW.keys(), Sins_energy_data_MW.values(), color=blue_MPI)
        ax4.set_title('MWh', fontsize=14)
        ax4.set_ylim([0, 210 * (cap_grid_MW/50)])
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        fig_name = 'fig_DESIGN_' + C.name + '__' + str(int(cap_grid_MW)) + '_MW' + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()


        counter=counter+1




        if plotting_schedule == 1:           # plotting scheduling of the selected design
            if C.name == 'p1l1m1_y2020_minCAP_DACL_0' or 'p1l1m1_y2020_minCAP_DACL_25' or 'p1l1m1_y2020_minCAP_DACL_50' or 'p1l1m1_y2020_minCAP_DACL_75' or 'p1l1m1_y2020' or 'p1s1m1_y2020' :
                index_capacity_to_plot = cap_sel # choose which plant size (capacity) should have scheduling plotted

                timer = TicTocTimer()
                timer.tic(msg=None)

                DE = C.de
                NU = C.nu
                CMP = C.cmp
                YEAR = C.year
                minCAP = C.minCAP
                switch_capex_max_cap_scaling = C.switch_capex_max_cap_scaling
                switch_capex_max_cap_scaling_equal_sizes = C.switch_capex_max_cap_scaling_equal_sizes

                df_wind, df_solar = TS_input()
                df = df_wind
                df['CFgen'] = C.res['ratio_wind_solar_selected'][index_capacity_to_plot] * df_wind['CFgen'] + (
                            1 - C.res['ratio_wind_solar_selected'][index_capacity_to_plot]) * df_solar['CFgen']

                df['CAPgen'] = C.res['CAPgen_ins_selected'][index_capacity_to_plot] * df['CFgen']
                CAPgen = df['CAPgen'].values

                del C.res['CAP_ins_selected'][index_capacity_to_plot]['GEN']
                C.res['CAP_ins_selected'][index_capacity_to_plot]['Curt'] = max(CAPgen)

                rampLimit = {key: 1 for key in C.res['CAP_ins_selected'][index_capacity_to_plot].keys()}
                rampLimit_slow_processes = 0.3
                rampLimit['MTS'] = rampLimit_slow_processes
                rampLimit['DAC'] = rampLimit_slow_processes
                rampLimit['HP_int'] = rampLimit_slow_processes
                rampLimit['HP_amb'] = rampLimit_slow_processes

                m = []
                opt = []

                m, opt, DT_equations, DT_write_model = build_schedule_model(DE, CAPgen, C.res['CAP_ins_selected'][index_capacity_to_plot], C.res['S_ins_selected'][index_capacity_to_plot],
                                                                            minCAP, rampLimit, timer)

                Production_annual_t, CAP_ins_actual, S_ins_actual, solver_status = solve_schedule_model(m, opt, 1)
                LCOMeOH, dLCOMeOH_all = calc_LCOMeOH(DE, C.res['ratio_wind_solar_selected'][index_capacity_to_plot], Production_annual_t,
                                                     CAP_ins_actual, S_ins_actual, NU, YEAR, CMP, C.res['CAPEXgen_list'][index_capacity_to_plot],
                                                     C.res['CAPEXgrid_list'][index_capacity_to_plot], C.res['Annual_land_lease_costs_list'][index_capacity_to_plot],
                                                     switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes, 0)

                print('CAPgen = ', CAPgen)
                print('CAP_ins = ', C.res['CAP_ins_selected'][index_capacity_to_plot])
                print('minCAP = ', minCAP)




for CS in CaseStudies_to_extract:
    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)
    Cases = []
    counter = 0
    for C in CS.cases:
        Cases.append(C.name)
        ax.plot(C.res['CAPgen_ins_array'] / 1000, C.res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_MPI[counter])
        counter=counter+1

    #plt.title(CS.name)
    #plt.title(extract_case_details(CS.name), y = 0.93)
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)

    for i in range(len(Cases)):
        Cases[i] = extract_case_details(Cases[i])

    legend1 = plt.legend(Cases, loc="upper right")
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)   # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_years_LCOMeOH_' + CS.name + '_maxPgrid_' + str(int(max(CS.cases[0].res['CAPgen_ins_array']/1000))) + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



plot_DAC_L_minCAP = 1
gray = np.array([100, 100, 100]) / 255
colors_blue_MPI = [blue_MPI, green_MPI, red_MPI, yellow_MPI, gray]
blue=blue_MPI
color_offset=0
colors_blue_MPI = [blue,
                   blue + (1 - blue) * (color_offset + 1) / 3,
                   blue + (1 - blue) * (color_offset + 2) / 3,
                   gray]

red = red_MPI
colors_red_MPI = [red,
                  red + (1 - red) * (color_offset + 1) / 3,
                  red + (1 - red) * (color_offset + 2) / 3,
                  gray - 30/255]

if plot_DAC_L_minCAP == 1:
    Cases_DAC_L_minCAP = [CS_plm_years, CS_plm_years_minCAP_DACL_25, CS_plm_years_minCAP_DACL_50]

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)
    counter = 0
    for CS in Cases_DAC_L_minCAP:
        ax.plot(CS.cases[0].res['CAPgen_ins_array'] / 1000, CS.cases[0].res['LCOMeOH_selected'], marker='.',
                markersize=20, color=colors_blue_MPI[counter])
        counter=counter+1

    counter = 0
    for CS in Cases_DAC_L_minCAP:
        ax.plot(CS.cases[2].res['CAPgen_ins_array'] / 1000, CS.cases[2].res['LCOMeOH_selected'], marker='.',
                markersize=20, color=colors_red_MPI[counter])
        counter = counter + 1

    plt.title('DAC-L', y=0.93)
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['2020, DAC-L minCAP = 0%',
                          '2020, DAC-L minCAP = 25%',
                          '2020, DAC-L minCAP = 50%',
                          '2050, DAC-L minCAP = 0%',
                          '2050, DAC-L minCAP = 25%',
                          '2050, DAC-L minCAP = 50%',
                          ],
                         loc="lower left", ncol=2, fontsize=8.5)  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    # plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
    # reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_DAC_L_flexibility' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)
    counter = 0
    for CS in Cases_DAC_L_minCAP:
        ax.plot(CS.cases[0].res['CAPgen_ins_array'] / 1000, CS.cases[0].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[counter])
        counter = counter + 1

    plt.title('Year: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['DAC-L minCAP = 0%',
                'DAC-L minCAP = 25%',
                'DAC-L minCAP = 50%',
                'DAC-S'], loc="lower right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
              # reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_DAC_L_flexibility_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()






    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_plm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[0])
    ax.plot(CS_plm_years_minCAP_DACL_25.cases[2].res['CAPgen_ins_array'] / 1000, CS_plm_years_minCAP_DACL_25.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[1])
    ax.plot(CS_plm_years_minCAP_DACL_50.cases[2].res['CAPgen_ins_array'] / 1000, CS_plm_years_minCAP_DACL_50.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[2])
    ax.plot(CS_psm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[3])

    plt.title('Year: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['DAC-L minCAP = 0%',
                'DAC-L minCAP = 25%',
                'DAC-L minCAP = 50%',
                'DAC-S'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
               #reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_DAC_L_flexibility_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()


plot_MTS_minCAP = 1
if plot_MTS_minCAP == 1:
    Cases_MTS_minCAP = [CS_psm_years, CS_psm_years_minCAP_MTS_25, CS_psm_years_minCAP_MTS_50]

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)
    counter = 0
    for CS in Cases_MTS_minCAP:
        ax.plot(CS.cases[0].res['CAPgen_ins_array'] / 1000, CS.cases[0].res['LCOMeOH_selected'], marker='.',
                markersize=20, color=colors_blue_MPI[counter])
        counter=counter+1

    counter = 0
    for CS in Cases_MTS_minCAP:
        ax.plot(CS.cases[2].res['CAPgen_ins_array'] / 1000, CS.cases[2].res['LCOMeOH_selected'], marker='.',
                markersize=20, color=colors_red_MPI[counter])
        counter = counter + 1

    plt.title('DAC-S', y=0.93)
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['2020, MTS minCAP = 0%',
                          '2020, MTS minCAP = 25%',
                          '2020, MTS minCAP = 50%',
                          '2050, MTS minCAP = 0%',
                          '2050, MTS minCAP = 25%',
                          '2050, MTS minCAP = 50%'
                          ],
                         loc="lower left", ncol=2, fontsize=9)  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    # plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
    # reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_MTS_flexibility' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)
    counter = 0
    for CS in Cases_MTS_minCAP:
        ax.plot(CS.cases[0].res['CAPgen_ins_array'] / 1000, CS.cases[0].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[counter])
        counter = counter + 1

    plt.title('DAC-S, Year: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['MTS minCAP = 0%',
                'MTS minCAP = 25%',
                'MTS minCAP = 50%'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
               #reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_MTS_flexibility_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[0])
    ax.plot(CS_psm_years_minCAP_MTS_25.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years_minCAP_MTS_25.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[1])
    ax.plot(CS_psm_years_minCAP_MTS_50.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years_minCAP_MTS_50.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_blue_MPI[2])

    plt.title('DAC-S, Year: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['MTS minCAP = 0%',
                'MTS minCAP = 25%',
                'MTS minCAP = 50%'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
    #           reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_MTS_flexibility_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()







plot_maxScaling=1

if plot_maxScaling == 1:
    Cases_maxScaling = [CS_psm_years, CS_psm_years_maxCAPscale, CS_plm_years, CS_plm_years_maxCAPscale]

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[0].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[0].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_blue_MPI[0])
    ax.plot(CS_psm_years_maxCAPscale.cases[0].res['CAPgen_ins_array'] / 1000,
            CS_psm_years_maxCAPscale.cases[0].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_blue_MPI[2])

    ax.plot(CS_psm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[2].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_red_MPI[0])
    ax.plot(CS_psm_years_maxCAPscale.cases[2].res['CAPgen_ins_array'] / 1000,
            CS_psm_years_maxCAPscale.cases[2].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_red_MPI[2])

    plt.title('DAC-S',y=0.93)
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['2020, unlimited max. cap.', '2020, limited max. cap.',
                                '2050, unlimited max. cap.', '2050, limited max. cap.'],
                         loc="lower left")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    # plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
    # reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_maxCAPscale_study_DAC_S_' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[0].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[0].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_psm_years_maxCAPscale.cases[0].res['CAPgen_ins_array'] / 1000, CS_psm_years_maxCAPscale.cases[0].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_MPI[1])

    plt.title('DAC-S, Year: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['unlimited max. cap.', 'limited max. cap.'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
               #reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_maxCAPscale_study_DAC_S_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[2].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_psm_years_maxCAPscale.cases[2].res['CAPgen_ins_array'] / 1000,
            CS_psm_years_maxCAPscale.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20,
            color=colors_MPI[1])

    plt.title('DAC-S, Year: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 1000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['unlimited max. cap.', 'limited max. cap.'],
                         loc="upper right")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
               #reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_maxCAPscale_study_DAC_S_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)

    plt.show()

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_plm_years.cases[0].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[0].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_blue_MPI[0])
    ax.plot(CS_plm_years_maxCAPscale.cases[0].res['CAPgen_ins_array'] / 1000,
            CS_plm_years_maxCAPscale.cases[0].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_blue_MPI[2])

    ax.plot(CS_plm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[2].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_red_MPI[0])
    ax.plot(CS_plm_years_maxCAPscale.cases[2].res['CAPgen_ins_array'] / 1000,
            CS_plm_years_maxCAPscale.cases[2].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_red_MPI[2])

    plt.title('DAC-L', y=0.93)
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['2020, unlimited max. cap.', '2020, limited max. cap.',
                          '2050, unlimited max. cap.', '2050, limited max. cap.'],
                         loc="upper right", bbox_to_anchor=(1, 0.90))  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    # plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
    # reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_maxCAPscale_study_DAC_L_' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()


    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)
    counter = 0

    ax.plot(CS_plm_years.cases[0].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[0].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_plm_years_maxCAPscale.cases[0].res['CAPgen_ins_array'] / 1000,
            CS_plm_years_maxCAPscale.cases[0].res['LCOMeOH_selected'], marker='.', markersize=20,
            color=colors_MPI[1])
    counter = counter + 1

    plt.title('DAC-L, Year: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['unlimited max. cap.', 'limited max. cap.'],
                         loc="upper right")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0,
               #reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_maxCAPscale_study_DAC_L_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_plm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[2].res['LCOMeOH_selected'],
            marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_plm_years_maxCAPscale.cases[2].res['CAPgen_ins_array'] / 1000,
            CS_plm_years_maxCAPscale.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20,
            color=colors_MPI[1])

    plt.title('DAC-L, Year: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 1000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['unlimited max. cap.', 'limited max. cap.'], loc="upper right")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_maxCAPscale_study_DAC_L_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()


plot_noGrid = 0
if plot_noGrid == 1:

    dLCOMeOH_grid = CS_psm_years.cases[0].res['dLCOMeOH']['Grid']
    LCOMeOH_noGrid = CS_psm_years.cases[0].res['LCOMeOH_selected'] - dLCOMeOH_grid

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[0].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[0].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_psm_years.cases[0].res['CAPgen_ins_array'] / 1000, LCOMeOH_noGrid, marker='.', markersize=20, color=colors_MPI[1])

    plt.title('DAC-S, Year: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['grid', 'no grid'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_noGrid_study_DAC_S_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

    dLCOMeOH_grid = CS_psm_years.cases[2].res['dLCOMeOH']['Grid']
    LCOMeOH_noGrid = CS_psm_years.cases[2].res['LCOMeOH_selected'] - dLCOMeOH_grid

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_psm_years.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_psm_years.cases[2].res['CAPgen_ins_array'] / 1000, LCOMeOH_noGrid, marker='.', markersize=20, color=colors_MPI[1])

    plt.title('DAC-S, Year: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 1000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['grid', 'no grid'], loc="upper right")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_noGrid_study_DAC_S_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()






    dLCOMeOH_grid = CS_plm_years.cases[0].res['dLCOMeOH']['Grid']
    LCOMeOH_noGrid = CS_plm_years.cases[0].res['LCOMeOH_selected'] - dLCOMeOH_grid

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_plm_years.cases[0].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[0].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_plm_years.cases[0].res['CAPgen_ins_array'] / 1000, LCOMeOH_noGrid, marker='.', markersize=20, color=colors_MPI[1])

    plt.title('DAC-L, Year: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['grid', 'no grid'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_noGrid_study_DAC_L_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

    dLCOMeOH_grid = CS_plm_years.cases[2].res['dLCOMeOH']['Grid']
    LCOMeOH_noGrid = CS_plm_years.cases[2].res['LCOMeOH_selected'] - dLCOMeOH_grid

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_plm_years.cases[2].res['CAPgen_ins_array'] / 1000, CS_plm_years.cases[2].res['LCOMeOH_selected'], marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_plm_years.cases[2].res['CAPgen_ins_array'] / 1000, LCOMeOH_noGrid, marker='.', markersize=20, color=colors_MPI[1])

    plt.title('DAC-L, Year: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 1000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['grid', 'no grid'], loc="upper right")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_noGrid_study_DAC_L_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



plot_DAC_S_vs_DAC_L = 0
if plot_DAC_S_vs_DAC_L == 1:

    LCOMeOH_DAC_S = CS_psm_years.cases[0].res['LCOMeOH_selected']
    LCOMeOH_DAC_L = CS_plm_years.cases[0].res['LCOMeOH_selected']

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[0].res['CAPgen_ins_array'] / 1000, LCOMeOH_DAC_S, marker='.', markersize=20, color=colors_MPI[0])
    ax.plot(CS_plm_years.cases[0].res['CAPgen_ins_array'] / 1000, LCOMeOH_DAC_L, marker='.', markersize=20, color=colors_MPI[1])

    plt.title('DAC-S vs. DAC-L: ' + '2020')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    #plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['DAC-S', 'DAC-L'], loc="upper right")   # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    #plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_DAC_S_vs_DAC_L_' + '2020' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()



    LCOMeOH_DAC_S = CS_psm_years.cases[2].res['LCOMeOH_selected']
    LCOMeOH_DAC_L = CS_plm_years.cases[2].res['LCOMeOH_selected']

    fig, ax = plt.subplots(figsize=(6, 6), dpi=600)

    ax.plot(CS_psm_years.cases[0].res['CAPgen_ins_array'] / 1000, LCOMeOH_DAC_S, marker='.', markersize=20,
            color=colors_MPI[0])
    ax.plot(CS_plm_years.cases[0].res['CAPgen_ins_array'] / 1000, LCOMeOH_DAC_L, marker='.', markersize=20,
            color=colors_MPI[1])

    plt.title('DAC-S vs. DAC-L: ' + '2050')
    plt.xlabel('Grid output capacity (MW)')
    plt.ylabel('LCOMeOH (USD/t)')
    plt.ylim(0, 2000)
    # plt.legend(Cases, bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
    legend1 = plt.legend(['DAC-S', 'DAC-L'],
                         loc="upper right")  # longest entry from previous legends (to replicated aspect ratio)
    plt.gca().add_artist(legend1)
    # plt.legend(['WEL replace'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0, reverse=True)  # longest entry from previous legends (to replicated aspect ratio)

    plt.tight_layout()
    fig_name = 'fig_DAC_S_vs_DAC_L_' + '2050' + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

x=1