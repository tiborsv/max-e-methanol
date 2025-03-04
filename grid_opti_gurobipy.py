import numpy as np
import networkx as nx
import gurobipy as gp
from gurobipy import GRB
import math
from dataclasses import dataclass, field



def grid_opt_loss_gurobi_scaled(G, Fexit, Fgen_cell_max, trenching_costs, road_costs, cable_install_costs, capex_Wind,
                         f_connect_eng, printing_results, limit_cables, land_lease_costs, f_cr):

    m = gp.Model("grid_opti_gurobipy")

    # Sets
    u_nodes = list(G.nodes())  # Set of nodes u
    v_nodes = list(G.nodes())  # Set of nodes v

    # Identifying predecessor and successor nodes
    pred = {u: list(G.predecessors(u)) for u in u_nodes}
    succe = {u: list(G.successors(u)) for u in u_nodes}

    # Combined set uv with actually active edges
    l_dict = {(u, v): G[u][v]['weight'] if G.has_edge(u, v) else 0 for u in u_nodes for v in
              v_nodes}  # [km] edge length parameter dictionary l(u, v)
    uv = [(u, v) for u in u_nodes for v in v_nodes if l_dict[(u, v)] > 0]

    # Parameters
    cost_SF = 1e5   # [-] cost-scaling factor
    i_SF = 1e3      # [-] current scaling factor

    length_factor = 1.15    # [-] ref: Zarkovic et al. 2021 uses 1.4 (even reports of 1.7), extra length due to obstacles leading to non-straight distances
    f = 50                  # [1/s] grid frequency

    land_lease_costs = land_lease_costs / cost_SF                       # [USD/MW/a / cost SF] land lease costs per MW, ref: Hau et al. 2016
    trenching_costs = trenching_costs /cost_SF                          # [USD/km  / cost SF] trenching costs
    road_costs = road_costs             /cost_SF                        # [USD/km   / cost SF] road costs
    cable_install_costs = cable_install_costs  /cost_SF                 # [USD/km   / cost SF] per each 3-phase cable
    costs_reactive_compensation = 28200 / cost_SF                       # [USD/MVAr  /cost SF] ref: national grid - shunt reactor
    capex_Wind_MW = capex_Wind * 1000       /cost_SF                    # [USD 2022/MWac   / cost SF]
    number_of_isolated_nodes = len(list(nx.isolates(G)))                # [-] some nodes in the graph are not considered (as the chosen overcapacity to allow for losses is smaller then the total number of nodes, the leftover nodes are just not connected to the rest of the graph)
    F_max = (G.number_of_nodes() - number_of_isolated_nodes - 1) * Fgen_cell_max + 1  # [MW] maximum possible energy flow
    Fexit = Fexit                                                       # [MW] flow exiting the grid slice
    print("Grid output [MW] = ", round(Fexit, 0))

    U = 33000           # [V] lower voltage level considered
    U_HV = 110000       # [V] higher voltage level considered
    power_factor = 1    # [-] taking power factor as equal to one as we also assume reactive power compensation
    I_max_possible = F_max * 1e6 / (np.sqrt(3) * U * power_factor) / i_SF


    @dataclass(kw_only=True)
    class Cable:
        S_mm: float
        U: float
        I_limit: float = float("nan")
        cost_cable: float = float("nan")
        R: float = float("nan")
        capacitance_microF: float = float("nan")
        Inductance: float = float("nan")
        X: float = float("nan")

        def cable_parametrisation(self, cost_SF=1, i_SF=1):
            self.I_limit = (51.643 * self.S_mm ** 0.4475) / i_SF # [A] cable limitation (unipolar) fitted based on the Hau et al. 2016 and reports of MVA for 20 kV and 110 kV for different cross-sectional area cables, cables larger than 800 mm2 are extrapolated from the values for smaller cables
            if self.U <= 33000:
                self.cost_cable = 1000 / cost_SF  * (0.0886 * self.S_mm + 11.925)  # [USD2022/km   / cost_SF] middle-voltage unipolar-cable costs, fitted based on Hau 2016
            else:
                self.cost_cable = 1000  / cost_SF * ((0.0886 * self.S_mm + 11.925) + 82.9 * (self.U/1000 - 20)/(110 - 20))  # [USD 2022/km   / cost_SF] high-voltage unipolar-cable costs, fitted based on Hau 2016 (20 kV) and adjusted to high voltage based on linearly scaling the difference reported for the 800 mm MV and HV cable costs

            self.R = 43.108 * self.S_mm **(-1.018)  # [Ohm/km] fitting based on data from Datasheet elandcable for aluminum cable and recalculated to 90 deg C based on Datasheet of Bahra.

            if self.U <= 66000:
                self.capacitance_microF = 0.0344*self.S_mm**0.3547 # [microF/km] based on data from Datasheet of elandcable
            else:
                self.capacitance_microF = 0.0183*self.S_mm**0.394  # [microF/km] based on data from Datasheet of Nexans

            self.Inductance = 0.864*self.S_mm**(-0.159)       # [mH/km]
            return

    cable_240_U = Cable(S_mm=240, U=U)
    cable_240_U.cable_parametrisation(cost_SF, i_SF)

    cable_400_U = Cable(S_mm=400, U=U)
    cable_400_U.cable_parametrisation(cost_SF, i_SF)

    cable_800_U = Cable(S_mm=800, U=U)
    cable_800_U.cable_parametrisation(cost_SF, i_SF)

    cable_1200_U = Cable(S_mm=1200, U=U)
    cable_1200_U.cable_parametrisation(cost_SF, i_SF)

    cable_1600_U = Cable(S_mm=1600, U=U)
    cable_1600_U.cable_parametrisation(cost_SF, i_SF)


    cable_240_U_HV = Cable(S_mm=240, U=U_HV)
    cable_240_U_HV.cable_parametrisation(cost_SF, i_SF)

    cable_400_U_HV = Cable(S_mm=400, U=U_HV)
    cable_400_U_HV.cable_parametrisation(cost_SF, i_SF)

    cable_800_U_HV = Cable(S_mm=800, U=U_HV)
    cable_800_U_HV.cable_parametrisation(cost_SF, i_SF)

    cable_1200_U_HV = Cable(S_mm=1200, U=U_HV)
    cable_1200_U_HV.cable_parametrisation(cost_SF, i_SF)

    cable_1600_U_HV = Cable(S_mm=1600, U=U_HV)
    cable_1600_U_HV.cable_parametrisation(cost_SF, i_SF)


    max_possible_flow_node = {}
    for node in G.nodes():
        max_possible_flow_node[node] = (len(nx.ancestors(G, node)) + 1) * Fgen_cell_max

    max_possible_I_total_node = {key: value * 1e6 / (np.sqrt(3) * U * power_factor) / i_SF for key, value in max_possible_flow_node.items()}
    max_possible_I_HV_total_node = {key: value * 1e6 / (np.sqrt(3) * U_HV * power_factor) / i_SF for key, value in max_possible_flow_node.items()}

    max_possible_N_cables_node_not_rounded = {key: value / cable_1200_U.I_limit for key, value in max_possible_I_total_node.items()}
    max_possible_N_cables_node = {key: int(math.ceil(value)) for key, value in max_possible_N_cables_node_not_rounded.items()}

    max_possible_N_HV_cables_node_not_rounded = {key: value / cable_1600_U_HV.I_limit for key, value in max_possible_I_HV_total_node.items()}
    max_possible_N_HV_cables_node = {key: int(math.ceil(value)) for key, value in max_possible_N_HV_cables_node_not_rounded.items()}

    # Variables
    x = m.addVars(uv, vtype=GRB.BINARY, name="x")

    F = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="F")
    F_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="F_cable")
    F_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="F_HV")
    F_cable_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="F_cable_HV")

    cost_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_cable")
    cost_cable_var = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_cable_var")
    cost_cable_HV_var = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_cable_HV_var")
    cost_cable_fix = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_cable_fix")
    cost_road = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_road")
    cost_trench = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_trench")

    cost_transform = m.addVars(u_nodes, vtype=GRB.CONTINUOUS, lb=0.0, name="cost_transform")
    cost_transform_exit = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="cost_transform_exit")

    #I_total = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=I_max_possible, name="I_total")
    #I_HV_total = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=I_max_possible, name="I_HV_total")


    limit_cables = limit_cables # turn-on limiting the amount of installed cables based on the largest HV cable (instead of max possible low voltage cable)

    if limit_cables == 1:
        N_cables = m.addVars(uv, vtype=GRB.INTEGER, lb=0, ub=max_possible_N_HV_cables_node[1], name="N_cables")
    else:
        N_cables = m.addVars(uv, vtype=GRB.INTEGER, lb=0, ub=max_possible_N_cables_node[1], name="N_cables")

    N_HV_cables = m.addVars(uv, vtype=GRB.INTEGER, lb=0, ub=max_possible_N_HV_cables_node[1], name="N_HV_cables")
    I = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="I")
    I_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="I_HV")

    # cable selection vars---------

    I_max = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="I_max")
    I_HV_max = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="I_HV_max")

    Q_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="Q_cable")
    Q = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="Q")
    Q_HV_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="Q_HV_cable")
    Q_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="Q_HV")
    Q_total = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="Q_total")

    R = m.addVars(uv, vtype=GRB.CONTINUOUS,lb=0.0, name="R")
    capacitance_microF = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="capacitance_microF")

    R_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="R_HV")
    capacitance_HV_microF = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="capacitance_HV_microF")

    C_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="C_cable")
    C_cable_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, name="C_cable_HV")

    #sel_cable_240_U = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_240_U")
    sel_cable_400_U = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_400_U")
    #sel_cable_800_U = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_800_U")
    sel_cable_1200_U = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_1200_U")

    #sel_cable_240_U_HV = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_240_U_HV")
    #sel_cable_400_U_HV = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_400_U_HV")
    sel_cable_800_U_HV = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_800_U_HV")
    #sel_cable_1200_U_HV = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_1200_U_HV")
    sel_cable_1600_U_HV = m.addVars(uv, vtype=GRB.BINARY, name="sel_cable_1600_U_HV")

    #------------------------------

    y_transform = m.addVars(u_nodes, vtype=GRB.BINARY, name='y_transform')

    Fgen = m.addVars(u_nodes, vtype=GRB.CONTINUOUS, lb=0.0, ub=Fgen_cell_max, name="Fgen")
    F_transform = m.addVars(u_nodes, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="F_transform")
    F_transform_exit = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="F_transform_exit")

    Fgen_total = m.addVar(vtype=GRB.CONTINUOUS, lb=Fexit, ub=F_max, name="Fgen_total")
    CAPEXgrid = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXgrid")
    CAPEXroad = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXroad")
    CAPEXtrench = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXtrench")
    CAPEXcables = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXcables")
    CAPEXreact = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXreact")
    CAPEXtransform = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXtransform")
    CAPEXgen = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, ub = F_max*capex_Wind_MW, name="CAPEXgen") # ub = F_max*capex_Wind_MW
    CAPEXtotal = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="CAPEXtotal")
    Annual_costs = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="Annual_costs")

    Floss = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="Floss")
    Floss_HV = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="Floss_HV")

    Floss_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="Floss_cable")
    Floss_HV_cable = m.addVars(uv, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="Floss_HV_cable")

    Floss_sum = m.addVars(u_nodes, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="Floss_sum")
    Floss_HV_sum = m.addVars(u_nodes, vtype=GRB.CONTINUOUS, lb=0.0, ub=F_max, name="Floss_HV_sum")


    # starting values
    m.update()
    if limit_cables == 1:
        for u, v in uv:
            if abs(u - v) > 1 and u > 3: # not considering cable installation on the same level (nodes next to each other) for the initial guess
                x[u, v].Start = 1
                sel_cable_1600_U_HV[u, v].Start = 1
                sel_cable_1200_U[u, v].Start = 0
                N_cables[u, v].Start = 0
                N_HV_cables[u, v].Start = max_possible_N_HV_cables_node[u]
            y_transform[u].Start = 1
    else:
        for u, v in uv:
            if abs(u-v) > 1 and u > 3: # not considering cable installation on the same level (nodes next to each other) for the initial guess
                x[u, v].Start = 1
                sel_cable_1600_U_HV[u, v].Start = 0
                sel_cable_1200_U[u, v].Start = 1
                N_cables[u, v].Start = 1 * max_possible_N_cables_node[u]
                N_HV_cables[u, v].Start = 0
            y_transform[u].Start = 0






    m.update()
    # Objective function
    m.setObjective(Annual_costs, GRB.MINIMIZE)

    # Cost constraints
    m.addConstr(Annual_costs == CAPEXtotal*f_cr + land_lease_costs * Fgen_total, "Annual_costs")
    m.addConstr(CAPEXtotal == CAPEXgen + CAPEXgrid, "CAPEXtotal")
    m.addConstr(CAPEXgen == Fgen_total * capex_Wind_MW, "CAPEXgen")
    m.addConstr(CAPEXgrid == CAPEXcables + CAPEXtrench + CAPEXroad + CAPEXtransform + CAPEXreact, "CAPEXgrid")
    m.addConstr(CAPEXroad == gp.quicksum(cost_road[u, v] for u, v in uv), "CAPEXroad")
    m.addConstr(CAPEXtrench == gp.quicksum(cost_trench[u, v] for u, v in uv), "CAPEXtrench")
    m.addConstr(CAPEXcables == gp.quicksum(cost_cable[u, v] for u, v in uv), "CAPEXcables")
    m.addConstr(CAPEXreact == costs_reactive_compensation * Q_total, "CAPEXreact")

    for u, v in uv:
        m.addConstr(cost_cable_var[u, v] + cost_cable_HV_var[u, v] + cost_cable_fix[u, v] == cost_cable[u, v], f"cost_l_rule_{u}_{v}")
        m.addConstr( 3 * C_cable[u, v] * l_dict[u, v] * length_factor * N_cables[u, v] * f_connect_eng == cost_cable_var[u, v], f"cost_cable_var_rule_{u}_{v}")
        m.addConstr( 3 * C_cable_HV[u, v] * l_dict[u, v] * length_factor * N_HV_cables[u, v] * f_connect_eng == cost_cable_HV_var[u, v], f"cost_cable_HV_var_rule_{u}_{v}")

        m.addConstr(road_costs * l_dict[u, v] * length_factor * x[u, v] == cost_road[u, v], f"cost_road_rule_{u}_{v}")

        m.addConstr((N_cables[u, v] + N_HV_cables[u, v]) * cable_install_costs * l_dict[u, v] * length_factor == cost_cable_fix[u, v], f"cost_cable_fix_rule_{u}_{v}")
        m.addConstr((N_cables[u, v] + N_HV_cables[u, v]) * trenching_costs * l_dict[u, v] * length_factor == cost_trench[u, v],f"cost_trench_rule_{u}_{v}")

    m.addConstrs(((F_transform[u]*1e6*0.009742 + 347146.7*y_transform[u] + (64435.6 + 1.2*U_HV)*y_transform[u] ) / cost_SF == cost_transform[u] for u in u_nodes), "cost_transform") #fitted data Lundberg 2003 linear, including the switchgear costs #[USD  / cost SF]
    m.addConstr((F_transform_exit*1e6*0.009742 + (347146.7 + (64435.6 + 1.2*U_HV))*(sel_cable_800_U_HV[1, 0] + sel_cable_1600_U_HV[1, 0]) ) / cost_SF == cost_transform_exit, "cost_transform_exit") #[USD  / cost SF]
    m.addConstrs((F_transform[u] >= 6.3 * y_transform[u] for u in u_nodes), 'F_transform_limit')  # data Lundberg 2003
    m.addConstrs((F_transform[u] <= max_possible_flow_node[u]*y_transform[u] for u in u_nodes), 'F_y_transform_link')

    m.addConstr(gp.quicksum(cost_transform[u] for u in u_nodes) + cost_transform_exit == CAPEXtransform,"CAPEXtransform")

    # Energy balances constraints

    m.addConstrs((F[u, v] <= max_possible_flow_node[u] * x[u, v] for u, v in uv), "max_flow") # old version was with F_max
    m.addConstrs((F_HV[u, v] <= max_possible_flow_node[u] * x[u, v] for u, v in uv), "max_flow_HV") # old version was with F_max

    m.addConstr(gp.quicksum(F[u, 0] for u in pred[0]) - Floss_sum[0] + F_transform_exit == Fexit,"flow_balance_0")
    m.addConstr(gp.quicksum(F_HV[u, 0] for u in pred[0]) - Floss_HV_sum[0] == F_transform_exit, "flow_balance_0_HV")

    m.addConstrs((gp.quicksum(F[v, u] for v in pred[u]) - gp.quicksum(F[u, v] for v in succe[u]) - Floss_sum[u] - F_transform[u] + Fgen[u] == 0 for u in u_nodes if u > 0),"flow_balance")
    m.addConstrs((gp.quicksum(F_HV[v, u] for v in pred[u]) - gp.quicksum(F_HV[u, v] for v in succe[u]) - Floss_HV_sum[u] + F_transform[u]*0.985 == 0 for u in u_nodes if u > 0), "flow_balance_HV") # assuming 98.5% transformer efficiency

    m.addConstr(gp.quicksum(Fgen[u] for u in u_nodes) == Fgen_total, "flow_total_inlet")
    m.addConstr(Fgen[0] == 0, "flow_inlet_node_0")


    # Cable selection constraints
    m.addConstrs((R[u, v] ==
                   #   sel_cable_240_U[u, v] * cable_240_U.R
                     sel_cable_400_U[u, v] * cable_400_U.R
                   # + sel_cable_800_U[u, v] * cable_800_U.R
                   + sel_cable_1200_U[u, v] * cable_1200_U.R
                  for u, v in uv), "sel_R")

    m.addConstrs((R_HV[u, v] ==
                 #   sel_cable_240_U_HV[u, v] * cable_240_U_HV.R
           #       + sel_cable_400_U_HV[u, v] * cable_400_U_HV.R
                   sel_cable_800_U_HV[u, v] * cable_800_U_HV.R
                  + sel_cable_1600_U_HV[u, v] * cable_1600_U_HV.R
                  for u, v in uv), "sel_R_HV")


    m.addConstrs((capacitance_microF[u, v] ==
                  #      sel_cable_240_U[u, v] * cable_240_U.capacitance_microF
                  sel_cable_400_U[u, v] * cable_400_U.capacitance_microF
                  #+ sel_cable_800_U[u, v] * cable_800_U.capacitance_microF
                  + sel_cable_1200_U[u, v] * cable_1200_U.capacitance_microF
                  for u, v in uv), "sel_capacitance")

    m.addConstrs((capacitance_HV_microF[u, v] ==
                  #     sel_cable_240_U_HV[u, v] * cable_240_U_HV.capacitance_microF
                  # + sel_cable_400_U_HV[u, v] * cable_400_U_HV.capacitance_microF
                  sel_cable_800_U_HV[u, v] * cable_800_U_HV.capacitance_microF
                  # + sel_cable_1200_U_HV[u, v] * cable_1200_U_HV.capacitance_microF
                  + sel_cable_1600_U_HV[u, v] * cable_1600_U_HV.capacitance_microF
                  for u, v in uv), "sel_capacitance_HV")

    m.addConstrs((C_cable[u, v] ==
                  #  sel_cable_240_U[u, v] * cable_240_U.cost_cable
                   sel_cable_400_U[u, v] * cable_400_U.cost_cable
                  #+ sel_cable_800_U[u, v] * cable_800_U.cost_cable
                  + sel_cable_1200_U[u, v] * cable_1200_U.cost_cable
                  for u, v in uv), "sel_C_cable")

    m.addConstrs((C_cable_HV[u, v] ==
                  #+ sel_cable_240_U_HV[u, v] * cable_240_U_HV.cost_cable
                  #+  sel_cable_400_U_HV[u, v] * cable_400_U_HV.cost_cable
                   sel_cable_800_U_HV[u, v] * cable_800_U_HV.cost_cable
                  #+ sel_cable_1200_U_HV[u, v] * cable_1200_U_HV.cost_cable
                  + sel_cable_1600_U_HV[u, v] * cable_1600_U_HV.cost_cable
                  for u, v in uv), "sel_C_cable_HV")

    m.addConstrs((I_max[u, v] ==
                   # sel_cable_240_U[u, v] * cable_240_U.I_limit
                   sel_cable_400_U[u, v] * cable_400_U.I_limit
                  #+ sel_cable_800_U[u, v] * cable_800_U.I_limit
                  + sel_cable_1200_U[u, v] * cable_1200_U.I_limit
                  for u, v in uv), "sel_I_max")

    m.addConstrs((I_HV_max[u, v] ==
                #    sel_cable_240_U_HV[u, v] * cable_240_U_HV.I_limit
                  #+ sel_cable_400_U_HV[u, v] * cable_400_U_HV.I_limit
                   sel_cable_800_U_HV[u, v] * cable_800_U_HV.I_limit
                  #+ sel_cable_1200_U_HV[u, v] * cable_1200_U_HV.I_limit
                  + sel_cable_1600_U_HV[u, v] * cable_1600_U_HV.I_limit
                  for u, v in uv), "sel_I_HV_max")

    m.addConstrs(( sel_cable_400_U[u, v] + sel_cable_1200_U[u, v] <= 1 for u, v in uv), "sel_limit_cable")
    m.addConstrs(( sel_cable_800_U_HV[u, v] + sel_cable_1600_U_HV[u, v] <= 1 for u, v in uv), "sel_limit_cable_HV")
    m.addConstrs(( sel_cable_400_U[u, v] + sel_cable_1200_U[u, v]
             + sel_cable_800_U_HV[u, v] + sel_cable_1600_U_HV[u, v] <= 1 for u, v in uv if v >= 3),"sel_limit_cable_MV_and_HV")

    # Current calculations constraints
    m.addConstrs((F[u, v] == F_cable[u, v]*N_cables[u, v] for u, v in uv), "F_cable")
    m.addConstrs((F_cable[u, v] * 1e6 / (np.sqrt(3) * U * power_factor) / i_SF == I[u, v] for u, v in uv), "I") # current in one core (conductor) of a 3-phase cable
    m.addConstrs((I[u, v] <= I_max[u, v] for u, v in uv), "I_max") # max current in one core of a 3-phase cable

    m.addConstrs((F_HV[u, v] == F_cable_HV[u, v] * N_HV_cables[u, v] for u, v in uv), "F_cable_HV")
    m.addConstrs((F_cable_HV[u, v] * 1e6 / (np.sqrt(3) * U_HV * power_factor) / i_SF == I_HV[u, v] for u, v in uv), "I_HV") # current in one core (conductor) of a 3-phase cable
    m.addConstrs((I_HV[u, v] <= I_HV_max[u, v] for u, v in uv), "I_HV_max")

    # Losses calculations constraints
    m.addConstrs((Floss_cable[u, v] == 3 *(R[u, v]) * l_dict[(u, v)] * length_factor * I[u, v]**2 / 1e6 *(i_SF**2) for u, v in uv), "flow_loss")
    m.addConstrs((Floss[u, v] == N_cables[u, v] * Floss_cable[u, v] for u, v in uv), "Floss_cable")
    m.addConstrs((Floss_sum[u] == gp.quicksum(Floss[v, u] for v in pred[u]) for u in u_nodes), "flow_loss_sum")

    m.addConstrs((Floss_HV_cable[u, v] ==  3 * (R_HV[u, v]) * l_dict[(u, v)] * length_factor * I_HV[u, v]**2 / 1e6 *(i_SF**2) for u, v in uv), "flow_loss_HV")
    m.addConstrs((Floss_HV[u, v] == N_HV_cables[u, v] * Floss_HV_cable[u, v] for u, v in uv), "Floss_HV_cable")
    m.addConstrs((Floss_HV_sum[u] == gp.quicksum(Floss_HV[v, u] for v in pred[u]) for u in u_nodes), "flow_loss_sum_HV")

    m.addConstrs((Q_cable[u, v] == 3 * U**2 * 2*np.pi*f * capacitance_microF[u,v]/1e6 * l_dict[(u, v)] * length_factor / 1e6 for u, v in uv), "Q_cable")
    m.addConstrs((Q[u, v] == Q_cable[u, v] * N_cables[u, v] for u, v in uv), "Q")

    m.addConstrs((Q_HV_cable[u, v] == 3 * U**2 * 2*np.pi*f * capacitance_HV_microF[u,v]/1e6 * l_dict[(u, v)] * length_factor / 1e6 for u, v in uv), "Q_HV_cable")
    m.addConstrs((Q_HV[u, v] == Q_HV_cable[u, v] * N_HV_cables[u, v] for u, v in uv), "Q_HV")

    m.addConstr(Q_total == gp.quicksum(Q[u,v] + Q_HV[u,v] for u, v in uv), "Q_total")

    # Tightening constraints
    for u in u_nodes:
        for v in succe[u]:
            if v == succe[u][0]: # Add the constraint only when the condition is true
                m.addConstr(gp.quicksum(x[u, suc] for suc in succe[u]) <= 1, f"successor_limit_{u}_{v}")

    for u, v in uv:
        m.addConstr(N_cables[u, v] <= max_possible_N_cables_node[u] * x[u, v], f"max_N_cables_{u}_{v}") # maximum for each edge going out of a node based on its ancestors

    for u, v in uv:
        m.addConstr(N_HV_cables[u, v] <= max_possible_N_HV_cables_node[u] * x[u, v], f"max_N_HV_cables_{u}_{v}") # maximum for each edge going out of a node based on its ancestors

    for u, v in uv:
        m.addConstr(F[u, v] <= max_possible_flow_node[u] * x[u, v],f"max_F_{u}_{v}")  # maximum for each edge going out of a node based on its ancestors

    for u, v in uv:
        m.addConstr(F_HV[u, v] <= max_possible_flow_node[u] * x[u, v],f"max_F_HV_{u}_{v}")  # maximum for each edge going out of a node based on its ancestors

    for u in u_nodes:
        m.addConstr(gp.quicksum(N_cables[u_pred,u]*sel_cable_400_U[u_pred,u] for u_pred in pred[u]) + 1  >= gp.quicksum(N_cables[u, u_succe]*sel_cable_400_U[u,u_succe] for u_succe in succe[u]), f"N_cable_pred_U_400_limit_{u}")
        m.addConstr(gp.quicksum(N_cables[u_pred,u]*sel_cable_1200_U[u_pred,u] for u_pred in pred[u]) + 1  >= gp.quicksum(N_cables[u, u_succe]*sel_cable_1200_U[u,u_succe] for u_succe in succe[u]), f"N_cable_pred_U_1200_limit_{u}")

        m.addConstr(gp.quicksum(N_HV_cables[u_pred, u] * sel_cable_800_U_HV[u_pred, u] for u_pred in pred[u]) + 1 >= gp.quicksum(N_HV_cables[u, u_succe] * sel_cable_800_U_HV[u, u_succe] for u_succe in succe[u]), f"N_cable_pred_U_HV_800_limit_{u}")
        m.addConstr(gp.quicksum(N_HV_cables[u_pred, u] * sel_cable_1600_U_HV[u_pred, u] for u_pred in pred[u]) + 1 >= gp.quicksum(N_HV_cables[u, u_succe] * sel_cable_1600_U_HV[u, u_succe] for u_succe in succe[u]),f"N_cable_pred_U_HV_1600_limit_{u}")



    # Optimize model
    m.params.FuncNonlinear = 0
    m.params.MIPGap = 0.015
    m.params.NumericFocus = 0
    m.write('grid_model_gurobipy.lp')

    m.optimize()

    if printing_results == 1:
        for v in m.getVars():
            print('%s %g' % (v.VarName, v.X)) # values printing
            #print('S %s %g' % (v.VarName, v.Start)) # start values printing

    obj_val = m.ObjVal
    Fgen_total_slice = Fgen_total.X
    CAPEXtotal_slice = CAPEXtotal.X * cost_SF  #[USD]
    CAPEXgrid_slice = CAPEXgrid.X * cost_SF    #[USD]
    CAPEXgen_slice = CAPEXgen.X * cost_SF     #[USD]
    CAPEXtransform_slice = CAPEXtransform.X * cost_SF #[USD]
    CAPEXroad_slice = CAPEXroad.X * cost_SF #[USD]
    CAPEXtrench_slice = CAPEXtrench.X * cost_SF #[USD]
    CAPEXcables_slice = CAPEXcables.X * cost_SF #[USD]
    CAPEXreact_slice = CAPEXreact.X * cost_SF #[USD]

    H = nx.DiGraph()
    for uv_el in uv:
        if F[uv_el].X > 0:
            H.add_edge(uv_el[0], uv_el[1], weight=F[uv_el].X, cables=N_cables[uv_el].X)

    H_HV = nx.DiGraph()
    for uv_el in uv:
        if F_HV[uv_el].X > 0:
            H_HV.add_edge(uv_el[0], uv_el[1], weight=F_HV[uv_el].X, cables=N_HV_cables[uv_el].X)

    loc_transformer = []
    for u in u_nodes:
        if F_transform[u].X > 0:
            loc_transformer.append(u)


    m.printQuality()

    print('Runtime = ', m.Runtime)
    print('Max N cables = ', N_cables[1,0].X)
    print('Max N HV cables = ', N_HV_cables[1, 0].X)


    return (H, H_HV, loc_transformer, CAPEXtotal_slice, CAPEXgen_slice, CAPEXgrid_slice,
            CAPEXcables_slice, CAPEXroad_slice, CAPEXtrench_slice, CAPEXreact_slice, CAPEXtransform_slice, Fgen_total_slice, Fexit)
