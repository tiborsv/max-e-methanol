from dataclasses import dataclass, field
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utility_functions import figure_subfolder
import os.path

@dataclass(kw_only=True)
class Process:
    name: str
    description: str
    LR: float = float("nan")
    EUR_to_USD: float = 1.10    # roughly the average for the last 5 years [https://www.google.com/finance/quote/EUR-USD?sa=X&ved=2ahUKEwiJzZz9o4qHAxVZg_0HHSkED0YQmY0JegQIBxAw&window=5Y]

    M: dict = field(default_factory = lambda: { "MeOH"  :32,
                                                 "H2"   : 2,
                                                 "CO2"  :44,
                                                 "H2O"  :18}) # molar weight [kg/kmol]

    LHV_MJ_kg: dict = field(default_factory = lambda: { "MeOH"  :19.9,
                                                         "H2"   :120,
                                                         "CO2"  :0,
                                                         "H2O"  :0}) # lower heating value [MJ/kg] ref: engineering toolbox

    HHV_MJ_kg: dict = field(default_factory = lambda: { "MeOH"  :23,
                                                         "H2"   :142,
                                                         "CO2"  :0,
                                                         "H2O"  :0}) # higher heating value [MJ/kg] ref: engineering toolbox


    CEPCI: dict = field(default_factory = lambda: { "2000" :394.1,
                                                    "2005" :468.2,
                                                    "2007" :525.4,
                                                    "2009" :521.9,
                                                    "2011" :585.7,
                                                    "2015" :556.8,
                                                    "2017" :567.5,
                                                    "2016" :541.7,
                                                    "2018" :603.1,
                                                    "2019" :607.5,
                                                    "2020" :596.2,
                                                    "2021" :708.8,
                                                    "2022" :816.0,
                                                    "2023" :800.8}) # Chemical Engineering Plant Cost Index [-] ref: https://www.training.itservices.manchester.ac.uk/public/gced/CEPCI.html?reactors/CEPCI/index.html

    stoich: dict = field(default_factory = lambda: {"MeOH" :0,
                                                    "H2"   :0,
                                                    "CO2"  :0,
                                                    "H2O"  :0,
                                                    "e"    :0,
                                                    "e_curt":0,
                                                    "q100" :0,
                                                    "q50"  :0,
                                                    "qamb" :0,
                                                    "BAT"  :0,
                                                    "CGH2" :0,
                                                    "CO2tank" :0,
                                                    "TES": 0}) # ambient heat source for heat pump (variable T)

    RO_desal_elec_req_kmolH2O_h: float = 0.11  # [kW/(kmol/h)] electricity requirement for reverse osmosis (RO) desalination per molecule of water (ref. Al-Kharagouli et al. 2013)

    def calc_flows(self, cap_kmol_hr_or_kW):
        flows = {key: value * cap_kmol_hr_or_kW for key, value in self.stoich.items()}
        return flows

    def eon_multiplier(self, N_units, LR):
        ''' function to calculate the average capex scaling multiplier (Y_cumul_avg) for economies of numbers
        based on the works of Chen and Grossmann 2019, Arora et al. 2019 and Palys et al. 2019 '''

        b = - np.log(1-LR)/np.log(2)        # [-] learning rate exponent

        Y = np.zeros(N_units)               # [-] multiplier for Xth unit
        Y_cumul = np.zeros(N_units)         # [-] cumulative multiplier Y until Xth unit
        Y_cumul_avg = np.zeros(N_units)     # [-] average multiplier Y from first to Xth unit

        for X in np.arange(1,N_units+1):
            X0 = 1                          # [-] assuming reference (initial) number of units to be 1, as in Arora et al. 2019
            Y[X-1] = (X/X0)**-b
            if X > 1:
                Y_cumul[X-1] = Y_cumul[X-2] + Y[X-1]
            else:
                Y_cumul[X-1] = 1

            Y_cumul_avg = Y_cumul / np.arange(1,N_units+1)

        return Y_cumul_avg[-1]


@dataclass(kw_only=True)
class WEL(Process):
    WEL_type: str
    reference_for_costs: str = 'Boehm et al. 2020'
    cap_MWel_ref: float = 5     # [MWel] reference capacity for capex scaling in MWel input

    WEL_efficiency_LHV: dict = field(default_factory = lambda: {"AEC": 0.68,
                                                                "PEM": 0.68,
                                                               "SOEC": 0.85}) # electrolyzer efficiency relative to LHV [-] ref. Chatenet et al. 2022 (adapted from IRENA 2020), taking top value of the given ranges for 2022 (as we have more future oriented scenarios)]


    df_initial_cost_share: pd.DataFrame = field(default_factory=lambda: pd.DataFrame({"Technology": ["AEC", "PEM", "SOEC"],
                                                                                        "Cell_stack": [0.50, 0.60, 0.30],
                                                                                        "Power_elec": [0.15, 0.15, 0.30],
                                                                                        "Gas_cond":   [0.15, 0.10, 0.06],
                                                                                        "BOP":        [0.20, 0.15, 0.34]})) # [-]

    df_scale_factor: pd.DataFrame = field(default_factory=lambda: pd.DataFrame({"Technology": ["AEC", "PEM", "SOEC"],
                                                                                  "f0_Cell_stack":  [0.88, 0.89, 0.87],
                                                                                  "Power_elec":     [0.75, 0.75, 0.75],
                                                                                  "Gas_cond":       [0.60, 0.60, 0.60],
                                                                                  "BOP":            [0.68, 0.73, 0.73]})) # [-]

    df_max_stack_size: pd.DataFrame = field(default_factory=lambda: pd.DataFrame({"Technology": ["AEC", "PEM", "SOEC"],
                                                                                        "2020": [3, 1.2, 0.5],
                                                                                        "2030": [4, 2  , 1  ],
                                                                                        "2050": [5, 5  , 3  ]})) # [MWel]

    df_initial_capex: pd.DataFrame = field(default_factory=lambda: pd.DataFrame({"Technology": ["AEC", "PEM", "SOEC"],
                                                                                    "2020": [1100, 1200, 2250],
                                                                                    "2030": [ 932,  701, 1272],
                                                                                    "2050": [ 511,  308,  508]})) # [EUR2017/kWel]

    def calc_stoich_WEL(self):
        self.stoich["H2"] = 1    # [kmol/kmol]
        self.stoich["H2O"] = -1  # [kmol/kmol]

        WEL_efficiency_HHV = {key: value * self.HHV_MJ_kg['H2']/self.LHV_MJ_kg['H2'] for key, value in self.WEL_efficiency_LHV.items()}

        e_consumption_kWh_kg = self.HHV_MJ_kg['H2'] * 1000 / WEL_efficiency_HHV[self.WEL_type] / 3600
        e_consumption_kWh_kmol = e_consumption_kWh_kg * self.M['H2']

        RO_desalination_e_req = self.stoich['H2O'] * self.RO_desal_elec_req_kmolH2O_h   # [kWel * h/kmol H2 (H2O)] extra electricity requirements for desalinating inlet water
        self.stoich["e"] = -1 * e_consumption_kWh_kmol + RO_desalination_e_req          # [kWel * h / kmol H2]

        if self.WEL_type=="SOEC":
            q100_consumption_kWh_kg = (self.HHV_MJ_kg['H2'] - self.LHV_MJ_kg['H2']) * 1000 / 3600
            q100_consumption_kWh_kmol = q100_consumption_kWh_kg * self.M['H2']
            self.stoich['q100'] = -1 * q100_consumption_kWh_kmol
        else:
            heat_recovery_efficiency = 0.80   # [-] ref: van der Roest et al. 2023
            q50_production_kWh_kg = e_consumption_kWh_kg * (1 - WEL_efficiency_HHV[self.WEL_type]) * heat_recovery_efficiency
            q50_production_kWh_kmol = q50_production_kWh_kg * self.M['H2']
            self.stoich['q50'] = q50_production_kWh_kmol

        return self.stoich

    def scale_capex_WEL(self, cap_kmolH2_h, switch_max_cap = 0, max_cap_sizing_equal_plants = 0):
        cap_MWel = cap_kmolH2_h * -1 * self.stoich['e'] / 1000  # [MWel] capacity in electricity input
        max_cap_MWel = 100                                      # [MWel] largest value investigated by Boehm et al. 2020, agrees with order of magnitude of offered scale of modules (20 MW)

        capex_EUR2017_kWel = {"2020": 0,
                              "2030": 0,
                              "2050": 0}
        stack_replacement_costs_EUR2017_kWel = {}

        cs_Cell_stack = self.df_initial_cost_share.loc[self.df_initial_cost_share['Technology'] == self.WEL_type, 'Cell_stack'].values[0]  # cost shares
        cs_Power_elec = self.df_initial_cost_share.loc[self.df_initial_cost_share['Technology'] == self.WEL_type, 'Power_elec'].values[0]
        cs_Gas_cond = self.df_initial_cost_share.loc[self.df_initial_cost_share['Technology'] == self.WEL_type, 'Gas_cond'].values[0]
        cs_BOP = self.df_initial_cost_share.loc[self.df_initial_cost_share['Technology'] == self.WEL_type, 'BOP'].values[0]

        f0_Cell_stack = self.df_scale_factor.loc[self.df_scale_factor["Technology"] == self.WEL_type, "f0_Cell_stack"].values[0] # scaling factors
        f_Power_elec = self.df_scale_factor.loc[self.df_scale_factor["Technology"] == self.WEL_type, "Power_elec"].values[0]
        f_Gas_cond = self.df_scale_factor.loc[self.df_scale_factor["Technology"] == self.WEL_type, "Gas_cond"].values[0]
        f_BOP = self.df_scale_factor.loc[self.df_scale_factor["Technology"] == self.WEL_type, "BOP"].values[0]


        def calc_capex_EUR2017_kWel(cap_MWel_input):
            capex_EUR2017_kWel_output = {}
            for year in capex_EUR2017_kWel.keys():
                S_max = self.df_max_stack_size.loc[self.df_max_stack_size["Technology"] == self.WEL_type, year].values[0]
                f_Cell_stack = 1 - (1 - f0_Cell_stack) * np.exp(-cap_MWel_input / S_max)
                capex_init = self.df_initial_capex.loc[self.df_initial_capex['Technology'] == self.WEL_type, year].values[0]

                capex_EUR2017_kWel_output[year] = capex_init * (
                        cs_Cell_stack * (cap_MWel_input / self.cap_MWel_ref) ** -(1 - f_Cell_stack) +
                        cs_Power_elec * (cap_MWel_input / self.cap_MWel_ref) ** -(1 - f_Power_elec) +
                        cs_Gas_cond * (cap_MWel_input / self.cap_MWel_ref) ** -(1 - f_Gas_cond) +
                        cs_BOP * (cap_MWel_input / self.cap_MWel_ref) ** -(1 - f_BOP))  # [EUR2017/kWel]

                N_stack_replacements = 2  # [-] number of times stack will be replaced (assuming ca. 8 years lifetime with 25 year project time = 2 replacements)
                stack_replacement_costs_EUR2017_kWel[year] =  N_stack_replacements * capex_init * (cs_Cell_stack * (cap_MWel_input / self.cap_MWel_ref) ** -(1 - f_Cell_stack))  # [EUR2017/kWel] stack replacement costs (taking full stack costs)
                #stack_replacement_costs_EUR2017_kWel[year] = capex_EUR2017_kWel_output[year] * 0.5  # [EUR2017/kWel]  assuming 50% of the initial investment (Brynolf et al. 2017, based on )

                capex_EUR2017_kWel_output[year] = capex_EUR2017_kWel_output[year] + 0*stack_replacement_costs_EUR2017_kWel[year]  # [EUR2017/kWel] adding stack replacement costs to the overall CAPEX
            return capex_EUR2017_kWel_output, stack_replacement_costs_EUR2017_kWel

        if switch_max_cap == 1:
            max_cap_plants_multiple = cap_MWel // max_cap_MWel

            if max_cap_sizing_equal_plants == 1:
                cap_equal_plant_sizes_MWel = cap_MWel / (max_cap_plants_multiple + 1)
                capex_EUR2017_kWel, stack_replacement_costs_EUR2017_kWel = calc_capex_EUR2017_kWel(cap_equal_plant_sizes_MWel)

            else:
                remainder_cap_MWel = cap_MWel % max_cap_MWel

                ratio_max_cap = max_cap_plants_multiple * max_cap_MWel / cap_MWel
                ratio_remainder_cap = remainder_cap_MWel / cap_MWel

                capex_max_EUR2017_kWel, stack_replacement_costs_EUR2017_kWel_max = calc_capex_EUR2017_kWel(max_cap_MWel)
                capex_rem_EUR2017_kWel, stack_replacement_costs_EUR2017_kWel_rem = calc_capex_EUR2017_kWel(remainder_cap_MWel)

                for year in capex_EUR2017_kWel.keys():
                    capex_EUR2017_kWel[year] = ratio_max_cap * capex_max_EUR2017_kWel[year] + ratio_remainder_cap * capex_rem_EUR2017_kWel[year]
                    stack_replacement_costs_EUR2017_kWel[year] = ratio_max_cap * stack_replacement_costs_EUR2017_kWel_max[year] + ratio_remainder_cap * stack_replacement_costs_EUR2017_kWel_rem[year]
        else:
            capex_EUR2017_kWel, stack_replacement_costs_EUR2017_kWel = calc_capex_EUR2017_kWel(cap_MWel)

        # conversion to USD2022 and kmol/h base
        capex_USD2022_kWel = {key: value * self.EUR_to_USD * self.CEPCI['2022']/self.CEPCI['2017'] for key, value in capex_EUR2017_kWel.items()}    # [USD2022/kWel]
        stack_replacement_costs_USD2022_kWel = {key: value * self.EUR_to_USD * self.CEPCI['2022'] / self.CEPCI['2017'] for key, value in stack_replacement_costs_EUR2017_kWel.items()}  # [USD2022/kWel]

        if self.stoich['e'] != 0:
            capex_USD2022_kmol_h = {key: value * -1 * self.stoich['e'] for key, value in capex_USD2022_kWel.items()}       # [USD2022/(kmol H2/h)]
            stack_replacement_costs_USD2022_kmol_h = {key: value * -1 * self.stoich['e'] for key, value in stack_replacement_costs_USD2022_kWel.items()} # [USD2022/(kmol H2/h)]
        else:
            raise ValueError("You need to calculate the energy consumption (self.stoich['e']) first!")

        return capex_USD2022_kmol_h, capex_EUR2017_kWel, cap_MWel, stack_replacement_costs_USD2022_kmol_h


@dataclass(kw_only=True)
class DAC(Process):
    DAC_type: str
    reference_for_costs: str = 'Young et al. 2023 and Sievert et al. 2024'
    cap_tCO2_ref: dict = field(default_factory=lambda: { "DAC-L": 980000,
                                                         "DAC-S":   4000})  # [tCO2/a] ref: Young et al. 2023 --> using value of 4000 tCO2/a for solid sorbent based on the values reported in Sievert et al. 2024

    costs_sorbent_per_tCO2: dict = field(default_factory=lambda: {"DAC-L": 1.4,     # [$2022/tCO2] for calcium carbonate and KOH losses, ref: Young et al. 2023 also agrees with IEAGHG 2021 report
                                                                  "DAC-S": 63.4})   # [$2022/tCO2] ref: Sievert et al. 2023 --> replacing solvent every 2 years (agrees well with Climeworks reports/targets of 180, 72 and 32 $/tCO2 for FOAK, NOAK and their long-term target respectively (as reported in IEAGHG 2021))

    df_DAC_L_costs: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(
                {   'Component': ["init_dir_mat_costs", "init_inst_costs", "scaling_factor"],
                    'Air_contactor':        [128, 238, 0.76],
                    'Pellet_reactor':       [86.2, 146, 0.67],
                    'Calciner_slaker':      [49.1, 87.1, 0.78],             # scaling factor combined for calciner and slaker (taken as middle value between 1 and 0.57 given in Sievert et al. 2024)
                    'Air_separation_unit':  [42.6, 60.9, 0.67],             # ASU costs left in as even if assuming electric calciner (which does not require O2 for oxyfuel combustion) as there would be extra development costs needed for the electric calciner
                    'Fines_filter':         [19.7, 34.6, 0.67],
                    'Compressor':           [14.2, 14.4, 0.73],
                    'Steam_turbine':        [7.5, 8.4, 0.42],
                    'Buildings_and_land':   [2.8, 7.51, 0.55],              # building scaling from Young et al. 2023
                    'Other_equipment':      [109, 115, 0.67]}).set_index('Component').transpose())      # costs in [M$ USD2018] ref: Young et al. 2023 and scaling factors from Sievert et al. 2024

    df_DAC_S_costs: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(
                {   'Component': ["init_dir_mat_costs_YOUNG", "init_inst_costs_YOUNG", "init_dir_mat_costs_SIEVERT_2022", "scaling_factor"],
                    'Contactors':           [0.76, 1.14, 3.7, 1],
                    'Blowers':              [0.433, 0.668, 0.1, 1],         # assumed scaling factor for blowers, since its not reported in Sievert et al. 2024, to be equal to 1 (not significant with little cost contribution)
                    'Vacuum pump 1':        [0.0638, 0.0999, 0.2, 0.63],
                    'Vacuum pump 2':        [0.0338, 0.065, 0.1, 0.63],
                    'Condensers':           [0.153, 0.242, 0.4, 0.63],
                    'Switching_valves':     [1.19, 1.19, 3.4, 0.63],
                    'Initial_sorbent':      [0.105, 0.105, 0.5, 1],
                    'Buildings_and_land':   [0.062, 0.166, 1, 0.55],        # building scaling from Young et al. 2023
                    'Compressor':           [1.23, 1.31, 2.6, 0.42]}).set_index('Component').transpose())      # costs in [M$ USD2018] ref: Young et al. 2023 and scaling factors from Sievert et al. 2024



    def calc_stoich_DAC(self):
        self.stoich["CO2"] = 1    # [kmol/kmol]

        if self.DAC_type=="DAC-L":
            heat_requirement = 5.3                      # [GJth/tCO2]                ref: Young et al. 2023
            e_requirement_no_heat_no_comp = 0.85        # [GJth/tCO2]                ref: Young et al. 2023
            e_requirement = 0.85 + heat_requirement     # [GJe/tCO2] assuming an electric calciner, no compression, ref: McQueen et al. 2021
            e_compression = 0.47                        # [GJe/tCO2]                 ref: Young et al. 2023
            water_usage = 4.8                           # [tH2O/tCO2]                ref: Young et al. 2023

            #H2_heat_requirement_kgH2_kgCO2 = heat_requirement * 1000 /1000 / self.LHV_MJ_kg['H2']    # assuming heat has to be sourced from renewable (gas) energy carrier and taking H2 as one of the alternatives to CH4 (electricity not chosen, due to the challenges and development needed for electrification of such high T processes)
            #H2_heat_requirement_kmolH2_kmolCO2 = H2_heat_requirement_kgH2_kgCO2 * self.M['CO2'] / self.M['H2']
            #self.stoich['H2'] = -1 * H2_heat_requirement_kmolH2_kmolCO2

        elif self.DAC_type=="DAC-S":
            heat_requirement = 9.8  # [GJth/tCO2]                ref: Young et al. 2023
            e_requirement = 0.52    # [GJe/tCO2] no compression, ref: Young et al. 2023
            e_compression = 0.47    # [GJe/tCO2]                 ref: Young et al. 2023
            water_usage = 0         # [tH2O/tCO2]                ref: Young et al. 2023

            heat_requirement_kWh_kg = heat_requirement * 1e6 /1000 /3600
            heat_requirement_kWh_kmol = heat_requirement_kWh_kg * self.M['CO2']
            self.stoich['q100'] = -1 * heat_requirement_kWh_kmol

        water_requirement = water_usage * self.M['CO2'] / self.M['H2O']
        self.stoich['H2O'] = -1 * water_requirement
        RO_desalination_e_req =  self.stoich['H2O'] * self.RO_desal_elec_req_kmolH2O_h  # [kWel * h/kmol CO2 (H2O)] extra electricity requirements for desalinating inlet water
        self.stoich['e'] = -1 * (e_requirement + e_compression) * 1e6/1000 /3600 * self.M['CO2'] + RO_desalination_e_req

        return self.stoich

    def scale_capex_DAC(self, cap_kmolCO2_h, switch_max_cap = 0, max_cap_sizing_equal_plants = 0):
        cap_tCO2_a = cap_kmolCO2_h * self.M['CO2'] * 8760 / 1000 # [tCO2/a] capacity to scale to converted from input capacity in kmolCO2/h

        if self.DAC_type == 'DAC-L':
            inflation_factor =  1.16    # [2019 vs 2022] calculated based on ratio of direct costs reported in Young et al. 2023 and Sievert et al. 2024
            self.df_DAC_L_costs['init_inst_costs_2022'] = self.df_DAC_L_costs['init_inst_costs'] * inflation_factor
            self.df_DAC_L_costs['scaled_inst_costs_2022'] = self.df_DAC_L_costs['init_inst_costs_2022'] * (cap_tCO2_a / self.cap_tCO2_ref['DAC-L'])**self.df_DAC_L_costs['scaling_factor']

            total_inst_costs = sum(self.df_DAC_L_costs['scaled_inst_costs_2022'])   # [M USD]

        elif self.DAC_type == 'DAC-S':
            max_cap_tCO2_a = 100000 # [tCO2/a] planned Climeworks-scale up capacity ref. Bissotti et al. 2024



            self.df_DAC_S_costs['installation_factors'] = self.df_DAC_S_costs['init_inst_costs_YOUNG'] / self.df_DAC_S_costs['init_dir_mat_costs_YOUNG']
            self.df_DAC_S_costs['init_inst_costs_SIEVERT_2022'] = self.df_DAC_S_costs['init_dir_mat_costs_SIEVERT_2022'] * self.df_DAC_S_costs['installation_factors']

            if switch_max_cap == 1:
                max_cap_plants_multiple = cap_tCO2_a // max_cap_tCO2_a

                if max_cap_sizing_equal_plants == 1:
                    cap_equal_plant_sizes_tCO2_a = cap_tCO2_a / (max_cap_plants_multiple + 1)
                    self.df_DAC_S_costs['scaled_inst_costs_2022'] = (max_cap_plants_multiple + 1) * self.df_DAC_S_costs['init_inst_costs_SIEVERT_2022'] * (cap_equal_plant_sizes_tCO2_a / self.cap_tCO2_ref['DAC-S']) ** self.df_DAC_S_costs['scaling_factor']

                else:
                    remainder_cap_tCO2_a = cap_tCO2_a % max_cap_tCO2_a
                    self.df_DAC_S_costs['scaled_inst_costs_2022'] = (max_cap_plants_multiple * self.df_DAC_S_costs['init_inst_costs_SIEVERT_2022'] * (max_cap_tCO2_a / self.cap_tCO2_ref['DAC-S'])**self.df_DAC_S_costs['scaling_factor'] +
                                                                                               self.df_DAC_S_costs['init_inst_costs_SIEVERT_2022'] * (remainder_cap_tCO2_a / self.cap_tCO2_ref['DAC-S']) ** self.df_DAC_S_costs['scaling_factor'])
            else:
                self.df_DAC_S_costs['scaled_inst_costs_2022'] = self.df_DAC_S_costs['init_inst_costs_SIEVERT_2022'] * (cap_tCO2_a / self.cap_tCO2_ref['DAC-S']) ** self.df_DAC_S_costs['scaling_factor']

            total_inst_costs = sum(self.df_DAC_S_costs['scaled_inst_costs_2022'])  # [M USD]

        epc_factor = 1.15                                                       # [-] ref: Young et al. 2023
        total_epc_costs = total_inst_costs * epc_factor                         # [M USD]
        capex_USD2022_tCO2_a = total_epc_costs * 1e6 / cap_tCO2_a               # [USD 2022/(tCO2/a)]

        capex_USD2022_kmol_h = capex_USD2022_tCO2_a / 1000 * 8760 * self.M['CO2']    # [USD 2022/(kmol/h)]

        capex_USD2022_kmol_h = {'2020': capex_USD2022_kmol_h,
                        '2030': capex_USD2022_kmol_h * 0.47,
                        '2050': capex_USD2022_kmol_h * 0.27} # [USD 2022/(kmol/h)] ref: expected capex reductions for future years based on data from Fasihi et al. 2019

        capex_USD2022_tCO2_a = {'2020': capex_USD2022_tCO2_a,
                        '2030': capex_USD2022_tCO2_a * 0.47,
                        '2050': capex_USD2022_tCO2_a * 0.27}  # [USD 2022/(tCO2/h)] ref: expected capex reductions for future years based on data from Fasihi et al. 2019

        return capex_USD2022_kmol_h, capex_USD2022_tCO2_a, cap_tCO2_a


@dataclass(kw_only=True)
class MTS(Process):
    reference_for_costs: str = 'Brynolf et al. 2018 (agrees well with Zhang et al. 2019 used in first article (Svitnic and Sundmacher 2022))'
    cap_ref_unit: str = "MW_fuel"
    cap_MWfuel_ref: float = 200 # [MWfuel] reference capacity for capex scaling in MWfuel of methanol output (based on LHV)

    def calc_stoich_MTS(self):
        self.stoich["MeOH"] = 0.965     # [kmol/kmol] Svitnic and Sundmacher 2022
        self.stoich["H2O"] = 0.965  * 0 # [kmol/kmol] assuming 0 clean water on the outlet (to account for the overall water consumption = desalination requirements properly)
        self.stoich["H2"] = -3          # [kmol/kmol]
        self.stoich["CO2"] = -1         # [kmol/kmol]
        self.stoich["e"] = -1.44        # [kWel/kmol]
        self.stoich["q100"] = 12.9      # [kWth/kmol] taking only the reaction heat at 250 degC (assuming that the purification is heat self-sufficient (MVR), with extra utilization of the purge combustion)
        return self.stoich

    def scale_capex_MTS(self, cap_kmolMeOH_h):
        cap_kgMeOH_s = cap_kmolMeOH_h * self.M['MeOH'] / 3600
        cap_MWfuel = cap_kgMeOH_s * self.LHV_MJ_kg['MeOH']                                                  # [MWfuel] capacity to scale to coverted to units, for which we have cost reports

        capex_EUR2015_kWfuel_ref = 300                                                                      # [EUR 2015/kW fuel] ref: Brynolf et al. 2018
        capex_EUR2015_kWfuel = capex_EUR2015_kWfuel_ref * (cap_MWfuel/self.cap_MWfuel_ref)**-(1-0.67)       # [EUR 2015/kW fuel] ref: Brynolf et al. 2018

        capex_USD2022_kWfuel = capex_EUR2015_kWfuel * self.EUR_to_USD * self.CEPCI['2022']/self.CEPCI['2015']    # [USD 2022/kW fuel]
        capex_USD2022_kg_s = capex_USD2022_kWfuel * 1000 * self.LHV_MJ_kg['MeOH']
        capex_USD2022_kg_h = capex_USD2022_kg_s / 3600
        capex_USD2022_kmol_h = capex_USD2022_kg_h * self.M['MeOH']

        capex_USD2022_kmol_h = {'2020': capex_USD2022_kmol_h,
                                '2030': capex_USD2022_kmol_h,
                                '2050': capex_USD2022_kmol_h}  # [USD 2022/(kmol/h)] ref: not expecting major technology reduction for established chemical processes in the methanol synthesis and separation processes

        return capex_USD2022_kmol_h, capex_EUR2015_kWfuel, cap_MWfuel



@dataclass(kw_only=True)
class HP(Process):
    reference_for_costs: str = 'Grosse et al. 2017 (AIT et al. report for the European Commission)'

    def calc_stoich_HP(self, Tsource_C, Tsink_C):
        Tsource = Tsource_C + 273.15
        Tsink = Tsink_C + 273

        efficiency_COP = 0.4                                # [-] ref: Meyers et al. 2018
        COP = efficiency_COP * (Tsink / (Tsink - Tsource))
        work_kWel_per_kWth = 1 / COP                        # [kWth] taking 1 kWth output as reference
        Q_source_kWth_per_kWth = 1 - work_kWel_per_kWth     # [kWth] taking 1 kWth output as reference

        self.stoich['e'] = - work_kWel_per_kWth
        self.stoich['q' + str(Tsink_C)] = 1                 # [kWth] taking 1 kWth output as reference

        if Tsource_C < 50:
            self.stoich['qamb'] = - Q_source_kWth_per_kWth  # condition setting q amb as heat source when below 50 degC

        else:
            self.stoich['q' + str(Tsource_C)] = - Q_source_kWth_per_kWth    # condition setting q based on T_source if above 50 degC


    def scale_capex_HP(self, cap_kWth):
        if cap_kWth == 0:
            capex_EUR2015_kWth = 0
        else:
            capex_EUR2015_kWth = 0.352*1e6*(cap_kWth/1000)**(-0.122) / 1000 # [EUR 2015/kWth] heat pump only costs ref: Grosse et al. 2017 (AIT report)

        capex_USD2022_kWth = capex_EUR2015_kWth * self.EUR_to_USD * self.CEPCI['2022'] / self.CEPCI['2015']

        capex_USD2022_kWth = capex_USD2022_kWth / 0.5                    # [USD 2022/kWth] total investment costs heat pump (heat pump itself represents 50%, ref: Grosse et al. 2017 (AIT report))

        capex_USD2022_kWth = {  '2020': capex_USD2022_kWth * 0.66/0.72,
                                '2030': capex_USD2022_kWth * 0.60/0.72,
                                '2050': capex_USD2022_kWth * 0.54/0.72}  # [USD 2022/kWth] projections done based on the ratios of reported nominal investments (M EUR/MWth) in ref: Grosse et al. 2017 (AIT report)

        return capex_USD2022_kWth, capex_EUR2015_kWth






PEM = WEL(name="PEM", description="PEM electrolyzer", WEL_type='PEM')
PEM.calc_stoich_WEL()
PEM.LR = 0.18  # [-] ref: Schmidt et al. 2017 (Uncertainty: 18+- 2%)

plotting_max_cap_study = 0
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

year = '2020'

if plotting_max_cap_study == 1:
    pem_cap_kmol_h = np.linspace(100,5000, 1000)
    pem_capex = []
    pem_capex_max =[]
    pem_capex_max_equal_plant_sizes = []
    pem_MWel = []

    for i in pem_cap_kmol_h:
        pem_MWel.append(PEM.scale_capex_WEL(i, 0, 0)[2])
        pem_capex.append(PEM.scale_capex_WEL(i, 0, 0)[1][year])
        pem_capex_max.append(PEM.scale_capex_WEL(i, 1, 0)[1][year])
        pem_capex_max_equal_plant_sizes.append(PEM.scale_capex_WEL(i, 1, 1)[1][year])

    plt.plot(pem_MWel, pem_capex, color=blue_MPI)
    plt.plot(pem_MWel, pem_capex_max, color=green_MPI)
    plt.plot(pem_MWel, pem_capex_max_equal_plant_sizes, color=red_MPI)
    plt.xlabel('PEM capacity [MW$_{el}$]')
    plt.ylabel('PEM capex [USD/kW$_{el}$]')
    plt.legend(['no max limit', 'max limit', 'max limit, equal plant sizes'], loc='lower right')
    plt.ylim([0, max(pem_capex)])
    plt.tight_layout()
    fig_name = 'fig_max_scaling_PEM_' + year + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

SOEC = WEL(name='SOEC', description='SOEC electrolyzer', WEL_type='SOEC')
SOEC.calc_stoich_WEL()
SOEC.LR = 0.28 # [-] ref: Schmidt et al. 2017 (Uncertainty: 28 +- 16%)

DAC_L = DAC(name="DAC-L", description="DAC liquid (based on Keith et al. 2018)", DAC_type='DAC-L')
DAC_L.calc_stoich_DAC()
DAC_L.LR = 0.10 # [-] ref: Young et al. 2023 (range  5-15%)

DAC_S = DAC(name="DAC-S", description="DAC solid (based on Climeworks)", DAC_type='DAC-S')
DAC_S.calc_stoich_DAC()
DAC_S.LR = 0.14 # [-] ref: Young et al. 2023 (range 10-18%)

if plotting_max_cap_study == 1:
    dac_S_cap_kmol_h = np.linspace(10, 2500, 1000)
    dac_S_capex = []
    dac_S_capex_max = []
    dac_S_capex_max_equal_plant_sizes = []
    dac_S_ktCO2_a = []

    for i in dac_S_cap_kmol_h:
        dac_S_ktCO2_a.append(DAC_S.scale_capex_DAC(i, 0, 0)[2] / 1000)
        dac_S_capex.append(DAC_S.scale_capex_DAC(i, 0, 0)[1][year])
        dac_S_capex_max.append(DAC_S.scale_capex_DAC(i, 1, 0)[1][year])
        dac_S_capex_max_equal_plant_sizes.append(DAC_S.scale_capex_DAC(i, 1, 1)[1][year])



    plt.plot(dac_S_ktCO2_a, dac_S_capex, color=blue_MPI)
    plt.plot(dac_S_ktCO2_a, dac_S_capex_max, color=green_MPI)
    plt.plot(dac_S_ktCO2_a, dac_S_capex_max_equal_plant_sizes, color=red_MPI)

    plt.xlabel('DAC-S capacity [kt$_{CO2}$/a]', fontsize=16)
    plt.ylabel('DAC-S capex [USD/(t$_{CO2}$/a)]', fontsize=16)
    plt.legend(['no max limit', 'max limit', 'max limit, equal plant sizes'], fontsize=14)
    plt.ylim([0, max(dac_S_capex)])
    plt.tight_layout()
    fig_name = 'fig_max_scaling_DAC_S_'+ year + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

if plotting_max_cap_study == 1:
    dac_L_cap_kmol_h = np.linspace(10, 2500, 1000)
    dac_L_capex = []
    dac_L_capex_max = []
    dac_L_capex_max_equal_plant_sizes = []
    dac_L_ktCO2_a = []

    for i in dac_L_cap_kmol_h:
        dac_L_ktCO2_a.append(DAC_L.scale_capex_DAC(i, 0, 0)[2] / 1000)
        dac_L_capex.append(DAC_L.scale_capex_DAC(i, 0, 0)[1][year])
        dac_L_capex_max.append(DAC_L.scale_capex_DAC(i, 1, 0)[1][year])
        dac_L_capex_max_equal_plant_sizes.append(DAC_L.scale_capex_DAC(i, 1, 1)[1][year])

    plt.plot(dac_L_ktCO2_a, dac_L_capex, color=blue_MPI)
    plt.plot(dac_L_ktCO2_a, dac_L_capex_max, color=green_MPI)
    plt.plot(dac_L_ktCO2_a, dac_L_capex_max_equal_plant_sizes, color=red_MPI)

    plt.xlabel('DAC-L capacity [kt$_{CO2}$/a]')
    plt.ylabel('DAC-L capex [USD/(t$_{CO2}$/a)]')
    plt.legend(['no max limit', 'max limit', 'max limit, equal plant sizes'])
    plt.ylim([0, max(dac_L_capex)])
    plt.tight_layout()
    fig_name = 'fig_max_scaling_DAC_L_'+ year + '.pdf'
    fig_name = os.path.join(figure_subfolder(), fig_name)
    plt.savefig(fig_name)
    plt.show()

#print(DAC_S.scale_capex_DAC(255, 0, 0)[2]/1000)
#print(DAC_S.scale_capex_DAC(255, 0, 0)[1][year])
#print(DAC_L.scale_capex_DAC(255, 0, 0)[1][year])



MT = MTS(name="MTS", description="Methanol synthesis and separation process, with stoichiometry from Svitnic and Sundmacher 2022")
MT.calc_stoich_MTS()
MT.LR = 0.03 # [-] assumption based on the recommended learning rates from ref: National Energy Technology Laboratory. Technology learning curve (FOAK to NOAK). DOE/NETL–341/081213, 2013

#results_MTS = MT.scale_capex_MTS(300*4)

T_amb = 15

HP_Tamb_50 = HP(name="HP_Tamb_50", description="heat pump from ambient T to degC")
HP_Tamb_50.calc_stoich_HP(T_amb, 50)

HP_Tamb_100 = HP(name="HP_Tamb_100", description="heat pump from ambient T to 100 degC")
HP_Tamb_100.calc_stoich_HP(T_amb, 100)

HP_50_100 = HP(name="HP_50_100", description="heat pump from 50 deg C to 100 degC")
HP_50_100.calc_stoich_HP(50, 100)

#results_HP = HP_Tamb_100.scale_capex_HP(10000)

BAT_in = Process(name="BAT_in", description="battery charging process")
BAT_in.stoich['e'] = -1
BAT_in.stoich['BAT'] = +1

BAT_out = Process(name="BAT_out", description="battery discharging process")
BAT_out.stoich['e'] = +0.85     # based ATB NREL assumption for roundtrip efficiency
BAT_out.stoich['BAT'] = -1

CGH2_in = Process(name="CGH2_in", description="compressed hydrogen storage charging process")
CGH2_in.stoich['H2'] = -1
CGH2_in.stoich['CGH2'] = +1
CGH2_in.stoich['e'] = -2.20

CGH2_out = Process(name="CGH2_out", description="compressed hydrogen storage discharging process")
CGH2_out.stoich['H2'] = +1
CGH2_out.stoich['CGH2'] = -1

CO2tank_in = Process(name="CO2tank_in", description="CO2 storage charging process")
CO2tank_in.stoich['CO2'] = -1
CO2tank_in.stoich['CO2tank'] = +1
CO2tank_in.stoich['e'] = -0.24

CO2tank_out = Process(name="CO2tank_out", description="CO2 stroage discharging process")
CO2tank_out.stoich['CO2'] = +1
CO2tank_out.stoich['CO2tank'] = -1

TES_in = Process(name="TES_in", description="thermal energy storage (q100) charging process")
TES_in.stoich['q100'] = -1
TES_in.stoich['TES'] = +1

TES_out = Process(name="TES_in", description="thermal energy storage (q100) discharging process")
TES_out.stoich['q100'] = +0.95
TES_out.stoich['TES'] = -1

Curt = Process(name="Curt", description="process for curtailing electricity")
Curt.stoich['e'] = -1
Curt.stoich['e_curt'] = 1

x=1


