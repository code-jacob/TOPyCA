# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 08:33:31 2024
Author: Jakub Trušina
Name: Topology_Optimization.py
"""
import numpy as np
import pandas as pd
import os
from scipy.spatial import KDTree
import time
start_time = time.time()

# minimize = "VMIS"             # von Mises stress
# minimize = "INVA_2"           # Equivalent strain
# minimize = "ENERGY"           # "pseudo/shear deformation energy density" calculated simply as equivalent stress*strain or density*strain**2
minimize = "HEAT_POWER"         # conductivity times Laplacian of temperature (heat power density)

p = 1
p_max = 3
p_step = 0.5
move = 0.2
e_tol = 1e-5
e_tol_end = 1e-4
density_min = 1e-3
density_max = 1
theta = 1/2

aim_volume_fraction = 0.25
volume_tol = 0.3                # Tolerance for volume constraint (increase if oscilation)
volume_tol_min = 0.1            # 0.1 = 10% tolerance for aim_volume_fraction
e_tol_vol = 0.1
Lambda = 1
lambda_multiplier = 1.1
max_iter = 200                  # Maximum iterations for Lambda adjustment

radius = 0.7                    # higher than element size to eliminate checkerboard pattern
radius_end = radius/2                  # used when p = 3

relaxation = "no"
# relaxation = "yes"
p_relax = 3                     # start relaxing when p = 3
if relaxation == "yes":
    relaxation_factor_end = 0.8  # 0.8 -> allow 20% density change in next iteration for each point

# "yes" "no"
symmetry = "no"
# symmetry = "yes"
if symmetry == "yes":
    treshold_symmetry = 0.5
    radius_symmetry = 0.7
    point_symmetry = (0, 25, 0)
    direction_symmetry = (0, 1, 0)

stamping = "no"
# stamping = "yes"
if stamping == "yes":
    radius_stamping = 0.1
    # direction_stamping = (0,0,1)     # to change the direction you have to edit the function 
                                       # change COOR_* accordingly, only cartesian for now

casting = "no"
# casting = "yes"
if casting == "yes":
    radius_casting = 0.1
    treshold_casting = 0.5
    # direction_casting = (0,0,1)      # to change the direction you have to edit the function 
                                       # change COOR_* accordingly, only cartesian for now

two_way_casting = "no"
# two_way_casting = "yes"
if two_way_casting == "yes":
    radius_casting = 0.1
    treshold_casting = 0.5
    # direction_casting = (0,0,1)      # to change the direction you have to edit the function 
                                       # change COOR_* accordingly, only cartesian for now

# ========================= manufacturing constraints ==========================

def symmetry_constraint():
    print("Applying symmetry constraint...")

    plane_point = np.array(point_symmetry)
    plane_normal = np.array(direction_symmetry)
    plane_normal = plane_normal / np.linalg.norm(plane_normal)

    new_density = df["density"].copy()
    for index, row in df.iterrows():
        x, y, z = row["COOR_X"], row["COOR_Y"], row["COOR_Z"]
        original_point = np.array([x, y, z])
        to_plane_vector = original_point - plane_point
        distance_to_plane = np.dot(to_plane_vector, plane_normal)
        reflected_point = original_point - 2 * distance_to_plane * plane_normal

        distances_original = np.sqrt((df["COOR_X"] - x)**2 +
                                     (df["COOR_Y"] - y)**2 +
                                     (df["COOR_Z"] - z)**2)

        distances_reflected = np.sqrt((df["COOR_X"] - reflected_point[0])**2 +
                                      (df["COOR_Y"] - reflected_point[1])**2 +
                                      (df["COOR_Z"] - reflected_point[2])**2)

        inside_original = distances_original <= radius_symmetry
        inside_reflected = distances_reflected <= radius_symmetry
        combined_mask = inside_original | inside_reflected

        density = df.loc[combined_mask, "density"].max()
        new_density.loc[combined_mask] = density

    df["density"] = new_density


def stamping_constraint():
    print("Applying stamping constraint...")

    new_density = df["density"].copy()
    for index, row in df.iterrows():
        cx, cy, cz = row["COOR_X"], row["COOR_Y"], row["COOR_Z"]
        
        # distances = np.sqrt((df["COOR_Y"] - cy)**2 + (df["COOR_Z"] - cz)**2)
        # distances = np.sqrt((df["COOR_Z"] - cz)**2 + (df["COOR_X"] - cx)**2)
        distances = np.sqrt((df["COOR_X"] - cx)**2 + (df["COOR_Y"] - cy)**2)

        inside_cylinder = distances <= radius_stamping
        average_density = df.loc[inside_cylinder, "density"].mean()
        new_density.loc[inside_cylinder] = average_density

    df["density"] = new_density


def casting_constraint():
    print("Applying casting constraint...")

    new_density = df["density"].copy()
    for index, row in df.iterrows():
        cx, cy, cz = row["COOR_X"], row["COOR_Y"], row["COOR_Z"]
        distances = np.sqrt((df["COOR_X"] - cx)**2 + (df["COOR_Y"] - cy)**2)

        inside_cylinder = distances <= radius_casting
        # print(inside_cylinder)
        nodes_cylinder = df.loc[inside_cylinder]
        # print(nodes_cylinder)
        # nodes_cylinder["index"] = nodes_cylinder.index
        nodes_cylinder_sorted = nodes_cylinder.sort_values(by="COOR_Z", ascending=False)
        # nodes_cylinder_sorted = nodes_cylinder_sorted.reset_index(drop=True).reset_index()
        # print(nodes_cylinder_sorted)

        try:
            first_index = nodes_cylinder_sorted[nodes_cylinder_sorted['density'] > treshold_casting].index[0]
            # print(first_index)
            # Get the first density value greater than 0.5
            # first_density_above = nodes_cylinder_sorted.loc[first_index, 'density']
            # print(first_density_above)
            max_density = nodes_cylinder_sorted.loc[first_index:, "density"].max()
            nodes_cylinder_sorted.loc[:, 'density'] = density_min
            # first_density_above
            nodes_cylinder_sorted.loc[first_index:, 'density'] = max_density
            # print(nodes_cylinder_sorted)
            density = nodes_cylinder_sorted.loc[inside_cylinder, "density"]
            new_density.loc[inside_cylinder] = density
            # new_density = nodes_cylinder_sorted["density"]
            # print(new_density)
        except:
            pass

    df["density"] = new_density


def two_way_casting_constraint():
    print("Applying two way casting constraint..")

    new_density = df["density"].copy()
    for index, row in df.iterrows():
        cx, cy, cz = row["COOR_X"], row["COOR_Y"], row["COOR_Z"]
        distances = np.sqrt((df["COOR_X"] - cx)**2 + (df["COOR_Y"] - cy)**2)

        inside_cylinder = distances <= radius_casting
        # print(inside_cylinder)
        nodes_cylinder = df.loc[inside_cylinder]
        # print(nodes_cylinder)
        # nodes_cylinder["index"] = nodes_cylinder.index
        nodes_cylinder_sorted = nodes_cylinder.sort_values(by="COOR_Z", ascending=True)
        # nodes_cylinder_sorted = nodes_cylinder_sorted.reset_index(drop=True).reset_index()
        # print(nodes_cylinder_sorted)

        try:
            first_index = nodes_cylinder_sorted[nodes_cylinder_sorted['density'] > treshold_casting].index[0]
            last_index = nodes_cylinder_sorted[nodes_cylinder_sorted['density'] > treshold_casting].index[-1]
            # print("kkkk",first_index, last_index)
            # Get the first density value greater than 0.5
            # first_density_above = nodes_cylinder_sorted.loc[first_index, 'density']
            # print(first_density_above)
            max_density = nodes_cylinder_sorted.loc[first_index:, "density"].max()
            nodes_cylinder_sorted.loc[:, 'density'] = density_min
            # first_density_above
            nodes_cylinder_sorted.loc[first_index:last_index,'density'] = max_density
            # print(nodes_cylinder_sorted)
            density = nodes_cylinder_sorted.loc[inside_cylinder, "density"]
            new_density.loc[inside_cylinder] = density
            # new_density = nodes_cylinder_sorted["density"]
            # print(new_density)
        except:
            pass

    df["density"] = new_density

# =============================================================================
# =============================================================================

cwd = os.getcwd()
print(cwd)
time_previous = 1
step_time_end = time_previous + 1  # current iteration

print("Iteration = ", step_time_end)
print("Aim volume fraction = ", aim_volume_fraction)
print("Minimize :", minimize)

if minimize == "HEAT_POWER":
    inp_1 = f"./RESULTS/FLUX_{time_previous:.0f}.csv"
    df_1 = pd.read_csv(inp_1, skiprows=4, sep=r'\s+')
    FLUX_MAG = np.sqrt(df_1["FLUX"]**2 + df_1["FLUY"]**2 + df_1["FLUZ"]**2 )
    # FLUX_MAG = np.linalg.norm(df_1[["FLUX", "FLUY", "FLUZ"]])
    df_1["FLUX_MAG"] = FLUX_MAG
else:
    inp_1 = f"./RESULTS/VMIS_{time_previous:.0f}.csv"
    df_1 = pd.read_csv(inp_1, skiprows=4, sep=r'\s+')
    inp_2 = f"./RESULTS/INVA_2_{time_previous:.0f}.csv"
    df_2 = pd.read_csv(inp_2, skiprows=4, sep=r'\s+')
# print(df_1)

volume_tol_start = volume_tol
e_tol_start = e_tol
if time_previous == 1:
    df = df_1
    if minimize == "HEAT_POWER":
        pass
    else:
        df["INVA_2"] = df_2["INVA_2"]
    e_prev = 0
    residual = 1
    error_vol = 1
    relaxation_factor = 0
    
    Convergence_1 = pd.DataFrame({'Time':                   [time_previous],
                                  'lambda':                 [Lambda],
                                  'p':                      [p],
                                  'e':                      [e_prev],
                                  'e_tol':                  [e_tol],
                                  'residual':               [residual],
                                  'vol':                    [aim_volume_fraction],
                                  'volume_tol':             [volume_tol],
                                  'error_vol':              [error_vol],
                                  'radius':                 [radius],
                                  'move':                   [move],
                                  'relaxation_factor':      [relaxation_factor],

                                  })
else:
    inp = f"./RESULTS/density_{time_previous:.0f}.csv"
    df = pd.read_csv(inp)
    if minimize == "HEAT_POWER":
        df["FLUX_MAG"] = FLUX_MAG
    else:
        df["VMIS"] = df_1["VMIS"]
        df["INVA_2"] = df_2["INVA_2"]
    Convergence_1 = pd.read_csv("./RESULTS/Convergence.csv",  sep='\t')
    Lambda = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'lambda'].values[0]
    p = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'p'].values[0]
    e_prev = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'e'].values[0]
    residual = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'residual'].values[0]
    volume_tol = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'volume_tol'].values[0]
    radius = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'radius'].values[0]
    move = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'move'].values[0]
    relaxation_factor = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'relaxation_factor'].values[0]

# print(df.columns.values)
# print(df)

def filtering():
    print("Filtering start")
    # Combine coordinates
    coords = np.vstack((df["COOR_X"], df["COOR_Y"], df["COOR_Z"])).T
    tree = KDTree(coords)
    filtered_density = np.zeros(len(df))

    for i, coord in enumerate(coords):
        indices = tree.query_ball_point(coord, radius)
        weights = radius - np.linalg.norm(coords[indices] - coord, axis=1)
        filtered_density[i] = np.sum(weights*df["density"].iloc[indices])/np.sum(weights)
    df["density"] = filtered_density
    print("Filtering complete")

def update_density():
    sensitivity = -p * df["density"]**(p-1) * e
    dV_dx_e = 1  # Assuming volume this is constant for all nodes
    B_e = -sensitivity / (Lambda * dV_dx_e)
    
    x_e_new = df["density"] * B_e**theta
    # x_e_new = np.clip(x_e_new, density_min, density_max)
    x_e_new = np.clip(x_e_new, np.maximum(df["density"] - move, density_min), np.minimum(df["density"] + move, density_max))
    # x_e_new = np.clip(x_e_new, np.maximum(x_e_new - move, density_min), np.minimum(x_e_new + move, density_max))
    df["density"] = x_e_new

def volume_constraint():
    global Lambda
    global current_volume_fraction, error_vol

    iter_count = 0
    current_volume_fraction = np.mean(df["density"])
    print("Current Volume Fraction:", current_volume_fraction)
    error_vol = abs(current_volume_fraction - aim_volume_fraction)/aim_volume_fraction
    
    while error_vol > volume_tol and iter_count < max_iter:
        if current_volume_fraction > aim_volume_fraction:
            Lambda *= lambda_multiplier  # Increase Lambda to reduce density
        else:
            Lambda /= lambda_multiplier  # Decrease Lambda to increase density
        update_density()
        
        current_volume_fraction = np.mean(df["density"])
        iter_count += 1
        print(f"Iteration {iter_count}: Lambda = {Lambda}, Volume Fraction = {current_volume_fraction}")
        error_vol = abs(current_volume_fraction - aim_volume_fraction)/aim_volume_fraction
    if iter_count == max_iter:
        print("\033[33m"+"Warning: Lambda adjustment did not converge.")
        print("\033[0m")
    print(
        f"Adjusted Lambda: {Lambda}, Final Volume Fraction: {current_volume_fraction}")

nodes = len(df["COOR_X"])
print("nodes =", nodes)
if time_previous == 1:
    for j in range(nodes):
        df.at[j, "density"] = aim_volume_fraction

if residual < e_tol_vol and p == 1:
    volume_tol = max(volume_tol / 2, volume_tol_min)
print("Tolerance =", volume_tol)

if minimize == "VMIS":
    e = df["VMIS"]
elif minimize == "INVA_2":
    e = df["INVA_2"]
elif minimize == "ENERGY":
    # e = df["VMIS"] * df["INVA_2"]
    e = df["density"] * df["INVA_2"]**2
elif minimize == "HEAT_POWER":
    df["GRAD_T_MAG"] = FLUX_MAG/df["density"]
    # e = df["GRAD_T_MAG"]*df["FLUX_MAG"]
    e = df["density"]*df["GRAD_T_MAG"]**2

update_density()
volume_constraint()
update_density()

# ========================= manufacturing constraints ==========================

if symmetry == "yes":
    symmetry_constraint()

if stamping == "yes":
    stamping_constraint()

if casting == "yes":
    casting_constraint()

if two_way_casting == "yes":
    two_way_casting_constraint()

# =============================================================================

filtering()

if relaxation == "yes" and round(p,3) >= p_relax:
    density_prev = df["density"]
    relaxation_factor = relaxation_factor_end
    # df["density"] = relaxation_factor * density_prev + (1-relaxation_factor) * df["density"]
    density_diff =  df["density"] - density_prev
    df["density"] = density_prev + density_diff*(1-relaxation_factor)
    print("Relaxation factor =", relaxation_factor)

e_final = np.linalg.norm(e)
if time_previous != 1:
    residual = abs((e_final - e_prev)/e_prev)
    residual_prev = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'residual'].values[0]
    p_prev = Convergence_1.loc[Convergence_1['Time'] == time_previous-1, 'p'].values[0]
    # Lambda_prev = Convergence_1.loc[Convergence_1['Time'] == time_previous, 'lambda'].values[0]
    
    if p >= p_max:  radius = radius_end
        
    if p > 1:       e_tol = e_tol_end
    else:           e_tol = e_tol_start
    
    # if Lambda != Lambda_prev and p >= 3:
    #     volume_tol_min = volume_tol_min*2
    #     volume_tol = max(volume_tol_min, volume_tol)

    if residual < e_tol and residual_prev < e_tol and p == p_prev :
        if error_vol < volume_tol_min:
            p = min(p + p_step, p_max)
            # p = min(p * p_step, p_max)
            if p >= p_max and p_prev >= p_max:
                print("Solution CONVERGED")
                with open("./RESULTS/stop.txt", "w") as file: pass

df["INST"] = step_time_end
if minimize == "HEAT_POWER": df["HEAT_POWER"] = e
else: df["ENERGY"] = e

print("Penalization factor =", p)
print("e_prev =", e_prev)
print("e_final =", e_final)

df.to_csv(f"./RESULTS/density_{step_time_end:.0f}.csv", sep=",", index=False)

Convergence_2 = pd.DataFrame({'Time':                   [step_time_end],
                              'lambda':                 [Lambda],
                              'p':                      [p],
                              'e':                      [e_final],
                              'e_tol':                  [e_tol],
                              'residual':               [residual],
                              'vol':                    [current_volume_fraction],
                              'volume_tol':             [volume_tol],
                              'error_vol':              [error_vol],
                              'radius':                 [radius],
                              'move':                   [move],
                              'relaxation_factor':      [relaxation_factor],

                              })

merged_Convergence = pd.concat([Convergence_1, Convergence_2], ignore_index=True)

merged_Convergence['lambda'] = merged_Convergence['lambda'].apply(lambda x: f"{x:.6E}")
merged_Convergence['p'] = merged_Convergence['p'].apply(lambda x: f"{x:.3g}")
merged_Convergence['e'] = merged_Convergence['e'].apply(lambda x: f"{x:.6E}")
merged_Convergence['e_tol'] = merged_Convergence['e_tol'].apply(lambda x: f"{x:.6E}")
merged_Convergence['residual'] = merged_Convergence['residual'].apply(lambda x: f"{x:.6E}")
merged_Convergence['vol'] = merged_Convergence['vol'].apply(lambda x: f"{x:.3f}")
merged_Convergence['volume_tol'] = merged_Convergence['volume_tol'].apply(lambda x: f"{x:.3f}")
merged_Convergence['error_vol'] = merged_Convergence['error_vol'].apply(lambda x: f"{x:.3f}")
merged_Convergence['radius'] = merged_Convergence['radius'].apply(lambda x: f"{x:g}")
merged_Convergence['move'] = merged_Convergence['move'].apply(lambda x: f"{x:g}")
merged_Convergence['relaxation_factor'] = merged_Convergence['relaxation_factor'].apply(lambda x: f"{x:g}")

merged_Convergence.to_csv("./RESULTS/Convergence.csv", sep='\t', index=False)
# merged_Convergence.to_csv("./RESULTS/Convergence.csv",  sep='\t', float_format="%.6E", index=False)

# pd.set_option('display.max_rows', None)  # Show all rows
# pd.set_option('display.max_columns', None)  # Show all columns
# print(df)
# pd.reset_option('display.max_rows')
# pd.reset_option('display.max_columns')

end_time = time.time()
elapsed_time = end_time - start_time
hours = int(elapsed_time // 3600)
minutes = int((elapsed_time % 3600) // 60)
seconds = elapsed_time % 60
print(f"Elapsed time: {hours} hr {minutes} min {seconds:.2f} sec")
