# -*- coding: utf-8 -*-

# Import required libraries
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from math import exp
from scipy.optimize import curve_fit

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

# Directory of the input CSV files
inputs = 'C:/MSc-thesis/data-analysis/data/inputs/uld-mono'

# Read the CSV files, create a list of city names and write the CSV files
# into a list of NumPy record arrays
city_names = []
uld_arrays = []
for root, dirs, files in os.walk(inputs):
    for f in files:
        city_names.append(f[:3])
        array = np.recfromcsv(os.path.join(inputs, f), delimiter=',')
        uld_arrays.append(array)

### Visualizing the ULD values of the urban areas ###

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

# Plot the original ULD values of the urban areas
plt.figure()
fig, axes = plt.subplots(2, 2)
fig.subplots_adjust(hspace=0.3)
for i, ax in enumerate(fig.axes):
    array = uld_arrays[i]
    for name, color, label in zip(array.dtype.names[1:], colors, labels):
        ax.plot(array['r_km'], array[name], color=color, label=label)
        ax.axis([min(array['r_km']), max(array['r_km']), 0, 1])
    if i==0:
        ax.set_ylabel('ULD')
    elif i==2:
        ax.set_xlabel('Distance from the CBD (km)')
        ax.set_ylabel('ULD')
    elif i==3:
        ax.set_xlabel('Distance from the CBD (km)')
    ax.set_title(titles[i])
plt.legend(
    loc='lower center', bbox_to_anchor=(0.5,-0.05), ncol=3,
    bbox_transform=plt.gcf().transFigure)
plt.savefig(figures+'/uld_mono.png', bbox_inches='tight')

# Fitting the function to the ULD values

# Define the urban land density function
def uld_func(r, alpha, c, D):
    return (1-c)/(1+exp(1)**(alpha*(((2*r)/D)-1)))+c

# Set the default parameters and their bounds
p0 = (4., 0.05, 30.)
bounds = ((0, 0, 0), (np.inf, 1, np.inf))

# Fit the function for each urban area to get the optimized parameters for
# each year
popt_outputs = 'C:/MSc-thesis/data-analysis/data/outputs/popt-mono'
for i in range(len(uld_arrays)):
    array = uld_arrays[i]
    index_names = []
    popt_list = []
    for name in array.dtype.names[1:]:
        index_names.append(name[4:])
        popt, pcov = curve_fit(
            uld_func, array['r_km'], array[name], p0=p0, method='trf',
            bounds=bounds)
        # Calculate residuals
        res = array[name]-uld_func(array['r_km'], popt[0], popt[1], popt[2])
        # Sum of squared residuals
        ss_res = np.sum(res**2)
        # Total sum of squares
        ss_tot = np.sum((array[name]-np.mean(array[name]))**2)
        # Calculate the R-squared value, append to 'popt', add the result
        # to the list and save into a CSV file
        r_squared = 1-(ss_res/ss_tot)
        popt = np.append(popt, r_squared)
        popt_list.append(popt)
        popt_df = pd.DataFrame(
            popt_list, index=index_names,
            columns=['alpha', 'c', 'D', 'R_squared'])
        name = city_names[i]+'_popt.csv'
        popt_df.to_csv(os.path.join(popt_outputs, name), sep=',')


# Create a list of dataframes
popt_dfs = []
for root, dirs, files in os.walk(popt_outputs):
    for f in files:
        popt_dfs.append(pd.read_csv(os.path.join(popt_outputs, f)))

# Plot the original ULD values of the urban areas with the fitted graphs
plt.figure()
fig, axes = plt.subplots(2, 2)
fig.subplots_adjust(hspace=0.3)
for i, ax in enumerate(fig.axes):
    array = uld_arrays[i]
    popt_array = popt_dfs[i][['alpha', 'c', 'D']].as_matrix()
    for popt, name, color, marker, label in zip(
        popt_array, array.dtype.names[1:], colors, markers, labels):
        fit = uld_func(array['r_km'], popt[0], popt[1], popt[2])
        ax.plot(array['r_km'], fit, color=color, label=label+' opt')
        ax.plot(
            array['r_km'], array[name], color=color, ls='None',
            marker=marker, mfc='None', ms=5, label=label+' emp')
        ax.axis([min(array['r_km']), max(array['r_km']), 0, 1])
    if i==0:
        ax.set_ylabel('ULD')
    elif i==2:
        ax.set_xlabel('Distance from the CBD (km)')
        ax.set_ylabel('ULD')
    elif i==3:
        ax.set_xlabel('Distance from the CBD (km)')
    ax.set_title(titles[i])
plt.legend(
    loc='lower center', bbox_to_anchor=(0.5,-0.1), ncol=3,
    bbox_transform=plt.gcf().transFigure)
plt.savefig(figures+'/fit_mono.png', bbox_inches='tight')
