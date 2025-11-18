# Copernicus CDS Integration for ESG Risk Analysis

This document describes the integration of Copernicus Climate Data Store (CDS) data into the ESG Risk Analysis Tool, specifically using the `sis-ecv-cmip5-bias-corrected` dataset.

## Overview

The Copernicus integration enhances the existing climate risk analysis by providing:

- **Multi-model CMIP5 ensemble data** with bias adjustment
- **Cross-validation** of existing CCKP projections
- **Higher-resolution baselines** (0.5° grid vs state-level)
- **Enhanced risk indicators** for drought and heat stress
- **Improved confidence scoring**

## What's Been Implemented

### 1. Core Functions (`risk_data_collector.py`)

#### Data Fetching
- `fetch_copernicus_climate_data()`: Fetch data from single climate model
- `aggregate_copernicus_models()`: Ensemble mean across multiple models
- `calculate_copernicus_extreme_heat_days()`: Estimate extreme heat events
- `calculate_copernicus_drought_index()`: Precipitation-based drought assessment

#### Integration Points
- Enhanced `calculate_climate_likelihood()` with Copernicus cross-validation
- Updated `calculate_data_confidence()` with Copernicus scoring
- Automatic inclusion in `collect_location_risk_data()` workflow

### 2. Configuration (`config.py`)

```python
# Copernicus CDS API settings
COPERNICUS_ENABLED = False  # Set to True after API setup
COPERNICUS_DATASET = "sis-ecv-cmip5-bias-corrected"
COPERNICUS_TIMEOUT = 300  # 5 minutes for large downloads
COPERNICUS_RATE_LIMIT_DELAY = 2.0

# Climate models and variables
COPERNICUS_MODELS = [
    'hadgem2_es_model',     # Met Office Hadley Centre
    'mpi_esm_lr_model',     # Max Planck Institute
    'gfdl_esm2m_model',     # NOAA GFDL
    'canesm2_model',        # Canadian Centre for Climate Modelling
]

COPERNICUS_VARIABLES = [
    'maximum_2m_temperature_in_the_last_24_hours',
    'mean_2m_temperature_in_the_last_24_hours',
    'minimum_2m_temperature_in_the_last_24_hours',
    'total_precipitation_in_the_last_24_hours',
]
```

### 3. Data Processing Features

#### Spatial Aggregation
- Automatically finds 0.5° grid cell containing city coordinates
- Aggregates gridded data to point locations
- Handles longitude conversion (0-360° range for CDS)

#### Unit Conversions
- Temperature: Kelvin → Celsius
- Precipitation: kg/m²/s → mm/day

#### Ensemble Processing
- Multi-model averaging reduces uncertainty
- Individual model data available for uncertainty analysis

### 4. Risk Analysis Enhancements

#### Cross-Validation
```python
# Example output showing CCKP vs Copernicus comparison
> Temp change: +2.3°C (CCKP projection)
> Copernicus max temp: 28.5°C (historical baseline)
> Projected max temp (2070s): 30.8°C (cross-validated)
```

#### Enhanced Indicators
- **Extreme Heat Days**: Estimated from climatology data
- **Drought Index**: 1-5 scale based on precipitation
- **Model Uncertainty**: Ensemble spread assessment

#### Confidence Scoring
- **+30 points** maximum for Copernicus data availability
- Separate scoring for temperature (+10), precipitation (+10), mean temp (+10)

## Setup Instructions

### 1. API Credentials
1. Register at https://cds.climate.copernicus.eu/
2. Accept terms for `sis-ecv-cmip5-bias-corrected` dataset
3. Create `~/.cdsapirc` file:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: your-uid:your-api-key
   ```

### 2. Dependencies
```bash
pip install cdsapi xarray netcdf4
```

### 3. Configuration
Set `COPERNICUS_ENABLED = True` in `config.py`

### 4. Testing
Run the test script to verify setup:
```bash
python test_copernicus_integration.py
```

## Usage in Risk Analysis

### Automatic Integration
Once enabled, Copernicus data is automatically included in the standard risk analysis workflow:

```python
# Standard analysis now includes Copernicus data
result = collector.collect_location_risk_data("PIRACICABA/SP", "Supplier")
print(f"Confidence: {result['confidence_score']}%")
```

### Enhanced Output
The analysis now includes additional fields:
- `copernicus_data`: Raw climate variables
- `copernicus_max_temp`: Historical maximum temperature
- `copernicus_precip`: Historical precipitation
- `copernicus_projected_max_temp`: Future projections
- `copernicus_extreme_heat_days`: Heat stress indicator
- `copernicus_drought_index`: Drought risk assessment

## Cross-Validation Benefits

### 1. Projection Validation
- Compare CCKP projections against Copernicus historical baselines
- Identify potential biases in climate model projections
- Enhance confidence in future climate scenarios

### 2. Multi-Source Validation
- **CCKP**: State-level CMIP6 projections
- **Copernicus**: 0.5° grid CMIP5 ensemble with bias adjustment
- **NASA POWER**: Point-based agro-meteorological data

### 3. Uncertainty Assessment
- Ensemble spread shows projection uncertainty
- Cross-validation identifies robust vs uncertain projections
- Better risk communication with confidence intervals

## Data Characteristics

| Aspect | Copernicus CDS | CCKP | NASA POWER |
|--------|----------------|------|------------|
| **Resolution** | 0.5° grid | 0.25° grid | Point data |
| **Models** | 4 CMIP5 models | 20+ CMIP6 models | Reanalysis |
| **Bias Adjustment** | DBS method | Ensemble mean | Quality controlled |
| **Variables** | Temp, precip | Temp, precip | 100+ variables |
| **Temporal** | Daily climatology | Annual/20yr means | Daily/3-hourly |
| **Coverage** | 1978-2100 | 1980-2100 | 1981-present |

## Performance Considerations

### Rate Limiting
- 2-second delay between API calls
- Large NetCDF downloads (100MB+ per request)
- Batch processing for multiple models

### Data Volume
- NetCDF files stored temporarily and cleaned up
- Ensemble processing requires multiple API calls
- Consider caching for repeated analyses

### Error Handling
- Automatic retry with exponential backoff
- Graceful degradation if Copernicus fails
- Detailed error logging for troubleshooting

## Future Enhancements

### Additional Variables
- Wind speed and direction
- Soil moisture
- Evapotranspiration
- Extreme precipitation indices

### Future Scenarios
- RCP4.5 and RCP8.5 projections (currently historical only)
- Time series analysis beyond climatology
- Seasonal variability assessment

### Advanced Analytics
- Model weighting based on performance
- Uncertainty quantification
- Climate change signal detection

## Testing and Validation

### Test Scripts
- `test_copernicus_integration.py`: Basic functionality tests
- `cross_validation_demo.py`: Cross-validation demonstrations

### Validation Metrics
- Temperature correlation with CCKP baselines
- Precipitation pattern agreement
- Extreme event frequency comparison
- Spatial consistency checks

## Troubleshooting

### Common Issues

1. **"Missing optional dependency 'openpyxl'"**
   - Install: `pip install openpyxl`

2. **"xarray not available"**
   - Install: `pip install xarray netcdf4`

3. **CDS API authentication failed**
   - Check `~/.cdsapirc` file format
   - Verify API key is correct
   - Accept dataset terms on CDS website

4. **Large download timeouts**
   - Increase `COPERNICUS_TIMEOUT` in config
   - Check internet connection stability

5. **Grid cell not found**
   - Verify coordinates are within valid range
   - Check longitude conversion (negative → 0-360°)

### Debug Mode
Enable verbose logging by modifying the functions to include debug prints.

## References

- **Dataset**: https://cds.climate.copernicus.eu/datasets/sis-ecv-cmip5-bias-corrected
- **API Documentation**: https://cds.climate.copernicus.eu/api-how-to
- **DBS Method**: https://www.smhi.se/en/research/research-departments/climate-research-departments/hydro-climate/staff/description-of-the-dbs-method-1.17084

---

**Integration Complete**: Copernicus CDS data is now fully integrated into the ESG Risk Analysis Tool, providing enhanced climate risk assessment with cross-validation capabilities.
