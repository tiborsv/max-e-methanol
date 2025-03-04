import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from itertools import chain

def res_subfolder():
    subfolder = 'result_files'
    return subfolder

def figure_subfolder():
    subfolder = 'figure_files'
    return subfolder

def data_subfolder():
    subfolder = 'data_files'
    return subfolder


def extract_case_details(case_name):
    """
    Extracts the year and DAC technology type from the case name and returns a formatted string.

    Parameters:
    - case_name (str): The case name string, e.g., "C_p1s1m1_y2020_extra".

    Returns:
    - str: A formatted string containing the DAC type, year, and any content after the year.
    """
    # Split the case name into parts
    parts = case_name.split('_')

    # Extract the year (assumes format 'yYYYY' is the last part containing 'y')
    year_index = next((i for i, part in enumerate(parts) if part.startswith('y')), -1)
    year = parts[year_index][1:]  # Remove the 'y' and extract the year

    # Check for DAC type ('s' or 'l') at the specific position
    dac_segment = parts[1]  # Example: "p1s1m1"
    dac_type = "S" if "s" in dac_segment else "L" if "l" in dac_segment else None

    # Get additional content after the year, replacing underscores with spaces
    extra_content = " ".join(parts[year_index + 1:])  # Join with space
    if extra_content!='':
        extra_content = ", " + extra_content

    # Format the output string
    if dac_type is None:
        return f"Invalid DAC type, {year}{extra_content}"
    return f"DAC-{dac_type.upper()}, {year}{extra_content}"

def adjust_legend(ax, exclude_list=None, text_replacements=None):
    """
    Adjust the legend of a Matplotlib Axes object by excluding specified entries
    and replacing parts of legend text.

    Parameters:
    - ax: matplotlib.axes.Axes
        The Axes object containing the legend to adjust.
    - exclude_list: list of str, optional
        List of legend labels to exclude from the legend.
    - text_replacements: dict, optional
        Dictionary for replacing parts of legend text, where keys are substrings
        to replace and values are the new strings.

    Returns:
    - filtered_handles: list
        The filtered legend handles.
    - filtered_labels: list
        The filtered and adjusted legend labels.
    """
    if exclude_list is None:
        exclude_list = []
    if text_replacements is None:
        text_replacements = {}

    # Get current handles and labels
    handles, labels = ax.get_legend_handles_labels()

    # Initialize lists for filtered handles and labels
    filtered_handles = []
    filtered_labels = []

    for handle, label in zip(handles, labels):
        # Exclude entries in the exclude_list
        if label in exclude_list:
            continue

        # Apply text replacements
        for old_text, new_text in text_replacements.items():
            label = label.replace(old_text, new_text)

        # Append adjusted handle and label
        filtered_handles.append(handle)
        filtered_labels.append(label)

    # Update the legend with filtered handles and labels
    ax.legend(filtered_handles, filtered_labels)

    return filtered_handles, filtered_labels

# Define the base colors in RGB format (normalized to [0, 1])
blue = np.array([31, 120, 180]) / 255
green = np.array([51, 160, 44]) / 255
red = np.array([227, 26, 28]) / 255
orange = np.array([255, 127, 0]) / 255
purple = np.array([106, 61, 154]) / 255
brown = np.array([177, 89, 40]) / 255
yellow = np.array([255, 255, 153]) / 255
gray = np.array([100, 100, 100]) / 255
white = np.array([255, 255, 255]) / 255
black = np.array([0, 0, 0]) / 255

blue_MPI = np.array((51 / 255, 165 / 255, 195 / 255))
red_MPI = np.array((120 / 255, 0 / 255, 75 / 255))
green_MPI = np.array((0 / 255, 118 / 255, 117 / 255))
darkening = 60
yellow_MPI = np.array([236-darkening, 233-darkening, 212-darkening]) / 255

color_MPI = green_MPI

blue = blue_MPI
red = red_MPI
green = yellow_MPI
orange = green_MPI

def colors_stacked_bar():
    # Number of different categories
    num_proc = 3
    num_DAC_HP = 4
    num_stor = 4
    num_wind = 3
    num_WEL = 2
    num_PV = 1
    num_biomass = 5
    num_indir = 2

    color_offset = 0

    # Generate the custom colormap
    colors_bar = np.vstack([
        orange,     # WIND gen
        orange + (1 - orange) * (color_offset + 1) / num_wind,  # WIND grid
        orange + (1 - orange) * (color_offset + 2) / num_wind,  # Land lease
        purple,                                                 # RO
        red,                                                    # DACsorb
        red + (1 - red) * (color_offset + 1) / num_DAC_HP, # DAC
        red + (1 - red) * (color_offset + 2) / num_DAC_HP, # HP_amb
        red + (1 - red) * (color_offset + 3) / num_DAC_HP, # HP_int
        black, # MTS
        blue, # WEL
        blue + (1 - blue) * (color_offset + 0.3) / num_WEL,  # WEL stack replacement
        green, # BAT
        green + (1 - green) * 1 / num_stor, #CGH2
        green + (1 - green) * 2 / num_stor, # CO2tank
        green + (1 - green) * 3 / num_stor, # TES
        gray, # indir_CAPEX
        gray + (1 - gray) * 1/ num_indir, #indir_OPEX
    ])

    # # Display the colors
    # plt.imshow([colormap_custom], aspect='auto')
    # plt.axis('off')
    # plt.show()
    return colors_bar


def cost_scaling(CAP_new, CAP_ref, COST_ref, scaling_factor):
    return COST_ref*(CAP_new/CAP_ref)**scaling_factor

def annual_factor(interest,lifetime):
    i = interest
    n = lifetime
    f_cr = i*(i + 1)**n / ((i + 1)**n - 1)
    return f_cr
def len_side(r1, r2, deg_1, deg_2):
    deg = np.abs(deg_1-deg_2)
    rad = np.deg2rad(deg)
    l_sq = r1 ** 2 + r2 ** 2 - 2 * r1 * r2 * np.cos(rad)
    l = np.sqrt(l_sq)
    return l

def angle_cos(a,b,c):
    cos_angle_rad = (a**2 + b**2 - c**2) /(2*a*b)
    deg = np.rad2deg(np.arccos(cos_angle_rad))
    return deg

def network_form(N_levels, N_division, r0, A0, N_cells_required):

    lvls = pd.Series(np.arange(0, N_levels + 1))
    c_lvl = pd.Series(np.arange(0, N_levels + 1) * N_division)
    c_lvl[0] = 1

    c = list(np.arange(1, (N_levels + 1) * 2, 2) ** 2)

    r = [r0]
    A_cell = [A0]
    dr = [0]
    rm = [0]
    deg = [360]

    for i in np.arange(N_levels):
        new_r = r[i] * ((c[i + 1]) / (c[i])) ** (0.5)
        r.append(new_r)
        dr.append(r[i + 1] - r[i])
        rm.append(r[i] + dr[i + 1] / 2)
        deg.append(360 / c_lvl[i + 1])

        new_A_cell = (new_r ** 2 - r[i] ** 2) * np.pi / c_lvl[i + 1]
        A_cell.append(new_A_cell)

    df = pd.DataFrame(lvls, columns=['lvl'])
    df['c_lvl'] = c_lvl
    c_sec = c_lvl / N_division
    c_sec[0] = 1
    df['c_sec'] = c_sec
    df['c'] = c
    df['r'] = r
    df['A_cell'] = A_cell
    df['dr'] = dr
    df['rm'] = rm
    df['deg'] = deg

    plotting = 1
    if plotting == 1:
        fig = plt.figure(dpi=200, figsize=(8, 8))
        ax = fig.add_subplot(projection='polar')

        blue_MPI = (51 / 255, 165 / 255, 195 / 255)
        red_MPI = (120 / 255, 0 / 255, 75 / 255)
        green_MPI = (0 / 255, 118 / 255, 117 / 255)
        color_MPI = blue_MPI

    rad_point_lvl = []
    deg_point_lvl = []
    deg_point_lvl_sec = []
    rm_point_lvl = []
    rm_point_lvl_sec = []

    for i in np.arange(N_levels):
        if plotting == 1:
            circle = plt.Circle((0, 0), df['r'][i], transform=ax.transData._b, fill=False)
            ax.add_artist(circle)
        rad_plot = []
        rad_point = []
        rm_point = []

        for j in np.arange(df['c_lvl'][i + 1]):
            rad_plot.append(np.deg2rad(df['deg'][i + 1]) * j)
            rad_point.append(rad_plot[j] + np.deg2rad(df['deg'][i + 1] / 2))
            rm_point.append(df['rm'][i + 1])

            if plotting == 1:
                plt.polar([rad_plot[j], rad_plot[j]], [r[i + 1], r[i]], color='k')
                plt.polar(rad_point[j], df['rm'][i + 1], color=color_MPI, marker='o')

        rad_point_lvl.append(rad_point)
        deg_point_lvl.append(np.rad2deg(rad_point))
        rm_point_lvl.append(rm_point)

        deg_point_lvl_sec.append(deg_point_lvl[i][0:int(df['c_lvl'][i + 1] / N_division)])
        rm_point_lvl_sec.append(rm_point_lvl[i][0:int(df['c_lvl'][i + 1] / N_division)])

    if plotting ==1:
        ax.set_ylim(0, max(df['r']))
        ax.set_xlim(0, np.deg2rad(360 / N_division))
        ax.yaxis.grid(False)
        ax.grid(False)
        plt.show()

    # calculating parameters for 1 section (_sec) only and points (_p) to prepare incidence matrix
    N_c_sec = sum(df['c_sec'])
    deg_p_sec = list(chain.from_iterable(deg_point_lvl_sec))
    rm_p_sec = list(chain.from_iterable(rm_point_lvl_sec))
    deg_p_sec.insert(0, 360)
    rm_p_sec.insert(0, 0)

    branch_limit_angle = 22  # limit edge branching based on angle relative to radius direction

    Aj = np.zeros([len(deg_p_sec), len(deg_p_sec)])

    for i in np.arange(len(deg_p_sec)):
        for j in np.arange(len(deg_p_sec)):
            #if i > j:
           if rm_p_sec[i] >= rm_p_sec[j] and i!=j:
                Aj[i, j] = len_side(rm_p_sec[i], rm_p_sec[j], deg_p_sec[i], deg_p_sec[j])

    angles = np.zeros([len(deg_p_sec), len(deg_p_sec)])

    filtering = 1
    if filtering == 1:
        for i in np.arange(len(deg_p_sec)):
            for j in np.arange(len(deg_p_sec)):
                if i > j:
                    angles[i, j] = angle_cos(Aj[i, j], rm_p_sec[i], rm_p_sec[j])
                    if angles[i, j] >= branch_limit_angle:          # limit edge branching based on angle relative to radius direction
                        if abs(rm_p_sec[i] - rm_p_sec[j]) != 0:     # filtering out all edges, which have a larger angle than limit relative to radius, ignoring edges at same level
                            Aj[i, j] = 0

                    if i in [5, 13, 25, 41, 61, 85, 113, 145, 181, 221, 265, 313, 365]: # filtering middle nodes and limiting their branching
                        if not ((i, j) in [(5, 3), (13, 8), (25, 19), (41, 32), (61, 51),
                                           (85, 72), (113, 99), (145, 128), (181, 163), (221, 200), (265, 243), (313, 288), (365, 339)]):  # ignoring some particular cells in filtering by angle
                            if angles[i, j] >= 12:
                                Aj[i, j] = 0


                    if abs(rm_p_sec[i] - rm_p_sec[j]) == 0 and abs(i - j) > 1:  # filter out non-neighbours on the same level
                        Aj[i, j] = 0

                    #if Aj[i, j] > 2 * df['dr'][1] and j!=0:  # filtering out all edges connected beyond N levels (even directly to origin node = 0)
                    #    Aj[i, j] = 0

                    if Aj[i, j] >= 2 * df['dr'][1] and i > len(deg_p_sec)*0:  # filtering out all edges connected beyond N levels (even directly to origin node = 0)
                        Aj[i, j] = 0

                    if j==0 and i in [9, 8, 5, 12, 13, 14, 17, 18, 19, 20, 3, 2]: # leaving out specific connections
                        Aj[i, j] = 0

                    if i > N_cells_required: # leaving out cells which are not required (over the over-capacity)
                        Aj[i, j] = 0

    filtering = 1
    if filtering == 1:
        for i in np.arange(len(deg_p_sec)):
            for j in np.arange(len(deg_p_sec)):
                if i > j:
                    if Aj[i, j] > 2 * df['dr'][1] and j != 0:  # filtering out all edges connected beyond N levels (even directly to origin node = 0)
                        Aj[i, j] = 0



    filtering = 1
    if filtering == 1:
        for i in np.arange(len(deg_p_sec)):
            for j in np.arange(len(deg_p_sec)):
                if j > i: # going the other direction
                    if j > N_cells_required: # leaving out cells which are not required (over the over-capacity)
                        Aj[i, j] = 0
                    if abs(rm_p_sec[i] - rm_p_sec[j]) == 0 and abs(i - j) > 1:  # filter out non-neighbours on the same level
                        Aj[i, j] = 0


    filtering = 1
    if filtering == 1:
        end_nodes_in_lvls = [0]
        middle_nodes_in_lvls = [0]
        begin_nodes_in_lvls = [0]

        for i in range(len(lvls)):
            node_per_level = lvls[i]
            end_nodes_in_lvls.append(node_per_level+end_nodes_in_lvls[-1])
            middle_nodes_in_lvls.append(np.ceil(end_nodes_in_lvls[i] + node_per_level/2))
            if i>1:
                node_per_level = lvls[i-1]
            begin_nodes_in_lvls.append(node_per_level + begin_nodes_in_lvls[-1])

        end_nodes_in_lvls.pop(0)
        middle_nodes_in_lvls.pop(0)
        begin_nodes_in_lvls.pop(0)

        for i in np.arange(len(deg_p_sec)):
            for j in np.arange(len(deg_p_sec)):
                if abs(rm_p_sec[i] - rm_p_sec[j]) == 0: # only connections on the same level
                    for lvl in np.arange(len(end_nodes_in_lvls)):
                        if i >= begin_nodes_in_lvls[lvl] and i <= end_nodes_in_lvls[lvl]:
                            if i <= middle_nodes_in_lvls[lvl] and i>j: # leave out connections leading away from the centre
                                Aj[i, j] = 0
                            if j > middle_nodes_in_lvls[lvl] and j>i: # leave out connections leading away from the centre
                                Aj[i, j] = 0
                            if (lvl-1) % 4 != 0:  # every n-th level should have connections on same level left out
                                Aj[i, j] = 0

    filtering = 1
    if filtering == 1:
        for i in np.arange(len(deg_p_sec)): # turns off all same level connections
            for j in np.arange(len(deg_p_sec)):
                if abs(rm_p_sec[i] - rm_p_sec[j]) == 0:
                    Aj[i, j] = 0

    G = nx.from_numpy_array(np.matrix(Aj), edge_attr='weight', create_using=nx.DiGraph)
    position = list(zip(np.deg2rad(deg_p_sec), rm_p_sec))
    return df, Aj, G, position


def slope_calc(x, y):  # function to linear fit of lines (based on first section of the data)
    slope = (y[1] - y[0]) / (x[1] - x[0])
    y_pred = []
    for i in range(len(x)):
        y_pred.append(y[0] + (x[i] - x[0]) * slope)
    return np.array(y_pred)