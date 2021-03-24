# Leading Question:
# How good are the reconstruction capabilities of the respective methods?
import pandas as pd
import numpy as np
import auxiliary_functions as aux
import plotting as plot
import correction_methods_attacking_vector as cm_av
import comparison as cmp
import testing as t
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import os
from time import time
import sys
import copy
from collections import defaultdict
import matplotlib.pyplot as plt

# STEP 0 Define the paths
path_g = "../input/official_data/generation_new_filled.csv"
path_d = "../input/official_data/demand.csv"
path_F = "../input/official_data/crossborder.csv"
path_g_d_com = "../output/attacking_vector/complete_set/g_d/"
path_g_d_att = "../output/attacking_vector/attacked_set/g_d/"
path_F_com = "../output/attacking_vector/complete_set/F.csv"
path_F_att =  "../output/attacking_vector/attacked_set/F.csv"
# Paths to clean sets


# STEP 1 Load the complete (fake reconciled) and the attacked data set
g_d_com = aux.load_all_csv_files(path_g_d_com)
F_com = pd.read_csv(path_F_com, index_col=0)
g_d_att = aux.load_all_csv_files(path_g_d_att)
F_att = pd.read_csv(path_F_att, index_col=0)
# Create deepcopies to maintain the original attacked data sets,
# since g_d_att, F_att are being altered by the correction methods
g_d_original = copy.deepcopy(g_d_att)
F_original = copy.deepcopy(F_att)

# STEP 2 Each methods creates a clean data set
#a_var, f_var = cm_av.external_sigma_approach(g_d_att, F_att, g_d_com, F_com)
#g_d_clean, F_clean = aux.make_clean(g_d_original, F_original, a_var, f_var, name="SIGE")
#done

#STEP 3 Calculate difference to complete data set
path_DEM = "../output/attacking_vector/clean_sets/DEM/"
path_CAS = "../output/attacking_vector/clean_sets/CAS/"
path_ADD = "../output/attacking_vector/clean_sets/ADD/"
path_FAC = "../output/attacking_vector/clean_sets/FAC/"
path_SIGI = "../output/attacking_vector/clean_sets/SIGI/"
path_SIGE = "../output/attacking_vector/clean_sets/SIGE/"
paths = {}
paths["DEM"] = path_DEM
paths["CAS"] = path_CAS
paths["ADD"] = path_ADD
paths["FAC"] = path_FAC
paths["SIGI"] = path_SIGI
paths["SIGE"] = path_SIGE

clean = {}
difference = {}
# Difference from g_d
for method, path in paths.items():
    difference[method] = 0
    clean[method] = aux.load_all_csv_files(path + "g_d/")
    F_clean = pd.read_csv(path + "F.csv", index_col=0)
    for country, df in clean[method].items():
        a = (df - g_d_com[country]) ** 2
        a = sum(a.sum())
        difference[method] += a
    b = (F_clean - F_com) ** 2
    b = sum(b.sum())
    difference[method] += b
    
base_value = difference["ADD"]
index = {}
for method, value in difference.items():
    index[method] = value / base_value


