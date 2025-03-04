import os
import numpy as np
import matplotlib.pyplot as plt
from utility_functions import slope_calc, res_subfolder, figure_subfolder
from pickle import load, dump

GCS_2020_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GCS_2020_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
GCS_2030_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GCS_2030_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
GCS_2050_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GCS_2050_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))

GCS_2020_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GCS_2020_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
GCS_2030_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GCS_2030_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))
GCS_2050_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14 = load(open(os.path.join(res_subfolder(), 'GCS_2050_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14__2025-02-20_20-37-35.pkl'), 'rb'))

GridCaseStudies_to_extract = [GCS_2020_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14,
                              GCS_2030_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14,
                              GCS_2050_PDsens_Nslice_1_CableLim_0_MWgrid_50_6000_np_14,
                              GCS_2020_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14,
                              GCS_2030_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14,
                              GCS_2050_pd_8_sensNslice_CableLim_0_MWgrid_50_6000_np_14]

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
    'savefig.dpi': 600,  # DPI for saving the figure
    'savefig.format': 'pdf',  # Format for saving the figure
    'savefig.bbox': 'tight',  # Ensures the plot is tightly cropped when saved
})
# colors_bar = colors_stacked_bar()
blue_MPI = (51 / 255, 165 / 255, 195 / 255)
red_MPI = (120 / 255, 0 / 255, 75 / 255)
green_MPI = (0 / 255, 118 / 255, 117 / 255)
gray_MPI = (135 / 255, 135 / 255, 141 / 255)
color_MPI = green_MPI
color_list = [blue_MPI, green_MPI, red_MPI, gray_MPI]

# PD sensitivity analysis
pd_nominal_list = []
Nslice_list = []

for GCS in GridCaseStudies_to_extract:
    for GC in GCS.cases:
        an_CAPEXgen_list = GC.res['an_CAPEXgen']
        an_CAPEXgrid_list = GC.res['an_CAPEXgrid']
        an_CAPEXgen_grid_list = GC.res['an_CAPEXgen_grid']
        an_CAPEXgen_grid_area_list = GC.res['an_CAPEXgen_grid_area']
        an_CAPEXgen_reference_list = GC.res['an_CAPEXgen_reference']
        energy_loss_list = GC.res['energy_loss']
        Area_total_list= GC.res['Area_total']
        Annual_land_lease_costs_list = GC.res['Annual_land_lease_costs']
        Pgrid_nominal_list = GC.res['Pgrid_nominal_list']
        year = GC.year
        limit_cable = GC.cable_limit
        pd_nominal_list.append(GC.pd_nominal)
        Nslice_list.append(GC.N_slices)

        an_CAPEX_area_pred = slope_calc(Pgrid_nominal_list, an_CAPEXgen_grid_area_list)
        an_CAPEXgen_grid_pred = slope_calc(Pgrid_nominal_list, an_CAPEXgen_grid_list)
        an_CAPEXgen_pred = slope_calc(Pgrid_nominal_list, an_CAPEXgen_list)
        energy_loss_pred = slope_calc(Pgrid_nominal_list, energy_loss_list)

        if (GCS.name == 'GCS_2020_PDsens_Nslice_1_CableLim_0'
                or GCS.name == 'GCS_2030_PDsens_Nslice_1_CableLim_0'
                or GCS.name == 'GCS_2050_PDsens_Nslice_1_CableLim_0'):

            fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

            ax.plot(Pgrid_nominal_list, an_CAPEXgen_grid_area_list / 1e6, marker='.', markersize=20, color=blue_MPI)
            ax.plot(Pgrid_nominal_list, an_CAPEXgen_grid_list / 1e6, marker='.', markersize=20, color=green_MPI)
            ax.plot(Pgrid_nominal_list, an_CAPEXgen_list / 1e6, marker='.', markersize=20, color=red_MPI)
            ax.plot(Pgrid_nominal_list, an_CAPEXgen_reference_list / 1e6, linestyle='--', linewidth=1.2, color=red_MPI)

            #plt.title(f"Year = {year}, Power density = {GC.pd_nominal} MW/km$^2$")
            plt.xlabel('Grid output capacity (MW)')
            plt.ylabel('Annualised total costs (mil. USD/a)')
            plt.ylim(0, 1200)
            plt.xlim(0, max(Pgrid_nominal_list))
            # plt.legend(['gen. + grid + area','gen. + grid','gen.'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
            plt.legend(['generation + grid + land', 'generation + grid', 'generation', 'generation, linear scaling'], loc='upper left')

            plt.tight_layout()
            fig_name = 'fig_grid_study_costs_' + year + '_cable_limit_' + str(limit_cable) + '_pd_' + str(GC.pd_nominal) + '.pdf'
            fig_name = os.path.join(figure_subfolder(), fig_name)
            plt.savefig(fig_name)
            plt.show()


            fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

            ax.plot(Pgrid_nominal_list, np.array(energy_loss_list) * 100, marker='.', markersize=20, color=blue_MPI)
            #ax.plot(Pgrid_nominal_list, energy_loss_pred * 100, linestyle='--', linewidth=0.5, color=blue_MPI)

            plt.title(f"Year = {year}, Power density = {GC.pd_nominal} MW/km$^2$")
            plt.xlabel('Grid output capacity (MW)')
            plt.ylabel('Grid power loss (%)', color=blue_MPI)
            plt.ylim([0, 4])
            ax.tick_params(axis='y', labelcolor=blue_MPI)

            ax2 = ax.twinx()
            ax2.plot(Pgrid_nominal_list, Area_total_list, marker='.', markersize=20,
                     color=red_MPI)  # 'b--' is a blue dashed line
            ax2.set_ylabel('Total area (km$^2$)', color=red_MPI)
            ax2.tick_params(axis='y', labelcolor=red_MPI)  # Set y-axis label and tick color
            plt.ylim([0, 1500])
            plt.xlim(0, max(Pgrid_nominal_list))

            plt.tight_layout()
            fig_name = 'fig_grid_study_area_losses_' + year + '_cable_limit_' + str(limit_cable) + '_pd_' + str(GC.pd_nominal) + '.pdf'
            fig_name = os.path.join(figure_subfolder(), fig_name)
            plt.savefig(fig_name)
            plt.show()

    if (GCS.name == 'GCS_2020_PDsens_Nslice_1_CableLim_0'
            or GCS.name == 'GCS_2030_PDsens_Nslice_1_CableLim_0'
            or GCS.name == 'GCS_2050_PDsens_Nslice_1_CableLim_0'):
        fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

        for j in range(len(GCS.cases)):
            ax.plot(Pgrid_nominal_list, GCS.cases[j].res['an_CAPEXgen_grid_area'] / 1e6, marker='.', markersize=20,
                    color=color_list[j])

        plt.title(f"Year = {year}")
        plt.xlabel('Grid output capacity (MW)')
        plt.ylabel('Annualised total costs (mil. USD/a)')
        plt.ylim(0, 1200)
        plt.xlim(0, max(Pgrid_nominal_list))
        # plt.legend(['gen. + grid + area','gen. + grid','gen.'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
        plt.legend([f"Power density = {pd_nominal_list[0]} MW/km$^2$", f"Power density = {pd_nominal_list[1]} MW/km$^2$",
                    f"Power density = {pd_nominal_list[2]} MW/km$^2$"], loc='upper left')

        plt.tight_layout()
        fig_name = 'fig_grid_study_PDsens_costs_' + year + '_cable_limit_' + str(limit_cable) + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

        for j in range(len(GCS.cases)):
            ax.plot(Pgrid_nominal_list, GCS.cases[j].res['an_CAPEXgrid']/ 1e6, marker='.', markersize=20, color=color_list[j])

        #plt.title(f"Year = {year}")
        plt.xlabel('Grid output capacity (MW)')
        plt.ylabel('Annualised grid costs (mil. USD/a)')
        plt.ylim(0, 150)
        plt.xlim(0, max(Pgrid_nominal_list))
        # plt.legend(['gen. + grid + area','gen. + grid','gen.'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
        plt.legend([f"Power density = {pd_nominal_list[0]} MW/km$^2$", f"Power density = {pd_nominal_list[1]} MW/km$^2$",
                    f"Power density = {pd_nominal_list[2]} MW/km$^2$"], loc='upper left')

        plt.tight_layout()
        fig_name = 'fig_grid_study_PDsens_gridcosts_' + year + '_cable_limit_' + str(limit_cable) + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

        for j in range(len(GCS.cases)):
            ax.plot(Pgrid_nominal_list, GCS.cases[j].res['Area_total'], marker='.', markersize=20, color=color_list[j])

        #plt.title(f"Year = {year}")
        plt.xlabel('Grid output capacity (MW)')
        plt.ylabel('Total area (km$^2$)')
        plt.ylim(0, 1500)
        plt.xlim(0, max(Pgrid_nominal_list))
        # plt.legend(['gen. + grid + area','gen. + grid','gen.'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
        plt.legend([f"Power density = {pd_nominal_list[0]} MW/km$^2$", f"Power density = {pd_nominal_list[1]} MW/km$^2$",
                    f"Power density = {pd_nominal_list[2]} MW/km$^2$"], loc='upper left')

        plt.tight_layout()
        fig_name = 'fig_grid_study_PDsens_area_' + year + '_cable_limit_' + str(limit_cable) + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

        for j in range(len(GCS.cases)):
            ax.plot(Pgrid_nominal_list, np.array(GCS.cases[j].res['energy_loss'])*100, marker='.', markersize=20, color=color_list[j])

        #plt.title(f"Year = {year}")
        plt.xlabel('Grid output capacity (MW)')
        plt.ylabel('Grid power loss (%)')
        plt.ylim([0, 4])
        plt.xlim(0, max(Pgrid_nominal_list))
        # plt.legend(['gen. + grid + area','gen. + grid','gen.'], bbox_to_anchor=(1.03, 0.5), loc="center left", borderaxespad=0)
        plt.legend([f"Power density = {pd_nominal_list[0]} MW/km$^2$", f"Power density = {pd_nominal_list[1]} MW/km$^2$",
                    f"Power density = {pd_nominal_list[2]} MW/km$^2$"], loc='lower right')

        plt.tight_layout()
        fig_name = 'fig_grid_study_PDsens_losses_' + year + '_cable_limit_' + str(limit_cable) + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        plt.show()

    sensN_slice = 1
    if sensN_slice == 1:
        if (GCS.name == 'GCS_2020_pd_8_sensNslice_CableLim_0'
                or GCS.name == 'GCS_2030_pd_8_sensNslice_CableLim_0'
                or GCS.name == 'GCS_2050_pd_8_sensNslice_CableLim_0'):
            fig, ax = plt.subplots(figsize=(8, 6), dpi=600)
            Nslice_list = []
            for j in range(len(GCS.cases)):
                Nslice_list.append(GCS.cases[j].N_slices)
                ax.plot(Pgrid_nominal_list, GCS.cases[j].res['an_CAPEXgrid']/ 1e6, marker='.', markersize=20, color=color_list[j])

            #plt.title(f"Year = {year}")
            plt.xlabel('Grid output capacity (MW)')
            plt.ylabel('Annualised grid costs (mil. USD/a)')
            plt.ylim(0, 150)
            plt.xlim(0, max(Pgrid_nominal_list))
            plt.legend([f"N$_{{slice}}$ = {Nslice_list[0]}", f"N$_{{slice}}$ = {Nslice_list[1]}",
                        f"N$_{{slice}}$ = {Nslice_list[2]}", f"N$_{{slice}}$ = {Nslice_list[3]}"], loc='upper left' )

            plt.tight_layout()
            fig_name = 'fig_grid_study_sensNslice_gridcosts_' + year + '_cable_limit_' + str(limit_cable) + '.pdf'
            fig_name = os.path.join(figure_subfolder(), fig_name)
            plt.savefig(fig_name)
            plt.show()

            fig, ax = plt.subplots(figsize=(8, 6), dpi=600)
            Nslice_list = []
            for j in range(len(GCS.cases)):
                Nslice_list.append(GCS.cases[j].N_slices)
                ax.plot(Pgrid_nominal_list, np.array(GCS.cases[j].res['energy_loss'])*100, marker='.', markersize=20,
                        color=color_list[j])

            # plt.title(f"Year = {year}")
            plt.xlabel('Grid output capacity (MW)')
            plt.ylabel('Grid power loss (%)')
            plt.ylim(0, 4)
            plt.xlim(0, max(Pgrid_nominal_list))
            plt.legend([f"N$_{{slice}}$ = {Nslice_list[0]}", f"N$_{{slice}}$ = {Nslice_list[1]}",
                        f"N$_{{slice}}$ = {Nslice_list[2]}", f"N$_{{slice}}$ = {Nslice_list[3]}"], loc='lower right')

            plt.tight_layout()
            fig_name = 'fig_grid_study_sensNslice_losses_' + year + '_cable_limit_' + str(limit_cable) + '.pdf'
            fig_name = os.path.join(figure_subfolder(), fig_name)
            plt.savefig(fig_name)
            plt.show()


