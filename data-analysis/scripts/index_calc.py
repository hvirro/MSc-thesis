# -*- coding: utf-8 -*-

# Import required libraries
import matplotlib.pyplot as plt
import pandas as pd
import os

# Parameters for the figures
plt.rcParams['lines.linewidth'] = 1.0
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.labelsize'] = 'large'
plt.rcParams['xtick.labelsize'] = 'medium'
plt.rcParams['ytick.labelsize'] = 'medium'
plt.rcParams['figure.figsize'] = 8, 6
plt.rcParams['figure.dpi'] = 300
plt.rcParams['legend.edgecolor'] = 'inherit'
plt.rcParams['legend.fancybox'] = False
plt.rcParams['legend.fontsize'] = 'large'

# Directory of the output figures
figures = 'C:/MSc-thesis/figures'

# Colors
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
# Line styles
lines = ['-', '--', '-.', ':']
# Markers
markers = ['o', 's', 'x', 'D']
# Legend labels
labels = ['1989', '2007', '2015/16']
# Titles
titles = ['Narva', u'Pärnu', 'Tallinn', 'Tartu']

# Directory of the input CSV files
inputs = 'C:/MSc-thesis/data-analysis/data/outputs/popt-mono'

# Create a list of dataframes
popt_dfs = []
for root, dirs, files in os.walk(popt_outputs):
    for f in files:
        popt_dfs.append(pd.read_csv(os.path.join(inputs, f), index_col=0))

# Define the functions for calculating the radii
def r1_func(D, alpha):
    return (D/2)*((-1.316957/alpha)+1)

def r0_func(D):
    return D/2

def r2_func(D, alpha):
    return(D/2)*((1.316957/alpha)+1)

# Calculate the radii
for df in popt_dfs:
    df['r1'] = r1_func(df.D, df.alpha)
    df['r0'] = r0_func(df.D)
    df['r2'] = r2_func(df.D, df.alpha)

# Define the compactness functions
def kp_func(r2, r1, D):
    return (r2-r1)/D

def ks_func(c, alpha, D):
    return 0.57735*(1-c)*alpha/(1.316957*D)

# Calculate compactness indicators
for df in popt_dfs:
    df['ks'] = ks_func(df.c, df.alpha, df.D)
    df['kp'] = kp_func(df.r2, df.r1, df.D)

kp_arrays = []
for df in popt_dfs:
     kp_arrays.append(np.array(df['kp']))
kp_df = pd.DataFrame(kp_arrays, index=titles, columns=labels)

ks_arrays = []
for df in popt_dfs:
     ks_arrays.append(np.array(df['ks']))
ks_df = pd.DataFrame(ks_arrays, index=titles, columns=labels)

# Plot the compactness parameters
kp_df = kp_df.T
plt.figure(figsize=(4, 3))
for title, line, marker in zip(titles, lines, markers):
    plt.plot(kp_df[title], color='k', ls=line, marker=marker, mfc='None', ms=5)
    plt.ylim(ymin=0, ymax=1)
plt.ylabel(r'$k_p$')
plt.legend(
    loc='center left', bbox_to_anchor=(0.9, 0.5),
    bbox_transform=plt.gcf().transFigure)
plt.savefig(os.path.join(figures, 'kp_fig.png'), bbox_inches='tight')

ks_df = ks_df.T
plt.figure(figsize=(4, 3))
for title, line, marker in zip(titles, lines, markers):
    plt.plot(ks_df[title], color='k', ls=line, marker=marker, mfc='None', ms=5)
plt.ylabel(r'$k_s$')
plt.legend(
    loc='center left', bbox_to_anchor=(0.9, 0.5),
    bbox_transform=plt.gcf().transFigure)
plt.savefig(os.path.join(figures, 'ks_fig.png'), bbox_inches='tight')

# Define the functions for calculating the degree of urban sprawl
def dr_func(r1, r1_prev, r2_prev):
    return (r1-r1_prev)*r2_prev

def Sr_func(dr2, dr1):
    return dr2/dr1

# Calculate the degree of urban sprawl
for df in popt_dfs:
    df['dr2'] = dr_func(df.r2, df['r2'].shift(), df['r1'].shift())
    df['dr1'] = dr_func(df.r1, df['r1'].shift(), df['r2'].shift())
    df['Sr'] = Sr_func(df.dr2, df.dr1)

# Write the data frames containing the optimized and derived model parameters
# into CSV files
outputs = 'C:/MSc-thesis/data-analysis/data/outputs/ix-mono'
for i in range(len(popt_dfs)):
    df = popt_dfs[i]
    name = city_names[i]+'_ix.csv'
    df.to_csv(os.path.join(outputs, name), sep=',')
