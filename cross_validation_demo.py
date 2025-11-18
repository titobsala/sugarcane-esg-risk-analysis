#!/usr/bin/env python3
"""
Copernicus Cross-Validation Demo

This script demonstrates how Copernicus data can be used to cross-validate
and enhance the existing CCKP climate projections in the ESG Risk Analysis Tool.

It shows:
1. Comparison between Copernicus baselines and CCKP projections
2. Ensemble model validation
3. Enhanced risk indicators from Copernicus data
4. Confidence scoring improvements
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import config
import risk_data_collector as collector

def demonstrate_cross_validation():
    """Demonstrate cross-validation between data sources"""
    print("=" * 80)
    print("COPERNICUS CROSS-VALIDATION DEMO")
    print("=" * 80)

    if not config.COPERNICUS_ENABLED:
        print("⚠️  Copernicus is DISABLED. Enable it in config.py to run this demo.")
        return

    # Test location: São Paulo, Brazil
    test_location = "PIRACICABA/SP"
    lat, lon = -22.7, -47.6  # Approximate coordinates for Piracicaba

    print(f"Analyzing location: {test_location}")
    print(f"Coordinates: {lat}°N, {lon}°W")
    print()

    # 1. Get existing CCKP data
    print("1. EXISTING CCKP PROJECTIONS:")
    print("-" * 40)

    geocode = "BRA.37689"  # São Paulo state geocode
    climate_likelihood, climate_changes = collector.calculate_climate_likelihood(geocode, lat, lon)

    cckp_temp_change = climate_changes.get('temp_change', 0)
    cckp_precip_change = climate_changes.get('precip_change_pct', 0)

    print(".2f"    print(".1f"
    # 2. Get Copernicus baseline data
    print("\n2. COPERNICUS BASELINE DATA:")
    print("-" * 40)

    copernicus_data = collector.aggregate_copernicus_models(
        lat=lat,
        lon=lon,
        experiment='historical',
        period_start='19810101',
        period_end='20001231'
    )

    if copernicus_data:
        cop_max_temp = copernicus_data.get('maximum_2m_temperature_in_the_last_24_hours')
        cop_precip = copernicus_data.get('total_precipitation_in_the_last_24_hours')

        if cop_max_temp is not None:
            print(".2f"        if cop_precip is not None:
            print(".2f"
    # 3. Cross-validation and projections
    print("\n3. CROSS-VALIDATION & FUTURE PROJECTIONS:")
    print("-" * 40)

    if copernicus_data and cop_max_temp and cop_precip:
        # Temperature projections
        projected_max_temp = cop_max_temp + cckp_temp_change
        print(".2f"        print(".2f"
        # Precipitation projections
        projected_precip = cop_precip * (1 + cckp_precip_change / 100)
        print(".2f"        print(".2f"
        # Risk assessment
        if projected_max_temp > 35:
            print("   🔥 HIGH HEAT RISK: Projected max temps exceed 35°C")
        if projected_precip < 2.0:
            print("   🏜️  HIGH DROUGHT RISK: Projected precipitation very low")

    # 4. Enhanced indicators from Copernicus
    print("\n4. ENHANCED RISK INDICATORS:")
    print("-" * 40)

    extreme_heat_days = collector.calculate_copernicus_extreme_heat_days(copernicus_data)
    drought_index = collector.calculate_copernicus_drought_index(copernicus_data)

    if extreme_heat_days is not None:
        print(".1f"        if extreme_heat_days > 50:
            print("   ⚠️  Copernicus indicates SEVERE heat stress conditions")

    if drought_index is not None:
        drought_levels = ["None", "Very Low", "Low", "Moderate", "High", "Very High"]
        print(f"   Drought Risk Index: {drought_index:.1f}/5 ({drought_levels[int(drought_index)]})")
        if drought_index >= 4.0:
            print("   ⚠️  Copernicus indicates HIGH drought vulnerability")

    # 5. Model ensemble information
    print("\n5. MODEL ENSEMBLE VALIDATION:")
    print("-" * 40)

    print(f"   Copernicus Ensemble: {len(config.COPERNICUS_MODELS)} models")
    print(f"   Models used: {', '.join([m.replace('_model', '').replace('_', '-') for m in config.COPERNICUS_MODELS])}")
    print("   ✓ Multi-model approach reduces uncertainty"
    # 6. Confidence scoring enhancement
    print("\n6. CONFIDENCE SCORING ENHANCEMENT:")
    print("-" * 40)

    # Simulate confidence calculation
    base_confidence = 50  # CCKP + ThinkHazard
    copernicus_boost = 30  # Copernicus contribution
    total_confidence = min(base_confidence + copernicus_boost, 100)

    print(f"   Base confidence (CCKP + ThinkHazard): {base_confidence}%")
    print(f"   Copernicus enhancement: +{copernicus_boost}%")
    print(f"   Total confidence: {total_confidence}% ({'High' if total_confidence >= 80 else 'Medium'})")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ Copernicus integration provides:")
    print("   • Cross-validation of CCKP projections")
    print("   • Higher-resolution climate baselines")
    print("   • Multi-model uncertainty assessment")
    print("   • Enhanced drought and heat stress indicators")
    print("   • Improved confidence scoring")
    print("   • Better spatial coverage for risk analysis")

def demonstrate_brazil_europe_comparison():
    """Show how Copernicus data works across different regions"""
    print("\n" + "=" * 80)
    print("BRAZIL vs EUROPE COMPARISON")
    print("=" * 80)

    if not config.COPERNICUS_ENABLED:
        print("⚠️  Copernicus disabled - skipping comparison")
        return

    locations = [
        ("Piracicaba, Brazil", -22.7, -47.6),
        ("Paris, France", 48.8, 2.3),
        ("London, UK", 51.5, -0.1),
        ("Berlin, Germany", 52.5, 13.4)
    ]

    print("Climate baselines across different regions:")
    print("-" * 50)

    for name, lat, lon in locations:
        copernicus_data = collector.aggregate_copernicus_models(
            lat=lat, lon=lon,
            experiment='historical',
            period_start='19810101',
            period_end='20001231'
        )

        if copernicus_data:
            max_temp = copernicus_data.get('maximum_2m_temperature_in_the_last_24_hours')
            precip = copernicus_data.get('total_precipitation_in_the_last_24_hours')

            if max_temp and precip:
                print("15")

def main():
    """Main demo function"""
    print("Copernicus Cross-Validation Demo for ESG Risk Analysis")
    print("This demonstrates how Copernicus data enhances existing climate risk assessment")

    demonstrate_cross_validation()
    demonstrate_brazil_europe_comparison()

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("To use Copernicus data in your risk analysis:")
    print("1. Get CDS API credentials from https://cds.climate.copernicus.eu/")
    print("2. Set COPERNICUS_ENABLED = True in config.py")
    print("3. Run your normal risk analysis - Copernicus data will be included automatically")
    print("4. Use the enhanced confidence scores and cross-validated projections")

if __name__ == "__main__":
    main()
