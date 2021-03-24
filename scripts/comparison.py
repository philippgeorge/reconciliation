# Comparison module
import auxiliary_functions as aux
import correction_methods as cm
import sys
import pandas as pd
import numpy as np
from time import time

def comparison_old():
    # Correction methods to be compared
    stack = [cm.external.sigma_approach, internal_sigma_approach]
    
    # Load the raw data
    #g_d, F = aux.load_data()
    
    # Apply correction method(s) to obtain cleaned data
    cleaned_data = {}
    #for correction_method in stack:
     #   print("Calculating", correction_method.__name__)
      #  cleaned_data[correction_method.__name__] = correction_method()
        
    # Attacking vector
    # Takes as input a country balance sheet and outputs the corrupted country balance
    # that should be corrected by the correction methods
    # Parameters, how likely to attack a value of the data frame: 
    # lower: how much minimal damage
    # upper: how much maximal damage
    balance = pd.read_csv("/Users/pg/bachelor_thesis/output/debugging/complete_energy_balance/HU.csv")
    # Drop redundant index column, drop mismatch columns
    balance = balance[[x for x in balance.columns.values if "Unnamed" not in x and "mismatch" not in x]]
    
def attacking_vector(g_d, F, gamma=0.33, lower=0.0, upper=1.0):
    start = time()
    for country, df in g_d.items():
        df.to_csv("../output/attacking_vector/complete_set/g_d/" + country + ".csv")
        for x in df.columns.values:
            for i in range(df.shape[0]):
                random = np.random.rand()
                if random < gamma:
                    # Magnitude of attack
                    mag = np.random.uniform(1 - upper, 1 - lower)
                    df[x].iloc[i] = df[x].iloc[i] * mag
        df.to_csv("../output/attacking_vector/attacked_set/g_d/" + country + ".csv")
    F.to_csv("../output/attacking_vector/complete_set/" + "F" + ".csv")
    for x in F.columns:
        for i in range(F.shape[0]):
            random = np.random.rand()
            if random < gamma:
                # Magnitude of attack
                mag = np.random.uniform(1 - upper, 1 - lower)
                F[x].iloc[i] = F[x].iloc[i] * mag
    F.to_csv("../output/attacking_vector/attacked_set/" + "F" + ".csv")
    # Print runtime
    end = time()
    print("Runtime:", end - start)  
    return g_d, F
    
    
    
def affected_values(g_d, F, g_d_clean, F_clean):
    report = {}
    number = []
    #for country, df in g_d.items():
       # for x in df.columns:
            #df[x] = np.where(g_d[country] != g_d_clean[country], 1, 0)
        #report[country] = df
    for country, _ in g_d.items():
        df = g_d[country] != g_d_clean[country]
        report[country] = df
        number.append(df.sum())
    #report["F"] = F != F_clean

    return report, number