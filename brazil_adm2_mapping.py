"""
Brazilian Municipality to ThinkHazard ADM2 Code Mapping
Maps Brazilian municipalities to administrative division codes for ThinkHazard API
"""

import requests
import time
from typing import Optional, Dict
import json

# Cache for ADM2 lookups to avoid repeated API calls
_adm2_cache: Dict[str, Optional[str]] = {}

# Manual lookup table for major Brazilian municipalities
# Format: "CITY/STATE" -> ADM2 code
# Note: ThinkHazard uses GAUL administrative boundaries
# These may need to be updated based on actual ThinkHazard data availability

# For Brazilian states, we'll use ADM1 (state-level) codes if ADM2 (municipality) is not available
# ThinkHazard codes for Brazilian states (ADM0 = 188 for Brazil)
BRAZIL_STATE_ADM_CODES = {
    "SP": "3598",  # São Paulo state - example, needs verification
    "GO": "3571",  # Goiás
    "MS": "3583",  # Mato Grosso do Sul
    "PR": "3594",  # Paraná
    "MG": "3582",  # Minas Gerais
    "MT": "3584",  # Mato Grosso
    "AL": "3559",  # Alagoas
    "PB": "3591",  # Paraíba
}

# Known municipality ADM2 codes (to be populated based on ThinkHazard data)
# This is a starter list - will be expanded with actual codes from API
MUNICIPALITY_ADM2_CODES = {
    # São Paulo municipalities
    "PIRACICABA/SP": None,  # To be discovered via API
    "NOVO HORIZONTE/SP": None,
    "SERRA AZUL/SP": None,
    "SÃO JOAQUIM DA BARRA/SP": None,
    "CHAVANTES/SP": None,
    "CESÁRIO LANGE/SP": None,
    "SERTÃOZINHO/SP": None,
    "ITAPURA/SP": None,
    "PENÁPOLIS/SP": None,
    "GUARAÇAÍ/SP": None,
    "OLÍMPIA/SP": None,
    "RANCHARIA/SP": None,
    "BARRINHA/SP": None,
    "VALPARAÍSO/SP": None,
    
    # Goiás municipalities
    "QUIRINÓPOLIS/GO": None,
    "VILA PROPÍCIO/GO": None,
    "JATAÍ/GO": None,
    "MINEIROS/GO": None,
    
    # Other states
    "CAARAPÓ/MS": None,
    "COLORADO/PR": None,
    "MANDAGUAÇU/PR": None,
    "ITURAMA/MG": None,
    "BARRA DO BUGRES/MT": None,
    "CORURIPE/AL": None,
    "SANTA RITA/PB": None,
}


def normalize_location_name(location: str) -> str:
    """
    Normalize location name for consistent lookups
    Handles special characters in Brazilian city names
    """
    # Remove extra spaces
    location = " ".join(location.split())
    # Convert to uppercase for consistency
    location = location.upper()
    return location


def parse_city_and_state(location_name: str) -> tuple:
    """
    Parse location string into city and state components
    Example: "PIRACICABA/SP" -> ("PIRACICABA", "SP")
    """
    if "/" in location_name:
        city, state_abbrev = location_name.split("/", 1)
        return city.strip(), state_abbrev.strip()
    return location_name.strip(), None


def search_thinkhazard_division(location_name: str, timeout: int = 30) -> Optional[str]:
    """
    Search ThinkHazard for a division code by location name
    This uses the ThinkHazard search functionality
    
    Note: ThinkHazard may not have detailed ADM2 data for all Brazilian municipalities.
    In that case, we fall back to state-level (ADM1) data.
    """
    city, state_abbrev = parse_city_and_state(location_name)
    
    if not city or not state_abbrev:
        return None
    
    try:
        # Try searching for the municipality
        # Note: This is a hypothetical endpoint - adjust based on actual ThinkHazard API
        search_url = f"https://thinkhazard.org/en/search?q={city}%20{state_abbrev}%20Brazil"
        
        time.sleep(0.5)  # Rate limiting
        
        # For now, return state-level code as fallback
        # In production, you'd parse the search results
        state_code = BRAZIL_STATE_ADM_CODES.get(state_abbrev)
        
        if state_code:
            print(f"  Using state-level code for {location_name}: {state_code}")
            return state_code
        
        return None
        
    except Exception as e:
        print(f"Error searching ThinkHazard for {location_name}: {e}")
        return None


def get_adm2_code(location_name: str, use_cache: bool = True) -> Optional[str]:
    """
    Get ADM2 (or ADM1) code for a Brazilian municipality
    
    Strategy:
    1. Check cache
    2. Check manual lookup table
    3. Extract state and use state-level code
    4. Search ThinkHazard API (if needed)
    
    Args:
        location_name: Location string like "PIRACICABA/SP"
        use_cache: Whether to use cached results
    
    Returns:
        ADM code string or None if not found
    """
    normalized_name = normalize_location_name(location_name)
    
    # Check cache
    if use_cache and normalized_name in _adm2_cache:
        return _adm2_cache[normalized_name]
    
    # Check manual lookup table
    if normalized_name in MUNICIPALITY_ADM2_CODES and MUNICIPALITY_ADM2_CODES[normalized_name]:
        adm_code = MUNICIPALITY_ADM2_CODES[normalized_name]
        _adm2_cache[normalized_name] = adm_code
        return adm_code
    
    # Extract state and use state-level code as fallback
    city, state_abbrev = parse_city_and_state(normalized_name)
    
    if state_abbrev and state_abbrev in BRAZIL_STATE_ADM_CODES:
        adm_code = BRAZIL_STATE_ADM_CODES[state_abbrev]
        _adm2_cache[normalized_name] = adm_code
        return adm_code
    
    # Last resort: search API
    adm_code = search_thinkhazard_division(normalized_name)
    _adm2_cache[normalized_name] = adm_code
    
    return adm_code


def get_brazil_adm0_code() -> str:
    """
    Get the ADM0 (country-level) code for Brazil
    """
    return "188"  # Brazil's country code in ThinkHazard


def save_cache_to_file(filepath: str = "adm2_cache.json"):
    """
    Save the ADM2 cache to a file for persistence
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(_adm2_cache, f, indent=2, ensure_ascii=False)
        print(f"ADM2 cache saved to {filepath}")
    except Exception as e:
        print(f"Error saving cache: {e}")


def load_cache_from_file(filepath: str = "adm2_cache.json"):
    """
    Load the ADM2 cache from a file
    """
    global _adm2_cache
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            _adm2_cache = json.load(f)
        print(f"ADM2 cache loaded from {filepath}: {len(_adm2_cache)} entries")
    except FileNotFoundError:
        print(f"No cache file found at {filepath}")
    except Exception as e:
        print(f"Error loading cache: {e}")

