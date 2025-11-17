"""
Integrated Monte Carlo Risk Simulation Module
Probabilistic risk analysis for all locations with batch processing support
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import config


def run_monte_carlo_for_location(
    location_name: str,
    climate_likelihood: float,
    impact_percent: float,
    n_simulations: Optional[int] = None,
    std_dev: Optional[float] = None
) -> Dict:
    """
    Run Monte Carlo simulation for a single location
    
    Args:
        location_name: Name of the location
        climate_likelihood: Climate risk score (0-5)
        impact_percent: Business impact as decimal (e.g., 0.12 for 12%)
        n_simulations: Number of simulations (default from config)
        std_dev: Standard deviation for yield loss (default from config)
    
    Returns:
        Dictionary with simulation results
    """
    if n_simulations is None:
        n_simulations = config.MONTE_CARLO_CONFIG['n_simulations']
    
    if std_dev is None:
        std_dev = config.MONTE_CARLO_CONFIG['std_dev_yield_loss']
    
    # Calculate mean yield loss based on climate likelihood score
    # A score of 5/5 means 50% average loss, scaled linearly
    mean_yield_loss_percent = (climate_likelihood / 5.0) * config.MONTE_CARLO_CONFIG['mean_loss_factor']
    
    # Run simulations
    simulated_royalty_losses = []
    
    for _ in range(n_simulations):
        # Simulate yield loss using normal distribution
        yield_loss = np.random.normal(mean_yield_loss_percent, std_dev)
        
        # Clamp between 0 and 100%
        yield_loss = np.clip(yield_loss, 0, 100)
        
        # Calculate royalty loss as percentage of total business
        royalty_loss_as_percent = (yield_loss / 100.0) * impact_percent
        
        # Store as percentage (e.g., 0.05 -> 5.0)
        simulated_royalty_losses.append(royalty_loss_as_percent * 100.0)
    
    # Calculate statistics
    losses_array = np.array(simulated_royalty_losses)
    
    results = {
        'location': location_name,
        'climate_likelihood': climate_likelihood,
        'impact_percent': impact_percent,
        'n_simulations': n_simulations,
        'mean_loss': float(np.mean(losses_array)),
        'std_dev': float(np.std(losses_array)),
        'min_loss': float(np.min(losses_array)),
        'max_loss': float(np.max(losses_array)),
        'var_90': float(np.percentile(losses_array, 90)),
        'var_95': float(np.percentile(losses_array, 95)),
        'var_99': float(np.percentile(losses_array, 99)),
        'median_loss': float(np.median(losses_array)),
        'simulated_losses': losses_array.tolist(),
    }
    
    return results


def run_monte_carlo_for_all_locations(
    locations_data: pd.DataFrame,
    progress_callback: Optional[callable] = None
) -> pd.DataFrame:
    """
    Run Monte Carlo simulations for all locations with progress tracking
    
    Args:
        locations_data: DataFrame with location risk data
        progress_callback: Optional callback function to report progress
                          Should accept (current, total, location_name)
    
    Returns:
        DataFrame with simulation results for all locations
    """
    results = []
    total = len(locations_data)
    
    for idx, row in locations_data.iterrows():
        location_name = row['location']
        climate_likelihood = row.get('climate_likelihood', 0)
        impact_percent = row.get('impact_percent', 0)
        
        # Report progress
        if progress_callback:
            progress_callback(idx + 1, total, location_name)
        
        # Run simulation
        mc_result = run_monte_carlo_for_location(
            location_name=location_name,
            climate_likelihood=climate_likelihood,
            impact_percent=impact_percent
        )
        
        results.append(mc_result)
    
    return pd.DataFrame(results)


def calculate_portfolio_metrics(mc_results: pd.DataFrame) -> Dict:
    """
    Calculate portfolio-level risk metrics from all Monte Carlo results
    
    Args:
        mc_results: DataFrame with Monte Carlo results for all locations
    
    Returns:
        Dictionary with portfolio metrics
    """
    # Aggregate statistics
    total_mean_loss = mc_results['mean_loss'].sum()
    total_var_95 = mc_results['var_95'].sum()
    total_var_99 = mc_results['var_99'].sum()
    
    # Find highest risk locations
    top_risks = mc_results.nlargest(5, 'var_95')[['location', 'var_95', 'mean_loss']]
    
    # Calculate concentration risk (Herfindahl index)
    impacts = mc_results['impact_percent'].values
    herfindahl_index = np.sum(impacts ** 2)
    
    metrics = {
        'total_mean_loss': total_mean_loss,
        'total_var_95': total_var_95,
        'total_var_99': total_var_99,
        'max_single_location_var95': mc_results['var_95'].max(),
        'avg_location_var95': mc_results['var_95'].mean(),
        'herfindahl_index': herfindahl_index,
        'diversification_score': 1 - herfindahl_index,  # Higher is more diversified
        'top_5_risks': top_risks.to_dict('records'),
        'num_high_risk_locations': len(mc_results[mc_results['var_95'] > 5.0]),
    }
    
    return metrics


def simulate_correlated_losses(
    locations_data: pd.DataFrame,
    correlation: float = 0.3,
    n_simulations: Optional[int] = None
) -> np.ndarray:
    """
    Simulate correlated losses across locations
    Useful for portfolio-level stress testing
    
    Args:
        locations_data: DataFrame with location data
        correlation: Correlation coefficient between locations (0-1)
        n_simulations: Number of simulations
    
    Returns:
        Array of shape (n_simulations, n_locations) with correlated losses
    """
    if n_simulations is None:
        n_simulations = config.MONTE_CARLO_CONFIG['n_simulations']
    
    n_locations = len(locations_data)
    
    # Create correlation matrix
    corr_matrix = np.full((n_locations, n_locations), correlation)
    np.fill_diagonal(corr_matrix, 1.0)
    
    # Generate correlated random variables using Cholesky decomposition
    L = np.linalg.cholesky(corr_matrix)
    
    # Generate independent standard normal variables
    independent_vars = np.random.randn(n_simulations, n_locations)
    
    # Transform to correlated variables
    correlated_vars = independent_vars @ L.T
    
    # Transform to losses for each location
    losses = np.zeros((n_simulations, n_locations))
    
    for i, row in enumerate(locations_data.itertuples()):
        climate_likelihood = getattr(row, 'climate_likelihood', 0)
        impact_percent = getattr(row, 'impact_percent', 0)
        
        mean_yield_loss = (climate_likelihood / 5.0) * config.MONTE_CARLO_CONFIG['mean_loss_factor']
        std_dev = config.MONTE_CARLO_CONFIG['std_dev_yield_loss']
        
        # Transform standard normal to yield loss
        yield_losses = correlated_vars[:, i] * std_dev + mean_yield_loss
        yield_losses = np.clip(yield_losses, 0, 100)
        
        # Convert to royalty loss
        losses[:, i] = (yield_losses / 100.0) * impact_percent * 100.0
    
    return losses


def run_stress_test(
    location_name: str,
    climate_likelihood: float,
    impact_percent: float,
    stress_factor: float = 1.5
) -> Tuple[Dict, Dict]:
    """
    Run stress test by increasing impact
    
    Args:
        location_name: Name of location
        climate_likelihood: Climate risk score
        impact_percent: Current business impact
        stress_factor: Multiplier for impact (e.g., 1.5 = +50%)
    
    Returns:
        Tuple of (baseline_results, stressed_results)
    """
    # Baseline scenario
    baseline = run_monte_carlo_for_location(
        location_name=location_name,
        climate_likelihood=climate_likelihood,
        impact_percent=impact_percent
    )
    
    # Stressed scenario
    stressed = run_monte_carlo_for_location(
        location_name=location_name,
        climate_likelihood=climate_likelihood,
        impact_percent=impact_percent * stress_factor
    )
    
    return baseline, stressed


def generate_loss_exceedance_curve(mc_results: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate loss exceedance curve data (for plotting)
    
    Args:
        mc_results: Monte Carlo results dictionary
    
    Returns:
        Tuple of (loss_levels, exceedance_probabilities)
    """
    simulated_losses = np.array(mc_results['simulated_losses'])
    
    # Sort losses
    sorted_losses = np.sort(simulated_losses)
    
    # Calculate exceedance probabilities
    n = len(sorted_losses)
    exceedance_probs = 1 - (np.arange(1, n + 1) / n)
    
    return sorted_losses, exceedance_probs


def calculate_expected_shortfall(simulated_losses: List[float], confidence_level: float = 0.95) -> float:
    """
    Calculate Expected Shortfall (Conditional VaR)
    Average loss in the worst (1-confidence_level) of scenarios
    
    Args:
        simulated_losses: List of simulated loss values
        confidence_level: Confidence level (e.g., 0.95 for 95%)
    
    Returns:
        Expected Shortfall value
    """
    losses_array = np.array(simulated_losses)
    var_threshold = np.percentile(losses_array, confidence_level * 100)
    
    # Get losses exceeding VaR
    tail_losses = losses_array[losses_array >= var_threshold]
    
    if len(tail_losses) == 0:
        return var_threshold
    
    return float(np.mean(tail_losses))


def create_mc_summary_stats(mc_results: Dict) -> pd.DataFrame:
    """
    Create a summary statistics table for Monte Carlo results
    
    Args:
        mc_results: Monte Carlo results dictionary
    
    Returns:
        DataFrame with summary statistics
    """
    stats = {
        'Metric': [
            'Mean Loss',
            'Median Loss',
            'Std Deviation',
            'Min Loss',
            'Max Loss',
            'VaR 90%',
            'VaR 95%',
            'VaR 99%',
        ],
        'Value (% of Total Royalties)': [
            f"{mc_results['mean_loss']:.2f}%",
            f"{mc_results['median_loss']:.2f}%",
            f"{mc_results['std_dev']:.2f}%",
            f"{mc_results['min_loss']:.2f}%",
            f"{mc_results['max_loss']:.2f}%",
            f"{mc_results['var_90']:.2f}%",
            f"{mc_results['var_95']:.2f}%",
            f"{mc_results['var_99']:.2f}%",
        ]
    }
    
    return pd.DataFrame(stats)

