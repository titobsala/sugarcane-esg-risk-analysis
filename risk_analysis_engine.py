"""
Risk Analysis Engine
Orchestrates data collection, risk analysis, and Monte Carlo simulations
Main entry point for the ESG risk analysis workflow
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import config
import risk_data_collector as collector
import monte_carlo_integrated as mc
import utils


def prepare_locations() -> Tuple[Dict, Dict]:
    """
    Prepare client and supplier location data
    Randomizes client impacts to sum to 1.0
    
    Returns:
        Tuple of (client_locations, supplier_locations)
    """
    # Randomize client impacts
    client_locations = config.randomize_client_impacts(config.CLIENT_LOCATIONS.copy())
    supplier_locations = config.SUPPLIER_LOCATIONS.copy()
    
    return client_locations, supplier_locations


def collect_all_risk_data(
    client_locations: Optional[Dict] = None,
    supplier_locations: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Collect comprehensive risk data for all locations
    Integrates climate risk (CCKP) and natural hazards (ThinkHazard)
    
    Args:
        client_locations: Optional custom client locations
        supplier_locations: Optional custom supplier locations
    
    Returns:
        DataFrame with comprehensive risk data
    """
    if client_locations is None or supplier_locations is None:
        client_locations, supplier_locations = prepare_locations()
    
    print("="*60)
    print("COLLECTING RISK DATA FOR ALL LOCATIONS")
    print("="*60)
    
    # Collect all data
    all_data = collector.collect_all_locations_data(
        client_locations=client_locations,
        supplier_locations=supplier_locations
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Calculate additional metrics
    df['impact_score'] = df['impact_percent'] * 100  # Convert to 0-100 scale
    df['climate_weighted_risk'] = df['climate_likelihood'] * df['impact_score']
    df['hazard_weighted_risk'] = df['hazard_severity'] * df['impact_score']
    
    # Calculate aggregate risk
    df['aggregate_risk'] = df.apply(
        lambda row: utils.calculate_aggregate_risk(
            row['climate_likelihood'],
            row['hazard_severity']
        ),
        axis=1
    )
    
    df['aggregate_weighted_risk'] = df['aggregate_risk'] * df['impact_score']
    
    # Add risk categories
    df['climate_category'] = df['climate_likelihood'].apply(
        lambda x: utils.get_risk_category(x, 5.0)
    )
    df['hazard_category'] = df['hazard_severity'].apply(
        lambda x: utils.get_risk_category(x, 5.0)
    )
    df['aggregate_category'] = df['aggregate_risk'].apply(
        lambda x: utils.get_risk_category(x, 5.0)
    )
    
    # Sort by aggregate weighted risk
    df = df.sort_values('aggregate_weighted_risk', ascending=False).reset_index(drop=True)
    
    print("\n" + "="*60)
    print("RISK DATA COLLECTION COMPLETE")
    print(f"Total locations analyzed: {len(df)}")
    print(f"Clients: {len(df[df['type'] == 'Client (Royalty)'])}")
    print(f"Suppliers: {len(df[df['type'] == 'Supplier (Seedling)'])}")
    print("="*60)
    
    return df


def run_monte_carlo_analysis(
    risk_data: pd.DataFrame,
    progress_callback: Optional[callable] = None
) -> pd.DataFrame:
    """
    Run Monte Carlo simulations for all locations
    
    Args:
        risk_data: DataFrame with risk data
        progress_callback: Optional progress callback
    
    Returns:
        DataFrame with Monte Carlo results
    """
    print("\n" + "="*60)
    print("RUNNING MONTE CARLO SIMULATIONS")
    print(f"Simulating {config.MONTE_CARLO_CONFIG['n_simulations']:,} scenarios per location")
    print("="*60)
    
    mc_results = mc.run_monte_carlo_for_all_locations(
        locations_data=risk_data,
        progress_callback=progress_callback
    )
    
    print("\n" + "="*60)
    print("MONTE CARLO SIMULATIONS COMPLETE")
    print("="*60)
    
    return mc_results


def calculate_portfolio_summary(
    risk_data: pd.DataFrame,
    mc_results: pd.DataFrame
) -> Dict:
    """
    Calculate portfolio-level summary statistics
    
    Args:
        risk_data: DataFrame with risk data
        mc_results: DataFrame with Monte Carlo results
    
    Returns:
        Dictionary with portfolio metrics
    """
    summary = {}
    
    # Risk distribution
    summary['total_locations'] = len(risk_data)
    summary['num_clients'] = len(risk_data[risk_data['type'] == 'Client (Royalty)'])
    summary['num_suppliers'] = len(risk_data[risk_data['type'] == 'Supplier (Seedling)'])
    
    # Climate risk stats
    summary['avg_climate_likelihood'] = risk_data['climate_likelihood'].mean()
    summary['max_climate_likelihood'] = risk_data['climate_likelihood'].max()
    summary['high_climate_risk_count'] = len(risk_data[risk_data['climate_likelihood'] >= 4])
    
    # Hazard risk stats
    summary['avg_hazard_severity'] = risk_data['hazard_severity'].mean()
    summary['max_hazard_severity'] = risk_data['hazard_severity'].max()
    summary['high_hazard_risk_count'] = len(risk_data[risk_data['hazard_severity'] >= 4])
    
    # Aggregate risk stats
    summary['avg_aggregate_risk'] = risk_data['aggregate_risk'].mean()
    summary['high_aggregate_risk_count'] = len(risk_data[risk_data['aggregate_risk'] >= 4])
    
    # Weighted risk stats
    summary['total_climate_weighted_risk'] = risk_data['climate_weighted_risk'].sum()
    summary['total_hazard_weighted_risk'] = risk_data['hazard_weighted_risk'].sum()
    summary['total_aggregate_weighted_risk'] = risk_data['aggregate_weighted_risk'].sum()
    
    # Top risks
    summary['top_5_climate_risks'] = risk_data.nlargest(5, 'climate_weighted_risk')[
        ['location', 'type', 'climate_likelihood', 'climate_weighted_risk']
    ].to_dict('records')
    
    summary['top_5_aggregate_risks'] = risk_data.nlargest(5, 'aggregate_weighted_risk')[
        ['location', 'type', 'aggregate_risk', 'aggregate_weighted_risk']
    ].to_dict('records')
    
    # Monte Carlo portfolio metrics
    if mc_results is not None and len(mc_results) > 0:
        mc_portfolio = mc.calculate_portfolio_metrics(mc_results)
        summary.update(mc_portfolio)
    
    # Value chain breakdown
    clients_data = risk_data[risk_data['type'] == 'Client (Royalty)']
    suppliers_data = risk_data[risk_data['type'] == 'Supplier (Seedling)']
    
    summary['client_avg_risk'] = clients_data['aggregate_risk'].mean()
    summary['supplier_avg_risk'] = suppliers_data['aggregate_risk'].mean()
    summary['client_total_weighted_risk'] = clients_data['aggregate_weighted_risk'].sum()
    summary['supplier_total_weighted_risk'] = suppliers_data['aggregate_weighted_risk'].sum()
    
    return summary


def run_sensitivity_analysis(
    risk_data: pd.DataFrame,
    stress_factor: float = 1.5
) -> Tuple[pd.DataFrame, Dict]:
    """
    Run sensitivity analysis by stressing top risk
    
    Args:
        risk_data: DataFrame with risk data
        stress_factor: Multiplier for impact
    
    Returns:
        Tuple of (stressed_df, analysis_dict)
    """
    print("\n" + "="*60)
    print("RUNNING SENSITIVITY ANALYSIS")
    print(f"Stress factor: +{(stress_factor - 1) * 100:.0f}%")
    print("="*60)
    
    # Find top risk client
    clients = risk_data[risk_data['type'] == 'Client (Royalty)'].copy()
    if len(clients) == 0:
        return risk_data, {}
    
    top_client = clients.iloc[0]
    
    print(f"\nStressing top risk: {top_client['location']}")
    print(f"Baseline Impact: {top_client['impact_score']:.2f}")
    print(f"Baseline Weighted Risk: {top_client['aggregate_weighted_risk']:.2f}")
    
    # Create stressed scenario
    stressed_df = risk_data.copy()
    stressed_df.loc[
        stressed_df['location'] == top_client['location'],
        'impact_score'
    ] *= stress_factor
    stressed_df.loc[
        stressed_df['location'] == top_client['location'],
        'impact_percent'
    ] *= stress_factor
    
    # Recalculate weighted risks
    stressed_df['climate_weighted_risk'] = stressed_df['climate_likelihood'] * stressed_df['impact_score']
    stressed_df['hazard_weighted_risk'] = stressed_df['hazard_severity'] * stressed_df['impact_score']
    stressed_df['aggregate_weighted_risk'] = stressed_df['aggregate_risk'] * stressed_df['impact_score']
    
    # Re-sort
    stressed_df = stressed_df.sort_values('aggregate_weighted_risk', ascending=False).reset_index(drop=True)
    
    stressed_top = stressed_df.iloc[0]
    
    analysis = {
        'top_client_name': top_client['location'],
        'baseline_impact': top_client['impact_score'],
        'baseline_weighted_risk': top_client['aggregate_weighted_risk'],
        'stressed_impact': stressed_top['impact_score'] if stressed_top['location'] == top_client['location'] else top_client['impact_score'] * stress_factor,
        'stressed_weighted_risk': stressed_df[stressed_df['location'] == top_client['location']]['aggregate_weighted_risk'].values[0],
        'new_top_risk': stressed_top['location'],
        'ranking_changed': stressed_top['location'] != top_client['location'],
    }
    
    print(f"\nStressed Impact: {analysis['stressed_impact']:.2f}")
    print(f"Stressed Weighted Risk: {analysis['stressed_weighted_risk']:.2f}")
    print(f"New top risk: {analysis['new_top_risk']}")
    print("="*60)
    
    return stressed_df, analysis


def export_results_to_csv(
    risk_data: pd.DataFrame,
    mc_results: Optional[pd.DataFrame] = None,
    portfolio_summary: Optional[Dict] = None,
    output_dir: str = "."
) -> Dict[str, str]:
    """
    Export analysis results to CSV files
    
    Args:
        risk_data: Risk data DataFrame
        mc_results: Monte Carlo results DataFrame
        portfolio_summary: Portfolio summary dictionary
        output_dir: Output directory path
    
    Returns:
        Dictionary mapping export type to file path
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    exports = {}
    
    # Export risk data
    risk_file = output_path / "risk_analysis_results.csv"
    risk_data.to_csv(risk_file, index=False)
    exports['risk_data'] = str(risk_file)
    
    # Export Monte Carlo results
    if mc_results is not None:
        mc_file = output_path / "monte_carlo_results.csv"
        mc_results.to_csv(mc_file, index=False)
        exports['monte_carlo'] = str(mc_file)
    
    # Export portfolio summary
    if portfolio_summary is not None:
        summary_file = output_path / "portfolio_summary.csv"
        summary_df = pd.DataFrame([portfolio_summary])
        summary_df.to_csv(summary_file, index=False)
        exports['summary'] = str(summary_file)
    
    print(f"\nResults exported to: {output_dir}")
    for export_type, file_path in exports.items():
        print(f"  - {export_type}: {file_path}")
    
    return exports


def run_full_analysis(
    export_csv: bool = False,
    output_dir: str = "."
) -> Dict:
    """
    Run complete end-to-end risk analysis
    
    Args:
        export_csv: Whether to export results to CSV
        output_dir: Output directory for exports
    
    Returns:
        Dictionary with all analysis results
    """
    print("\n" + "="*80)
    print(" "*20 + "ESG RISK ANALYSIS TOOL")
    print(" "*15 + "Sugarcane Supply Chain Risk Assessment")
    print("="*80)
    
    # Step 1: Collect risk data
    risk_data = collect_all_risk_data()
    
    # Step 2: Run Monte Carlo simulations
    mc_results = run_monte_carlo_analysis(risk_data)
    
    # Step 3: Calculate portfolio summary
    portfolio_summary = calculate_portfolio_summary(risk_data, mc_results)
    
    # Step 4: Run sensitivity analysis
    stressed_df, sensitivity_analysis = run_sensitivity_analysis(risk_data)
    
    # Step 5: Export if requested
    export_paths = None
    if export_csv:
        export_paths = export_results_to_csv(
            risk_data=risk_data,
            mc_results=mc_results,
            portfolio_summary=portfolio_summary,
            output_dir=output_dir
        )
    
    print("\n" + "="*80)
    print(" "*25 + "ANALYSIS COMPLETE")
    print("="*80)
    
    return {
        'risk_data': risk_data,
        'mc_results': mc_results,
        'portfolio_summary': portfolio_summary,
        'stressed_scenario': stressed_df,
        'sensitivity_analysis': sensitivity_analysis,
        'export_paths': export_paths,
    }


if __name__ == "__main__":
    # Run standalone analysis
    results = run_full_analysis(export_csv=True)
    
    # Print summary
    print("\n" + "="*80)
    print("PORTFOLIO SUMMARY")
    print("="*80)
    
    summary = results['portfolio_summary']
    print(f"\nTotal Locations: {summary['total_locations']}")
    print(f"  - Clients: {summary['num_clients']}")
    print(f"  - Suppliers: {summary['num_suppliers']}")
    
    print(f"\nAverage Climate Risk: {summary['avg_climate_likelihood']:.2f}/5")
    print(f"Average Hazard Severity: {summary['avg_hazard_severity']:.2f}/5")
    print(f"Average Aggregate Risk: {summary['avg_aggregate_risk']:.2f}/5")
    
    print(f"\nPortfolio VaR (95%): {summary.get('total_var_95', 0):.2f}% of total royalties")
    print(f"Portfolio VaR (99%): {summary.get('total_var_99', 0):.2f}% of total royalties")
    
    print("\nTop 5 Risks by Aggregate Weighted Score:")
    for i, risk in enumerate(summary['top_5_aggregate_risks'], 1):
        print(f"  {i}. {risk['location']} ({risk['type']}): {risk['aggregate_weighted_risk']:.2f}")
    
    print("\n" + "="*80)

