import pandas as pd
import numpy as np
import auxiliary_functions as aux
import plotting as plot
import correction_methods as cm
import comparison as cmp
import testing as t
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import os
from time import time
import sys
import copy
from collections import defaultdict

path_g = "../input/official_data/generation_new_filled.csv"
path_d = "../input/official_data/demand.csv"
path_F = "../input/official_data/crossborder.csv"

path_DEM = "/Users/pg/bachelor_thesis/output/clean_sets/DEM"
path_CAS = "/Users/pg/bachelor_thesis/output/clean_sets/CAS"
path_ADD = "/Users/pg/bachelor_thesis/output/clean_sets/ADD"
path_FAC = "/Users/pg/bachelor_thesis/output/clean_sets/FAC"
path_SIGI = "/Users/pg/bachelor_thesis/output/clean_sets/SIGI"
path_SIGE = "/Users/pg/bachelor_thesis/output/clean_sets/SIGE"

paths = {}
paths["DEM"] = path_DEM
paths["CAS"] = path_CAS
paths["ADD"] = path_ADD
paths["FAC"] = path_FAC
paths["SIGI"] = path_SIGI
paths["SIGE"] = path_SIGE

yearly = {}

for method, path in paths.items():
    temp = aux.load_all_csv_files(path)
    yearly[method] = aux.make_yearly(temp)

set0, set1, set2, set3, set4, set5 = yearly.values()
plot.plot_yearly_production_multiple(set0, set1, set2, set3, set4, set5)

# Get all production types
#g_d, F = aux.load_data(path_g, path_d, path_F)
#all_p = cm.additive_approach(g_d, F)
ren = ["biomass", "hydro", "other_renewable", "solar", "wind_offshore", "wind_onshore"]
fos = ["gas", "hard_coal", "lignite", "nuclear", "oil", "other_fossil", "waste"]
met = yearly.keys()
con = yearly["DEM"].keys()

# Save renewable share per method and country
ren_share  = {}
for method, v in yearly.items():
    ren_share[method] = {}
    for country, v_1 in v.items():
        for p, v_2 in v_1["x_y"].items():
            temp_ren = {p : v_2 for p, v_2 in v_1["x_y"].items() if p in ren}
            temp_fos = {p : v_2 for p, v_2 in v_1["x_y"].items() if p in fos}
            sum_ren = sum(temp_ren.values())
            sum_fos = sum(temp_fos.values())
            ren_share[method][country] = sum_ren / (sum_ren + sum_fos)
            
ren_share_order = {n:[ren_share[i][n] for i in met] for n in con}

# Where is the biggest delta?
# What is smalles delta?
# What is average delta?
delta = {}
for country, v in ren_share_order.items():
    delta[country] = max(v) - min(v)
    
# Sort from smallest to biggest delta
delta_order = {k: v for k, v in sorted(delta.items(), key=lambda item: item[1])}
average = sum(delta.values()) / len(delta)
     



