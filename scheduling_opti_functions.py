import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from utility_functions import annual_factor, colors_stacked_bar, figure_subfolder
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition
import numpy as np
import os.path



def build_schedule_model(DE, CAPgen, CAP_ins, S_ins, minCAP, rampLimit, timer):
    # report_timing()
    m = pyo.ConcreteModel()

    # Sets
    m.p = pyo.Set(initialize=DE.keys())  # Processes
    m.c = pyo.Set(initialize=DE['MTS'].stoich.keys())  # Components
    m.s = pyo.Set(initialize=['CGH2', 'BAT', 'CO2tank', 'TES'])
    m.t = pyo.Set(initialize=range(CAPgen.shape[0]))  # Time periods (hours)

    # Parameters
    def stoich_init(m, p, c):
        return DE[p].stoich[c]

    # generating table of stoichiometric coefficients
    #dict_stoich = {}
    #for p in DE.keys():
    #    dict_stoich.update({p : DE[p].stoich})

    #dict_stoich.pop('TES_in')
    #dict_stoich.pop('TES_out')
    #dict_stoich.pop('HP_int')

    #df_stoich = pd.DataFrame.from_dict(dict_stoich, orient="index")

    m.stoich = pyo.Param(m.p, m.c, initialize=stoich_init)
    m.CAP_ins = pyo.Param(m.p, initialize=CAP_ins, mutable=True)
    m.S_ins = pyo.Param(m.s, initialize=S_ins, mutable=True)
    m.CAPgen = pyo.Param(m.t, initialize=CAPgen, mutable=True)
    m.minCAP = pyo.Param(m.p, initialize=minCAP, mutable=True)
    m.rampLimit = pyo.Param(m.p, initialize=rampLimit)

    # Variables
    m.CAP = pyo.Var(m.p, m.t, domain=pyo.NonNegativeReals)
    m.F_ext = pyo.Var(m.c, m.t, domain=pyo.Reals)
    m.S = pyo.Var(m.s, m.t, domain=pyo.NonNegativeReals)
    m.MeOH_prod = pyo.Var(domain=pyo.Reals)
    m.delta_CAP_POS = pyo.Var(m.p, m.t, domain=pyo.NonNegativeReals)
    m.delta_CAP_NEG = pyo.Var(m.p, m.t, domain=pyo.NonNegativeReals)

    # Objective function
    def objective_function(m):
        return m.MeOH_prod * 32 / 1000

    # Constraints
    def MeOH_prod_constraint(m):
        return m.MeOH_prod == pyo.quicksum(m.F_ext['MeOH', t] for t in m.t)

    def delta_CAP_constraint(m, p, t):
        if t < (8760 - 1):
            return (m.CAP[p, t + 1] - m.CAP[p, t]) / 1 == m.delta_CAP_POS[p, t] - m.delta_CAP_NEG[p, t]
        else:
            return (m.CAP[p, 0] - m.CAP[p, t]) / 1 == m.delta_CAP_POS[p, t] - m.delta_CAP_NEG[p, t]

    def CAP_constraint(m, p, t):
        return m.CAP[p, t] <= m.CAP_ins[p]

    def minCAP_constraint(m, p, t):
        return m.CAP[p, t] >= m.minCAP[p] * m.CAP_ins[p]

    def rampLimit_up_constraint(m, p, t):
        if t < (8760 - 1):
            return (m.CAP[p, t + 1] - m.CAP[p, t]) / 1 >= (-1) * m.rampLimit[p] * m.CAP_ins[p]
        else:
            return (m.CAP[p, 0] - m.CAP[p, t]) / 1 >= (-1) * m.rampLimit[p] * m.CAP_ins[p]

    def rampLimit_down_constraint(m, p, t):
        if t < (8760 - 1):
            return (m.CAP[p, t + 1] - m.CAP[p, t]) / 1 <= m.rampLimit[p] * m.CAP_ins[p]
        else:
            return (m.CAP[p, 0] - m.CAP[p, t]) / 1 <= m.rampLimit[p] * m.CAP_ins[p]

    def S_constraint(m, s, t):
        return m.S[s, t] <= m.S_ins[s]

    def MB_component_constraint(m, c, t):
        if c not in m.s:
            return pyo.quicksum(m.CAP[p, t] * m.stoich[p, c] for p in m.p) == m.F_ext[c, t]
        else:
            return pyo.Constraint.Skip

    def F_ext_constraint(m, c, t):
        if c not in m.s:
            if c not in ['MeOH', 'qamb', 'H2O']:
                if c == 'e':
                    return m.F_ext[c, t] == m.CAPgen[t] * (-1)
                elif c in ['q50', 'q100', 'e_curt']:
                    return m.F_ext[c, t] >= 0
                else:
                    return m.F_ext[c, t] == 0
            else:
                return pyo.Constraint.Skip
        return pyo.Constraint.Skip

    def S_balance_constraint(m, s, t):
        if t < (8760 - 1):
            return m.S[s, t + 1] == m.S[s, t] + 1 * (sum(m.CAP[p, t] * m.stoich[p, s] for p in m.p))
        else:
            return m.S[s, 0] == m.S[s, t] + 1 * (sum(m.CAP[p, t] * m.stoich[p, s] for p in m.p))

    m.objective = pyo.Objective(rule=objective_function, sense=pyo.maximize)

    m.MeOH_prod_constraint = pyo.Constraint(rule=MeOH_prod_constraint)
    m.delta_CAP_constraint = pyo.Constraint(m.p, m.t, rule=delta_CAP_constraint)
    m.CAP_constraint = pyo.Constraint(m.p, m.t, rule=CAP_constraint)
    m.minCAP_constraint = pyo.Constraint(m.p, m.t, rule=minCAP_constraint)
    m.rampLimit_up_constraint = pyo.Constraint(m.p, m.t, rule=rampLimit_up_constraint)
    m.rampLimit_down_constraint = pyo.Constraint(m.p, m.t, rule=rampLimit_down_constraint)

    m.MB_component_constraint = pyo.Constraint(m.c, m.t, rule=MB_component_constraint)
    m.F_ext_constraint = pyo.Constraint(m.c, m.t, rule=F_ext_constraint)

    m.S_constraint = pyo.Constraint(m.s, m.t, rule=S_constraint)
    m.S_balance_constraint = pyo.Constraint(m.s, m.t, rule=S_balance_constraint)

    DT_equations = timer.toc(msg=None)

    # Solver
    opt = pyo.SolverFactory('gurobi_persistent')  # Choose solver
    opt.set_instance(m)
    DT_write_model = timer.toc(msg=None)

    return m, opt, DT_equations, DT_write_model


def extract_results(m, plotting, resampling):
    CAP_val = {(p, t): m.CAP[p, t].value for p in m.p for t in m.t}
    df_CAP = pd.DataFrame.from_dict(CAP_val, orient='index', columns=['CAP']).reset_index()
    df_CAP[['proc', 't']] = pd.DataFrame(df_CAP['index'].tolist(), index=df_CAP.index)
    df_CAP = df_CAP.pivot(index='t', columns='proc', values='CAP')
    df_CAP['GEN'] = [m.CAPgen[t].value for t in m.t]


    df_CAP_m = df_CAP[['WEL', 'MTS', 'DAC', 'CGH2_in', 'CGH2_out', 'CO2tank_in', 'CO2tank_out']]
    df_CAP_e = df_CAP[['GEN', 'Curt', 'HP_amb', 'HP_int', 'BAT_in', 'BAT_out', 'TES_in', 'TES_out']]

    S_val = {(s, t): m.S[s, t].value for s in m.s for t in m.t}
    df_S = pd.DataFrame.from_dict(S_val, orient='index', columns=['S']).reset_index()
    df_S[['stor', 't']] = pd.DataFrame(df_S['index'].tolist(), index=df_S.index)
    df_S = df_S.pivot(index='t', columns='stor', values='S')

    minCAP_MTS = round(min(df_CAP_m['MTS']/max(df_CAP_m['MTS'])),2)
    minCAP_DAC = round(min(df_CAP_m['DAC']/max(df_CAP_m['DAC'])),2)

    cap_gen_MW = int(round(max(df_CAP_e['GEN']/1000)/10,0)*10)

    interactive_plot=0
    if plotting == 1:
        if interactive_plot==1:
            fig = px.line(df_CAP_m, x=df_CAP_m.index, y=df_CAP_m.columns, markers=True, title='Capacity profile [kmol/h]')
            fig.show()

            fig = px.line(df_CAP_e, x=df_CAP_e.index, y=df_CAP_e.columns, markers=True, title='Capacity profile [kWh/h]')
            fig.show()

            fig = px.line(df_S, x=df_S.index, y=df_S.columns, markers=True, title='Storage profile [kmol or kWh]')
            fig.show()

        # matplotlib plots--------------------------------
        gray = np.array([100, 100, 100]) / 255
        white = np.array([255, 255, 255]) / 255
        black = np.array([0, 0, 0]) / 255
        blue_MPI = np.array((51 / 255, 165 / 255, 195 / 255))
        red_MPI = np.array((120 / 255, 0 / 255, 75 / 255))
        green_MPI = np.array((0 / 255, 118 / 255, 117 / 255))
        darkening = 60
        yellow_MPI = np.array([236 - darkening, 233 - darkening, 212 - darkening]) / 255

        colors = [blue_MPI, black, red_MPI]


        fig, ax = plt.subplots(2,2, figsize=(18, 8), dpi=600)
        counter=0
        for column in df_CAP_m.columns[0:3]:
            ax[0, 0].plot(df_CAP_m.index, df_CAP_m[column], marker='o', label=column, color=colors[counter], alpha=0.75)
            counter += 1

        #ax.set_title('Capacity profile [kmol/h]', fontsize=20)
        #ax[0, 0].set_xlabel('Time (h)', fontsize=18)
        ax[0, 0].set_ylabel('Capacity profile (kmol/h)', fontsize=18)
        ax[0, 0].legend(loc='upper right', fontsize=15)
        ax[0, 0].set_xlim([0, 8760])
        ax[0, 0].set_ylim(bottom=0)

        counter = 0
        for column in df_CAP_m.columns[0:3]:
            ax[0, 1].plot(df_CAP_m.index, df_CAP_m[column], marker='o', label=column, color=colors[counter], alpha=0.75)
            counter += 1

        # ax.set_title('Capacity profile [kmol/h]', fontsize=20)
        #ax[0, 1].set_xlabel('Time (h)', fontsize=18)
        #ax[0, 1].set_ylabel('Capacity profile (kmol/h)', fontsize=18)
        ax[0, 1].legend(loc='upper right', fontsize=15)
        ax[0, 1].set_xlim([4400, 4600])
        ax[0, 1].set_ylim(bottom=0)



        colors = [green_MPI, blue_MPI, red_MPI]

        counter = 0
        for column in df_S.columns[0:3]:
            ax[1, 0].plot(df_S.index, df_S[column]/1000, marker='o', label=column, color=colors[counter], alpha=0.75)
            counter += 1

        # ax.set_title('Capacity profile [kmol/h]', fontsize=20)
        ax[1, 0].set_xlabel('Time (h)', fontsize=18)
        ax[1, 0].set_ylabel('Storage (Mmol or MWh)', fontsize=18)
        ax[1, 0].legend(loc='upper right', fontsize=15)
        ax[1, 0].set_xlim([0, 8760])
        ax[1, 0].set_ylim(bottom=0)


        counter = 0
        for column in df_S.columns[0:3]:
            ax[1, 1].plot(df_S.index, df_S[column]/1000, marker='o', label=column, color=colors[counter], alpha=0.75)
            counter += 1

        # ax.set_title('Capacity profile [kmol/h]', fontsize=20)
        ax[1, 1].set_xlabel('Time (h)', fontsize=18)
        ax[1, 1].legend(loc='upper right', fontsize=15)
        ax[1, 1].set_xlim([4400, 4600])
        ax[1, 1].set_ylim(bottom=0)



        plt.tight_layout()



        fig_name = 'fig_SCHEDULE_' + 'minCAP_DAC_' + str(minCAP_DAC) + '_MTS_' + str(minCAP_MTS) + '_' + str(cap_gen_MW) + '_MW.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()





    if resampling == 1 and plotting == 1:
        df_CAP_m_2h = df_CAP_m.copy()
        df_CAP_e_2h = df_CAP_e.copy()
        df_S_2h = df_S.copy()

        df_CAP_m_2h.index = pd.to_timedelta(df_CAP_m_2h.index, unit='h')
        df_CAP_e_2h.index = pd.to_timedelta(df_CAP_e_2h.index, unit='h')
        df_S_2h.index = pd.to_timedelta(df_S_2h.index, unit='h')

        df_CAP_m_2h = df_CAP_m_2h.resample('2h').mean()
        df_CAP_e_2h = df_CAP_e_2h.resample('2h').mean()
        df_S_2h = df_S_2h.resample('2h').mean()

        fig = px.line(df_CAP_m_2h, x=df_CAP_m_2h.index, y=df_CAP_m_2h.columns, markers=True, title='Resampled capacity profile [kmol/h]')
        fig.show()

        fig = px.line(df_CAP_e_2h, x=df_CAP_e_2h.index, y=df_CAP_e_2h.columns, markers=True, title='Resampled capacity profile [kWh/h]')
        fig.show()

        fig = px.line(df_S_2h, x=df_S_2h.index, y=df_S_2h.columns, markers=True, title='Resampled storage profile [kmol or kWh]')
        fig.show()

    return df_CAP, df_S


def solve_schedule_model(m, opt, plotting):
    results = opt.solve(m, save_results=False, tee=False)  # Solve the instance

    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        df_CAP, df_S = extract_results(m, plotting, 0)
        Production_annual_t = m.MeOH_prod.value * 32 / 1000
        #print('Obj. MeOH production (t/a) = ', round(m.objective(), 2))

        CAP_ins_actual = {column: max(df_CAP[column]) for column in df_CAP.columns}
        S_ins_actual = {column: max(df_S[column] - min(df_S[column])) for column in df_S.columns}

        solver_status = results.solver.status

    elif (results.solver.termination_condition == TerminationCondition.infeasible):   # Do something when model is infeasible
        solver_status = results.solver.status
        print('Model is infeasible')
        Production_annual_t = 1
        CAP_ins_actual = {  'WEL': 1,  # [kmol/h]
                            'DAC': 1,
                            'MTS': 1,
                            'HP_amb': 1,  # [kWh/h]
                            'HP_int': 0,
                            "BAT_in": 0,  # ATB NREL - typical 4h battery duration
                            "BAT_out": 0,
                            "CGH2_in": 0,
                            "CGH2_out": 0,
                            "TES_in": 0,
                            "TES_out": 0,
                            "CO2tank_in": 0,
                            "CO2tank_out": 0,
                            "Curt": 1}
        CAP_ins_actual['GEN'] = 100

        S_ins_actual = {'CGH2': 0,
                      'CO2tank': 0,
                      'BAT': 0,
                      'TES': 0}

    else:
        solver_status = results.solver.status
        print("Solver Status: ", results.solver.status)       # Something else is wrong
        Production_annual_t = 1
        CAP_ins_actual = {'WEL': 1,  # [kmol/h]
                          'DAC': 1,
                          'MTS': 1,
                          'HP_amb': 1,  # [kWh/h]
                          'HP_int': 0,
                          "BAT_in": 0,  # ATB NREL - typical 4h battery duration
                          "BAT_out": 0,
                          "CGH2_in": 0,
                          "CGH2_out": 0,
                          "TES_in": 0,
                          "TES_out": 0,
                          "CO2tank_in": 0,
                          "CO2tank_out": 0,
                          "Curt": 1}
        CAP_ins_actual['GEN'] = 100

        S_ins_actual = {'CGH2': 0,
                        'CO2tank': 0,
                        'BAT': 0,
                        'TES': 0}

    return Production_annual_t, CAP_ins_actual, S_ins_actual, solver_status


def rebuild_schedule_model(m, opt, CAP_ins, CAP_ins_new, S_ins, S_ins_new, minCAP, minCAP_new):
    # identify which processes and storages have a changed installed capacity
    diff_CAP_ins_keys = []
    for key in CAP_ins.keys():
        if CAP_ins[key] != CAP_ins_new[key]:
            diff_CAP_ins_keys.append(key)

    diff_minCAP_keys = []
    for key in minCAP.keys():
        if minCAP[key] != minCAP_new[key]:
            diff_minCAP_keys.append(key)

    diff_S_ins_keys = []
    for key in S_ins.keys():
        if S_ins[key] != S_ins_new[key]:
            diff_S_ins_keys.append(key)

    # adjust constraint with processes with a changed installed capacity
    # removing constraints, which need to be adjusted
    for t in m.t:
        for p in m.p:
            if p in diff_CAP_ins_keys:
                opt.remove_constraint(m.CAP_constraint[p, t])
                opt.remove_constraint(m.rampLimit_up_constraint[p, t])
                opt.remove_constraint(m.rampLimit_down_constraint[p, t])
                m.CAP_ins[p].value = CAP_ins_new[p]

        for p in m.p:
            if p in diff_minCAP_keys:
                opt.remove_constraint(m.minCAP_constraint[p, t])
                m.minCAP[p].value = minCAP_new[p]

    # adding new constraints

    for t in m.t:
        for p in m.p:
            if p in diff_CAP_ins_keys:
                opt.add_constraint(m.CAP_constraint[p, t])
                opt.add_constraint(m.rampLimit_up_constraint[p, t])
                opt.add_constraint(m.rampLimit_down_constraint[p, t])

        for p in m.p:
            if p in diff_minCAP_keys:
                opt.add_constraint(m.minCAP_constraint[p, t])

    # adjust constraint with storages with a changed installed capacity
    for t in m.t:
        for s in m.s:
            if s in diff_S_ins_keys:
                opt.remove_constraint(m.S_constraint[s, t])
                m.S_ins[s].value = S_ins_new[s]

    for t in m.t:
        for s in m.s:
            if s in diff_S_ins_keys:
                opt.add_constraint(m.S_constraint[s, t])

    return m, opt


def calc_LCOMeOH(DE, ratio_wind_solar, Production_annual_t, CAP_ins, S_ins, NU, YEAR, CMP, CAPEXgen, CAPEXgrid, Annual_land_lease_costs, switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes, plotting):
    # Economic evaluation
    plant_lifetime = 25
    f_cr = annual_factor(0.07, plant_lifetime)
    CAP_ins_unit = {}
    CAPEX_unit = {}
    CAPEX = {}
    dLCOMeOH = {}

    Production_annual_kmol = Production_annual_t / 32                               # [kmolMeOH/a]
    Production_annual_kmol_CO2 = Production_annual_kmol / DE['MTS'].stoich['MeOH']  # [kmolCO2/a]
    Production_annual_t_CO2 = Production_annual_kmol_CO2 * 44                       # [tCO2/a] total CO2 produced per year

    dLCOMeOH['DACsorb'] = Production_annual_t_CO2 * DE['DAC'].costs_sorbent_per_tCO2[DE['DAC'].DAC_type] / Production_annual_t  # [$/tMeOH]

    for k in CAP_ins.keys():
        if k in ['WEL', 'DAC', 'MTS', 'HP_int', 'HP_amb']:
            CAP_ins_unit[k] = CAP_ins[k] / NU[k]

    CAPEX_unit['WEL'] = DE['WEL'].scale_capex_WEL(CAP_ins_unit['WEL'], switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes)[0][YEAR]* CAP_ins_unit['WEL']
    Cost_stack_replacement_WEL = DE['WEL'].scale_capex_WEL(CAP_ins_unit['WEL'], switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes)[3][YEAR] * CAP_ins_unit['WEL']
    CAPEX_unit['DAC'] = DE['DAC'].scale_capex_DAC(CAP_ins_unit['DAC'], switch_capex_max_cap_scaling, switch_capex_max_cap_scaling_equal_sizes)[0][YEAR] * CAP_ins_unit['DAC']
    CAPEX_unit['MTS'] = DE['MTS'].scale_capex_MTS(CAP_ins_unit['MTS'])[0][YEAR] * CAP_ins_unit['MTS']
    CAPEX_unit['HP_int'] = DE['HP_int'].scale_capex_HP(CAP_ins_unit['HP_int'])[0][YEAR] * CAP_ins_unit['HP_int']
    CAPEX_unit['HP_amb'] = DE['HP_amb'].scale_capex_HP(CAP_ins_unit['HP_amb'])[0][YEAR] * CAP_ins_unit['HP_amb']

    for k in CAP_ins.keys():
        if k in ['WEL', 'DAC', 'MTS', 'HP_int', 'HP_amb']:
            CAPEX[k] = CAPEX_unit[k] * NU[k] * DE[k].eon_multiplier(NU[k], CMP[k])
            dLCOMeOH[k] = CAPEX[k] * f_cr / Production_annual_t

    dLCOMeOH_stack_replacement = Cost_stack_replacement_WEL / plant_lifetime / Production_annual_t

    capex_RO = 821 * DE['CGH2_in'].CEPCI['2022'] / DE['CGH2_in'].CEPCI['2017'] # capex of reverse osmosis [$ 2022 / (kmolH20/h)] ref: Alkaisi et al. 2017, (696 EUR/ (kmolH2O/h) used in Svitnic and Sundmacher 2022)
    RO_max_needed_capacity_kmol_h = -1* (DE['DAC'].stoich['H2O'] * CAP_ins_unit['DAC'] * NU['DAC'] + DE['WEL'].stoich['H2O'] * CAP_ins_unit['WEL'] * NU['WEL'] )
    CAPEX_RO = capex_RO * RO_max_needed_capacity_kmol_h

    capex_s = {}
    capex_BAT = {}
    capex_TES = {}
    capex_CGH2 = {}
    capex_CO2tank = {}

    BAT_hours_storage = 4
    capex_BAT['2020'] = 2101/BAT_hours_storage  # [$/kWh]   moderate scenario for 4h storage, reference: https://atb.nrel.gov/electricity/2024/technologies
    capex_BAT['2030'] = 1451/BAT_hours_storage  # [$/kWh]
    capex_BAT['2050'] = 1036/BAT_hours_storage  # [$/kWh]

    capex_s['BAT'] = capex_BAT

    capex_TES['2020'] = 80  # [$/kWh]      JUST A GUESS AT THIS POINT (80!)
    capex_TES['2030'] = 80  # [$/kWh]      JUST A GUESS AT THIS POINT (80!)
    capex_TES['2050'] = 80  # [$/kWh]      JUST A GUESS AT THIS POINT (80!)

    capex_s['TES'] = capex_TES

    capex_CGH2['2020'] = 560 * 2        # [$/kmol H2]  pessimistic case from Fulham et al. 2024 (730 $/kg)
    capex_CGH2['2030'] = 560 * 2        # [$/kmol H2]  base case from Fulham et al. 2024 (560 $/kg)
    capex_CGH2['2050'] = 560 * 2        # [$/kmol H2]  optimistic case from Fulham et al. 2024 (400 $/kg)

    capex_s['CGH2'] = capex_CGH2

    capex_CO2tank['2020'] = 18 * 44    # [$/kmol CO2] pessimistic case from Fulham et al. 2024 (26 $/kg)
    capex_CO2tank['2030'] = 18 * 44    # [$/kmol CO2] base case from Fulham et al. 2024 (18 $/kg)
    capex_CO2tank['2050'] = 18 * 44    # [$/kmol CO2] optimistic case from Fulham et al. 2024 (14 $/kg)

    capex_s['CO2tank'] = capex_CO2tank


    CAPEX_s = {}
    dLCOMeOH_s = {}
    for k in S_ins.keys():
        CAPEX_s[k] = S_ins[k] * capex_s[k][YEAR]
        dLCOMeOH_s[k] = CAPEX_s[k] * f_cr / Production_annual_t

    if CAPEX_s['CGH2'] > 0: # adding compressor costs if H2 storage is selected (need a condition because the correlation incorporates fixed costs)
        CAPEX_CGH2_compressor = (8400 + 3100*(CAP_ins['CGH2_in']*DE['CGH2_in'].stoich['e']*(-1))**0.6) * DE['CGH2_in'].CEPCI['2022'] / DE['CGH2_in'].CEPCI['2007']     # [$ 2022] cost correlation based on Towler and Sinnott 2008
        CAPEX_s['CGH2'] = CAPEX_s['CGH2'] + CAPEX_CGH2_compressor


    dLCOMeOH_gen = CAPEXgen * f_cr / Production_annual_t
    dLCOMeOH_grid = CAPEXgrid * f_cr / Production_annual_t
    dLCOMeOH_land_lease = Annual_land_lease_costs / Production_annual_t

    dLCOMeOH_RO = CAPEX_RO * f_cr / Production_annual_t

    CAPEX_p_sum = sum(CAPEX.values())
    CAPEX_s_sum = sum(CAPEX_s.values())
    dLCOMeOH_p_sum = sum(dLCOMeOH.values())
    dLCOMeOH_s_sum = sum(dLCOMeOH_s.values())

    CAPEX_TOTAL = CAPEX_p_sum + CAPEX_s_sum + CAPEXgen + CAPEXgrid + CAPEX_RO

    # indirect OPEX calculations

    # labor costs (based on Albrecht et al. 2017, originally on Peters et al. standard costing textbook)
    N_processing_steps = 5 # number of processing steps (GEN, WEL, DAC, MTS syn, MTS sep)
    operating_labor_hours_per_year = 2.13 * (Production_annual_t*1000/8760)**0.242 * N_processing_steps*8760/24
    operator_salary = 40000                                     # [$/a] estimate based on value between Oman, Brazil and US, ref: Young et al. 2023
    working_hours_in_a_year = 2080                              # [work hours h/a] estimation based on 52 weeks with 40 hour work week
    hourly_wage = operator_salary/working_hours_in_a_year       # [$/h]
    operating_labor_costs = operating_labor_hours_per_year * hourly_wage
    operating_supervision_costs = 0.15 * operating_labor_costs
    laboratory_charges = 0.2 * operating_labor_costs

    maintenance_labor_costs = CAPEX_TOTAL * 0.02 / plant_lifetime
    maintenance_material_costs = CAPEX_TOTAL * 0.02 / plant_lifetime
    insurance_and_taxes = CAPEX_TOTAL * 0.02 / plant_lifetime
    operating_supplies = (maintenance_material_costs + maintenance_labor_costs) * 0.15

    total_labor_costs = operating_labor_costs + operating_supervision_costs + maintenance_labor_costs
    plant_overhead_costs = 0.6 * total_labor_costs
    administrative_costs = 0.25 * plant_overhead_costs

    indirect_OPEX = total_labor_costs + maintenance_material_costs + operating_supplies + laboratory_charges + insurance_and_taxes + plant_overhead_costs + administrative_costs
    indirect_CAPEX = 0.10 * CAPEX_TOTAL

    dLCOMeOH_indir_OPEX = indirect_OPEX / Production_annual_t
    dLCOMeOH_indir_CAPEX = indirect_CAPEX * f_cr / Production_annual_t

    LCOMeOH = dLCOMeOH_p_sum + dLCOMeOH_s_sum + dLCOMeOH_gen + dLCOMeOH_grid + dLCOMeOH_indir_CAPEX + dLCOMeOH_indir_OPEX + dLCOMeOH_land_lease + dLCOMeOH_RO + dLCOMeOH_stack_replacement

    dLCOMeOH_all = {}
    dLCOMeOH_all['Generation'] = dLCOMeOH_gen
    dLCOMeOH_all['Grid'] = dLCOMeOH_grid
    dLCOMeOH_all['Land lease'] = dLCOMeOH_land_lease
    dLCOMeOH_all['RO'] = dLCOMeOH_RO


    for k in dLCOMeOH.keys():
        dLCOMeOH_all[k] = dLCOMeOH[k]

    dLCOMeOH_all['WEL replace'] = dLCOMeOH_stack_replacement
    for k in dLCOMeOH_s.keys():
        dLCOMeOH_all[k] = dLCOMeOH_s[k]

    dLCOMeOH_all['indir_CAPEX'] = dLCOMeOH_indir_CAPEX
    dLCOMeOH_all['indir_OPEX'] = dLCOMeOH_indir_OPEX

    df_LCOMeOH_stacked_bar = pd.DataFrame(dLCOMeOH_all, index=[0])
    if plotting == 1:
        df_LCOMeOH_stacked_bar.plot(kind='bar', stacked=True, figsize=(10, 6))
        plt.xlabel('run')
        plt.ylabel('LCOMeOH (USD/t)')
        plt.legend(reverse=True)
        plt.show()

    return LCOMeOH, dLCOMeOH_all