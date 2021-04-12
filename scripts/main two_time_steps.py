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

# STEP 0 Define paths
#path_g = "../input/official_data/generation_new.csv"
path_g = "../input/official_data/generation_new_filled.csv"
path_d = "../input/official_data/demand.csv"
path_F = "../input/official_data/crossborder.csv"

# STEP 1 Load the data
g_d, F = aux.load_data(path_g, path_d, path_F, subset=False)
for country, df in g_d.items():
    g_d[country] = df.iloc[0:2]
F = F.iloc[0:2]




# STEP 2 Apply correction method
a_var, f_var = cm.internal_sigma_approach(g_d, F)

print("success")
sys.exit()