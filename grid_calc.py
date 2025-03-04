import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from utility_functions import network_form, annual_factor, figure_subfolder
from grid_opti_gurobipy import grid_opt_loss_gurobi_scaled
from process_parameters import Process
import time
from datetime import datetime
import math
import os

def grid_calculation(Pgrid_nominal, pd_nominal, N_slices, year, limit_cables, f_cr, printing_results, plotting):

    Pgrid_nominal = Pgrid_nominal           # [MW] nominal power capacity the grid is designed for (is supposed to deliver to the chemical plant)
    Pgrid_total = 1.05 * Pgrid_nominal      # [MW] total capacity of grid considered for calculation (need to consider a larger grid due to energy losses for the optimization)

    # INPUT for network construction
    N_division = 8      # [-] determines the number of slices into which a circle is divided
    N_slices = N_slices # [-] number of slices considered in the grid (can be more slices added together)
    r0 = 1              # [km] radius of cell at 0th level (first cell)
    A0 = np.pi * r0**2  # [km2/cell] area of 1 cell

    turbine_vestasV150_capacity = 6   # [MW] rated capacity
    turbine_vestasV150_diameter = 150 # [m] turbine diameter https://www.vestas.com/en/energy-solutions/onshore-wind-turbines/enventus-platform/v150-6-0

    # Power density parameters
    area_utilization = 1                                                    # [-] ratio of area which can be utilized for installation of generation technologies
    pd_nominal = pd_nominal                                                 # [MW/km2] nominal power density of generation technology (8 MW/km2 our reference value)
    turbine_capacity = turbine_vestasV150_capacity                          # [MW/turbine] selected turbine rated power
    turbine_diameter = turbine_vestasV150_diameter                          # [m] selected turbine diameter

    turbine_spacing_diameters = 5                                                       # [-] number of diameters used for spacing of turbines, ref: Stevens et al. 2016 = 4.375
    turbine_spacing_area = (turbine_diameter * turbine_spacing_diameters/1000)**2       # [km2/turbine] assuming square layout
    pd_nominal_turbine_spacing = turbine_capacity / turbine_spacing_area                # [MW/km2] nominal power density based on spacing of wind-turbines

    turbine_density = pd_nominal / turbine_capacity * area_utilization        # [turbine/km2]
    turbine_per_cell = A0 * turbine_density                                   # [turbine/cell]
    capacity_per_cell = turbine_capacity * turbine_per_cell                   # [MW/cell]

    N_cells_required = math.ceil(Pgrid_total / capacity_per_cell / N_slices)  # [-] number of cells required in one slice

    levels = 1
    N_cells = 0
    N_cells_per_level = 1
    while N_cells < N_cells_required:                   # calculating the number of required levels in our grid to reach the required Pgrid_total capacity (N_cells_required)
        N_cells = N_cells + N_cells_per_level
        N_cells_per_level = N_cells_per_level + 1
        levels = levels + 1                             # number of cells in each level corresponds to the number of levels actually

    N_levels = levels-1
    df, Aj, G, position = network_form(N_levels, N_division, r0, A0, N_cells_required)

    # Parameters for optimization
    CEPCI_values = Process(name="CEPCI_values", description="importing a process where CEPCI values are saved")
    road_costs = 80000          * CEPCI_values.CEPCI["2022"] / CEPCI_values.CEPCI["2016"]                               # [USD 2022/km] ref: Stevens 2016, Hau 2016 reports costs of 100 EUR/m
    trenching_costs = 25000     * CEPCI_values.EUR_to_USD  * CEPCI_values.CEPCI["2022"] / CEPCI_values.CEPCI["2016"]    # [USD 2022/km] ref: Stevens 2016, Hau report 12-15 EUR/m on 20kV, 25-30 EUR/m on 110 kV (trenching +  cable install costs)
    cable_install_costs = 5000  * CEPCI_values.EUR_to_USD  * CEPCI_values.CEPCI["2022"] / CEPCI_values.CEPCI["2016"]    # [USD 2022/km] ref: Stevens 2016
    land_lease_costs_per_MW_per_year = 30000/3000 * CEPCI_values.EUR_to_USD * 1000                                      # [USD 2016/MW/a] ref: Hau 2016 (10000 EUR/MW/a),  Stevens 2016 reports 8000 or 4000-6000 USD 2016/MW/a, Mona and Hand 2015 report 8000 USD/MW/a
    land_lease_costs = land_lease_costs_per_MW_per_year * CEPCI_values.CEPCI["2022"] / CEPCI_values.CEPCI["2016"]       # [USD 2022/MW/a] ref: Hau 2016

    f_connect_eng = 1.2 # [-] cable connections and engineering overhead factor with regards to total cable costs (trench+inst.+cable) ref: Stevens 2016, Hau 2016 also report extra costs of 25% for the overall installation including cable connections
    cable_install_costs = cable_install_costs * f_connect_eng
    trenching_costs = trenching_costs * f_connect_eng

    Pin_max = capacity_per_cell                         # [MW] (1 area)
    Pin_total = (G.number_of_nodes() - 1) * Pin_max

    time_plot = '{date:%Y-%m-%d_%H-%M-%S}'.format(date=datetime.now())

    if plotting ==1:
        # FIGURE 1
        fig = plt.figure(dpi=600, figsize=(8, 8))
        ax = fig.add_subplot(projection='polar')
        blue_MPI =  ( 51/255, 165/255, 195/255)
        red_MPI =   (120/255,   0/255,  75/255)
        green_MPI = (  0/255, 118/255, 117/255)
        color_MPI = blue_MPI
        nx.draw_networkx_nodes(G, pos=position, node_color=[color_MPI] * len(G.nodes()))
        nx.draw_networkx_labels(G, position, font_family='Times New Roman', font_color='white')
        nx.draw_networkx_edges(G, pos=position, width=0.5, alpha=0.5, style='solid')

        ax.set_ylim(0, max(df['r']))
        ax.set_xlim(0, np.deg2rad(360/N_division))
        ax.yaxis.grid(False)
        ax.grid(False)
        fig_name = 'fig_grid_network_' + str(int(round(Pgrid_nominal,0))) + '_MW_' + time_plot + '.pdf'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)
        fig_name = 'fig_grid_network_jpg_' + str(int(round(Pgrid_nominal,0))) + '_MW_' + time_plot +  '.jpg'
        fig_name = os.path.join(figure_subfolder(), fig_name)
        plt.savefig(fig_name)

        plt.show()

    # Costs energy generation --> reference: https://atb.nrel.gov/electricity/2024/technologies
    capex_PV = {}
    ILR = 1.34  # [-] inverter loading ration used in the reference
    capex_PV['2020'] = 1483 / ILR  # [USD2022/kW DC] capex with a base year of 2022
    capex_PV['2030'] = 1193 / ILR  # [USD2022/kW DC] moderate cost scenario 2030
    capex_PV['2050'] = 683 / ILR  # [USD2022/kW DC] moderate cost scenario 2050

    capex_Wind = {}
    capex_Wind['2020'] = 1666  # [USD2022/kW AC] capex with a base year of 2022
    capex_Wind['2030'] = 1408  # [USD2022/kW AC] moderate cost scenario 2030
    capex_Wind['2050'] = 1115  # [USD2022/kW AC] moderate cost scenario 2050

    (H, H_HV, loc_transformer, CAPEXtotal_slice, CAPEXgen_slice, CAPEXgrid_slice,
     CAPEXcables_slice, CAPEXroad_slice, CAPEXtrench_slice, CAPEXreact_slice,
     CAPEXtransform_slice, Fgen_total_slice, Fexit_slice) = grid_opt_loss_gurobi_scaled(G, Pgrid_nominal/N_slices, Pin_max,
                                                                                  trenching_costs, road_costs, cable_install_costs,
                                                                                  capex_Wind[year], f_connect_eng, printing_results,
                                                                                  limit_cables, land_lease_costs, f_cr)

    Fgen_total = Fgen_total_slice*N_slices  # [MW] total installed generation capacity (all slices)
    Fexit = Fexit_slice*N_slices    #[MW] total exit power capacity of the whole grid (incl. losses)
    Area_total = Fgen_total / pd_nominal #[km2]
    Annual_land_lease_costs= land_lease_costs * Fgen_total #[USD2022/a]

    CAPEXgen_grid = CAPEXtotal_slice*N_slices  # [USD2022]
    CAPEXgrid = CAPEXgrid_slice*N_slices    # [USD2022]
    CAPEXtrench = CAPEXtrench_slice*N_slices # [USD2022]
    CAPEXroad = CAPEXroad_slice*N_slices # [USD2022]
    CAPEXreact = CAPEXreact_slice*N_slices # [USD2022]
    CAPEXtransform = CAPEXtransform_slice*N_slices # [USD2022]
    CAPEXcables= CAPEXcables_slice*N_slices #[USD2022]
    CAPEXgen = CAPEXgen_slice*N_slices      # [USD2022]
    energy_loss = (Fgen_total_slice-Fexit_slice) / Fgen_total_slice #[-]
    CAPEXgen_reference = capex_Wind[year] * Fexit * 1000 # [USD2022]

    if printing_results == 1:
        print('Total output capacity of the grid (MW) = ', round(Fexit_slice, 1), 'x', N_slices)
        print('Total installed generation capacity (MW) = ', round(Fgen_total_slice, 1), 'x', N_slices)
        print('Energy loss (%) = ', round(energy_loss * 100, 2))
        print('Costs area (Mil. USD/a) = ', round(Annual_land_lease_costs/1e6, 1))
        print('CAPEX gen. + grid (Mil. USD) = ', round(CAPEXgen_grid / 1e6, 1))
        print('CAPEX grid (Mil. USD) = ', round(CAPEXgrid/1e6, 1))
        print('     CAPEXcables (Mil. USD) = ', round(CAPEXcables / 1e6, 1))
        print('     CAPEXtrench (Mil. USD) = ', round(CAPEXtrench / 1e6, 1))
        print('     CAPEXroad (Mil. USD) = ', round(CAPEXroad / 1e6, 1))
        print('     CAPEXtransform (Mil. USD) = ', round(CAPEXtransform / 1e6, 1))
        print('     CAPEXreact (Mil. USD) = ', round(CAPEXreact / 1e6, 1))
        print('CAPEX generation (Mil. USD) = ', round(CAPEXgen/1e6, 1))
        print('Percentage CAPEX grid (%) = ', round(CAPEXgrid/CAPEXgen_grid*100, 2))
        print('Extra costs considering grid (%) = ', round((CAPEXgen_grid / CAPEXgen_reference - 1)*100, 2))

    # SOLVING OPTIMIZATION
    costs_connection = []
    Fgen_total_list = []

    for i in np.arange(len(Fgen_total_list)+1):

        costs_connection.append(CAPEXgen_grid)
        Fgen_total_list.append(Fgen_total)

        if plotting == 1:

            # FIGURE 2
            fig = plt.figure(dpi=600, figsize=(8, 8))
            ax = fig.add_subplot(projection='polar')

            nx.draw_networkx_nodes(G, pos=position, node_color=[color_MPI] * len(G.nodes()))
            nx.draw_networkx_labels(G, position, font_family='Times New Roman', font_color='white')
            nx.draw_networkx_edges(G, pos=position, width=0.3, alpha=0.1, style='solid')

            node_colors_H = [red_MPI if node in loc_transformer else color_MPI for node in H.nodes()]
            nx.draw_networkx_nodes(H, position, label=True, node_color=color_MPI, edgecolors=node_colors_H)

            # Function to adjust the angles slightly to avoid overlap
            def offset_polar_positions(pos, angle_offset=0.005):
                return [(angle + angle_offset, dist) for angle, dist in pos]

            for edge in H.edges(data='weight'):
                nx.draw_networkx_edges(H, position, edgelist=[edge], width=edge[2] ** 0.3 / 2, edge_color=[color_MPI] * len(H.edges()))

            for edge in H_HV.edges(data='weight'):
                nx.draw_networkx_edges(H_HV, offset_polar_positions(position), edgelist=[edge], width=edge[2] ** 0.3 / 2, edge_color=[red_MPI] * len(H_HV.edges()))

            edge_labels = {(u,v): str(int(H[u][v]['cables'])) for u,v in H.edges()}
            nx.draw_networkx_edge_labels(H, pos=position, edge_labels=edge_labels, font_size=2, font_color='white', bbox=dict(facecolor="none", edgecolor="none"))

            edge_labels = {(u,v): str(int(H_HV[u][v]['cables'])) for u,v in H_HV.edges()}
            nx.draw_networkx_edge_labels(H_HV, pos=offset_polar_positions(position), edge_labels=edge_labels, font_size=2, font_color='white', bbox=dict(facecolor="none", edgecolor="none"))

            ax.set_ylim(0, max(df['r']))
            ax.set_xlim(0, np.deg2rad(360 / N_division))
            ax.yaxis.grid(False)
            ax.grid(False)
            fig_name = 'fig_grid_network_solved' + str(int(round(Pgrid_nominal,0))) + '_MW_' + time_plot +  '.pdf'
            fig_name = os.path.join(figure_subfolder(), fig_name)
            plt.savefig(fig_name)
            fig_name = 'fig_grid_network_solved_jpg' + str(int(round(Pgrid_nominal,0))) + '_MW_' + time_plot + '.jpg'
            fig_name = os.path.join(figure_subfolder(), fig_name)
            plt.savefig(fig_name)
            plt.show()


    x=1
    return (CAPEXgen_grid, CAPEXgen, CAPEXgrid, CAPEXcables, CAPEXtrench, CAPEXroad, CAPEXtransform, CAPEXreact,
            Annual_land_lease_costs, Fexit, Area_total, energy_loss, CAPEXgen_reference)

single_run = 0

if single_run == 1:
    f_cr = annual_factor(0.07, 25)
    (CAPEXgen_grid, CAPEXgen, CAPEXgrid, CAPEXcables,
     CAPEXtrench, CAPEXroad, CAPEXtransform, CAPEXreact,
     Annual_land_lease_costs, Fexit,
     Area_total, energy_loss, CAPEXgen_reference) = grid_calculation(4169,
                                                                               8,
                                                                               1,
                                                                               '2020',
                                                                               0,
                                                                                f_cr,
                                                                               1,
                                                                               1)







x=1
