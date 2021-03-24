# Leading Questions:
# How much does the share of exports on generation vary?
# How much does the share of import on demand vary?

import pandas as pd
import numpy as np
import auxiliary_functions as aux
import plotting as p
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

# Get import export columns
g_d, F = aux.load_data(path_g, path_d, path_F)
# INDEX WORK 
n_index = np.asarray(list(g_d.keys()))
# Index for time steps
t_index = list(g_d.values())[0].index.values
# Production type indices
p_index = {}
for country, df in g_d.items():  
    p_index[country] = [x for x in df.columns.values if "demand" not in x if "total" not in x]
    # Index for all production types
p_global = np.array(list(set( [item for sublist in p_index.values() for item in sublist])))
p_global.sort()

# Prepare the country-dependent indices
# Direction import
i_index = {}
for country in g_d.keys():
    i_index[country] = [x for x in F.columns.values if country in x[-2:]]
# Direction export
e_index = {}
for country in g_d.keys():
    e_index[country] = [x for x in F.columns.values if country in x[:2]]
# Index for all links
f_index = np.array(F.columns.values)
f_index.sort()


met = yearly.keys()
con = yearly["DEM"].keys()

ren = ["biomass", "hydro", "other_renewable", "solar", "wind_offshore", "wind_onshore"]
fos = ["gas", "hard_coal", "lignite", "nuclear", "oil", "other_fossil", "waste"]
gen = ren + fos
# Save renewable share per method and country
imp_share  = {}
for method, v in yearly.items():
    imp_share[method] = {}
    for country, v_1 in v.items():
        for p, v_2 in v_1["x_y"].items():
            temp_imp = {p : v_2 for p, v_2 in v_1["x_y"].items() if p in i_index[country]}
            temp_gen = {p : v_2 for p, v_2 in v_1["x_y"].items() if "demand" in p}
            sum_imp = sum(temp_imp.values())
            sum_gen = sum(temp_gen.values())
            imp_share[method][country] = sum_imp / (sum_imp + sum_gen)
         
imp_share_order = {n:[imp_share[i][n] for i in met] for n in con}

# Where is the biggest delta_imp?
# What is smalles delta_imp?
# What is average delta?
delta_imp = {}
for country, v in imp_share_order.items():
    delta_imp[country] = max(v) - min(v)
    
# Sort from smallest to biggest delta_imp
delta_imp_order = {k: v for k, v in sorted(delta_imp.items(), key=lambda item: item[1])}
delta_imp_average = sum(delta_imp.values()) / len(delta_imp)


exp_share  = {}
for method, v in yearly.items():
    exp_share[method] = {}
    for country, v_1 in v.items():
        for p, v_2 in v_1["x_y"].items():
            temp_exp = {p : v_2 for p, v_2 in v_1["x_y"].items() if p in e_index[country]}
            temp_gen = {p : v_2 for p, v_2 in v_1["x_y"].items() if p in gen}
            sum_exp = sum(temp_exp.values())
            sum_gen = sum(temp_gen.values())
            exp_share[method][country] = sum_exp / (sum_exp + sum_gen)
         
exp_share_order = {n:[exp_share[i][n] for i in met] for n in con}

# Where is the biggest delta_exp?
# What is smalles delta_exp?
# What is average delta?
delta_exp = {}
for country, v in exp_share_order.items():
    delta_exp[country] = max(v) - min(v)
    
# Sort from smallest to biggest delta_exp
delta_exp_order = {k: v for k, v in sorted(delta_exp.items(), key=lambda item: item[1])}
delta_exp_average = sum(delta_exp.values()) / len(delta_exp)
     



