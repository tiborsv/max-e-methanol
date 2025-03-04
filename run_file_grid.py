import os
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import timedelta, datetime
from utility_functions import network_form, annual_factor, slope_calc, res_subfolder
from pickle import load, dump
from case_studies import GCS_2020_PDsens_Nslice_1_CableLim_0,GCS_2030_PDsens_Nslice_1_CableLim_0, GCS_2050_PDsens_Nslice_1_CableLim_0, \
    GCS_2020_PDsens_Nslice_1_CableLim_1,GCS_2030_PDsens_Nslice_1_CableLim_1, GCS_2050_PDsens_Nslice_1_CableLim_1, GCS_2020_pd_8_sensNslice_CableLim_0, \
    GCS_2030_pd_8_sensNslice_CableLim_0, GCS_2050_pd_8_sensNslice_CableLim_0, GCS_test, \
    GCS_2020_pd_8_Nslice_1_sensCableLim,GCS_2030_pd_8_Nslice_1_sensCableLim,GCS_2050_pd_8_Nslice_1_sensCableLim

from grid_calc import grid_calculation

GridCaseStudies_to_run = [GCS_test]
    #[GCS_2020_PDsens_Nslice_1_CableLim_0,GCS_2030_PDsens_Nslice_1_CableLim_0, GCS_2050_PDsens_Nslice_1_CableLim_0,
    #                      GCS_2020_pd_8_sensNslice_CableLim_0, GCS_2050_pd_8_sensNslice_CableLim_0, GCS_2030_pd_8_sensNslice_CableLim_0]
    #[GCS_2020_PDsens_Nslice_1_CableLim_0,GCS_2030_PDsens_Nslice_1_CableLim_0, GCS_2050_PDsens_Nslice_1_CableLim_0]
    #[GCS_2020_pd_8_sensNslice_CableLim_0, GCS_2050_pd_8_sensNslice_CableLim_0, GCS_2030_pd_8_sensNslice_CableLim_0]
    #[GCS_2020_pd_8_Nslice_1_sensCableLim,GCS_2030_pd_8_Nslice_1_sensCableLim,GCS_2050_pd_8_Nslice_1_sensCableLim]
    #[GCS_2020_PDsens_Nslice_1_CableLim_0,GCS_2030_PDsens_Nslice_1_CableLim_0, GCS_2050_PDsens_Nslice_1_CableLim_0]
                         # GCS_2020_PDsens_Nslice_1_CableLim_1,GCS_2030_PDsens_Nslice_1_CableLim_1, GCS_2050_PDsens_Nslice_1_CableLim_1]

Pgrid_nominal_list = np.linspace(50, 6000, 14)
#Pgrid_nominal_list = np.linspace(50, 4626.92307692, 11)
#Pgrid_nominal_list = Pgrid_nominal_list[:-1]
#Pgrid_nominal_list = np.linspace(100,100,1)

f_cr = annual_factor(0.07, 25)

total_start_time = time.time()
time_of_run = '{date:%Y-%m-%d_%H-%M-%S}'.format(date=datetime.now())


for GCS in GridCaseStudies_to_run:
    for GC in GCS.cases:
        GC.time_of_run = time_of_run

        # Run grid_calculation for every P in Pgrid_nominal_list
        calc_results = [grid_calculation(P, GC.pd_nominal, GC.N_slices, GC.year, GC.cable_limit, f_cr, 1, 1)
            for P in Pgrid_nominal_list]

        # Unpack the list of tuples into separate lists in the original order:
        (CAPEXgen_grid_list, CAPEXgen_list, CAPEXgrid_list, CAPEXcables_list, CAPEXtrench_list,
         CAPEXroad_list, CAPEXtransform_list, CAPEXreact_list, Annual_land_lease_costs_list, Fexit_list,
         Area_total_list, energy_loss_list, CAPEXgen_reference_list) = map(list, zip(*calc_results))

        # Compute annualized costs using numpy arrays
        an_CAPEXgen_grid_list      = f_cr * np.array(CAPEXgen_grid_list)
        an_CAPEXgen_list           = f_cr * np.array(CAPEXgen_list)
        an_CAPEXgrid_list          = f_cr * np.array(CAPEXgrid_list)
        an_CAPEXcables_list        = f_cr * np.array(CAPEXcables_list)
        an_CAPEXtrench_list        = f_cr * np.array(CAPEXtrench_list)
        an_CAPEXroad_list          = f_cr * np.array(CAPEXroad_list)
        an_CAPEXtransform_list     = f_cr * np.array(CAPEXtransform_list)
        an_CAPEXreact_list         = f_cr * np.array(CAPEXreact_list)
        an_CAPEXgen_reference_list = f_cr * np.array(CAPEXgen_reference_list)
        an_CAPEXgen_grid_area      = an_CAPEXgen_grid_list + np.array(Annual_land_lease_costs_list)

        # Store results in the GC.res dictionary
        GC.res.update({
            'CAPEXgen_list': CAPEXgen_list,
            'CAPEXgrid_list': CAPEXgrid_list,
            'CAPEXcables_list': CAPEXcables_list,
            'CAPEXtrench_list': CAPEXtrench_list,
            'CAPEXroad_list': CAPEXroad_list,
            'CAPEXtransform_list': CAPEXtransform_list,
            'CAPEXreact_list': CAPEXreact_list,
            'an_CAPEXcables':an_CAPEXcables_list,
            'an_CAPEXtrench':an_CAPEXtrench_list,
            'an_CAPEXroad':an_CAPEXroad_list,
            'an_CAPEXtransform':an_CAPEXtransform_list,
            'an_CAPEXreact':an_CAPEXreact_list,
            'an_CAPEXgen': an_CAPEXgen_list,
            'an_CAPEXgrid': an_CAPEXgrid_list,
            'an_CAPEXgen_grid': an_CAPEXgen_grid_list,
            'an_CAPEXgen_grid_area': an_CAPEXgen_grid_area,
            'an_CAPEXgen_reference': an_CAPEXgen_reference_list,
            'energy_loss': energy_loss_list,
            'Area_total': Area_total_list,
            'Annual_land_lease_costs': Annual_land_lease_costs_list,
            'Pgrid_nominal_list': Pgrid_nominal_list
        })

        # Build filename and dump GC to file
        filename = f"{GC.name}_MWgrid_{int(min(Pgrid_nominal_list))}_{int(max(Pgrid_nominal_list))}_np_{len(Pgrid_nominal_list)}__{time_of_run}.pkl"
        filename = os.path.join(res_subfolder(), filename)
        dump(GC, open(filename, 'wb'))

    # Dump the GridCaseStudy object after processing all its cases
    filename = f"{GCS.name}_MWgrid_{int(min(Pgrid_nominal_list))}_{int(max(Pgrid_nominal_list))}_np_{len(Pgrid_nominal_list)}__{time_of_run}.pkl"
    filename = os.path.join(res_subfolder(), filename)
    dump(GCS, open(filename, 'wb'))

