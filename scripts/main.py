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
g_d_original = copy.deepcopy(g_d)
F_original = copy.deepcopy(F)

# STEP 2 Apply correction method
a_var, f_var = cm.internal_sigma_approach(g_d, F)
print("success")
sys.exit()

# STEP 3 Create reconciled data set from raw data and correction factors
g_d_clean, F_clean = aux.make_clean(g_d_original, F_original, a_var, f_var)

# Optional: STEP 4 Make country balances
#country_balances = aux.make_country_balances(g_d_clean, F_clean, name="SIGE/")
country_balances = aux.make_country_balances(g_d_original, F_original, name="SIGE/")

# Optional: STEP 5 Verify whether balancing equation is fulfilled
#report = t.verify_balancing_condition(country_balances)

# Optional: STEP 7 Measure affected values
#for country, _ in g_d_original.items():
    #g_d_original[country].to_csv("../output/debugging/factorial_approach/" + "g_d_original_" + country + ".csv")
    #g_d_clean[country].to_csv("../output/debugging/factorial_approach/" + "g_d_clean_" + country + ".csv")

#F_original.to_csv("../output/debugging/factorial_approach/" + "F_original" + ".csv")
#F_clean.to_csv("../output/debugging/factorial_approach/" + "F_clean" + ".csv")
#report, number =  cmp.affected_values(g_d_original, F_original, g_d_clean, F_clean)
#for country, _ in report.items():
#    report[country].to_csv("../output/debugging/factorial_approach/" + "affection_" + country + ".csv")

