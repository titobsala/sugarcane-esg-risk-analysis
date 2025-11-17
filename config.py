"""
Configuration file for ESG Risk Analysis Tool
Contains location data, API settings, and risk parameters
"""

import numpy as np

# --- LOCATION DATA ---

# Suppliers (Seedling providers) - Equal impact distribution
SUPPLIER_LOCATIONS = {
    "PIRACICABA/SP": 1.0 / 6.0,
    "BARRINHA/SP": 1.0 / 6.0,
    "VALPARAÍSO/SP": 1.0 / 6.0,
    "QUIRINÓPOLIS/GO": 1.0 / 6.0,
    "MANDAGUAÇU/PR": 1.0 / 6.0,
    "SANTA RITA/PB": 1.0 / 6.0,
}

# Clients (Royalty locations) - Randomized impact distribution
# Note: These will be randomized using Dirichlet distribution at runtime
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
    "ITURAMA/MG": {"impact_percent": 0.01},
    "BARRA DO BUGRES/MT": {"impact_percent": 0.02},
    "CORURIPE/AL": {"impact_percent": 0.01},
    "Pompeu/MG": {"impact_percent": 0.02},
}

# --- API CONFIGURATION ---

# World Bank Climate Change Knowledge Portal (CCKP) API
CCKP_BASE_URL = "https://cckpapi.worldbank.org/cckp/v1"
CCKP_TIMEOUT = 30
CCKP_RATE_LIMIT_DELAY = 0.3  # seconds between requests

# ThinkHazard API
THINKHAZARD_BASE_URL = "https://thinkhazard.org/en"
THINKHAZARD_TIMEOUT = 30
THINKHAZARD_RATE_LIMIT_DELAY = 0.5  # seconds between requests

# NASA POWER API (Phase 2 implementation - ENABLED)
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
NASA_POWER_TIMEOUT = 30
NASA_POWER_RATE_LIMIT_DELAY = 0.5  # seconds between requests
NASA_POWER_ENABLED = True  # Enabled for enhanced climate risk assessment

# NASA POWER Variables to fetch
# See docs/DATA_SOURCES.md for detailed descriptions
NASA_POWER_VARIABLES = [
    'T2M',                  # Temperature at 2 meters (°C)
    'T2M_MAX',              # Maximum Temperature (°C)
    'PRECTOTCORR',          # Precipitation (mm/day)
    'CDD',                  # Consecutive Dry Days (days)
    'ALLSKY_SFC_SW_DWN',    # Solar Radiation (MJ/m²/day)
]

# Note: T2M_MAX_GT35 not always available, will be derived from T2M_MAX data

# API Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff multiplier

# --- RISK SCORING PARAMETERS ---

# Climate Risk Thresholds
CLIMATE_RISK_THRESHOLDS = {
    'temp_change': {
        'high': 2.5,      # °C increase
        'medium': 1.5,
    },
    'temp_max_change': {
        'high': 3.5,      # °C increase in max temp
        'medium': 2.0,
    },
    'precipitation_change': {
        'high': 20,       # % change (absolute value)
        'medium': 10,
    }
}

# Hazard Level to Score Mapping (ThinkHazard)
HAZARD_LEVEL_SCORES = {
    'HIG': 3,      # High
    'MED': 2,      # Medium
    'LOW': 1,      # Low
    'VLO': 0.5,    # Very Low
    None: 0,       # No data
}

# Hazard Weighting by Relevance to Sugarcane (for future enhanced scoring)
HAZARD_WEIGHTS = {
    'FL': 0.30,    # Flood (critical - waterlogging kills crops)
    'DR': 0.30,    # Drought (critical - major yield impact)
    'WF': 0.20,    # Wildfire (high - can destroy crops)
    'LS': 0.10,    # Landslide (moderate - infrastructure impact)
    'EQ': 0.05,    # Earthquake (low - facility damage only)
    'CY': 0.05,    # Cyclone (low - rare in sugarcane regions)
    'UF': 0.15,    # Urban Flood (moderate)
    'CF': 0.10,    # Coastal Flood (moderate)
    'TS': 0.02,    # Tsunami (very low)
    'VO': 0.02,    # Volcano (very low)
    'EH': 0.25,    # Extreme Heat (high - already in climate)
}

# Risk Score Weights for Combined Risk
RISK_WEIGHTS = {
    'climate': 0.6,
    'hazard': 0.4,
}

# Enhanced Risk Thresholds for NASA POWER variables (Phase 2)
ENHANCED_CLIMATE_THRESHOLDS = {
    'consecutive_dry_days': {
        'high': 30,      # days
        'medium': 20,
    },
    'extreme_heat_days': {
        'high': 50,      # days/year increase
        'medium': 30,
    },
    'growing_degree_days_change': {
        'high': 15,      # % change
        'medium': 10,
    },
    'solar_radiation_change': {
        'high': 10,      # % change
        'medium': 5,
    },
}

# Confidence Scoring Parameters
CONFIDENCE_WEIGHTS = {
    'cckp_temperature': 20,
    'cckp_precipitation': 20,
    'cckp_tasmax': 10,
    'thinkhazard_flood': 10,
    'thinkhazard_drought': 10,
    'nasa_power_cdd': 15,        # When implemented
    'nasa_power_extreme_heat': 10,  # When implemented
    'firms_wildfire': 5,          # When implemented
}

# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    'high': 80,      # 80-100% = High confidence
    'medium': 50,    # 50-79% = Medium confidence
    'low': 0,        # 0-49% = Low confidence
}

# --- MONTE CARLO PARAMETERS ---

MONTE_CARLO_CONFIG = {
    'n_simulations': 10000,
    'std_dev_yield_loss': 15.0,  # Standard deviation for yield loss
    'mean_loss_factor': 50.0,    # Max mean loss at likelihood 5/5 (50%)
}

# --- VISUALIZATION SETTINGS ---

# Color scheme for risk levels
RISK_COLORS = {
    'high': '#d62728',      # Red
    'medium': '#ff7f0e',    # Orange
    'low': '#2ca02c',       # Green
    'very_low': '#98df8a',  # Light green
}

# Chart theme
CHART_THEME = 'plotly_white'

# Geographic bounds for Brazil
BRAZIL_BOUNDS = {
    'lat_min': -34.0,
    'lat_max': 5.0,
    'lon_min': -74.0,
    'lon_max': -34.0,
}

# --- HELPER FUNCTIONS ---

def randomize_client_impacts(locations_dict):
    """
    Randomize CLIENT_LOCATIONS impact_percent so they sum to 1.0
    Uses Dirichlet distribution for realistic business allocation
    """
    keys = list(locations_dict.keys())
    if not keys:
        return locations_dict
    
    # Use Dirichlet distribution to generate weights that sum to 1
    weights = np.random.dirichlet(np.ones(len(keys)))
    
    for key, w in zip(keys, weights):
        locations_dict[key]["impact_percent"] = float(w)
    
    return locations_dict

# --- STATE ABBREVIATION MAPPING ---

BRAZIL_STATE_ABBREV_TO_NAME = {
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

