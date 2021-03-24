import pandas as pd
import numpy as np
import auxiliary_functions as aux
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import os
from time import time
import sys
import matplotlib.pyplot as plt

# Compare aggregated clean vs. raw data given a country and a correction method
def plot_raw_cleaned_aggregated(correction_method, country):
    raw_data = aux.load_data(subset=False, country_balance=True)
    cleaned_data = {}
    g_d_cleaned, F_cleaned, alpha_gamma, beta = correction_method()
    # Bring g_d_cleaned and F_cleaned into country balance format
    for c, df in g_d_cleaned.items():
        print(c)
        generation_col = [col for col in df.columns if "demand" not in col]
        # Get column values for demand
        demand_col = [col for col in df.columns if "demand" in col]
        # Get column values for crossborder
        flow_col = [col for col in F_cleaned.columns if c in col]
        temp_g = df[generation_col]
        # Cut the suffix "_corrected"
        temp_g.columns = [x[:-10] for x in temp_g.columns]
        #temp_g.columns = [x[3:] for x in temp_g.columns.values]
        temp_d = df[demand_col]
        temp_d.columns = ["demand"]
        #temp_d.columns = [x[3:] for x in temp_d.columns.values]
        temp_f = F_cleaned[flow_col]
        cleaned_data[c] = pd.concat([temp_g, temp_d, temp_f], ignore_index=False, axis=1)
        if c == country:
            aggregated = {}
            # Debugging
            cols = cleaned_data[c].columns.values
            raw_data[c] = raw_data[c][cols]
            cleaned_data[c].to_csv("../output/debugging/factorial_approach/" + "cleaned_country_balance" + ".csv")
            raw_data[c].to_csv("../output/debugging/factorial_approach/" + "raw_country_balance" + ".csv")
            for x in raw_data[c]:
                aggregated[x] = (raw_data[c][x].sum(axis=0), cleaned_data[c][x].sum(axis=0))
            x = aggregated.keys()
            y1 = [p[0] for p in aggregated.values()]
            y2 = [p[1] for p in aggregated.values()]
            _x = np.arange(len(x))
            fig = plt.figure()
            ax = fig.add_axes([0,0,1,1])
            ax.bar(_x + 0.00, y1, color = "b", width = 0.25)
            ax.bar(_x + 0.25, y2, color = "g", width = 0.25)
            plt.xticks(_x, x)

    return aggregated

# Plot relative mismatch
def plot_rel_mismatch(g_d, F):
    rel_error = {}
    abs_error = {}
    sum_generation = {}
    sum_load = {}
    sum_import = {}
    sum_export = {}
    rel_extra_generation = {}
    rel_extra_load = {}
    average_mismatch_in_percent = {}
    total = {}
    
    print("Plotting energy balance per country. Positive values in import/export indicate imports")
    # For every country add a column "Error" = Generation + Import - Load - Export
    for country, df in g_d.items():  
        all_cols = g_d[country].columns.values
        # Get generation columns
        g_cols = [col for col in all_cols if "demand" not in col]
        l_cols = [col for col in all_cols if "demand" in col]
        i_cols = [x for x in F.columns.values if country in x[-2:]]  
        e_cols = [x for x in F.columns.values if country in x[:2]]  
        df = df[g_cols].join(  F[i_cols]).join(  df[l_cols]).join(F[e_cols])
        df["mismatch"] = df[g_cols].sum(axis=1) + df[i_cols].sum(axis=1) - df["demand"] - df[e_cols].sum(axis=1)
        df["mismatch_in_percent"] = abs(df["mismatch"] / (df["demand"] + df[e_cols].sum(axis=1)))
        df.to_csv("../output/debugging/complete_energy_balance/" + country + ".csv")
        average_mismatch_in_percent[country] = df["mismatch_in_percent"].sum(axis=0) / 8760
        df["mismatch_absolute"] = df["mismatch"].abs()
        total[country] = df["mismatch_absolute"].sum(axis=0) / 1000000
    
    # Plot relative mismatch
    temp = dict(sorted(average_mismatch_in_percent.items(), key=lambda item: item[1], reverse=True))
    fig = plt.figure()
    x = [k for k, v in temp.items()]
    #x = x[10:-2]
    y = [v for k, v in temp.items()]
    #y = y[10:-2]
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_title("Average relative mismatch")
    ax.bar(x, y)

# Plot yearly production values by different methods
def plot_yearly_production_multiple(set0, set1, set2, set3, set4, set5):
    for country, value in set0.items():
        x = set0[country]["x"]
        _x = np.arange(len(x))
        y_0 = set0[country]["y"]
        y_1 = set1[country]["y"]
        y_2 = set2[country]["y"]
        y_3 = set3[country]["y"]
        y_4 = set4[country]["y"]
        y_5 = set5[country]["y"]
        # Filter for generation only
        def condition(x): return "->" in x
        output = [idx for idx, element in enumerate(x) if condition(element)]
        if output:
            limit = min(output)
            x = x[:limit]
            _x = _x[:limit]
            y_0 = y_0[:limit]
            y_1 = y_1[:limit]
            y_2 = y_2[:limit]
            y_3 = y_3[:limit]
            y_4 = y_4[:limit]
            y_5 = y_5[:limit]
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_title("Yearly values " + country)
        w = 1.0/(len(x) + 4)
        ax.bar(_x + 0 * w, y_0, color = "b", width=w)
        ax.bar(_x + 1 * w, y_1, color = "g", width=w)
        ax.bar(_x + 2 * w, y_2, color = "r", width=w)
        ax.bar(_x + 3 * w, y_3, color = "c", width=w)
        ax.bar(_x + 4 * w, y_4, color = "m", width=w)
        ax.bar(_x + 5 * w, y_5, color = "y", width=w)
        plt.xticks(_x, x)
        plt.xticks(rotation=70)
        ax.set_ylabel("MW")
    
def horizontal_bar_plot(x, y) :
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    y_pos = np.arange(len(x))
    ax.barh(y_pos, y)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(x)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel("Relative distance")
    ax.set_title("Distance to targets")    
