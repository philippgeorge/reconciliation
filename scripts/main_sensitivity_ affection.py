# Leading Question:
# How many of the ~6 Mio data points are affected by the correction methods?

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
import matplotlib.pyplot as plt

path_g = "../input/official_data/generation_new_filled.csv"
path_d = "../input/official_data/demand.csv"
path_F = "../input/official_data/crossborder.csv"
path_t = "../input/official_data/gen_targets.csv"

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


# Load original data set
g_d, F = aux.load_data(path_g, path_d, path_F)
# Bring original data to country balances form
country_balances = aux.make_country_balances(g_d, F)
# Load reconciled data sets
clean_set = {}
for method, path in paths.items():
    clean_set[method] = aux.load_all_csv_files(path)

report = {}
number = {}
for method, v in clean_set.items():
    number[method] = {}
    for country, df in g_d.items():
        # Drop 'mismatch' from table scheme
        country_balances[country] = country_balances[country][[x for x in country_balances[country].columns if "->"  in x]]
        clean_set[method][country] = clean_set[method][country][[x for x in clean_set[method][country].columns if "->"  in x]]

        a = country_balances[country].columns.values
        #clean_set["SIGI"][country] = clean_set["SIGI"][country][[x for x in clean_set["SIGI"][country].columns if "mismatch" not in x]]
        b = clean_set[method][country].columns.values
        
        bool_df = abs(country_balances[country] - clean_set[method][country]) > 1
        report[country] = bool_df
        number[method][country] = bool_df.sum()

        # Number of values per country
        total_number = 8760 * len(country_balances[country].columns)
        if total_number == 0:
            continue
        affection =  2*(sum(number[method][country]) / total_number)
        print(method, country)
        print(affection)
        print()
        #number.append(df.sum())




