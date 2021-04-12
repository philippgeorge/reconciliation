import pandas as pd
import numpy as np
import auxiliary_functions as aux
import correction_methods as cm
import comparison as cmp
import testing as t
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import os
from time import time
import sys
import copy
import matplotlib.pyplot as plt
import auxiliary_functions as aux

#Define paths
path_g = "../input/official_data/generation_new_filled.csv"
path_d = "../input/official_data/demand.csv"
path_F = "../input/official_data/crossborder.csv"

# Load the data
g_d, F = aux.load_data(path_g, path_d, path_F, subset=False)

# Get a list of the included countries
countries = g_d.keys()

# Get a list of the production types
p_index = {}
for country, df in g_d.items():  
    p_index[country] = [x for x in df.columns.values if "demand" not in x if "total" not in x]
# Index for all production types
p_global = np.array(list(set( [item for sublist in p_index.values() for item in sublist])))
p_global.sort()

# Get the total of generation data of the included countries
total_production_dict = {}
for country, df in g_d.items():
    df = df[[x for x in df.columns if "demand" not in x]]
    total_production_dict[country] = sum(df.sum())
    
total_production = sum(total_production_dict.values())

# Get the total demand data of the included countries
total_demand_dict = {}
for country, df in g_d.items():
    df = df[[x for x in df.columns if "demand" in x]]
    total_demand_dict[country] = sum(df.sum())
total_demand = sum(total_demand_dict.values())

# Get the total cross-border flows of the included countries
total_cross = sum(F.sum())
# Get the cross-border flows that got lost for Lithuania
F_raw = pd.read_csv(path_F)
F_LT = F_raw[[x for x in F_raw.columns if x in ["BY - LT", "LT - RU"]]]
F_LT = F_LT.abs()
lost_cross = F_LT.sum()ost

sys.exit()

# Find the number of time steps the left side has been bigger
#path_g_d_com = "../output/attacking_vector/complete_set/g_d/"
#g_d_com = aux.load_all_csv_files(path_g_d_com)

# Mock up data
x = (1, 2, 3, )
y1 = (-1, 2, 3)
y2 = (-3, -2, -1)
y3 = (-0.5, 0,5)  # invisible to hold the 0-axis in the middle

fig = plt.figure()

ax = fig.add_axes([0, 0, 1, 1])

# Move left y-axis and bottim x-axis to centre, passing through (0,0)
ax.spines["left"].set_position("center")


# Eliminate upper and right axes
ax.spines["right"].set_color("none")
ax.spines["top"].set_color("none")

# Show ticks in the left and lower axes only
ax.xaxis.set_ticks_position("bottom")
ax.set_yticklabels([])
ax.set_xticklabels([])


#ax.yaxis.set_ticks_position("left")


ax.barh(x, y1)
ax.barh(x, y2, color="g")

plt.show()