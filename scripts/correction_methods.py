# This file contains 6 correction methods for data reconciliation
import pandas as pd
import numpy as np
import auxiliary_functions as aux
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import os
from time import time
import sys
import copy


# Demand scaling approach (DEM)
def demand_scaling(g_d, F):
    # Measure the runtime
    start = time()
    # Intialize dictionaries holding the varibales used for reconciliation
    a_var = {}
    a_var["g_d"] = {}
    f_var = {}
    f_var["g_d"] = {}
    # Apply case method
    for country, df in g_d.items():        
        g_d_columns = df.columns.values
        g_columns = [x for x in df.columns.values if "demand" not in x]
        i_columns = [x for x in F.columns.values if country in x[-2:]]
        e_columns = [x for x in F.columns.values if country in x[:2]]
        df = pd.concat([df[g_columns], F[i_columns], df["demand"], F[e_columns]], axis=1)
        # Calculate the mismatch per timestep
        df["mismatch"] = df[g_columns].sum(axis=1) + df[i_columns].sum(axis=1)\
                                - (df["demand"] + df[e_columns].sum(axis=1))
        # Apply demand scaling
        df["delta_d"] = df["mismatch"]
        df["gamma"] = (df["delta_d"] + df["demand"]) / df["demand"]
        # Create the variables used for reconciliation
        a_var["g_d"][country] = pd.DataFrame\
                                (0, index=np.arange(df.shape[0]), columns=g_d_columns)
        f_var["g_d"][country] = pd.DataFrame\
                                (1, index=np.arange(df.shape[0]), columns=g_d_columns)
        f_var["g_d"][country]["demand"] = df["gamma"]
        #f_var["g_d"][country].to_csv("../output/debugging/factorial_approach/" + "demand_scaling_" + country + ".csv")
    a_var["F"] = pd.DataFrame(0, index=np.arange(F.shape[0]), columns=F.columns)
    f_var["F"] = pd.DataFrame(1, index=np.arange(F.shape[0]), columns=F.columns)
    # Print runtime
    end = time()
    print("Runtime:", end - start)    
    return a_var, f_var
    

# Case approach (CAS)
def case_approach(g_d, F):
    # Measure the runtime
    start = time()
    # Filter F
    valid_links = [x for x in F.columns.values if x[:2] in g_d.keys() and x[-2:] in g_d.keys()]
    F = F[valid_links]
    # Intialize dictionaries holding the varibales used for reconciliation
    a_var = {}
    a_var["g_d"] = {}
    f_var = {}
    f_var["g_d"] = {}
    # Apply case method
    for country, df in g_d.items():
        g_d_columns = df.columns.values
        g_columns = [x for x in df.columns.values if "demand" not in x]
        i_columns = [x for x in F.columns.values if country in x[-2:]]
        e_columns = [x for x in F.columns.values if country in x[:2]]
        df = pd.concat([df[g_columns], F[i_columns], df["demand"], F[e_columns]], axis=1)
        # Calculate the mismatch per timestep
        df["mismatch"] = df[g_columns].sum(axis=1) + df[i_columns].sum(axis=1)\
                                - (df["demand"] + df[e_columns].sum(axis=1))
        # Apply the case rule
        # Case 1 generation and imports are smaller than demand and exports
        df["delta_g"] = df["mismatch"].apply(lambda x: -x  if x < 0 else 0)
        df["total_generation"] = df[g_columns].sum(axis=1)
        df["alpha"] = (df["delta_g"] + df["total_generation"]) / df["total_generation"]
        # Case 2 generation and imports are greater than demand and exports
        df["delta_d"] = df["mismatch"].apply(lambda x: x  if x > 0 else 0) 
        df["gamma"] = (df["delta_d"] + df["demand"]) / df["demand"]
        # Create the variables used for reconciliation
        a_var["g_d"][country] = pd.DataFrame\
                                (0, index=np.arange(df.shape[0]), columns=g_d_columns)
        f_var["g_d"][country] = pd.DataFrame\
                                (1, index=np.arange(df.shape[0]), columns=g_d_columns)
        for p in g_columns:
            f_var["g_d"][country][p] = df["alpha"]
        f_var["g_d"][country]["demand"] = df["gamma"]
    a_var["F"] = pd.DataFrame(0, index=np.arange(F.shape[0]), columns=F.columns)
    f_var["F"] = pd.DataFrame(1, index=np.arange(F.shape[0]), columns=F.columns)
    # Print runtime
    end = time()
    print("Runtime:", end - start)
    return a_var, f_var
      

# Additive approach (ADD)
def additive_approach(g_d, F):
    # Measure the runtime
    start = time()    
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
    # PYOMO WORK
    model = pyo.ConcreteModel()
    # Index declartions
    model.n_index = pyo.Set(initialize=n_index)
    model.t_index = pyo.Set(initialize=t_index)
    model.p_global = pyo.Set(initialize=p_global)
    model.f_index = pyo.Set(initialize=f_index)
    # Variable declarations
    model.delta_g = pyo.Var(model.n_index, model.t_index, model.p_global, bounds=(0.0, None))
    model.delta_d = pyo.Var(model.n_index, model.t_index, bounds=(0.0, None))
    model.delta_F = pyo.Var(model.t_index, model.f_index, bounds=(0.0, None))
    def balance_rule(model, n, t):
            return  sum(model.delta_g[n, t, p] + g_d[n][p][t] for p in p_index[n]) + sum(model.delta_F[t, l] + F[l][t] for l in i_index[n]) ==  \
                        model.delta_d[n, t] + g_d[n]["demand"][t]                  + sum(model.delta_F[t, l] + F[l][t] for l in e_index[n])
    model.balance_rule = pyo.Constraint(model.n_index, model.t_index, rule=balance_rule)
    def ObjRule(model):
        return sum(model.delta_g[n, t, p] ** 2 for n in model.n_index for t in model.t_index for p in p_index[n]) \
             + sum(model.delta_F[t, l] ** 2 for t in model.t_index for l in model.f_index)\
             + sum(model.delta_d[n, t] ** 2 for n in model.n_index for t in model.t_index)
    model.obj = pyo.Objective(rule=ObjRule, sense=pyo.minimize)
    opt = SolverFactory("gurobi", solver_io="python")
    # Solve the model
    opt.solve(model)
    # Save the results in csv-files
    # Convert the pyomo variables to pandas data frames
    a_var = {}
    a_var["g_d"] = {}
    f_var = {}
    f_var["g_d"] = {}
    for n in n_index:
        table = []
        for t in t_index:
            row = []
            for p in p_index[n]:
                row.append(model.delta_g[n, t, p].value)
            # Append delta_d value to "row"
            row.append(model.delta_d[n, t].value)
            table.append(row)
        p_index[n].append("demand")
        a_var["g_d"][n] = pd.DataFrame.from_records(table)
        f_var["g_d"][n] = pd.DataFrame\
                                (1, index=np.arange(df.shape[0]), columns=g_d[n].columns)
        a_var["g_d"][n].columns = p_index[n]
        #a_var["g_d"][n].to_csv("../output/debugging/factorial_approach/" + "a_var_" + n + ".csv")
    #delta_F    
    table = []
    for t in t_index:
        row = []
        for l in f_index:
            row.append(model.delta_F[t, l].value)
        table.append(row)
    a_var["F"] = pd.DataFrame.from_records(table)
    a_var["F"].columns = f_index
    #a_var["F"].to_csv("../output/debugging/factorial_approach/a_var_F.csv")
    f_var["F"] = pd.DataFrame(1, index=np.arange(F.shape[0]), columns=F.columns)
    end = time()
    print("Runtime:", end - start)
    return a_var, f_var


# Factorial approach (FAC)
def factorial_approach(g_d, F):
    # Measure the runtime
    start = time()    
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
    # PYOMO WORK
    model = pyo.ConcreteModel()
    # Index declartions
    model.n_index = pyo.Set(initialize=n_index)
    model.t_index = pyo.Set(initialize=t_index)
    model.p_global = pyo.Set(initialize=p_global)
    model.f_index = pyo.Set(initialize=f_index)
    # Variable declarations
    model.alpha = pyo.Var(model.n_index, model.t_index, model.p_global, bounds=(1.0, None))
    model.gamma = pyo.Var(model.n_index, model.t_index, bounds=(1.0, None))
    model.beta = pyo.Var(model.t_index, model.f_index, bounds=(1.0, None))
    def balance_rule(model, n, t):
            return  sum(model.alpha[n, t, p] * g_d[n][p][t] for p in p_index[n]) + sum(model.beta[t, l] * F[l][t] for l in i_index[n]) ==  \
                        model.gamma[n, t] * g_d[n]["demand"][t]                  + sum(model.beta[t, l] * F[l][t] for l in e_index[n])
    model.balance_rule = pyo.Constraint(model.n_index, model.t_index, rule=balance_rule)
    def ObjRule(model):
        return sum(model.alpha[n, t, p] ** 2 for n in model.n_index for t in model.t_index for p in p_index[n]) \
             + sum(model.beta[t, l] ** 2 for t in model.t_index for l in model.f_index)\
             + sum(model.gamma[n, t] ** 2 for n in model.n_index for t in model.t_index)
    model.obj = pyo.Objective(rule=ObjRule, sense=pyo.minimize)
    opt = SolverFactory("gurobi", solver_io="python")
    # Solve the model
    opt.solve(model)
    # Convert the pyomo variables to pandas data frames
    # alpha, gamma
    a_var = {}
    a_var["g_d"] = {}
    f_var = {}
    f_var["g_d"] = {}
    for n in n_index:
        table = []
        for t in t_index:
            row = []
            for p in p_index[n]:
                row.append(model.alpha[n, t, p].value)
            # Append gamma value to "row"
            row.append(model.gamma[n, t].value)
            table.append(row)
        f_var["g_d"][n] = pd.DataFrame.from_records(table)
        p_index[n].append("demand")
        f_var["g_d"][n].columns = p_index[n]
        a_var["g_d"][n] = pd.DataFrame\
                                (0, index=np.arange(df.shape[0]), columns=g_d[n].columns)
        if not os.path.exists("../output/debugging/factorial_approach/"):
            os.makedirs("../output/debugging/factorial_approach/")
        f_var["g_d"][n].to_csv("../output/debugging/factorial_approach/" + n + ".csv")
    #beta    
    table = []
    for t in t_index:
        row = []
        for l in f_index:
            row.append(model.beta[t, l].value)
        table.append(row)
    f_var["F"] = pd.DataFrame.from_records(table)
    f_var["F"].columns = f_index
    f_var["F"].to_csv("../output/debugging/factorial_approach/beta.csv")
    a_var["F"] = pd.DataFrame(0, index=np.arange(F.shape[0]), columns=F.columns)
    end = time()
    print("Runtime:", end - start)
    return a_var, f_var

        
# Internal sigma approach (SIGI)
# Credits go to Chalendar
def internal_sigma_approach(g_d, F, A=100, eta=0.1):
    # Measure the runtime
    start = time()
    # Load sigma, the confidence coefficient for generation, demand and links
    #sigma = aux.calculate_sigma(g_d, F, aux.g_2018_entsoe, aux.d_2018_entsoe, aux.g_by_source, aux.F_default, aux.F_specific)
    #F.to_csv("../output/debugging/factorial_approach/F.csv")
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
    # 10 day rolling average of demand
    #s = g_d["DK"]["demand"]
    #g_d["DK"]["R_demand"] = pd.DataFrame(s).apply(lambda x: 5 if x.name == 'a' else x.name ,1)
    #g_d["DK"]["R_demand"] = pd.DataFrame(s).apply(rolling_average, 1)
    # Calculate 10-day rolling average for every segment
    g_d_1 = copy.deepcopy(g_d)
    F_1 = copy.deepcopy(F)
    sigma = aux.calculate_internal_sigma(g_d_1, F_1, A, eta)
    # PYOMO WORK
    model = pyo.ConcreteModel()
    # Index declartions
    model.n_index = pyo.Set(initialize=n_index)
    model.t_index = pyo.Set(initialize=t_index)
    model.p_global = pyo.Set(initialize=p_global)
    model.f_index = pyo.Set(initialize=f_index)
    # Variable declarations
    model.delta_g = pyo.Var(model.n_index, model.t_index, model.p_global, bounds=(0.0, None))
    model.delta_d = pyo.Var(model.n_index, model.t_index, bounds=(0.0, None))
    model.delta_F = pyo.Var(model.t_index, model.f_index, bounds=(0.0, None))
    def balance_rule(model, n, t):
            return  sum(model.delta_g[n, t, p] + g_d[n][p][t] for p in p_index[n]) + sum(model.delta_F[t, l] + F[l][t] for l in i_index[n]) ==  \
                        model.delta_d[n, t] + g_d[n]["demand"][t]                  + sum(model.delta_F[t, l] + F[l][t] for l in e_index[n])
    model.balance_rule = pyo.Constraint(model.n_index, model.t_index, rule=balance_rule)
    def ObjRule(model):
        return sum(model.delta_g[n, t, p] ** 2 * float(sigma[n][p].iloc[t]) for n in model.n_index for t in model.t_index for p in p_index[n]) \
             + sum(model.delta_F[t, l] ** 2 * float(sigma["F"][l].iloc[t]) for t in model.t_index for l in model.f_index)\
             + sum(model.delta_d[n, t] ** 2 * float(sigma[n]["demand"].iloc[t]) for n in model.n_index for t in model.t_index)
    model.obj = pyo.Objective(rule=ObjRule, sense=pyo.minimize)
    opt = SolverFactory("gurobi", solver_io="python")
    # Solve the model
    opt.solve(model)
    # Convert the variables into data frames
    a_var = {}
    a_var["g_d"] = {}
    f_var = {}
    f_var["g_d"] = {}
    for n in n_index:
        table = []
        for t in t_index:
            row = []
            for p in p_index[n]:
                row.append(model.delta_g[n, t, p].value)
            # Append delta_d value to "row"
            row.append(model.delta_d[n, t].value)
            table.append(row)
        a_var["g_d"][n] = pd.DataFrame.from_records(table)
        p_index[n].append("demand")
        a_var["g_d"][n].columns = p_index[n]
        f_var["g_d"][n] = pd.DataFrame\
                                (1, index=np.arange(df.shape[0]), columns=g_d[n].columns)
       # if not os.path.exists("../output/debugging/factorial_approach/"):
        #    os.makedirs("../output/debugging/factorial_approach/")
        #f_var["g_d"][n].to_csv("../output/debugging/factorial_approach/" + "internal_sigma_f_var" + n + ".csv")
    #delta_F    
    table = []
    for t in t_index:
        row = []
        for l in f_index:
            row.append(model.delta_F[t, l].value)
        table.append(row)
    a_var["F"] = pd.DataFrame.from_records(table)
    a_var["F"].columns = f_index
    #a_var["F"].to_csv("../output/debugging/factorial_approach/internal_sigma_f_var_F.csv")
    f_var["F"] = pd.DataFrame(1, index=np.arange(F.shape[0]), columns=F.columns)
    end = time()
    print("Runtime:", end - start)
    return a_var, f_var


# External sigma approach        
def external_sigma_approach(g_d, F):
    # Measure the runtime
    start = time()
    # Load sigma, the confidence coefficient for generation, demand and links
    sigma = aux.calculate_sigma(g_d, F, aux.g_2018_entsoe, aux.d_2018_entsoe, aux.g_by_source, aux.F_default, aux.F_specific)
    #F.to_csv("../output/debugging/factorial_approach/F.csv")
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
    # PYOMO WORK
    model = pyo.ConcreteModel()
    # Index declartions
    model.n_index = pyo.Set(initialize=n_index)
    model.t_index = pyo.Set(initialize=t_index)
    model.p_global = pyo.Set(initialize=p_global)
    model.f_index = pyo.Set(initialize=f_index) 
    # Variable declarations
    model.alpha = pyo.Var(model.n_index, model.t_index, model.p_global, bounds=(1.0, None))
    model.gamma = pyo.Var(model.n_index, model.t_index, bounds=(1.0, None))
    model.beta = pyo.Var(model.t_index, model.f_index, bounds=(1.0, None))
    
    def balance_rule(model, n, t):
            return  sum(model.alpha[n, t, p] * g_d[n][p][t] for p in p_index[n]) + sum(model.beta[t, l] * F[l][t] for l in i_index[n]) ==  \
                        model.gamma[n, t] * g_d[n]["demand"][t]                  + sum(model.beta[t, l] * F[l][t] for l in e_index[n])
    model.balance_rule = pyo.Constraint(model.n_index, model.t_index, rule=balance_rule)
    def ObjRule(model):
        return sum((model.alpha[n, t, p] * sigma["g"][n][p]) ** 2 for n in model.n_index for t in model.t_index for p in p_index[n]) \
             + sum((model.beta[t, l] * sigma["F"][l]) ** 2 for t in model.t_index for l in model.f_index)\
             + sum((model.gamma[n, t] * sigma["d"][n]) ** 2 for n in model.n_index for t in model.t_index)
    model.obj = pyo.Objective(rule=ObjRule, sense=pyo.minimize)
    opt = SolverFactory("gurobi", solver_io="python")
    # Solve the model
    opt.solve(model) 
    # Convert the variables into data frames
    a_var = {}
    a_var["g_d"] = {}
    f_var = {}
    f_var["g_d"] = {}
    for n in n_index:
        table = []
        for t in t_index:
            row = []
            for p in p_index[n]:
                row.append(model.alpha[n, t, p].value)
            # Append gamma value to "row"
            row.append(model.gamma[n, t].value)
            table.append(row)
        f_var["g_d"][n] = pd.DataFrame.from_records(table)
        p_index[n].append("demand")
        f_var["g_d"][n].columns = p_index[n]
        a_var["g_d"][n] = pd.DataFrame\
                                (0, index=np.arange(df.shape[0]), columns=g_d[n].columns)
        if not os.path.exists("../output/debugging/factorial_approach/"):
            os.makedirs("../output/debugging/factorial_approach/")
        f_var["g_d"][n].to_csv("../output/debugging/factorial_approach/" + "external_sigma_f_var" + n + ".csv")
    #beta    
    table = []
    for t in t_index:
        row = []
        for l in f_index:
            row.append(model.beta[t, l].value)
        table.append(row)
    f_var["F"] = pd.DataFrame.from_records(table)
    f_var["F"].columns = f_index
    f_var["F"].to_csv("../output/debugging/factorial_approach/external_sigma_f_var_F.csv")
    a_var["F"] = pd.DataFrame(0, index=np.arange(F.shape[0]), columns=F.columns)
    end = time()
    print("Runtime:", end - start)
    return a_var, f_var
