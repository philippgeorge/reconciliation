# Testing module
from correction_methods import factorial_approach, external_sigma_approach
import time
import sys
import numpy as np
import pandas as pd

def testing_old():
    g_d_cleaned, F_cleaned, alpha_gamma, beta = internal_sigma_approach()
    
    # Add links to the country sheets to make the electricity balance complete
    
    country_report = {}
    # for every country and for every time step check whether the balance condition holds
    for country, df in g_d_cleaned.items():
        df = pd.concat([df, F_cleaned[[x for x in F_cleaned.columns.values if country in x]]], axis=1)
        df["total_generation"] = df[[x for x in df.columns.values if "corrected" in x and "demand" not in x]].sum(axis=1)
        df["total_import"] = df[[x for x in df.columns.values if country in x[-2:]]].sum(axis=1)
        df["total_export"] = df[[x for x in df.columns.values if country in x[:2]]].sum(axis=1)
        # Check whether the difference between generation + import and demand + export
        # is smaller than epsilon
        epsilon = 0.000001
        df["difference"] = df["total_generation"] + df["total_import"] - (df["demand_corrected"] + df["total_export"])
        
        number_of_errors = 0
        row_iterator = df.iterrows()
        for i, row in row_iterator:
            # Verbose
            if row["difference"] < epsilon:
                continue
                #print("Energy balance holds for " + country + " at time step " + str(i))
            else:
                number_of_errors += 1
        if number_of_errors == 0:
            country_report[country] = "For " + country + " the balancing condition was fulfilled at every time step"
        else:
            country_report[country] = "For " + country + " the balancing condition was NOT fulfilled at every time step\
                                      \nIn total there where "  + str(number_of_errors) + " violations."
    
    for country, message in country_report.items():
        print(message)
            
        #if country == "DK":
            #df.to_csv("../output/debugging/factorial_approach/" + country + ".csv")
            
def verify_balancing_condition(country_balances, epsilon=0.01):
    report = {}
    for country, df in country_balances.items():
        df["total_generation"] = df[[x for x in df.columns.values if "demand" not in x and "->" not in x]].sum(axis=1)
        df["total_import"] = df[[x for x in df.columns.values if country in x[-2:]]].sum(axis=1)
        df["total_export"] = df[[x for x in df.columns.values if country in x[:2]]].sum(axis=1)
        df["difference"] = df["total_generation"] + df["total_import"] - (df["demand"] + df["total_export"])
        number_of_errors = 0
        row_iterator = df.iterrows()
        for i, row in row_iterator:
            # Verbose
            if row["difference"] < epsilon:
                continue
                #print("Energy balance holds for " + country + " at time step " + str(i))
            else:
                number_of_errors += 1
        if number_of_errors == 0:
            report[country] = "For " + country + " the balancing condition was fulfilled at every time step"
        else:
            report[country] = "For " + country + " the balancing condition was NOT fulfilled at every time step\
                                      \nIn total there where "  + str(number_of_errors) + " violations."

    return report
    
