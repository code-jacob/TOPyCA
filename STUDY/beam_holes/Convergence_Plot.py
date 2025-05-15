# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 08:33:31 2024
Author: Jakub Trušina
Name: Convergence_Plot.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("dark_background")
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
    plt.rcParams[param] = '0.9'  # very light grey
for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '#212946'  # bluish dark grey
plt.rcParams['axes.edgecolor'] = "2A3459" # '#2A546D'

df = pd.read_csv("./RESULTS/Convergence.csv", sep='\t')

fig = plt.figure(num=3, figsize=(12,8), dpi=80 )
plt.title( "Topology Optimization" , fontsize= 18)

df["e_norm"] = df["e"]/df["e"].max() ; df = df.rename(columns={'e_norm': 'Energy Norm'})
df = df.rename(columns={'lambda': '$\lambda$'})
df = df.rename(columns={'p': 'Penalization Factor'})
df = df.rename(columns={'p_step': 'Penalization Factor Step'})
df = df.rename(columns={'e': 'Energy'})
df = df.rename(columns={'e_tol': 'Energy Tolerance'})
df = df.rename(columns={'residual': 'Residual'})
df = df.rename(columns={'vol': 'Volume Fraction'})
df = df.rename(columns={'volume_tol': 'Volume Fraction Tolerance'})
df = df.rename(columns={'error_vol': 'Volume Fraction Error'})
df = df.rename(columns={'radius': 'Filtering Radius'})
df = df.rename(columns={'move': 'Move Limit'})
df = df.rename(columns={'relaxation_factor': 'Relaxation Factor'})

columns = df.columns
print("columns =", list(columns)  )

curve_color_0 = plt.cm.jet(np.linspace(0, 1, len(columns)-1))
def lighten_color(color, factor):
    white = np.array([255/255, 255/255, 255/255])  # Light blue-ish white
    lightened_rgb = (1 - factor) * color[:3] + factor * white
    return np.append(lightened_rgb, color[3])
curve_color = curve_color_0.copy()
curve_color[0] = lighten_color(curve_color_0[0], factor=0.2)  # Lighten only the first color

k = -2
for column in columns:
    if column != "Time":  # Exclude Time from being plotted against itself
        k+=1 
        plt.plot(df["Time"], df[column], "-", label=column +" = "+ str("%.3E"%(df[column].iloc[-1])), color=curve_color[k+1],  linewidth= 3, )
        # plt.text(df["Time"].iloc[-1], df[column].iloc[-1] , str("%.3E"%(df[column].iloc[-1])), fontsize= 14 , horizontalalignment='right', verticalalignment='bottom',)    
        # plt.plot(df["Time"], df['Energy'], "-", label=column +" = "+ str("%.3E"%(df[column].iloc[-1])), color=curve_color[k+1],  linewidth= 3, )

# num_curves = len(plt.gca().get_lines())
# import matplotlib as mpl
# cmap = mpl.cm.get_cmap('rainbow', num_curves)
# lines = plt.gca().get_lines()
# for ci, line in enumerate(lines):
#     line.set_color(cmap(ci))


plt.rc('xtick', labelsize= 14)   
plt.rc('ytick', labelsize= 14) 
# plt.gca().ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
# plt.yscale('symlog')
# plt.xscale('log')
plt.xlabel('$Iteration$' + ' $[-]$ ' , fontsize = 14)
plt.legend(loc='best', shadow= True,  ncol=1, fontsize= 14)
plt.tight_layout()
plt.grid(linestyle= '--', linewidth= 1, color='#2A3459')
plt.show(block= False )  
fig.canvas.draw() 
plt.style.use("default")







