# Leading Question:
# What is the relative mismatch per country?
# Are there more time steps where generation side is bigger thand demand side?
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
path_F_unfiltered = "/Users/pg/entso-e_cross-border_data/output/cross_border_flow/cross_border_flow_data_hourly.csv"
path_g_d_com = "../output/attacking_vector/complete_set/g_d/"
path_g_d_att = "../output/attacking_vector/attacked_set/g_d/"
path_F_com = "../output/attacking_vector/complete_set/F.csv"
path_F_att =  "../output/attacking_vector/attacked_set/F.csv"


# By how much the quality filtering reduces the amount of links?


# Load data
g_d, _ = aux.load_data(path_g, path_d, path_F, subset=False)

# Load F
F = pd.read_csv(path_F)

# Load unfiltered F
F_unfiltered = pd.read_csv(path_F_unfiltered)
print("Success")
sys.exit()

# Calculate and visualize the average relative mismatch
rel = plot.plot_rel_mismatch(g_d, F)

# Complete data frames include slack variables that can be used as indicator
# number of zeros of s_r indicates that generation side is smaller
g_d_com = aux.load_all_csv_files(path_g_d_com)
F_com = pd.read_csv(path_F_com, index_col=0)

zeros_s_r = {}
zeros_s_l = {}
amount_s_r = {}
amount_s_l = {}
# Get number how many times left side is bigger than right side
# Get the size of the error
for country, df in g_d_com.items():
   zeros_s_r[country] = max(df[df["s_r"] == 0].count())
   zeros_s_l[country] = max(df[df["s_l"] == 0].count())
   amount_s_r[country] = df["s_r"].sum(axis=0)
   amount_s_l[country] = df["s_l"].sum(axis=0)
   
average_s_r = {}
average_s_l = {}   
count = 0
count_1 = 0
# Calculate average size of error
for country in amount_s_r.keys():
    average_s_r[country] = amount_s_r[country] / (8760 - zeros_s_r[country])
    average_s_l[country] = amount_s_l[country] / (8760 - zeros_s_l[country])
    if average_s_r[country] < average_s_l[country]:
        #print(country, "average s_r is smalle than average s_l")
        count += 1
    if amount_s_r[country] < amount_s_l[country]:
        print(country, "in total the we had to correct the left side more")
        count_1 += 1
    

a = sum(zeros_s_l.values())
b = len(zeros_s_l)
c = a / b
d = c / 8760

