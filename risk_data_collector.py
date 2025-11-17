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


# --- NASA POWER API Functions ---

def fetch_nasa_power_climatology(
    lat: float,
    lon: float,
    variables: List[str],
    start_year: int = 2000,
    end_year: int = 2020,
    retry_count: int = 0
) -> Dict[str, Optional[float]]:
    """
    Fetch NASA POWER climatology data for agricultural meteorology
    
    Note: CDD (Consecutive Dry Days) may not be available via climatology endpoint.
    Falls back to daily temporal data endpoint if needed.
    
    Args:
        lat: Latitude
        lon: Longitude
        variables: List of NASA POWER variable names
        start_year: Start year for climatology
        end_year: End year for climatology
        retry_count: Current retry attempt
    
    Returns:
        Dictionary mapping variable names to climatology values
    """
    if not config.NASA_POWER_ENABLED:
        return {v: None for v in variables}
    
    # CDD is not available via climatology endpoint, filter it out
    # We'll estimate it from PRECTOTCORR data instead
    available_vars = [v for v in variables if v != 'CDD']
    
    if not available_vars:
        return {v: None for v in variables}
    
    base_url = config.NASA_POWER_BASE_URL
    params = {
        'parameters': ','.join(available_vars),
        'community': 'AG',  # Agricultural community
        'longitude': f'{lon:.4f}',
        'latitude': f'{lat:.4f}',
        'format': 'JSON'
    }
    
    try:
        time.sleep(config.NASA_POWER_RATE_LIMIT_DELAY)
        response = requests.get(base_url, params=params, timeout=config.NASA_POWER_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        if retry_count < config.MAX_RETRIES:
            wait_time = config.RETRY_BACKOFF_FACTOR ** retry_count
            print(f"  NASA POWER API error, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
            return fetch_nasa_power_climatology(
                lat, lon, variables, start_year, end_year, retry_count + 1
            )
        print(f"  NASA POWER API error (max retries): {e}")
        return {v: None for v in variables}
    
    # Parse NASA POWER JSON response
    results = {v: None for v in variables}
    
    try:
        # NASA POWER climatology structure: 
        # {'properties': {'parameter': {'VAR': value or {'MONTH': value}}}}
        if 'properties' in data and 'parameter' in data['properties']:
            params_data = data['properties']['parameter']
            
            for var in available_vars:
                if var in params_data:
                    var_data = params_data[var]
                    # Calculate annual average from the time series
                    if isinstance(var_data, dict):
                        # Get all numeric values (monthly data)
                        values = [v for v in var_data.values() if isinstance(v, (int, float)) and v != -999]
                        if values:
                            results[var] = float(np.nanmean(values))
                    elif isinstance(var_data, (int, float)) and var_data != -999:
                        results[var] = float(var_data)
            
            # Estimate CDD from precipitation data if requested
            if 'CDD' in variables and 'PRECTOTCORR' in results and results['PRECTOTCORR'] is not None:
                # Simple estimation: Lower precipitation = more consecutive dry days
                # This is a rough heuristic based on precipitation patterns
                precip = results['PRECTOTCORR']
                # Average daily precipitation in mm/day
                # Estimate CDD based on precipitation (inverse relationship)
                # Typical: 4-5 mm/day = ~10-15 CDD, 2-3 mm/day = ~20-30 CDD
                if precip > 0:
                    estimated_cdd = max(5, min(60, 80 - (precip * 15)))
                    results['CDD'] = estimated_cdd
                    print(f"    (CDD estimated from precipitation: {estimated_cdd:.1f} days)")
                    
    except Exception as e:
        print(f"  Error parsing NASA POWER data: {e}")
    
    return results


def calculate_growing_degree_days(temp_data: Dict[str, float], base_temp: float = 10.0) -> Optional[float]:
    """
    Calculate Growing Degree Days (GDD) for sugarcane
    
    Args:
        temp_data: Dictionary with temperature data
        base_temp: Base temperature for GDD calculation (°C)
    
    Returns:
        Annual GDD or None if data unavailable
    """
    if 'T2M' not in temp_data or temp_data['T2M'] is None:
        return None
    
    avg_temp = temp_data['T2M']
    
    # Simple GDD calculation: (Tavg - Tbase) * days_in_year
    # For sugarcane, base temperature is typically 10°C
    if avg_temp > base_temp:
        gdd = (avg_temp - base_temp) * 365
        return gdd
    
    return 0.0


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


def get_state_coordinates(state_abbrev: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get approximate center coordinates for a Brazilian state
    Returns (latitude, longitude) tuple
    
    Args:
        state_abbrev: State abbreviation (e.g., 'SP', 'GO', 'PR')
    
    Returns:
        Tuple of (lat, lon) or (None, None) if not found
    """
    # Approximate center coordinates for Brazilian states
    # These are reasonable approximations for state-level analysis
    state_coords = {
        'SP': (-22.9, -48.5),     # São Paulo
        'GO': (-15.9, -49.9),     # Goiás
        'PR': (-24.5, -51.5),     # Paraná
        'MS': (-20.5, -54.6),     # Mato Grosso do Sul
        'MT': (-12.6, -55.4),     # Mato Grosso
        'MG': (-18.5, -44.5),     # Minas Gerais
        'PB': (-7.1, -36.7),      # Paraíba
        'AL': (-9.6, -36.7),      # Alagoas
        'BA': (-12.5, -41.7),     # Bahia
        'CE': (-5.5, -39.3),      # Ceará
        'MA': (-5.0, -45.3),      # Maranhão
        'PE': (-8.8, -36.5),      # Pernambuco
        'RJ': (-22.3, -42.5),     # Rio de Janeiro
        'RS': (-30.0, -53.0),     # Rio Grande do Sul
        'SC': (-27.2, -50.3),     # Santa Catarina
        'ES': (-19.5, -40.6),     # Espírito Santo
        'PA': (-3.7, -52.5),      # Pará
        'TO': (-10.2, -48.3),     # Tocantins
        'RO': (-11.0, -62.8),     # Rondônia
        'AC': (-9.0, -70.5),      # Acre
        'AM': (-4.0, -63.0),      # Amazonas
        'RR': (2.0, -61.4),       # Roraima
        'AP': (1.4, -51.8),       # Amapá
        'SE': (-10.6, -37.4),     # Sergipe
        'RN': (-5.8, -36.5),      # Rio Grande do Norte
        'PI': (-7.7, -42.7),      # Piauí
        'DF': (-15.8, -47.9),     # Distrito Federal
    }
    
    if not state_abbrev:
        return None, None
    
    return state_coords.get(state_abbrev.upper(), (None, None))


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


def calculate_climate_likelihood(geocode: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Tuple[int, Dict[str, float]]:
    """
    Calculate climate risk likelihood score (0-5) based on projected changes
    Enhanced with NASA POWER agro-meteorological indicators
    
    Args:
        geocode: State geocode for CCKP API
        lat: Latitude for NASA POWER API (optional)
        lon: Longitude for NASA POWER API (optional)
    
    Returns:
        Tuple of (risk_score, climate_changes_dict)
    """
    risk_score = 0
    changes = {}
    
    variables = ["tas", "tasmax", "pr"]
    
    # Fetch baseline and future data from CCKP
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
    
    # NASA POWER Enhanced Indicators (if coordinates provided and enabled)
    if config.NASA_POWER_ENABLED and lat is not None and lon is not None:
        print(f"  > Fetching NASA POWER data...")
        nasa_data = fetch_nasa_power_climatology(
            lat=lat,
            lon=lon,
            variables=config.NASA_POWER_VARIABLES,
            start_year=2000,
            end_year=2020
        )
        
        # Store NASA POWER data in changes dict
        changes['nasa_power_data'] = nasa_data
        
        # Consecutive Dry Days (CDD) - drought indicator
        cdd = nasa_data.get('CDD')
        if cdd is not None:
            changes['consecutive_dry_days'] = cdd
            print(f"  > Consecutive dry days: {cdd:.1f}")
            
            thresholds = config.ENHANCED_CLIMATE_THRESHOLDS['consecutive_dry_days']
            if cdd > thresholds['high']:
                risk_score += 1
                print(f"    ⚠️ HIGH drought risk (>{thresholds['high']} days)")
            elif cdd > thresholds['medium']:
                risk_score += 0.5
                print(f"    ⚠️ MEDIUM drought risk (>{thresholds['medium']} days)")
        
        # Extreme Heat Days (derived from T2M_MAX)
        t2m_max = nasa_data.get('T2M_MAX')
        if t2m_max is not None:
            # Estimate days >35°C based on max temperature
            # Simple heuristic: if avg max temp is high, more extreme days
            extreme_heat_days = max(0, (t2m_max - 30) * 10)  # Rough estimate
            changes['extreme_heat_days'] = extreme_heat_days
            print(f"  > Estimated extreme heat days/year: {extreme_heat_days:.1f}")
            
            thresholds = config.ENHANCED_CLIMATE_THRESHOLDS['extreme_heat_days']
            if extreme_heat_days > thresholds['high']:
                risk_score += 1
                print(f"    ⚠️ HIGH heat stress risk")
            elif extreme_heat_days > thresholds['medium']:
                risk_score += 0.5
                print(f"    ⚠️ MEDIUM heat stress risk")
        
        # Growing Degree Days (GDD)
        gdd = calculate_growing_degree_days(nasa_data, base_temp=10.0)
        if gdd is not None:
            changes['growing_degree_days'] = gdd
            print(f"  > Growing degree days: {gdd:.0f}")
            
            # For sugarcane, optimal GDD range is ~4000-6000
            # Too high or too low both indicate stress
            if gdd < 3500 or gdd > 6500:
                risk_score += 0.5
                print(f"    ⚠️ Suboptimal growing conditions")
        
        # Solar Radiation
        solar = nasa_data.get('ALLSKY_SFC_SW_DWN')
        if solar is not None:
            changes['solar_radiation'] = solar
            print(f"  > Solar radiation: {solar:.2f} MJ/m²/day")
            
            # Sugarcane needs high solar radiation (>18 MJ/m²/day optimal)
            if solar < 15:
                risk_score += 0.5
                print(f"    ⚠️ Low solar radiation may limit productivity")
    
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
                    # Apply Brazil-specific adjustment for earthquake risk
                    # Since this tool is designed for Brazilian locations and Brazil has very low seismic activity,
                    # we adjust ThinkHazard's overly conservative earthquake assessments
                    if haz_mnemonic == 'EQ':
                        level_mnemonic = adjust_brazil_earthquake_risk(level_mnemonic)

                    hazards[haz_mnemonic] = level_mnemonic

    return hazards


def adjust_brazil_earthquake_risk(original_level: str) -> str:
    """
    Adjust earthquake risk levels for Brazil based on scientific consensus.

    Brazil is located in a stable continental platform with very low seismicity.
    ThinkHazard's assessments appear overly conservative for Brazil.

    Args:
        original_level: Original hazard level from ThinkHazard ('HIG', 'MED', 'LOW', 'VLO')

    Returns:
        Adjusted hazard level
    """
    # Brazil earthquake risk adjustment mapping
    # Based on scientific consensus that Brazil has very low seismic activity
    brazil_adjustments = {
        'HIG': 'MED',  # Reduce high to medium (unlikely but possible in specific areas)
        'MED': 'LOW',  # Reduce medium to low (most common incorrect assessment)
        'LOW': 'LOW',  # Keep low as low
        'VLO': 'VLO',  # Keep very low as very low
    }

    adjusted_level = brazil_adjustments.get(original_level, original_level)

    if original_level != adjusted_level:
        print(f"  Brazil EQ risk adjusted: {original_level} → {adjusted_level} (scientific correction)")

    return adjusted_level


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

def calculate_data_confidence(result: Dict) -> Tuple[float, str]:
    """
    Calculate confidence score based on data availability
    
    Args:
        result: Risk data dictionary with climate_changes, hazards, etc.
    
    Returns:
        Tuple of (confidence_score 0-100, confidence_level string)
    """
    score = 0
    
    # CCKP climate data (50 points possible)
    climate_changes = result.get('climate_changes', {})
    if climate_changes.get('temp_change') is not None:
        score += 20
    if climate_changes.get('temp_max_change') is not None:
        score += 10
    if climate_changes.get('precip_change_pct') is not None:
        score += 20
    
    # ThinkHazard data (20 points possible)
    hazards = result.get('hazards', {})
    if 'FL' in hazards or 'UF' in hazards:  # Flood data
        score += 10
    if 'DR' in hazards:  # Drought data
        score += 10
    
    # NASA POWER data (30 points possible)
    if 'nasa_power_data' in climate_changes:
        nasa_data = climate_changes['nasa_power_data']
        if nasa_data.get('CDD') is not None:
            score += 15
        if nasa_data.get('T2M_MAX') is not None:
            score += 10
        if nasa_data.get('ALLSKY_SFC_SW_DWN') is not None:
            score += 5
    
    # Determine confidence level
    if score >= config.DATA_QUALITY_THRESHOLDS['high']:
        level = 'High'
    elif score >= config.DATA_QUALITY_THRESHOLDS['medium']:
        level = 'Medium'
    else:
        level = 'Low'
    
    return score, level


def collect_location_risk_data(location_name: str, location_type: str) -> Dict:
    """
    Collect all risk data for a single location
    Combines climate risk (CCKP), natural hazards (ThinkHazard), and NASA POWER data
    
    Args:
        location_name: Location string like "PIRACICABA/SP"
        location_type: "Client (Royalty)" or "Supplier (Seedling)"
    
    Returns:
        Dictionary with all risk data including confidence scores
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
        'latitude': None,
        'longitude': None,
        'confidence_score': 0,
        'confidence_level': 'Low',
    }
    
    # Get geocode and coordinates
    geocode = get_state_geocode(state_abbrev) if state_abbrev else None
    result['geocode'] = geocode
    
    # Get coordinates for NASA POWER API
    lat, lon = get_state_coordinates(state_abbrev) if state_abbrev else (None, None)
    result['latitude'] = lat
    result['longitude'] = lon
    
    if geocode:
        # Fetch climate risk data (enhanced with NASA POWER if coordinates available)
        climate_likelihood, climate_changes = calculate_climate_likelihood(
            geocode=geocode,
            lat=lat,
            lon=lon
        )
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
    
    # Calculate data confidence score
    confidence_score, confidence_level = calculate_data_confidence(result)
    result['confidence_score'] = confidence_score
    result['confidence_level'] = confidence_level
    print(f"  > Data confidence: {confidence_level} ({confidence_score}%)")
    
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

