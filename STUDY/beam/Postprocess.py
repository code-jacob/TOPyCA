# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 08:33:31 2024
Author: Jakub Trušina
Name: Topology_Optimization_Postprocess.py
"""
import pandas as pd
import glob
import time
start_time = time.time()

aim_volume_fraction = 0.5

file_pattern = "./RESULTS/density_*.csv"
files = glob.glob(file_pattern)
sorted_files = sorted(files, key=lambda x: int(x.split('_')[-1].split('.')[0]))

merged_df = pd.DataFrame()
for inp in sorted_files:
    # print(inp)
    df = pd.read_csv(inp) # ,low_memory=False)
    merged_df = pd.concat([merged_df, df], ignore_index=True)
# print(merged_df.columns.values)  
df1 = df.copy()
df1['INST'] = 1
df1['density'] = aim_volume_fraction

merged_df = pd.concat([df1,merged_df], ignore_index=True)
# print(merged_df)
output_file_path = "./RESULTS/all_density.csv"
merged_df.to_csv(output_file_path, index=False)
print("density .csv files merged")



end_time = time.time()
elapsed_time = end_time - start_time
hours = int(elapsed_time // 3600)
minutes = int((elapsed_time % 3600) // 60)
seconds = elapsed_time % 60
print(f"Postprocess - Elapsed time: {hours} hr {minutes} min {seconds:.2f} sec")
