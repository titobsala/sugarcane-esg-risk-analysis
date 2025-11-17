"""
Risk Data Collector
Unified API integration for World Bank CCKP and ThinkHazard APIs
Handles climate risk and natural hazard data collection
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import requests
import numpy as np

# Local imports
import config
import brazil_adm2_mapping as adm2

# Load geonames for state geocodes
GEONAMES_PATH = Path(__file__).parent / "geonames.json"


def load_brazil_state_name_to_code() -> Dict[str, str]:
    """
    Load Brazil state name to geocode mapping from geonames.json
    Returns dict like {"Sao Paulo": "BRA.37689", ...}
    """
    try:
        with open(GEONAMES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        states = data["country"]["BRA"]["S"]
        # Invert: code -> name to name -> code
        name_to_code = {v: k for k, v in states.items()}
        return name_to_code
    except Exception as e:
        print(f"Error loading geonames.json: {e}")
        return {}


BRAZIL_STATE_NAME_TO_CODE = load_brazil_state_name_to_code()


# --- CCKP API Functions ---

def parse_city_and_state(location_name: str) -> Tuple[str, Optional[str]]:
    """
    Parse location string like 'PIRACICABA/SP' into ('PIRACICABA', 'SP')
    """
    if "/" in location_name:
        city, state_abbrev = location_name.split("/", 1)
        return city.strip(), state_abbrev.strip()
    return location_name.strip(), None


def get_state_geocode(state_abbrev: str) -> Optional[str]:
    """
    Get state geocode for CCKP API from state abbreviation
    Example: 'SP' -> 'BRA.37689'
    """
    if not state_abbrev:
        return None
    state_name = config.BRAZIL_STATE_ABBREV_TO_NAME.get(state_abbrev.upper())
    if not state_name:
        return None
    return BRAZIL_STATE_NAME_TO_CODE.get(state_name)


def build_cckp_url(variables_csv: str, period_code: str, scenario_code: str, geocode: str) -> str:
    """
    Build CCKP v1 API URL for climatology annual means
    """
    return (
        f"{config.CCKP_BASE_URL}/cmip6-x0.25_climatology_{variables_csv}_climatology_annual_"
        f"{period_code}_median_{scenario_code}_ensemble_all_mean/{geocode}?_format=json"
    )


def fetch_cckp_climatology_means(
    variables: List[str], 
    period_code: str, 
    scenario_code: str, 
    geocode: str,
    retry_count: int = 0
) -> Dict[str, Optional[float]]:
    """
    Fetch mean climatology values from CCKP API
    
    Args:
        variables: List of climate variables (e.g., ['tas', 'tasmax', 'pr'])
        period_code: Time period (e.g., '1995-2014')
        scenario_code: Climate scenario (e.g., 'historical', 'ssp585')
        geocode: Geographic code (e.g., 'BRA.37689')
        retry_count: Current retry attempt
    
    Returns:
        Dictionary mapping variable names to values
    """
    variables_csv = ",".join(variables)
    url = build_cckp_url(variables_csv, period_code, scenario_code, geocode)
    
    try:
        time.sleep(config.CCKP_RATE_LIMIT_DELAY)
        resp = requests.get(url, timeout=config.CCKP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        if retry_count < config.MAX_RETRIES:
            wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
            print(f"  CCKP API error, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
            return fetch_cckp_climatology_means(
                variables, period_code, scenario_code, geocode, retry_count + 1
            )
        print(f"  CCKP API error (max retries): {e}")
        return {v: None for v in variables}
    
    # Parse the nested JSON structure
    results = {v: None for v in variables}
    
    try:
        # Structure: {'data': {'tas': {'BRA.37689': {'1995-07': 22.7}}, ...}}
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
            for v in variables:
                var_data = data["data"].get(v)
                if isinstance(var_data, dict):
                    # Check if nested by geocode
                    if geocode in var_data and isinstance(var_data[geocode], dict):
                        # Extract values from date-keyed dict
                        date_values = var_data[geocode]
                        if date_values:
                            numeric_values = [
                                val for val in date_values.values() 
                                if isinstance(val, (int, float))
                            ]
                            if numeric_values:
                                results[v] = float(np.nanmean(numeric_values))
                    # Direct value
                    elif isinstance(var_data, (int, float)):
                        results[v] = float(var_data)
                    elif isinstance(var_data, list) and var_data:
                        try:
                            results[v] = float(np.nanmean([
                                x for x in var_data if isinstance(x, (int, float))
                            ]))
                        except Exception:
                            pass
                elif isinstance(var_data, (int, float)):
                    results[v] = float(var_data)
    except Exception as e:
        print(f"  Error parsing CCKP data for {geocode}: {e}")
    
    return results


def calculate_climate_likelihood(geocode: str) -> Tuple[int, Dict[str, float]]:
    """
    Calculate climate risk likelihood score (0-5) based on projected changes
    
    Args:
        geocode: State geocode for CCKP API
    
    Returns:
        Tuple of (risk_score, climate_changes_dict)
    """
    risk_score = 0
    changes = {}
    
    variables = ["tas", "tasmax", "pr"]
    
    # Fetch baseline and future data
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
        changes['temp_change'] = change_temp
        print(f"  > Temp change: {change_temp:.2f}°C")
        
        thresholds = config.CLIMATE_RISK_THRESHOLDS['temp_change']
        if change_temp > thresholds['high']:
            risk_score += 2
        elif change_temp > thresholds['medium']:
            risk_score += 1
    
    # Max Temperature (tasmax)
    hist_tasmax = baseline.get("tasmax")
    fut_tasmax = future.get("tasmax")
    if hist_tasmax is not None and fut_tasmax is not None:
        change_tasmax = fut_tasmax - hist_tasmax
        changes['temp_max_change'] = change_tasmax
        print(f"  > Max temp change: {change_tasmax:.2f}°C")
        
        thresholds = config.CLIMATE_RISK_THRESHOLDS['temp_max_change']
        if change_tasmax > thresholds['high']:
            risk_score += 2
        elif change_tasmax > thresholds['medium']:
            risk_score += 1
    
    # Precipitation (pr)
    hist_pr = baseline.get("pr")
    fut_pr = future.get("pr")
    if hist_pr is not None and fut_pr is not None and hist_pr != 0:
        percent_change_rain = ((fut_pr - hist_pr) / hist_pr) * 100.0
        changes['precip_change_pct'] = percent_change_rain
        print(f"  > Rainfall change: {percent_change_rain:.1f}%")
        
        thresholds = config.CLIMATE_RISK_THRESHOLDS['precipitation_change']
        if abs(percent_change_rain) > thresholds['high']:
            risk_score += 2
        elif abs(percent_change_rain) > thresholds['medium']:
            risk_score += 1
    
    return min(risk_score, 5), changes


# --- ThinkHazard API Functions ---

def fetch_thinkhazard_report(division_code: str, retry_count: int = 0) -> Optional[Dict]:
    """
    Fetch hazard report from ThinkHazard API for a division
    
    Args:
        division_code: ADM division code
        retry_count: Current retry attempt
    
    Returns:
        Dictionary with hazard levels or None
    """
    url = f"{config.THINKHAZARD_BASE_URL}/report/{division_code}.json"
    
    try:
        time.sleep(config.THINKHAZARD_RATE_LIMIT_DELAY)
        resp = requests.get(url, timeout=config.THINKHAZARD_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        if retry_count < config.MAX_RETRIES:
            wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
            print(f"  ThinkHazard API error, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
            return fetch_thinkhazard_report(division_code, retry_count + 1)
        print(f"  ThinkHazard API error (max retries): {e}")
        return None


def parse_thinkhazard_hazards(report_data: Optional[Dict]) -> Dict[str, str]:
    """
    Parse ThinkHazard report to extract hazard levels
    
    Args:
        report_data: JSON response from ThinkHazard API
    
    Returns:
        Dictionary mapping hazard types to levels
        Example: {'FL': 'HIG', 'EQ': 'MED', 'LS': 'LOW', ...}
    """
    hazards = {}
    
    if not report_data or not isinstance(report_data, list):
        return hazards
    
    # ThinkHazard returns list of hazard objects
    for item in report_data:
        if isinstance(item, dict):
            hazard_type = item.get('hazardtype', {})
            hazard_level = item.get('hazardlevel', {})
            
            if isinstance(hazard_type, dict) and isinstance(hazard_level, dict):
                haz_mnemonic = hazard_type.get('mnemonic')
                level_mnemonic = hazard_level.get('mnemonic')
                
                if haz_mnemonic and level_mnemonic:
                    hazards[haz_mnemonic] = level_mnemonic
    
    return hazards


def calculate_hazard_severity(hazards: Dict[str, str]) -> Tuple[int, Dict[str, int]]:
    """
    Calculate aggregate hazard severity score from ThinkHazard data
    
    Args:
        hazards: Dictionary mapping hazard types to levels
    
    Returns:
        Tuple of (total_score, individual_scores)
    """
    individual_scores = {}
    total_score = 0
    
    for hazard_type, level in hazards.items():
        score = config.HAZARD_LEVEL_SCORES.get(level, 0)
        individual_scores[hazard_type] = score
        total_score += score
    
    # Normalize to 0-5 scale (assuming max 5 hazards × 3 points each = 15)
    normalized_score = min(int((total_score / 15) * 5), 5) if total_score > 0 else 0
    
    return normalized_score, individual_scores


# --- Combined Data Collection ---

def collect_location_risk_data(location_name: str, location_type: str) -> Dict:
    """
    Collect all risk data for a single location
    Combines climate risk (CCKP) and natural hazards (ThinkHazard)
    
    Args:
        location_name: Location string like "PIRACICABA/SP"
        location_type: "Client (Royalty)" or "Supplier (Seedling)"
    
    Returns:
        Dictionary with all risk data
    """
    print(f"\nAnalyzing {location_type}: {location_name}")
    
    _, state_abbrev = parse_city_and_state(location_name)
    
    # Initialize result
    result = {
        'location': location_name,
        'type': location_type,
        'state': state_abbrev,
        'climate_likelihood': 0,
        'climate_changes': {},
        'hazards': {},
        'hazard_severity': 0,
        'hazard_scores': {},
        'geocode': None,
        'adm_code': None,
    }
    
    # Get geocode for CCKP
    geocode = get_state_geocode(state_abbrev) if state_abbrev else None
    result['geocode'] = geocode
    
    if geocode:
        # Fetch climate risk data
        climate_likelihood, climate_changes = calculate_climate_likelihood(geocode)
        result['climate_likelihood'] = climate_likelihood
        result['climate_changes'] = climate_changes
    else:
        print(f"  Warning: No geocode found for {location_name}")
    
    # Get ADM code for ThinkHazard
    adm_code = adm2.get_adm2_code(location_name)
    result['adm_code'] = adm_code
    
    if adm_code:
        # Fetch hazard data
        hazard_report = fetch_thinkhazard_report(adm_code)
        hazards = parse_thinkhazard_hazards(hazard_report)
        result['hazards'] = hazards
        
        if hazards:
            hazard_severity, hazard_scores = calculate_hazard_severity(hazards)
            result['hazard_severity'] = hazard_severity
            result['hazard_scores'] = hazard_scores
            print(f"  > Hazards detected: {', '.join([f'{k}={v}' for k, v in hazards.items()])}")
    else:
        print(f"  Warning: No ADM code found for {location_name}")
    
    return result


def collect_all_locations_data(
    client_locations: Dict,
    supplier_locations: Dict
) -> List[Dict]:
    """
    Collect risk data for all locations (clients and suppliers)
    
    Args:
        client_locations: Dictionary of client locations
        supplier_locations: Dictionary of supplier locations
    
    Returns:
        List of risk data dictionaries
    """
    all_data = []
    
    # Process clients
    for location, data in client_locations.items():
        if isinstance(data, dict):
            impact_percent = data['impact_percent']
        else:
            impact_percent = data
        
        risk_data = collect_location_risk_data(location, "Client (Royalty)")
        risk_data['impact_percent'] = impact_percent
        all_data.append(risk_data)
    
    # Process suppliers
    for location, impact_percent in supplier_locations.items():
        risk_data = collect_location_risk_data(location, "Supplier (Seedling)")
        risk_data['impact_percent'] = impact_percent
        all_data.append(risk_data)
    
    return all_data

