# Archive
# Functions, data structures not used anymore but in some circumstance helpful

months = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]

index_to_month = {
                    0: "January",
                    1: "February",
                    2: "March",
                    3: "April",
                    4: "May",
                    5: "June",
                    6: "July",
                    7: "August",
                    8: "September",
                    9: "October",
                   10: "November",
                   11: "December"}


""" Monthly segmentation by index
jan = 744
feb = 1416
mar = 2160
apr = 2880
may = 3624
jun = 4344
jul = 5088
aug = 5832
sep = 6552
okt = 7296
nov = 8016
dec = 8760
"""
month_to_index = [0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760]

code_to_name = {
    "AL": "Albania",
    "AT": "Austria",
    "BA": "Bosnia and Herzegovina",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CH": "Switzerland",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "Great Britain",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "ME": "Montenegro",
    "MK": "Macedonia",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RS": "Serbia",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "KV": "Kosovo",
    # Needed for crossborder flows
    "TR": "Turkey",
    "UA": "Ukraine",
    "RU": "Russia",
    "BY": "Belarus",
    "MT": "Malta"
    }

# Prepare crossborder link sheet
def make_link_dict(df, country_list):
    """
    Input:
        df: Dataframe containing all cross-border flow values
        country_list: List containing all countries that are considered
    Output:
        Dictionary of dataframes of same dimensions holding the country
        specific information
    """
    link_dict = {}
    template_df = df.copy()
    for country in country_list:
        # Setting all values to zero that do not belong to country
        all_columns = df.columns.values
        country_columns = [col for col in df.columns.values if  country in col[0:7]]
        rest_columns = [x for x in all_columns if x not in country_columns]
        for col in rest_columns:
            df[col].values[:] = 0
        link_dict[country] = df
        df = template_df.copy()
        link_dict[country].to_csv("../output/debugging/link_dict/" + country + ".csv")
        
    return link_dict    

def make_flow_table(df, country_list_extended):
    """
    Input:
        df: Dataframe containing all cross-border flow values
        country_list: List containing all countries that are considered
    Output:
        Dictionary of data frames with all cross-border flows at a given time 
        step

    """
    flow_table_dict = {}
    df = df.iloc[:, 1:]
    for i in range(len(df)):
        df_ = pd.DataFrame(index=country_list_extended, columns=country_list_extended)
        df_ = df_.fillna(0) 
        row = df.iloc[i]
        for j in row.index.values:
            
            df_[j[:2]][j[-2:]] = row[j]
        flow_table_dict[i] = df_
    return flow_table_dict

def standardize_generation(df):
    """
    Parameters
    ----------
    df : pandas data frame
        Holding generation data from all countries

    Returns
    -------
    stand_g_dict: dictionary with standardized generation per country

    """
    # Dictionary that will be filled and returned
    stand_g_dict = {}
    #Dictionary that  holds gen_dem value for arbitrary countries AA, BB
    gen_dem = {}
    gen_dem["AA"] = [30, 50, 70, 80, 90]
    gen_dem["BB"] = [70, 90, 20, 30, 70]
    gen_dem["CC"] = [80, 70, 60, 65, 60]
    # Get all countries
    countries = df.columns.values
    countries = [x[:2] for x in countries]
    countries = set(countries)
    countries = list(countries)
    countries.sort()
    # Get all production types
    production_types = set(df.iloc[0])
    production_types = list(production_types)
    production_types.sort()
    #print(df["country_A"][0])
    # make column names unique
    def renaming_columns(x):
        extension = df[x][0]
        x = x[:2]
        return x + "_" + extension
    df = df.rename(columns=renaming_columns)
    df = df.iloc[1:]
    df.reset_index(drop=True, inplace=True)
    # Make template data frame with all production types filled with zeros
    template_df = pd.DataFrame(index=range(len(df)), columns=production_types)
    template_df.fillna(0, inplace=True)
    for country in countries:
        country_df = template_df.copy()
        columns = [x for x in df.columns.values if country in x]
        for column in columns:
            country_df[column[3:]] = df[column]
        country_df["demand"] = gen_dem[country]
        country_df = country_df.astype(float)
        stand_g_dict[country] = country_df
    return stand_g_dict

def make_g_d_F(country_balances):
    g_d = {}
    F_columns = set()
    F = pd.DataFrame()
    # F is a dataframe
    for country, df in country_balances.items():
        g_d[country] = df[[x for x in df.columns if "->" not in x]]
        g_d[country].to_csv("../output/debugging/attacking_vector/" + "g_d_" + country + ".csv")
        cross_columns = [x for x in df.columns if "->" in x]
        cross_columns.sort()
        
        for c in cross_columns:
            df[c] = df[c].apply(lambda x: -float(x) if c[:2] > c[-2:] else float(x))
            if c[:2] < c[-2:]:
                df[c[:2] + " - " + c[-2:]] = df[c[:2] + " -> " + c[-2:]] + df[c[-2:] + " -> " + c[:2]]
                if c[:2] + " - " + c[-2:] not in F:
                    F[c[:2] + " - " + c[-2:]] = df[c[:2] + " - " + c[-2:]]
        df = df.drop(columns=[x for x in df.columns if "->" in x])
        #df.to_csv("../output/debugging/attacking_vector/" + country + ".csv")
    F.to_csv("../output/debugging/attacking_vector/" + "F" + ".csv")
        #print(b)
        #print(temp)
        #for c_column in [x for x in df.columns if "->" in x].sort(key=str.lower):
         #   print(c_column)
            #double[c_column] = [x[:2] + " - " + x[-2:], x[-2:] + " - " + x[2:]]
    return g_d, F