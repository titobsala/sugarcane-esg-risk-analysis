"""
Utility functions for ESG Risk Analysis Tool
Helper functions for data processing, scoring, and visualization
"""

import unicodedata
from typing import Optional, Dict, Any
import config


def normalize_location_name(location: str) -> str:
    """
    Normalize location name for consistent processing
    Handles special characters in Brazilian city names
    
    Args:
        location: Raw location string
    
    Returns:
        Normalized location string
    """
    # Remove extra whitespace
    location = " ".join(location.split())
    
    # Uppercase for consistency
    location = location.upper()
    
    return location


def remove_accents(text: str) -> str:
    """
    Remove accents from text for ASCII compatibility
    
    Args:
        text: Text with accents
    
    Returns:
        Text without accents
    """
    # Normalize to NFD form (decomposed)
    nfd_form = unicodedata.normalize('NFD', text)
    
    # Filter out combining characters (accents)
    return ''.join([c for c in nfd_form if unicodedata.category(c) != 'Mn'])


def convert_hazard_level_to_score(level: str) -> float:
    """
    Convert ThinkHazard level string to numeric score
    
    Args:
        level: Hazard level mnemonic (HIG, MED, LOW, VLO)
    
    Returns:
        Numeric score
    """
    return config.HAZARD_LEVEL_SCORES.get(level, 0)


def get_risk_color(score: float, max_score: float = 5.0) -> str:
    """
    Get color for risk visualization based on score
    
    Args:
        score: Risk score
        max_score: Maximum possible score
    
    Returns:
        Hex color code
    """
    if max_score == 0:
        return config.RISK_COLORS['very_low']
    
    normalized = score / max_score
    
    if normalized >= 0.7:
        return config.RISK_COLORS['high']
    elif normalized >= 0.4:
        return config.RISK_COLORS['medium']
    elif normalized >= 0.15:
        return config.RISK_COLORS['low']
    else:
        return config.RISK_COLORS['very_low']


def get_risk_category(score: float, max_score: float = 5.0) -> str:
    """
    Get risk category label based on score
    
    Args:
        score: Risk score
        max_score: Maximum possible score
    
    Returns:
        Category label
    """
    if max_score == 0:
        return 'Very Low'
    
    normalized = score / max_score
    
    if normalized >= 0.7:
        return 'High'
    elif normalized >= 0.4:
        return 'Medium'
    elif normalized >= 0.15:
        return 'Low'
    else:
        return 'Very Low'


def calculate_aggregate_risk(
    climate_likelihood: float,
    hazard_severity: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate aggregate risk score from climate and hazard components
    
    Args:
        climate_likelihood: Climate risk score (0-5)
        hazard_severity: Hazard severity score (0-5)
        weights: Optional custom weights dict with 'climate' and 'hazard' keys
    
    Returns:
        Aggregate risk score (0-5)
    """
    if weights is None:
        weights = config.RISK_WEIGHTS
    
    climate_weight = weights.get('climate', 0.6)
    hazard_weight = weights.get('hazard', 0.4)
    
    aggregate = (climate_likelihood * climate_weight) + (hazard_severity * hazard_weight)
    
    return min(aggregate, 5.0)


def calculate_weighted_risk(likelihood: float, impact: float) -> float:
    """
    Calculate weighted risk score (L × I)
    
    Args:
        likelihood: Likelihood score
        impact: Impact score
    
    Returns:
        Weighted risk score
    """
    return likelihood * impact


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage string
    
    Args:
        value: Numeric value (0.0 to 1.0 or percentage)
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_currency(value: float, currency: str = "R$") -> str:
    """
    Format value as currency string
    
    Args:
        value: Numeric value
        currency: Currency symbol
    
    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    return f"{currency} {value:,.2f}"


def format_temperature(value: float) -> str:
    """
    Format temperature value
    
    Args:
        value: Temperature in Celsius
    
    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    return f"{value:.1f}°C"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling zero division
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
    
    Returns:
        Result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def get_hazard_icon(hazard_type: str) -> str:
    """
    Get emoji icon for hazard type
    
    Args:
        hazard_type: Hazard type mnemonic (FL, EQ, LS, etc.)
    
    Returns:
        Emoji string
    """
    icons = {
        'FL': '🌊',  # Flood
        'EQ': '🏚️',  # Earthquake
        'LS': '⛰️',  # Landslide
        'WF': '🔥',  # Wildfire
        'DR': '🌵',  # Drought
        'CY': '🌀',  # Cyclone
        'UF': '💧',  # Urban Flood
        'CF': '🌊',  # Coastal Flood
        'TS': '🌊',  # Tsunami
        'VO': '🌋',  # Volcano
        'EH': '🌡️',  # Extreme Heat
    }
    return icons.get(hazard_type, '⚠️')


def get_hazard_name(hazard_type: str) -> str:
    """
    Get full name for hazard type
    
    Args:
        hazard_type: Hazard type mnemonic
    
    Returns:
        Full name string
    """
    names = {
        'FL': 'River Flood',
        'EQ': 'Earthquake',
        'LS': 'Landslide',
        'WF': 'Wildfire',
        'DR': 'Drought',
        'CY': 'Cyclone',
        'UF': 'Urban Flood',
        'CF': 'Coastal Flood',
        'TS': 'Tsunami',
        'VO': 'Volcano',
        'EH': 'Extreme Heat',
    }
    return names.get(hazard_type, hazard_type)


def create_risk_summary(data: Dict[str, Any]) -> str:
    """
    Create a text summary of risk data
    
    Args:
        data: Risk data dictionary
    
    Returns:
        Formatted summary string
    """
    location = data.get('location', 'Unknown')
    climate_likelihood = data.get('climate_likelihood', 0)
    hazard_severity = data.get('hazard_severity', 0)
    
    summary = f"**{location}**\n\n"
    summary += f"Climate Risk: {get_risk_category(climate_likelihood)} ({climate_likelihood}/5)\n"
    summary += f"Hazard Severity: {get_risk_category(hazard_severity)} ({hazard_severity}/5)\n"
    
    hazards = data.get('hazards', {})
    if hazards:
        summary += f"\nDetected Hazards:\n"
        for haz_type, level in hazards.items():
            icon = get_hazard_icon(haz_type)
            name = get_hazard_name(haz_type)
            summary += f"- {icon} {name}: {level}\n"
    
    return summary


def validate_risk_data(data: Dict[str, Any]) -> bool:
    """
    Validate that risk data has required fields
    
    Args:
        data: Risk data dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['location', 'type', 'climate_likelihood', 'impact_percent']
    
    for field in required_fields:
        if field not in data:
            return False
        if data[field] is None:
            return False
    
    return True


def calculate_portfolio_var(risks: list, confidence_level: float = 0.95) -> float:
    """
    Calculate portfolio-level Value at Risk
    
    Args:
        risks: List of risk scores
        confidence_level: Confidence level (0.0 to 1.0)
    
    Returns:
        VaR value
    """
    import numpy as np
    
    if not risks:
        return 0.0
    
    return float(np.percentile(risks, confidence_level * 100))

