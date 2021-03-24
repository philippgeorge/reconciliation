# Auxiliary functions
import pandas as pd
import sys
import numpy as np
import os
import matplotlib.pyplot as plt
import math

# Helper functions
# Generation limits derived from installed capacity per country in MW
# Source: ENTOS-E Statistial Factsheet 2018
generation_limits = {
                        "AL": 1932,
                        "AT": 25413,
                        "BA": 4044,
                        "BE": 22671,
                        "BG": 11454,
                        "CH": 17895,
                        "CY": 1768,
                        "CZ": 20820,
                        "DE": 215046,
                        "DK": 16055,
                        "EE": 2832,
                        "ES": 104094,
                        "FI": 17371,
                        "FR": 132869,
                        "GB": 90207,
                        "GR": 16392,
                        "HR": 4832,
                        "HU": 8474,
                        "IE": 10510,
                        "IS": 2733,
                        "IT": 130935,
                        "LT": 3553,
                        "LU": 1744,
                        "LV": 2829,
                        "ME": 952,
                        "MK": 1894,
                        "NL": 30531,
                        "NO": 35022,
                        "PL": 39878,
                        "PT": 19978,
                        "RO": 19766,
                        "RS": 8766,
                        "SE": 39908,
                        "SI": 3958,
                        "SK": 7728,
                        "TR": 88551
                    }

# Load limits derived from maximum hourly values in 2018
# Source: ENTSO-E Transparency Platform 
# Remark: the maximum loads are strictly smaller than the installed capacity
load_limits =       {
                        "AL": 1480.41,
                        "AT": 12073.0,
                        "BA": 2080.0,
                        "BE": 13453.0,
                        "BG": 6468.93,
                        "CH": 9762.0,
                        "CZ": 11142.0,
                        "DE": 80687.5816,
                        "DK": 6075.5,
                        "EE": 1531.7,
                        "ES": 40611.0,
                        "FI": 14155.01,
                        "FR": 96328.0,
                        "GB": 61437.0,
                        "GR": 9061.62,
                        "HR": 3168.0,
                        "HU": 6572.28,
                        "IE": 4895.36,
                        "IT": 57572.0,
                        "LT": 1999.0,
                        "LU": 1030.7,
                        "LV": 1252.0,
                        "ME": 590.0,
                        "MK": 1388.0,
                        "NL": 18479.0,
                        "NO": 24108.0,
                        "PL": 24964.2857,
                        "PT": 8721.0,
                        "RO": 8920.0,
                        "RS": 6867.0,
                        "SE": 27380.0,
                        "SI": 2381.0,
                        "SK": 4518.55,
                        "KV": 1220.8
                    }

# Physical cross-border flow limits derived from maximum absolute hourly values in 2018
# Source: ENTSO-E Transparency Platform 
crossborder_limits = {
                        "AL - GR": 624.0,
                        "AL - ME": 529.73,
                        "AL - RS": 251.96,
                        "AT - CH": 1791.41,
                        "AT - CZ": 2526.0,
                        "AT - DE": 4708.4,
                        "AT - HU": 1456.3,
                        "AT - IT": 300.0,
                        "AT - SI": 1334.69,
                        "BA - HR": 1655.0,
                        "BA - ME": 761.39,
                        "BA - RS": 448.78,
                        "BE - FR": 4166.65,
                        "BE - LU": 315.84,
                        "BE - NL": 3565.13,
                        "BG - GR": 599.0,
                        "BG - RO": 1119.0,
                        "BG - RS": 662.79,
                        "BY - LT": 954.0,
                        "CH - DE": 6245.69,
                        "CH - FR": 3768.95,
                        "CH - IT": 4905.0,
                        "CZ - DE": 3031.56,
                        "CZ - PL": 1749.34,
                        "CZ - SK": 2224.7,
                        "DE - DK": 2213.19,
                        "DE - FR": 4569.0,
                        "DE - LU": 819.4,
                        "DE - NL": 5134.0,
                        "DE - PL": 2139.3,
                        "DE - SE": 611.9,
                        "DK - NO": 1618.12,
                        "DK - SE": 2268.8,
                        "ES - FR": 5567.41,
                        "ES - PT": 3977.86,
                        "FI - NO": 119.53,
                        "FI - RU": 1523.3,
                        "FI - SE": 2769.5,
                        "FR - GB": 2024.0,
                        "FR - IT": 3343.0,
                        "GB - NL": 1103.0,
                        "GR - IT": 511.0,
                        "GR - MK": 717.0,
                        "GR - TR": 723.0,
                        "HR - HU": 1751.83,
                        "HR - RS": 606.0,
                        "HR - SI": 1913.0,
                        "HU - RO": 566.08,
                        "HU - RS": 729.01,
                        "HU - SK": 1807.09,
                        "HU - UA": 1127.41,
                        "IT - MT": 254.0,
                        "IT - SI": 1730.0,
                        "LT - LV": 1315.0,
                        "LT - PL": 495.56,
                        "LT - RU": 630.0,
                        "LT - SE": 733.8,
                        "LV - RU": 344.0,
                        "ME - RS": 566.06,
                        "MK - RS": 590.41,
                        "NL - NO": 732.0,
                        "NO - SE": 4210.51,
                        "PL - SE": 600.8,
                        "PL - SK": 1054.1,
                        "PL - UA": 218.62,
                        "RO - RS": 714.25,
                        "RO - UA": 641.0,
                        "SK - UA": 773.83
                     }

# Generation values for 2018 from the Statistical Factsheet
# Published by ENTSO-E 05th June 2019
# in TWh
g_2018_entsoe = {
    "AL": 8.1,
    "AT": 67.5,
    "BA": 17.3,
    "BE": 69.1,
    "BG": 42.3,
    "CH": 67.6,
    "CY": 5.0,
    "CZ": 81.8,
    "DE": 597.6,
    "DK": 28.9,
    "EE": 10.3,
    "ES": 261.0,
    "FI": 67.5,
    "FR": 548.6,
    "GB": 285.8,
    "GR": 45.3,
    "HR": 12.1,
    "HU": 28.2,
    "IE": 29.3,
    "IS": 19.3,
    "IT": 280.5,
    "LT": 3.2,
    "LU": 2.0,
    "LV": 6.5,
    "ME": 3.6,
    "MK": 5.2,
    "NL": 108.6,
    "NO": 145.7,
    "PL": 157.1,
    "PT": 55.1,
    "RO": 60.7,
    "RS": 39.6,
    "SE": 158.3,
    "SI": 15.0,
    "SK": 25.1,
    "TR": 300.4   
    }

d_2018_entsoe = {
    "AL": 7.2,
    "AT": 71.4,
    "BA": 12.6,
    "BE": 85.1,
    "BG": 34.1,
    "CH": 67.6,
    "CY": 5.0,
    "CZ": 66.6,
    "DE": 538.1,
    "DK": 34.1,
    "EE": 8.7,
    "ES": 268.9,
    "FI": 87.4,
    "FR": 478.3,
    "GB": 304.0,
    "GR": 51.6,
    "HR": 18.2,
    "HU": 42.5,
    "IE": 28.7,
    "IS": 19.3,
    "IT": 322.2,
    "LT": 12.1,
    "LU": 6.4,
    "LV": 7.4,
    "ME": 3.4,
    "MK": 7.1,
    "NL": 116.5,
    "NO": 135.5,
    "PL": 162.2,
    "PT": 50.9,
    "RO": 57.9,
    "RS": 39.1,
    "SE": 141.1,
    "SI": 14.4,
    "SK": 28.5,
    "TR": 300.0
    }

g_by_source = {
    # Source E-Control AT Betriebsstatistik 2018
    "AT":
        {
        "biomass": 4.62,
         "gas": 10.07,
         "geothermal": 0.0,
         "hard_coal": 1.79,
         "hydro": 41.18,
         "other_fossil": 0.96,
         "solar": 0.82,
         "wind_onshore": 6.03,
         },
    # Source CREG Annual Report 2018
    "BE":
        {
            "gas": 19.33,
        "hydro": 1.14,
        "nuclear": 27.23
        },
    # Source GlobalPetrolPrices.com    
    "BG":
        {
        "nuclear": 15.32,
        "hydro": 4.81,
        "solar": 1.34,
        "wind_onshore": 1.32
        },
    # Source Verband Schweizerischer Elektrizitätsunternehmen strom.ch
    "CH":
        {
        "hydro": 37.43,
         "nuclear": 24.41,
         "solar": 1.33,
         "wind_onshore": 0.11
         },
    # Source IEA and Euracoal
    "CZ":
        {
        "biomass": 4.73,
         "gas": 3.75,
         "hard_coal": 5.8,
         "hydro": 2.68,
         "lignite": 37.7,
         "nuclear": 29.92,
         "oil": 0.11,
         "other_fossil": 0.13,
         "solar": 2.36,
         "waste": 0.18,
         "wind_onshore": 0.61
         },
    # Source Fraunhofer ISE, Destatis, BMWi
    "DE":
        {
        "biomass": 44.7,
        "gas": 44.1,
        "geothermal": 0.2,
        "hard_coal": 72.7,
        "hydro": 16.3,
        "lignite": 131.4,
        "nuclear": 72.2,
        "oil": 5.2,
        "other_fossil": 27.0,
        "other_renewable": None,
        "solar": 45.7,
        "waste": 6.2,
        "wind_offshore": 24.7,
        "wind_onshore": 101.1
        },
    # Source Danish Energy Agency, IEA
    # Notice share of offshore wind production is assumed 46%
    "DK":
        {
        "biomass": 5.04,
        "gas": 1.94,
        "hard_coal": 6.57,
        "oil": 0.27,
        "solar": 0.95,
        "waste": 1.56,
        "wind_offshore": 6.39,
        "wind_onshore": 7.5
        },
    # Source Statistics Estonia, IEA
    # Notice oil shale is considered "oil" on ENTSO-E and "coal" on IEA
    "EE":
        {
        "biomass": 1.21,
         "gas": 0.06,
         "hydro": 0.02,
         "oil": 10.13,
         "other_fossil": None,
         "other_renewable": None,
         "waste": 0.14,
         "wind_onshore": 0.64
         },
    # Source Red Electrica, IEA
    # Notice lignite share of coal production is assumed 10%
    "ES":
        {
        "biomass": 5.16,
        "gas": 58.00,
        "hard_coal": 34.85,
        "hydro": 36.80,
        "lignite": 3.87,
        "nuclear": 55.77,
        "oil": 14.50,
        "other_fossil": None,
        "other_renewable": None,
        "solar": 12.74,
        "waste": 1.78,
        "wind_onshore": 50.90
        },
    # Source Statistics Finland's PxWeb databases, IEA
    "FI":
        {
        "biomass": 12.25,
        "gas": 4.19,
        "hard_coal": 10.07,
        "hydro": 13.14,
        "nuclear": 21.88,
        "oil": 0.27,
        "other_fossil": None,
        "other_renewable": None,
        "waste": 1.18,
        "wind_onshore": 5.84
        },
    # Source Rte, IEA
    "FR":
        {
        "biomass": 9.7,
        "gas": 31.4,
        "hard_coal": 5.8,
        "hydro": 68.3,
        "nuclear": 393.2,
        "oil": 2.2,
        "solar": 10.2,
        "waste": 4.6,
        "wind_onshore": 27.8
        },
    # Source Department for Business, Energy and Industrial Strategy, IEA
    # Notice assumed share of offshore of wind production 34%
    "GB":
        {
        "biomass": 31.91, # 102.2
        "gas": 131.49,
        "hard_coal": 17.6,
        "hydro": 8.0,
        "nuclear": 65.06,
        "oil": 1.07,
        "other_fossil": None,
        "solar": 12.86,
        "wind_offshore": 19.35,
        "wind_onshore": 36.99
        },
    # Source IEA
    "GR":
        {
        "gas": 14.08,
        "lignite": 17.19,
        "solar": 3.79,
        "wind_onshore": 6.3
        },
    # Source IAEA, IEA
    "HU":
        {
        "biomass": 2.13,
        "gas": 7.23,
        "hydro": 0.22,
        "lignite": 4.83,
        "nuclear": 15.73,
        "oil": 0.09,
        "other_fossil": None,
        "other_renewable": None,
        "waste": 0.38,
        "wind_onshore": 0.61
        },
    # Source IEA
    "IE":
        {
        "gas": 16.01,
        "hard_coal": 4.25,
        "hydro": 0.93,
        "oil": 0.14,
        "other_fossil": None,
        "wind_onshore": 8.64
        },
    # Source IEA
    "IT":
        {
        "biomass": 16.78,
        "gas": 128.54,
        "geothermal": 6.11,
        "hard_coal": 30.96,
        "hydro": 50.50,
        "oil": 11.03,
        "other_fossil": None,
        "solar": 22.65,
        "waste": 4.83,
        "wind_onshore": 17.72
        },
    # Source IEA
    "LT":
        {
        "biomass": 0.50,
        "gas": 0.33,
        "hydro": 0.96,
        "oil": 0.13,
        "other_fossil": None,
        "solar": 0.09,
        "waste": 0.13,
        "wind_onshore": 1.14
        },
    # Source IEA
    "LV":
        {
        "biomass": 0.94,
        "gas": 3.22,
        "hydro": 2.43,
        "other_fossil": None,
        "wind_onshore": 0.12
        },
    # Source IEA
    "ME":
        {
        "hard_coal": None,
        "hydro": 2.11,
        "lignite": 1.56,
        "wind_onshore": 0.14
        },
    # Source IEA
    # Offshore share of wind production is assumed 50%
    "NL":
        {
        "biomass": 2.38,
        "gas": 58.36,
        "hard_coal": 30.30,
        "nuclear": 3.52,
        "other_fossil": None,
        "solar": 3.69,
        "waste": 4.18,
        "wind_offshore": 5.28,
        "wind_onshore": 5.28
        },
    # Source Statistics Norway
    "NO":
        {
        "hydro": 139.51,
        "gas": 3.46,
        "wind_onshore": 3.88
        },
    # Source IEA
    # Lignite share of coal production is assumed 35%
    "PL":
        {
        "biomass": 6.46,
        "gas": 12.63,
        "hard_coal": 86.45,
        "hydro": 2.39,
        "lignite": 46.55,
        "oil": 1.8,
        "other_fossil": None,
        "wind_onshore": 12.8
        },
    # Source IEA
    "PT":
        {
        "biomass": 2.83,
        "gas": 15.61,
        "hard_coal": 12.01,
        "hydro": 13.63,
        "other_fossil": None,
        "solar": 1.01,
        "wind_onshore": 12.62
        },
    # Source IEA
    # Lignite share of coal production is assumed 92%
    "RO":
        {
        "biomass": 0.53,
        "gas": 10.52,
        "hard_coal": 1.26,
        "hydro": 18.10,
        "lignite": 14.49,
        "nuclear": 11.38,
        "solar": 1.77,
        "wind_onshore": 6.32
        },
    # Source IEA
    "RS":
        {
        "biomass": 0.10,
        "gas": 0.60,
        "hydro": 11.39,
        "lignite": 25.11,
        "other_fossil": None
        },
    # Source Swedish Energy Agency, IEA
    "SE":
        {
        "hydro": 62.25,
        "nuclear": 68.55,
        "other_fossil": None,
        "wind_onshore": 16.16
        },
    # Source IEA
    "SI":
        {
        "biomass": 0.27,
        "gas": 0.48,
        "hydro": 4.89,
        "lignite": 4.62,
        "nuclear": 5.78,
        "oil": 0.02,
        "solar": 0.26,
        "waste": 0.01,
        "wind_onshore": 0.01
        },
    # Source IEA
    # Lignite share of coal production assumed 65%
    "SK":
        {
        "biomass": 1.61,
        "gas": 1.86,
        "hard_coal": 1.25,
        "hydro": 3.88,
        "lignite": 2.33,
        "nuclear": 14.84,
        "oil": 0.46,
        "other_fossil": None,
        "other_renewable": None,
        "solar": 0.59
        }
}
    
# Annual import/export data
# Source Eurostat Energy Data | 2020 Edition
F_default = {
    "AT":
        {
        "import": 28.08,
        "export": 19.13
        },
    "BE":
        {
        "import": 21.64,
        "export": 4.31
        },
    "BG":
        {
        "import": 2.22,
        "export": 10.03
        },
    # Source Swiss Federal Office of Energy
    "CH":
        {
        "import": 31.0,
        "export": 32.6
        },
    "CZ":
        {
        "import": 11.57,
        "export": 25.48
        },
    "DE":
        {
        "import": 31.23,
        "export": 80.46
        },
    "DK":
        {
        "import": 15.63,
        "export": 10.41
        },
    "EE":
        {
        "import": 3.05,
        "export": 4.95
        },
    "ES":
        {
        "import": 24.02,
        "export": 29.92
        },
    "FI":
        {
        "import": 22.55,
        "export": 2.61
        },
    "FR":
        {
        "import": 13.56,
        "export": 76.53
        },
    "GB":
        {
        "import": 21.33,
        "export": 2.22
        },
    "GR":
        {
        "import": 8.55,
        "export": 2.27
        },
    "HU":
        {
        "import": 18.61,
        "export": 4.26
        },
    "IE":
        {
        "import": 1.62,
        "export": 1.65
        },
    "IT":
        {
        "import": 47.17,
        "export": 3.27
        },
    "LT":
        {
        "import": 12.85,
        "export": 3.21
        },
    "LV":
        {
        "import": 5.17,
        "export": 4.26
        },
    "ME":
        {
        "import": 0.78,
        "export": 0.98
        },
    "NL":
        {
        "import": 26.75,
        "export": 18.78
        },
    "NO":
        {
        "import": 8.34,
        "export": 18.49
        },
    "PL":
        {
        "import": 13.82,
        "export": 8.12
        },
    "PT":
        {
        "import": 5.67,
        "export": 8.32
        },
    "RO":
        {
        "import": 3.70,
        "export": 6.24
        },
    "RS":
        {
        "import": 6.40,
        "export": 6.28
        },
    "SE":
        {
        "import": 12.20,
        "export": 29.43
        },
    "SI":
        {
        "import": 8.93,
        "export": 9.43
        },
    "SK":
        {
        "import": 12.43,
        "export": 8.75
        }
}
    
F_specific = {
                # Source Energieverbrauch in Deutschland Daten für das 1.-4. Quartal 2018
                # AG Energiebilanzen
                "NL -> DE": 0.76,
                "AT -> DE": 4.08,
                "CH -> DE": 3.86,
                "CZ -> DE": 4.90,
                "PL -> DE": 0.02,
                "LU -> DE": 1.23,
                "DK -> DE": 4.42,
                "FR -> DE": 10.98,
                "SE -> DE": 1.30,
                "DE -> NL": 20.91,
                "DE -> AT": 16.34,
                "DE -> CH": 16.09,
                "DE -> CZ": 7.58,
                "DE -> PL": 7.06,
                "DE -> LU": 5.86,
                "DE -> DK": 5.82,
                "DE -> FR": 2.54,
                "DE -> SE": 0.48,
                # Source Bach, Electricity in Denmark 2018
                "NO -> DK": 5.00,
                "SE -> DK": 4.70,
                "DK -> NO": 2.60,
                "DK -> SE": 3.20,
                # Source Rte, Electricity Report 2018
                "CH -> FR": 7.00,
                "ES -> FR": 4.40,
                "GB -> FR": 1.80,
                "IT -> FR": 0.50,
                "FR -> CH": 17.60,
                "FR -> ES": 16.4,
                "FR -> GB": 14.70,
                "FR -> IT": 19.10,
                # Source Eurotstat "Exports of electricity and derived heat by partner country"
                "AT -> CZ": 10.86,
                "AT -> IT": 23.94,
                "AT -> HU": 0.59,
                "AT -> SI": 0.40,
                "BE -> FR": 10.77,
                "BE -> NL": 10.78,
                "BA -> ME": 0.17,
                "BA -> RS": 1.00,
                "BG -> RO": 0.85,
                "BG -> RS": 0.04,
                "CZ -> DE": 7.58,
                "CZ -> AT": 0.11,
                "CZ -> PL": 3.77,
                "CZ -> SK": 0.11,
                "CZ -> ME": 0.25,
                "EE -> LV": 0.04,
                "EE -> FI": 2.37,
                "FI -> EE": 1.13,
                "FI -> SE": 13.59,
                "FI -> NO": 0.19,
                "FR -> BE": 2.19,
                "FR -> ES": 3.47,
                "GR -> BG": 2.12,
                "GR -> IT": 0.61,
                "HU -> AT": 3.75,
                "HU -> RO": 2.57,
                "HU -> SK": 6.81,
                "HU -> RS": 1.23,
                "IE -> GB": 1.62,
                "IT -> GR": 1.08,
                "IT -> AT": 1.42,
                "IT -> SI": 6.86,
                "LV -> EE": 3.82,
                "LV -> LT": 0.72,
                "LT -> LV": 4.22,
                "LT -> PL": 0.72,
                "LT -> SE": 2.87,
                "ME -> RS": 0.16,
                "ME -> BA": 1.25,
                "NL -> BE": 1.78,
                "NL -> NO": 4.02,
                "NL -> GB": 0.21,
                "NO -> NL": 0.33,
                "NO -> SE": 4.31,
                "PL -> CZ": 0.64,
                "PL -> LT": 1.62,
                "PL -> SE": 3.01,
                "PT -> ES": 5.67,
                "RO -> BG": 1.21,
                "RO -> HU": 0.59,
                "RO -> RS": 0.22,
                "RS -> BG": 2.30,
                "RS -> HU": 0.27,
                "RS -> RO": 2.59,
                "RS -> ME": 0.30,
                "RS -> BA": 0.49,
                "SK -> CZ": 9.08,
                "SK -> HU": 0.06,
                "SK -> PL": 2.3,
                "SI -> IT": 0.06,
                "SI -> AT": 4.01,
                "SI -> ME": 0.09,
                "ES -> PT": 8.32,
                "SE -> LT": 0.22,
                "SE -> PL": 0.38,
                "SE -> FI": 0.17,
                "SE -> NO": 9.34,
                "CH -> IT": 1.14,
                "CH -> AT": 5.46,
                "GB -> IE": 1.65,
                "GB -> NL": 6.93,
                }


def load_data(path_g, path_d, path_F, country_balance=False, subset=False):
    """
    

    Parameters
    ----------
    path_g : string
        Path to the original generation data.
    path_d : string
        Path to the original demand data
    path_F : string
        Path to the original cross-border data
    country_balance : boolean, optional
        Output country balances. The default is False.
    subset : TYPE, optional
        Only return a subset of countries . The default is False.

    Returns
    -------
    g_d: dictionary
        Holding the generation and demand data per country.
    F: pd.dataframe
        Holds the cross-border flows of all links.
    """
    # Load data from paths given as parameters
    df_g = pd.read_csv(path_g, low_memory=False)
    df_d = pd.read_csv(path_d, low_memory=False)
    F = pd.read_csv(path_F, low_memory=False)
    
    # Prepare generation.csv
    g_col = df_g.columns.values
    # Only keep columns with country data, data from smaller geographic areas is being dropped
    g_col = [x for x in g_col if "_" not in x]
    df_g = df_g[g_col]
    # Rename columns <country_productiontype>
    new_names = [x[:2] + "_" + df_g[x][0] for x in df_g.columns]
    df_g.columns = new_names
    # Remove the first 5 rows
    df_g = df_g.iloc[2:]
    # Replace np.nan with zeros
    df_g = df_g.fillna(0)
    # Make values numeric for calculations
    df_g.iloc[:,1:] = df_g.iloc[:,1:].apply(pd.to_numeric)
    # Reset index to make it start at 0
    df_g = df_g.reset_index(drop=True)
    
    
    # Prepare demand.csv
    # Rename columns <country_"demand">
    new_names = [x + "_demand" for x in df_d.columns]
    df_d.columns = new_names
    
     
    # Prepare crossborder.csv
    # A bit more work since one entry is missing because of time shift
    # A empty line is added at the point where the time was set forth
    line = pd.DataFrame({"DateTime" : "2018-03-25 02:00:00"}, index = [1994])
    # Make data frame numeric apart from the first column
    F.iloc[:,1:] = F.iloc[:,1:].apply(pd.to_numeric) 
    F = pd.concat([F.iloc[:1994], line, F.iloc[1994:]]).reset_index(drop=True)
    df_dates = F["DateTime"].to_frame()
    # Let's select the entire datafram apart from the DateTime  column
    F.iloc[1994:, 1:] = F.iloc[1994:, 1:].shift(-1)
    # Drop the DateTime column
    F = F.iloc[:, 1:]
    # 2020-10-28 02:00:00 corresponds to index 7202
    new_line = (F.iloc[7201] + F.iloc[7202]) / 2
    new_line.name = 8760
    F = F.append([new_line])
    F = pd.concat([F, F.iloc[7202:]]).reset_index(drop=True)
    # Drop the unecessary rows before the appended row
    F = F.drop(F.index[7202:8760])
    # Drop the last two rows
    F = F.iloc[:8760]
    F = F.reset_index(drop=True)
    # Insert date column at the very beginning
    #F.insert(loc=0, column="DateTime", value=df_dates["DateTime"])
    # Create unidirectional columns from the bidirectional ones
    for b in F.columns.values:
        # Set new column names
        e = b[:2] + " -> " + b[-2:]
        i = b[-2:] + " -> " + b[:2]
        # Fill export column when > 0, else fill import column
        F[e] = 0
        F.loc[F[b] > 0, e] = F[b]
        F[i] = 0
        F.loc[F[b] < 0, i] = abs(F[b])
    droplist = [x for x in F.columns.values if "->" not in x]
    F.drop(droplist,axis=1,inplace=True)
    
   
    # Create country specific dataframes if parameter is set to True
    countries_generation = set([x[:2] for x in df_g.columns.values])
    countries_demand = set([x[:2] for x in df_d.columns.values])
    countries = set.intersection(*[countries_generation, countries_demand])
    g_d = {}
    # If the keyword country_balance is true, include links
    if country_balance:
        for country in countries:
            # Get column values for generation
            g_col = [col for col in df_g.columns if country in col[0:2]]
            # Get column values for demand
            demand_col = [col for col in df_d.columns if country in col]
            
            # Get column values for crossborder
            flow_col = [col for col in F.columns if country in col]
            temp_g = df_g[g_col]
            temp_g.columns = [x[3:] for x in temp_g.columns.values]
            temp_d = df_d[demand_col]
            temp_d.columns = [x[3:] for x in temp_d.columns.values]
            temp_f = F[flow_col]
            g_d[country] = pd.concat([temp_g, temp_d, temp_f], ignore_index=False, axis=1)
        if subset:
            g_d = {k: g_d[k] for k in["AT", "DE", "DK", "SE"]}
        return g_d

    else: 
        for country in countries:
            # Get column values for generation
            g_col = [col for col in df_g.columns if country in col[0:2]]
            # Get column values for demand
            demand_col = [col for col in df_d.columns if country in col]
            temp_g = df_g[g_col]
            temp_g.columns = [x[3:] for x in temp_g.columns.values]
            temp_d = df_d[demand_col]
            temp_d.columns = [x[3:] for x in temp_d.columns.values]
            # Put country specific generation and demand data in dictionary
            g_d[country] = pd.concat([temp_g, temp_d], ignore_index=False, axis=1)
    # If parameter subset=True only return data for a subset of countries
    if subset:
        for country, df in g_d.items():
            g_d[country] = df.iloc[:][:]
            g_d = {k: g_d[k] for k in["AT", "DE", "DK", "SE"]}
        F = F.iloc[:][:]
    # Filter F so that only links persist where origin and destination are 
    # within considered countries
    valid_links = [x for x in F.columns.values if x[:2] in g_d.keys() and x[-2:] in g_d.keys()]
    F = F[valid_links]
    return (g_d, F)


def calculate_sigma(g_d, F, g_2018_entsoe, d_2018_entsoe, g_by_source, F_default, F_specific):
    path_t = "../input/official_data/gen_targets.csv"
    sigma = {}
    # Calculate sigma for generation and demand
    sigma["g"] = {}
    sigma["d"] = {}
    sigma["F"] = {}
    p_index = {}
    # Load target from ENTSO-E Statistical Factsheet 2018
    targets = pd.read_csv(path_t)
    new_names = [x[:2] + "_" + targets[x][0] for x in targets.columns]
    targets.columns = new_names
    #targets = targets[[x for x in targets.columns if x[:2] in included_countries]]
    targets = targets.iloc[2:]
    for country, df in g_d.items():
        sigma["g"][country] = {}
        sigma["d"][country] = {}
        # Obtain country specific production types
        p_index[country] = [x for x in df.columns.values if "demand" not in x]
        #g_d[country]["total"] = df[production_types].sum(axis=1)
        # Get yearly generation
        # Debugging new way to get the sigma_g
        # Now with the production targets from ENTSO-E statistical factsheet
        for p in p_index[country]:
            if float(targets[country + "_" + p].iloc[0]) == 0:
                targets[country + "_" + p].iloc[0] = 1
            sigma_g = sigma_g = g_d[country][p].sum(axis=0) / float(targets[country + "_" + p].iloc[0])
            sigma["g"][country][p] = sigma_g
        # Get yearly demand
        sigma_d = g_d[country]["demand"].sum(axis=0) / d_2018_entsoe[country] / 1000000
        sigma["d"][country] = sigma_d
    # Calculate sigma for the links
    sigma["F"] = {}
    for l in F.columns.values:
        # Set default value of 0.8
        sigma["F"][l] = 0.8
        if l in F_specific:
            sigma_F = F[l].sum(axis=0) / F_specific[l] / 1000000
        # Don't allow numbers larger than 1.0
            #if sigma_F > 1.0:
             #   sigma_F = 1.0
            sigma["F"][l] = sigma_F
    return sigma


def filter_links(F, g_d):
    valid_links = [x for x in F.columns.values if x[:2] in g_d.keys() and x[-2:] in g_d.keys()]
    F = F[valid_links]
    return F

def calculate_internal_sigma(g_d, F, A, eta):
    sigma = {}
    # Construct sigma for generation and demand
    for country, df in g_d.items():
        for column in df.columns.values:
            df[column + "_rolling_average"] = 0
            for i in range(10):
                df[column + "_rolling_average"] += df[column].shift(24 * i) * 0.1
            df[column + "_rolling_average"].fillna(df[column], inplace=True)
            # Leave value or replace by eta if too small
            df[column + "_rolling_average"] = df[column + "_rolling_average"].apply(lambda x: eta if x < eta else x)
            # Calculate sigma on basis of constant A, cut-off value eta and the rolling average
            df[column + "_rolling_average"] = df[column + "_rolling_average"].apply(lambda x:  A/x)

        df = df[[x for x in df.columns.values if "rolling_average" in x]]
        df.columns = [[x[:-16] for x in df.columns.values]]
        sigma[country] = df

    # Construct sigma values for cross-border flows
    for link in F.columns.values:
        F[link + "_rolling_average"] = 0
        for i in range(10):
            F[link + "_rolling_average"] += F[link].shift(24 * i) * 0.1
        F[link + "_rolling_average"].fillna(F[link], inplace=True)
        # Leave value or replace by eta if too small
        F[link + "_rolling_average"] = F[link + "_rolling_average"].apply(lambda x: eta if x < eta else x)
        # Calculate sigma on basis of constant A, cut-off value eta and the rolling average
        F[link + "_rolling_average"] = F[link + "_rolling_average"].apply(lambda x:  A/x)
    F = F[[x for x in F.columns.values if "rolling_average" in x]]
    F.columns = [[x[:-16] for x in F.columns.values]]
    sigma["F"] = F

    return sigma


def make_clean(g_d, F, a_var, f_var, name=""):
    g_d_clean = {}
    for country, df in g_d.items():
        for x in df.columns:
            df[x] = a_var["g_d"][country][x] + df[x] * f_var["g_d"][country][x]
        g_d_clean[country] = df
        df.to_csv("../output/attacking_vector/clean_sets/" + name + "/g_d/" + country + ".csv")
    # Cross-border flows
    for x in F.columns:
        F[x] = a_var["F"][x] + F[x] * f_var["F"][x]
    F_clean = F
    F_clean.to_csv("../output/attacking_vector/clean_sets/" + name + "/" + "F" + ".csv")
    return g_d_clean, F_clean

def make_country_balances(g_d, F, name=""):
    country_balances = {}
    for country, df in g_d.items():
        sub_F_i = F[[x for x in F.columns if country in x[-2:]]]
        sub_F_e = F[[x for x in F.columns if country in x[:2]]]
        d = df["demand"]
        g = df[[x for x in df.columns if "demand" not in x]]
        country_balances[country] = pd.concat([g, sub_F_i, d, sub_F_e], ignore_index=False, axis=1)
        country_balances[country]["mismatch"] = df[[x for x in df.columns if "demand" not in x]].sum(axis=1) + \
                                                F[[x for x in F.columns if country in x[-2:]]].sum(axis=1) - \
                                                df["demand"] -\
                                                F[[x for x in F.columns if country in x[:2]]].sum(axis=1)
        #country_balances[country].to_csv("../output/clean_sets/"  + name + country + ".csv")
    return country_balances


# WORK IN PROGRESS
def make_yearly(country_balances):
    yearly = {}
    for country, df in country_balances.items():
        yearly[country] = {}
        yearly[country]["y"] = list(df.sum())
        yearly[country]["x_y"] = df.sum().to_dict()
        yearly[country]["x"] = df.columns.values
    return yearly
        
def get_zero_rows(country_balances):
    zero_indices_list = {}
    for country, df in country_balances.items():
        index = df.index
        df["total"] = df[[x for x in df.columns if "->" not in x and "demand" not in x and "mismatch" not in x]].sum(axis=1)
        condition = df["total"] == 0
        zero_indices = index[condition]
        zero_indices_list[country] = zero_indices.tolist()
    return zero_indices_list

def load_all_csv_files(path):
    country_balances = {}
    directory = path
    for root,dirs,files in os.walk(directory):
        for file in files:
           if file.endswith(".csv"):
               name = file[:2]
               country_balances[name] = pd.read_csv(directory + "/" + file, index_col=0)
    return country_balances
        
def fake_reconciliation(g_d, F, name="complete_"):
    country_balances = {}
    for country, df in g_d.items():
        sub_F_i = F[[x for x in F.columns if country in x[-2:]]]
        sub_F_e = F[[x for x in F.columns if country in x[:2]]]
        d = df["demand"]
        g = df[[x for x in df.columns if "demand" not in x]]
        country_balances[country] = pd.concat([g, sub_F_i, d, sub_F_e], ignore_index=False, axis=1)
        country_balances[country]["mismatch"] = df[[x for x in df.columns if "demand" not in x]].sum(axis=1) + \
                                                F[[x for x in F.columns if country in x[-2:]]].sum(axis=1) - \
                                                df["demand"] -\
                                                F[[x for x in F.columns if country in x[:2]]].sum(axis=1)
                                                
        country_balances[country]["s_l"] = country_balances[country]["mismatch"].apply(lambda x: -x if x < 0 else 0)
        country_balances[country]["s_r"] = country_balances[country]["mismatch"].apply(lambda x: x if x > 0 else 0)
        country_balances[country] = country_balances[country].drop(columns=["mismatch"])
        #country_balances[country].to_csv("../output/debugging/attacking_vector/"  + name + country + ".csv")
    return country_balances


def calculate_external_sigma_av(g_d, F, g_2018_entsoe, d_2018_entsoe, g_by_source, F_default, F_specific, g_d_complete, F_complete):
    path_t = "../input/official_data/gen_targets.csv"
    sigma = {}
    # Calculate sigma for generation and demand
    sigma["g"] = {}
    sigma["d"] = {}
    sigma["s_r"] = {}
    sigma["F"] = {}
    p_index = {}
    # Load target from ENTSO-E Statistical Factsheet 2018
    targets = pd.read_csv(path_t)
    new_names = [x[:2] + "_" + targets[x][0] for x in targets.columns]
    targets.columns = new_names
    #targets = targets[[x for x in targets.columns if x[:2] in included_countries]]
    targets = targets.iloc[2:]
    for country, df in g_d.items():
        sigma["g"][country] = {}
        sigma["d"][country] = {}
        # Obtain country specific production types
        p_index[country] = [x for x in df.columns.values if "demand" not in x and "s_r" not in x and "s_l" not in x]
        #g_d[country]["total"] = df[production_types].sum(axis=1)
        # Get yearly generation
        # Debugging new way to get the sigma_g
        # Now with the production targets from ENTSO-E statistical factsheet
        for p in p_index[country]:
            if p == "other_renewable" and country == "AT":
                sigma["g"][country][p] = 0.83
            else:
                sigma_g = g_d[country][p].sum(axis=0) / g_d_complete[country][p].sum(axis=0)
                sigma["g"][country][p] = sigma_g
        # Add target for slack variable "s_l"
        sigma["g"][country]["s_l"] = g_d[country]["s_l"].sum(axis=0) / g_d_complete[country]["s_l"].sum(axis=0)
        # Add target for slack variable "s_r"
        sigma["s_r"][country] = g_d[country]["s_r"].sum(axis=0) / g_d_complete[country]["s_r"].sum(axis=0)
        # Get yearly demand
        sigma_d = g_d[country]["demand"].sum(axis=0) / g_d_complete[country]["demand"].sum(axis=0)
        sigma["d"][country] = sigma_d
    # Calculate sigma for the links
    sigma["F"] = {}
    for l in F.columns.values:
            sigma_F = F[l].sum(axis=0) / F_complete[l].sum(axis=0)
        # Don't allow numbers larger than 1.0
            #if sigma_F > 1.0:
             #   sigma_F = 1.0
            sigma["F"][l] = sigma_F
    return sigma


    

def make_g_d_F(country_balances):
    g_d = {}
    F = pd.DataFrame()
    for country, df in country_balances.items():
        g_d[country] = df[[x for x in df.columns if "->" not in x]]
        #g_d[country].to_csv("../output/debugging/attacking_vector/" + "g_d_" + country + ".csv")
        cross_columns = [x for x in df.columns if "->" in x]
        for c in cross_columns:
            if c not in F.columns:
                F[c] = df[c]

        #df.to_csv("../output/debugging/attacking_vector/" + country + ".csv")
    F.to_csv("../output/debugging/attacking_vector/" + "F" + ".csv")

    return g_d, F
    
def get_original_F(path_F):
    pass
    
        