import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
import requests

# --- 1. USER CONFIGURATION: YOU MUST EDIT THIS SECTION ---

# Define your 15 suppliers. We'll assume equal impact (1/6 per location)
# for this example, but you can make this more complex.
SUPPLIER_LOCATIONS = {
    "PIRACICABA/SP": 1.0 / 6.0,
    "BARRINHA/SP": 1.0 / 6.0,
    "VALPARAÍSO/SP": 1.0 / 6.0,
    "QUIRINÓPOLIS/GO": 1.0 / 6.0,
    "MANDAGUAÇU/PR": 1.0 / 6.0,
    "SANTA RITA/PB": 1.0 / 6.0,
}

# Define your 20 client locations.
# !! CRITICAL !!
CLIENT_LOCATIONS = {
    "NOVO HORIZONTE/SP": {"impact_percent": 0.07},
    "SERRA AZUL/SP": {"impact_percent": 0.03},
    "SÃO JOAQUIM DA BARRA/SP": {"impact_percent": 0.02},
    "CHAVANTES/SP": {"impact_percent": 0.01},
    "CESÁRIO LANGE/SP": {"impact_percent": 0.01},
    "SERTÃOZINHO/SP": {"impact_percent": 0.03},
    "ITAPURA/SP": {"impact_percent": 0.08},
    "PENÁPOLIS/SP": {"impact_percent": 0.04},
    "GUARAÇAÍ/SP": {"impact_percent": 0.005},
    "OLÍMPIA/SP": {"impact_percent": 0.015},
    "RANCHARIA/SP": {"impact_percent": 0.01},
    "QUIRINÓPOLIS/GO": {"impact_percent": 0.06},
    "VILA PROPÍCIO/GO": {"impact_percent": 0.04},
    "JATAÍ/GO": {"impact_percent": 0.02},
    "MINEIROS/GO": {"impact_percent": 0.08},
    "CAARAPÓ/MS": {"impact_percent": 0.035},
    "COLORADO/PR": {"impact_percent": 0.045},
    "ITURAMA/MG": {"impact_percent": 0.03},
    "BARRA DO BUGRES/MT": {"impact_percent": 0.02},
    "CORURIPE/AL": {"impact_percent": 0.01},
}

# --- 2. SETUP ---

# Randomize CLIENT_LOCATIONS impact_percent so they sum to 1.0
def randomize_client_impacts(locations_dict):
    keys = list(locations_dict.keys())
    if not keys:
        return locations_dict
    weights = np.random.dirichlet(np.ones(len(keys)))
    for key, w in zip(keys, weights):
        # Keep as decimal fraction (e.g., 0.12 for 12%)
        locations_dict[key]["impact_percent"] = float(w)
    return locations_dict

CLIENT_LOCATIONS = randomize_client_impacts(CLIENT_LOCATIONS)

# Paths
GEONAMES_PATH = Path(__file__).parent / "geonames.json"

# Brazil state abbreviation to full state name (matching geonames.json capitalization)
BRAZIL_ABBREV_TO_NAME = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapa",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceara",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso Do Sul",
    "MG": "Minas Gerais",
    "PA": "Para",
    "PB": "Paraiba",
    "PR": "Parana",
    "PE": "Pernambuco",
    "PI": "Piaui",
    "RJ": "Rio De Janeiro",
    "RN": "Rio Grande Do Norte",
    "RS": "Rio Grande Do Sul",
    "RO": "Rondonia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "Sao Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Invert Brazil state name to geocode (from geonames.json)
def load_brazil_state_name_to_code():
    try:
        with open(GEONAMES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        states = data["country"]["BRA"]["S"]
        # states is like {"BRA.37665": "Acre", ...}
        name_to_code = {v: k for k, v in states.items()}
        return name_to_code
    except Exception as e:
        print(f"Error loading geonames.json: {e}")
        return {}

BRAZIL_STATE_NAME_TO_CODE = load_brazil_state_name_to_code()

# --- 3. CORE FUNCTIONS (state-level CCKP API) ---

def parse_city_and_state(location_name):
    """
    Parses strings like 'PIRACICABA/SP' into ('PIRACICABA', 'SP').
    If no '/', returns (location_name, None).
    """
    if "/" in location_name:
        city, state_abbrev = location_name.split("/", 1)
        return city.strip(), state_abbrev.strip()
    return location_name, None

def get_state_geocode(state_abbrev):
    """
    Given 'SP', returns 'BRA.37689' using geonames.json mapping.
    """
    if not state_abbrev:
        return None
    state_name = BRAZIL_ABBREV_TO_NAME.get(state_abbrev.upper())
    if not state_name:
        return None
    return BRAZIL_STATE_NAME_TO_CODE.get(state_name)

def build_cckp_url(variables_csv, period_code, scenario_code, geocode):
    """
    Build a CCKP v1 API URL for climatology annual means.
    Example:
    https://cckpapi.worldbank.org/cckp/v1/cmip6-x0.25_climatology_tas,pr_climatology_annual_1995-2014_median_historical_ensemble_all_mean/BRA.37689?_format=json
    """
    base = "https://cckpapi.worldbank.org/cckp/v1"
    # collection: cmip6-x0.25
    # type: climatology
    # variables: provided as csv in {variables_csv}
    # product: climatology
    # aggregation: annual
    # percentile: median
    # scenario: historical or ssp585 (example)
    # model: ensemble
    # model-calculation: all
    # statistic: mean
    # geocode: e.g., BRA.37689 (Sao Paulo)
    return (
        f"{base}/cmip6-x0.25_climatology_{variables_csv}_climatology_annual_"
        f"{period_code}_median_{scenario_code}_ensemble_all_mean/{geocode}?_format=json"
    )

def fetch_cckp_climatology_means(variables, period_code, scenario_code, geocode):
    """
    Fetch mean climatology values for a given set of variables and state geocode.
    Returns dict {variable: value or None}.
    This function is robust to different JSON payload shapes from the API.
    """
    variables_csv = ",".join(variables)
    url = build_cckp_url(variables_csv, period_code, scenario_code, geocode)
    try:
        time.sleep(0.3)  # be polite
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"API error ({url}): {e}")
        return {v: None for v in variables}

    # Heuristic parsing: try common shapes
    results = {v: None for v in variables}
    try:
        # Case 1a: Nested structure like {'data': {'tas': {'BRA.37689': {'1995-07': 22.7}}, ...}}
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
            for v in variables:
                var_data = data["data"].get(v)
                if isinstance(var_data, dict):
                    # Check if it's nested by geocode
                    if geocode in var_data and isinstance(var_data[geocode], dict):
                        # Extract values from the date-keyed dict
                        date_values = var_data[geocode]
                        if date_values:
                            # Get all numeric values and average them
                            numeric_values = [val for val in date_values.values() if isinstance(val, (int, float))]
                            if numeric_values:
                                results[v] = float(np.nanmean(numeric_values))
                    # Otherwise check if it's a direct value
                    elif isinstance(var_data, (int, float)):
                        results[v] = float(var_data)
                    elif isinstance(var_data, list) and var_data:
                        # average if list of monthly values
                        try:
                            results[v] = float(np.nanmean([x for x in var_data if isinstance(x, (int, float))]))
                        except Exception:
                            pass
                elif isinstance(var_data, (int, float)):
                    results[v] = float(var_data)
                elif isinstance(var_data, list) and var_data:
                    # average if list of monthly values
                    try:
                        results[v] = float(np.nanmean([x for x in var_data if isinstance(x, (int, float))]))
                    except Exception:
                        pass
        # Case 2: list of { 'variable': 'tas', 'mean': 23.4 } or {'value': ...}
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                var = item.get("variable") or item.get("name")
                if var in variables:
                    val = item.get("mean") or item.get("value") or item.get("annual_mean")
                    if isinstance(val, (int, float)):
                        results[var] = float(val)
                    elif isinstance(val, list) and val:
                        try:
                            results[var] = float(np.nanmean([x for x in val if isinstance(x, (int, float))]))
                        except Exception:
                            pass
        # Fallback: flat dict with variables as keys
        elif isinstance(data, dict):
            for v in variables:
                val = data.get(v)
                if isinstance(val, (int, float)):
                    results[v] = float(val)
                elif isinstance(val, list) and val:
                    try:
                        results[v] = float(np.nanmean([x for x in val if isinstance(x, (int, float))]))
                    except Exception:
                        pass
    except Exception as e:
        print(f"Unexpected JSON shape from CCKP for {geocode}: {e}")

    return results

def calculate_climate_likelihood_state(geocode):
    """
    Calculates a simple 'Climate Risk Likelihood' score (1-5) for a state geocode,
    based on change between baseline (1995-2014, historical) and future (2040-2059, ssp585).
    Uses variables: tas (°C), tasmax (°C), pr (mm).
    """
    risk_score = 0

    variables = ["tas", "tasmax", "pr"]

    baseline = fetch_cckp_climatology_means(
        variables=variables,
        period_code="1995-2014",
        scenario_code="historical",
        geocode=geocode,
    )
    future = fetch_cckp_climatology_means(
        variables=variables,
        period_code="2040-2059",
        scenario_code="ssp585",
        geocode=geocode,
    )

    # Temperature (tas)
    hist_temp = baseline.get("tas")
    fut_temp = future.get("tas")
    if hist_temp is not None and fut_temp is not None:
        change_temp = fut_temp - hist_temp
        print(f"  > Projected change in avg temp (tas): {change_temp:.2f}°C")
        if change_temp > 2.5:
            risk_score += 2
        elif change_temp > 1.5:
            risk_score += 1
    else:
        print(f"  WARNING: Temperature (tas) data unavailable (baseline={hist_temp}, future={fut_temp})")

    # Max Temperature (tasmax)
    hist_tasmax = baseline.get("tasmax")
    fut_tasmax = future.get("tasmax")
    if hist_tasmax is not None and fut_tasmax is not None:
        change_tasmax = fut_tasmax - hist_tasmax
        print(f"  > Projected change in max temp (tasmax): {change_tasmax:.2f}°C")
        if change_tasmax > 3.5:
            risk_score += 2
        elif change_tasmax > 2.0:
            risk_score += 1
    else:
        print(f"  WARNING: Max temperature (tasmax) data unavailable (baseline={hist_tasmax}, future={fut_tasmax})")

    # Precipitation (pr)
    hist_pr = baseline.get("pr")
    fut_pr = future.get("pr")
    if hist_pr is not None and fut_pr is not None and hist_pr != 0:
        percent_change_rain = ((fut_pr - hist_pr) / hist_pr) * 100.0
        print(f"  > Projected change in rainfall (pr): {percent_change_rain:.1f}%")
        if abs(percent_change_rain) > 20:
            risk_score += 2
        elif abs(percent_change_rain) > 10:
            risk_score += 1
    else:
        print(f"  WARNING: Precipitation (pr) data unavailable (baseline={hist_pr}, future={fut_pr})")

    return min(risk_score, 5)

# --- 4. MAIN ANALYSIS SCRIPT ---

def run_analysis(locations, location_type):
    """
    Main function to run the analysis for a list of locations.
    """
    results = []
    
    for location, data in locations.items():
        print(f"\nAnalyzing {location_type}: {location}")
        
        # In the supplier dict, data is just the impact float.
        # In the client dict, data is a dict {'impact_percent': float}
        if isinstance(data, dict):
            impact_percent = data["impact_percent"]
        else:
            impact_percent = data

        # Extract UF (state) from "CITY/UF"
        _, uf = parse_city_and_state(location)
        geocode = get_state_geocode(uf) if uf else None
        if not geocode:
            print(f"Warning: Could not map state for {location}. Skipping.")
            continue
        
        # This is the "L" (Likelihood) in your L x I formula
        likelihood_score = calculate_climate_likelihood_state(geocode)
        
        # This is the "I" (Impact)
        # We scale 5% impact (0.05) to a 1-5 scale (0.05 * 100 = 5)
        # This assumes 1% = 1 point on a 100-pt scale.
        # A 5% client is an impact of 5. A 20% client is an impact of 20.
        impact_score = impact_percent * 100 
        
        # The final Integrated Risk Score
        weighted_risk_score = likelihood_score * impact_score
        
        results.append({
            "Location": location,
            "Type": location_type,
            "State UF": uf,
            "State Geocode": geocode,
            "Impact (I)": impact_score,
            "Climate Likelihood (L)": likelihood_score,
            "Weighted Risk Score (L x I)": weighted_risk_score
        })
        
    return pd.DataFrame(results)

# --- 5. NEW: SENSITIVITY ANALYSIS ---

def run_sensitivity_analysis(baseline_results_df):
    """
    Runs a simple sensitivity analysis.
    It takes your highest-risk client and shows what happens if
    their impact on your business is 50% higher than you thought.
    """
    print("\n\n--- 🔬 🔬 SENSITIVITY ANALYSIS 🔬 🔬 ---")
    
    # Find the top-ranked client from the baseline results
    client_results = baseline_results_df[baseline_results_df['Type'] == 'Client (Royalty)'].copy()
    if client_results.empty:
        print("No client data to analyze.")
        return
        
    top_client = client_results.iloc[0]
    
    print(f"Running sensitivity test on your top-ranked client: {top_client['Location']}")
    print(f"Baseline Impact (I): {top_client['Impact (I)']:.2f}")
    print(f"Baseline Weighted Risk: {top_client['Weighted Risk Score (L x I)']:.2f}")

    # Create a new "stressed" DataFrame
    stressed_results_df = baseline_results_df.copy()
    
    # Get the index of the top client
    top_client_index = stressed_results_df.index[
        (stressed_results_df['Location'] == top_client['Location']) &
        (stressed_results_df['Type'] == 'Client (Royalty)')
    ].tolist()[0]

    # STRESS: Increase the impact of this client by 50%
    stressed_impact = top_client['Impact (I)'] * 1.50
    stressed_likelihood = top_client['Climate Likelihood (L)']
    stressed_risk_score = stressed_likelihood * stressed_impact
    
    # Update the 'stressed' DataFrame
    stressed_results_df.loc[top_client_index, 'Impact (I)'] = stressed_impact
    stressed_results_df.loc[top_client_index, 'Weighted Risk Score (L x I)'] = stressed_risk_score

    print(f"\nSTRESSED Impact (I) (+50%): {stressed_impact:.2f}")
    print(f"STRESSED Weighted Risk: {stressed_risk_score:.2f}")
    
    # Re-sort the DataFrame to see if the ranking changed
    stressed_results_df = stressed_results_df.sort_values(by="Weighted Risk Score (L x I)", ascending=False)
    
    print("\n--- New 'Stressed' Risk Ranking ---")
    print(stressed_results_df.head(10))
    print("...")
    
    # Check if the top risk is still the same
    if stressed_results_df.iloc[0]['Location'] == top_client['Location']:
        print(f"\nAnalysis: {top_client['Location']} remains your #1 risk.")
    else:
        new_top_risk = stressed_results_df.iloc[0]['Location']
        print(f"\nAnalysis: Increasing {top_client['Location']}'s impact by 50% makes {new_top_risk} your new #1 risk.")
    
    print("This shows how sensitive your risk profile is to your assumptions about client importance.")


if __name__ == "__main__":
    print("--- Running Sugarcane Risk Analysis ---")
    print("This script will fetch live data from the World Bank CCKP v1 API (state-level).")
    print("It may take several minutes due to API calls and rate limiting.\n")
    
    # Run analysis for clients
    client_results_df = run_analysis(CLIENT_LOCATIONS, "Client (Royalty)")
    
    # Run analysis for suppliers
    # We create a dummy dict for suppliers to match the client structure
    supplier_locations_dict = {loc: {'impact_percent': impact} for loc, impact in SUPPLIER_LOCATIONS.items()}
    supplier_results_df = run_analysis(supplier_locations_dict, "Supplier (Seedling)")
    
    # Combine and show results
    final_results = pd.concat([client_results_df, supplier_results_df]).sort_values(
        by="Weighted Risk Score (L x I)", ascending=False
    )
    
    print("\n\n--- ☀️ 🌴 FINAL RISK ANALYSIS REPORT 🌴 ☀️ ---")
    print("Higher 'Weighted Risk Score' means a higher priority for you.")
    print("This score integrates your Business Impact (I) with Climate Likelihood (L).")
    
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print(final_results)
    
    print("\n--- End of Report ---")
    
    # Run the new sensitivity analysis
    run_sensitivity_analysis(final_results)