import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from utility_functions import res_subfolder, annual_factor
from case_studies import  CS_psm_years, CS_plm_years, CS_plm_years_maxCAPscale, \
    CS_psm_years_maxCAPscale, CS_plm_years_minCAP_DACL_25, CS_plm_years_minCAP_DACL_50, \
    CS_psm_years_minCAP_MTS_25, CS_psm_years_minCAP_MTS_50
from scheduling_opti import scheduling_optimization
from sizing_cases import Sync_WDM, Sync_WD, Sync_W
import concurrent.futures
import multiprocessing as mp
import time
from datetime import timedelta, datetime
from pickle import load, dump
from grid_calc import grid_calculation


def main():

    test_run = 1    # switch between demonstration (test) run with small scale designs for quick solution and a run where all the cases in the article are solved (takes a long time)
    multiproc = 1   # switch to turn on multiprocessing (parallel solution)

    if test_run == 1: # runs a smaller demonstration (test) case
        CAPgen_ins_array = np.linspace(50, 500,2) * 1000  # [kW] capacities of the energy generation section (output from the generation section)
        CaseStudies_to_run = [CS_psm_years]
        SizingCases_to_run = [Sync_WDM]  # sizing cases to be run (designs out of which the best one for a particular capacity and case will be selected)

    else:    # runs all the cases presented in the article
        CAPgen_ins_array = np.linspace(50, 6000, 14) * 1000
        CaseStudies_to_run = [CS_psm_years, CS_plm_years, CS_psm_years_maxCAPscale, CS_plm_years_maxCAPscale, CS_plm_years_minCAP_DACL_25, CS_plm_years_minCAP_DACL_50, CS_psm_years_minCAP_MTS_25, CS_psm_years_minCAP_MTS_50]
        SizingCases_to_run = [Sync_WDM, Sync_WD, Sync_W]     # sizing cases to be run (designs out of which the best one for a particular capacity and case will be selected)


    ratio_wind_solar_array = np.array([1])                                  # [-] ratio of wind and solar generation technologies (currently model set-up fully for wind only (=1) generation)
    pd_nominal = 8                                                          # [MW/km2]  power density of wind turbines (installed/nominal wind capacity), reference value = 8 MW/km2

    total_start_time = time.time()
    time_of_run = '{date:%Y-%m-%d_%H-%M-%S}'.format(date=datetime.now())


    for CS in CaseStudies_to_run:
        for C in CS.cases:

            C.time_of_run = time_of_run

            # Grid design
            CAPEXgen_grid_list = []
            CAPEXgen_list = []
            CAPEXgrid_list = []
            Annual_land_lease_costs_list = []

            N_slices_grid = 1  # [-] number of circle slices (8 divisions) considered in the generation grid
            year_grid = C.year
            cable_limit = 0

            # load previous grid calculation results and check if we did not already calculate the desired configuration (to save recalculating it again)!
            GC_2020_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(),'GC_2020_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
            GC_2030_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(),'GC_2030_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
            GC_2050_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(),'GC_2050_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))

            list_grid_results = [GC_2020_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14,
                                 GC_2030_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14,
                                 GC_2050_pd_8_sensNslice_1_CableLim_0_MWgrid_50_6000_np_14]

            G_results_already_calculated = 0

            for G in list_grid_results:
                check_pd_nominal = G.pd_nominal == pd_nominal
                check_cable_limit = G.cable_limit == cable_limit
                check_year = G.year == year_grid
                check_N_slices = G.N_slices == N_slices_grid
                check_Pgrid_nominal = np.array_equal(np.array(G.res['Pgrid_nominal_list']*1000), CAPgen_ins_array)
                checks = [check_pd_nominal, check_cable_limit, check_year, check_N_slices, check_Pgrid_nominal]

                if all(checks):
                    G_results_already_calculated = G

            if G_results_already_calculated != 0:
                CAPEXgen_list = G_results_already_calculated.res['CAPEXgen_list']
                CAPEXgrid_list = G_results_already_calculated.res['CAPEXgrid_list']
                Annual_land_lease_costs_list = G_results_already_calculated.res['Annual_land_lease_costs']


            else:
                for i in CAPgen_ins_array:
                    CAPgen_ins_MW = i / 1000  # [MW] conversion to MW
                    f_cr = annual_factor(0.07, 25)
                    CAPEXgen_grid, CAPEXgen, CAPEXgrid, CAPEXcables, CAPEXtrench, CAPEXroad, CAPEXtransform, CAPEXreact, Annual_land_lease_costs, Fexit, Area_total, energy_loss, CAPEXgen_reference = grid_calculation(
                        CAPgen_ins_MW, pd_nominal, N_slices_grid, year_grid, cable_limit, f_cr, 0, 0)
                    print('Gen. grid optimization results: desired Cap. (MW) = ', CAPgen_ins_MW, ', N_slices = ',
                          N_slices_grid, ', year = ', year_grid)
                    print('Gen. grid rated output (MW) = ', Fexit)
                    print('Gen. grid total capex (mil. USD) = ', round(CAPEXgen_grid / 1e6, 2))
                    print('Gen. grid total area (km2) = ', round(Area_total, 1))
                    print('Gen. grid land lease cost (mil. USD/a) = ', round(Annual_land_lease_costs / 1e6, 2))
                    CAPEXgen_grid_list.append(CAPEXgen_grid)
                    CAPEXgen_list.append(CAPEXgen)
                    CAPEXgrid_list.append(CAPEXgrid)
                    Annual_land_lease_costs_list.append(Annual_land_lease_costs)


            C.res['CAPEXgen_list'] = CAPEXgen_list
            C.res['CAPEXgrid_list'] = CAPEXgrid_list
            C.res['Annual_land_lease_costs_list'] = Annual_land_lease_costs_list

            # Design of plant
            Selected_LCOMeOH = []
            Selected_Production_annual_t = []
            Selected_CAP_ins = []
            Selected_S_ins = []
            Selected_dLCOMeOH = []
            Selected_rel_CAP_ins = []
            Selected_S_days_of_storage = []

            Selected_CAPgen_ins = []
            Selected_ratio_wind_solar = []

            Selected_LCOMeOH_one_CAPgen = []
            Selected_Production_annual_t_one_CAPgen = []
            Selected_CAP_ins_one_CAPgen = []
            Selected_S_ins_one_CAPgen = []
            Selected_dLCOMeOH_one_CAPgen = []
            Selected_CAPgen_ins_one_CAPgen = []
            Selected_ratio_wind_solar_one_CAPgen = []
            Selected_rel_CAP_ins_one_CAPgen = []
            Selected_S_days_of_storage_one_CAPgen = []

            iter_CAPgen_ins = []
            iter_CAPEXgen = []
            iter_CAPEXgrid = []
            iter_Annual_land_lease_costs = []
            iter_ratio_wind_solar = []
            Results_list = []

            input_CASE = C

            if multiproc == 1:
                with concurrent.futures.ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
                    for i in range(len(CAPgen_ins_array)):
                        for j in ratio_wind_solar_array:
                            iter_CAPgen_ins.append(CAPgen_ins_array[i])
                            iter_CAPEXgen.append(CAPEXgen_list[i])
                            iter_CAPEXgrid.append(CAPEXgrid_list[i])
                            iter_Annual_land_lease_costs.append(Annual_land_lease_costs_list[i])
                            iter_ratio_wind_solar.append(j)

                    iter_CASE = [input_CASE] * len(iter_CAPgen_ins)
                    iter_SizingCases = [SizingCases_to_run] * len(iter_CAPgen_ins)

                    Results = executor.map(scheduling_optimization, iter_CASE, iter_CAPgen_ins, iter_ratio_wind_solar, iter_CAPEXgen, iter_CAPEXgrid, iter_Annual_land_lease_costs, iter_SizingCases)
                    for result in Results:
                        Results_list.append(result)

            else:

                for i in range(len(CAPgen_ins_array)):
                    for j in ratio_wind_solar_array:
                        iter_CAPgen_ins.append(CAPgen_ins_array[i])
                        iter_ratio_wind_solar.append(j)

                        Results = scheduling_optimization(CASE=input_CASE, CAPgen_ins=CAPgen_ins_array[i], ratio_wind_solar=j, CAPEXgen=CAPEXgen_list[i], CAPEXgrid=CAPEXgrid_list[i], Annual_land_lease_costs=Annual_land_lease_costs_list[i], SizingCases_list=SizingCases_to_run)
                        Results_list.append(Results)

            print(Results_list)

            print(Results_list[0].LCOMeOH_selected)

            counter = 0
            for i in range(len(CAPgen_ins_array)):
                for j in range(len(ratio_wind_solar_array)):
                    if iter_CAPgen_ins[counter] == CAPgen_ins_array[i]:
                        Selected_LCOMeOH_one_CAPgen.append(Results_list[counter].LCOMeOH_selected)
                        Selected_Production_annual_t_one_CAPgen.append(Results_list[counter].Production_annual_t_selected)
                        Selected_CAP_ins_one_CAPgen.append(Results_list[counter].CAP_ins_selected)
                        Selected_S_ins_one_CAPgen.append(Results_list[counter].S_ins_selected)
                        Selected_dLCOMeOH_one_CAPgen.append(Results_list[counter].df_LCOMeOH_stacked_bar_selected)
                        Selected_CAPgen_ins_one_CAPgen.append(Results_list[counter].CAPgen_ins)
                        Selected_ratio_wind_solar_one_CAPgen.append(Results_list[counter].ratio_wind_solar)
                        Selected_rel_CAP_ins_one_CAPgen.append(Results_list[counter].rel_CAP_ins_selected)
                        Selected_S_days_of_storage_one_CAPgen.append(Results_list[counter].S_days_of_storage_selected)

                    counter = counter + 1

                Selected_LCOMeOH.append(min(Selected_LCOMeOH_one_CAPgen))
                min_index = Selected_LCOMeOH_one_CAPgen.index(min(Selected_LCOMeOH_one_CAPgen))

                Selected_Production_annual_t.append(Selected_Production_annual_t_one_CAPgen[min_index])
                Selected_CAP_ins.append(Selected_CAP_ins_one_CAPgen[min_index])
                Selected_S_ins.append(Selected_S_ins_one_CAPgen[min_index])
                Selected_dLCOMeOH.append(Selected_dLCOMeOH_one_CAPgen[min_index])
                Selected_rel_CAP_ins.append(Selected_rel_CAP_ins_one_CAPgen[min_index])
                Selected_S_days_of_storage.append(Selected_S_days_of_storage_one_CAPgen[min_index])

                Selected_CAPgen_ins.append(Selected_CAPgen_ins_one_CAPgen[min_index])
                Selected_ratio_wind_solar.append(Selected_ratio_wind_solar_one_CAPgen[min_index])

                Selected_LCOMeOH_one_CAPgen = []
                Selected_Production_annual_t_one_CAPgen = []
                Selected_CAP_ins_one_CAPgen = []
                Selected_S_ins_one_CAPgen = []
                Selected_dLCOMeOH_one_CAPgen = []

                Selected_CAPgen_ins_one_CAPgen = []
                Selected_ratio_wind_solar_one_CAPgen = []

            df_selected_dLCOMeOH = pd.concat(Selected_dLCOMeOH, axis=0)

            C.res['SizingCases_run'] = SizingCases_to_run
            C.res['CAPgen_ins_array'] = CAPgen_ins_array
            C.res['production_MeOH'] = Selected_Production_annual_t
            C.res['CAP_ins_selected'] = Selected_CAP_ins
            C.res['S_ins_selected'] = Selected_S_ins
            C.res['LCOMeOH_selected'] = Selected_LCOMeOH
            C.res['dLCOMeOH'] = df_selected_dLCOMeOH
            C.res['CAPgen_ins_selected'] = Selected_CAPgen_ins
            C.res['ratio_wind_solar_selected'] = Selected_ratio_wind_solar
            C.res['rel_CAP_ins_selected'] = Selected_rel_CAP_ins
            C.res['S_days_of_storage_selected'] = Selected_S_days_of_storage

            filename =  C.name + '_maxPgrid_' + str(int(max(CAPgen_ins_array/1000))) + '__' + time_of_run + '.pkl'
            result_path = os.path.join(res_subfolder(), filename)
            dump(C, open(result_path, 'wb'))


            ax = df_selected_dLCOMeOH.plot(kind='bar', stacked=True)
            xticklabels = np.array([round(elem/1000, 0)*1000 for elem in Selected_Production_annual_t])
            ax.set_xticklabels(xticklabels.astype(int), rotation=45, ha='right', rotation_mode='anchor')
            plt.title(C.name)
            plt.xlabel('Produced MeOH (t/a)')
            plt.ylabel('LCOMeOH (USD/t)')
            plt.legend(bbox_to_anchor=(0.96, 0.5), loc="center left", borderaxespad=0, reverse=True)
            plt.tight_layout()
            plt.show()

            print('Selected LCOMeOH = ', Selected_LCOMeOH)
            print('Selected dLCOMeOH = ', Selected_dLCOMeOH)

            total_end_time = time.time()
            print("Total run time = {}".format(timedelta(seconds= total_end_time - total_start_time)))

        filename = CS.name + '_maxPgrid_' + str(int(max(CAPgen_ins_array/1000))) + '__' + time_of_run + '.pkl'
        result_path = os.path.join(res_subfolder(), filename)
        dump(CS, open(result_path, 'wb'))

if __name__ == '__main__': # Important not to get stuck in a multiprocessing loop
    main()