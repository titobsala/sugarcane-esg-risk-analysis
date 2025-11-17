# Data Sources Documentation

## Table of Contents
1. [Overview](#overview)
2. [Current Data Sources](#current-data-sources)
3. [Proposed Additional Sources](#proposed-additional-sources)
4. [Data Integration Architecture](#data-integration-architecture)
5. [Data Quality Assessment](#data-quality-assessment)

---

## Overview

This document provides comprehensive information about all data sources used in the ESG Risk Analysis Tool, including their characteristics, access methods, limitations, and integration details.

### Data Requirements

For comprehensive sugarcane supply chain risk assessment, we need:

1. **Climate Projections**: Future temperature and precipitation scenarios
2. **Extreme Weather Indices**: Heat stress, drought, flooding indicators
3. **Natural Hazard Data**: Multi-hazard exposure by location
4. **Agricultural Indicators**: Crop-specific stress metrics
5. **Historical Validation**: Observed data for calibration

---

## Current Data Sources

### 1. World Bank Climate Change Knowledge Portal (CCKP)

#### Overview
- **Provider**: World Bank Group
- **URL**: https://climateknowledgeportal.worldbank.org/
- **API Endpoint**: https://cckpapi.worldbank.org/cckp/v1
- **Cost**: Free, no registration required
- **Update Frequency**: Major updates every 2-3 years (follows IPCC assessment cycles)

#### Data Provided

**Climate Variables**:
- `tas`: Near-surface air temperature (°C)
- `tasmax`: Maximum daily temperature (°C)
- `tasmin`: Minimum daily temperature (°C)
- `pr`: Precipitation (mm)
- `tasmaxgt35`: Days with max temperature >35°C

**Temporal Coverage**:
- Historical: 1901-2020 (CRU observational data)
- Baseline: 1995-2014 (used for comparison)
- Projections: 2020-2100 in 20-year periods

**Scenarios**:
- Historical: Observed climate
- SSP1-2.6: Low emissions, Paris Agreement goals
- SSP2-4.5: Intermediate emissions
- SSP3-7.0: Medium-high emissions
- **SSP5-8.5**: High emissions (used in tool for conservative risk assessment)

**Spatial Resolution**:
- 0.25° × 0.25° grid (~25km at equator)
- Aggregated to administrative boundaries (ADM0, ADM1, ADM2)
- **Tool uses**: State-level (ADM1) for Brazil

####

 Model Ensemble

Based on **CMIP6** (Coupled Model Intercomparison Project Phase 6):
- Ensemble of 20+ global climate models
- Median value used (reduces model bias)
- Represents consensus projection

**Participating Models** (selection):
- ACCESS-CM2 (Australia)
- CMCC-ESM2 (Italy)
- MIROC6 (Japan)
- MPI-ESM1-2-LR (Germany)
- NorESM2-MM (Norway)

#### Why SSP5-8.5?

**Rationale for using high-emissions scenario**:

1. **Risk Management**: Conservative approach for business planning
2. **Current Trajectory**: Global emissions closer to SSP5-8.5 than lower scenarios
3. **Irreversibility**: Climate impacts lag emissions by decades
4. **Prudent Planning**: Better to over-prepare than under-prepare
5. **Adaptation Lead Time**: Infrastructure decisions made today affect 30+ year horizons

**Alternative Scenarios** (for future implementation):
- SSP2-4.5: More likely mid-range outcome
- SSP1-2.6: Optimistic Paris Agreement compliance

#### API Usage

**Request Format**:
```
GET https://cckpapi.worldbank.org/cckp/v1/cmip6-x0.25_climatology_{variables}_climatology_annual_{period}_median_{scenario}_ensemble_all_mean/{geocode}?_format=json
```

**Example**:
```
GET https://cckpapi.worldbank.org/cckp/v1/cmip6-x0.25_climatology_tas,tasmax,pr_climatology_annual_2040-2059_median_ssp585_ensemble_all_mean/BRA.37689?_format=json
```

**Response Format**:
```json
{
  "metadata": {...},
  "data": {
    "tas": {
      "BRA.37689": {"2040-07": 24.68}
    },
    "tasmax": {
      "BRA.37689": {"2040-07": 29.45}
    },
    "pr": {
      "BRA.37689": {"2040-07": 1438.32}
    }
  }
}
```

#### Rate Limiting
- No strict rate limits documented
- **Tool implementation**: 0.3 second delay between requests
- **Retry logic**: Exponential backoff (3 retries)
- **Daily limit**: Estimated thousands of requests (reasonable use)

#### Known Limitations

1. **Spatial Resolution**: 25km grid may miss local topographic effects
2. **Seasonal Detail**: Annual means don't capture intra-season variability
3. **Extreme Events**: Better at averages than rare extremes
4. **Regional Bias**: Some CMIP6 models overestimate Brazilian Amazonia rainfall
5. **Uncertainty**: ±20-30% uncertainty band in regional projections

#### Data Quality
- **Reliability**: High (World Bank curated, peer-reviewed models)
- **Validation**: Models validated against historical observations
- **Completeness**: Full coverage for Brazil at state level
- **Timeliness**: Updated with each IPCC assessment cycle

---

### 2. ThinkHazard! (GFDRR)

#### Overview
- **Provider**: World Bank Global Facility for Disaster Reduction and Recovery (GFDRR)
- **URL**: https://thinkhazard.org/
- **API Endpoint**: https://thinkhazard.org/en/report/{division_code}.json
- **Cost**: Free, no registration required
- **Update Frequency**: Varies by hazard type, generally every 2-5 years

#### Data Provided

**Hazard Types** (11 total):
1. **FL**: River flood
2. **UF**: Urban flood
3. **CF**: Coastal flood
4. **EQ**: Earthquake
5. **LS**: Landslide
6. **TS**: Tsunami
7. **VO**: Volcanic activity
8. **CY**: Tropical cyclone
9. **DR**: Drought
10. **EH**: Extreme heat
11. **WF**: Wildfire

**Hazard Levels**:
- **VLO** (Very Low): Return period >200 years
- **LOW**: Return period 100-200 years
- **MED** (Medium): Return period 25-100 years
- **HIG** (High): Return period <25 years

#### Administrative Boundaries

Uses **GAUL** (Global Administrative Unit Layers):
- ADM0: Country level
- ADM1: State/Province level
- ADM2: District/Municipality level

**Brazil Coverage**:
- ADM0: 188 (Brazil)
- ADM1: 27 states
- ADM2: Variable (not all municipalities mapped)

#### Methodology

**Data Sources by Hazard**:
- **Flood**: GLOFRIS (Global Flood Risk with Image Scenarios)
- **Earthquake**: GSHAP (Global Seismic Hazard Assessment Program)
- **Landslide**: NASA/NGI global susceptibility mapping
- **Cyclone**: IBTrACS (International Best Track Archive)
- **Drought**: Global drought frequency analysis
- **Wildfire**: Regional fire risk mapping

**Assessment Approach**:
1. Hazard frequency/probability analysis
2. Exposure mapping (population, assets)
3. Vulnerability assessment
4. Risk classification by return period

#### API Usage

**Request Format**:
```
GET https://thinkhazard.org/en/report/{division_code}.json
```

**Example**:
```
GET https://thinkhazard.org/en/report/3598.json  # São Paulo state
```

**Response Format**:
```json
[
  {
    "hazardlevel": {"mnemonic": "HIG", "title": "High"},
    "hazardtype": {"mnemonic": "FL", "hazardtype": "River flood"}
  },
  {
    "hazardlevel": {"mnemonic": "MED", "title": "Medium"},
    "hazardtype": {"mnemonic": "DR", "hazardtype": "Drought"}
  }
]
```

#### Rate Limiting
- No documented rate limits
- **Tool implementation**: 0.5 second delay between requests
- **Typical usage**: 26 requests per full analysis

#### Known Limitations

1. **Coverage Gaps**: Not all Brazilian municipalities have ADM2 codes
   - **Workaround**: Fall back to state-level (ADM1) data
2. **Static Assessment**: Does not account for climate change impacts on hazard frequency
3. **Coarse Categories**: Four levels may not capture nuanced differences
4. **Data Vintage**: Some hazard layers based on 2000s-era data
5. **No Magnitude**: Indicates presence/frequency, not intensity
6. **Binary Nature**: Either a hazard is present or not; no gradation within levels

#### Data Quality
- **Reliability**: Medium-High (varies by hazard type)
- **Validation**: Hazards validated against historical disaster databases
- **Completeness**: Good for major hazards (flood, earthquake), variable for others
- **Timeliness**: Updates lag current research by 2-5 years

---

## Proposed Additional Sources

### 3. NASA POWER API

#### Overview
- **Provider**: NASA Langley Research Center
- **URL**: https://power.larc.nasa.gov/
- **API Endpoint**: https://power.larc.nasa.gov/api/temporal/daily/point
- **Cost**: Free, no registration required
- **Status**: **PROPOSED - Not yet integrated**

#### Value Proposition

**Why add NASA POWER?**
1. **Higher Resolution**: 0.5° × 0.5° grid (~50km)
2. **More Variables**: Solar radiation, humidity, wind, agro-meteorological indices
3. **Daily Data**: Sub-annual temporal resolution
4. **Validation Quality**: NASA-quality control and validation
5. **Complementary**: Fills gaps in CCKP data

#### Data Provided

**Agricultural Meteorology Parameters**:
- `T2M`: Temperature at 2 meters (°C)
- `T2M_MAX`: Maximum temperature (°C)
- `T2M_MIN`: Minimum temperature (°C)
- `PRECTOTCORR`: Precipitation (mm/day)
- `ALLSKY_SFC_SW_DWN`: Solar radiation (MJ/m²/day)
- `RH2M`: Relative humidity (%)
- `WS2M`: Wind speed at 2m (m/s)

**Agro-climatic Indices**:
- `CDD`: Consecutive dry days (drought indicator)
- `CWD`: Consecutive wet days (flood indicator)
- `T2M_MAX_GT35`: Days with temp >35°C
- `FROST_DAYS`: Days with temp <0°C
- **GDD**: Growing degree days (calculable)

**Temporal Coverage**:
- Historical: 1981-present (near real-time updates)
- Climate normals: 1991-2020 period available
- Future: Can be combined with climate projections

#### Proposed Integration

**Use Cases**:
1. **Drought Stress**: Consecutive dry days (CDD) directly indicates drought severity
2. **Heat Stress**: Days >35°C affects sugarcane growth
3. **Solar Radiation**: Important for photosynthesis, currently not captured
4. **Growing Degree Days**: Better predictor of crop development than temperature alone
5. **Validation**: Historical data to validate CCKP projections

**API Example**:
```
GET https://power.larc.nasa.gov/api/temporal/climatology/point?
    parameters=T2M,T2M_MAX,PRECTOTCORR,CDD,ALLSKY_SFC_SW_DWN
    &community=AG
    &longitude=-47.6&latitude=-22.7
    &start=20000101&end=20201231
    &format=JSON
```

#### Implementation Plan

1. Add NASA POWER config to `config.py`
2. Create `fetch_nasa_power_data()` in `risk_data_collector.py`
3. Integrate CDD, extreme heat days, GDD into climate scoring
4. Cross-validate with CCKP temperature/precipitation

#### Rate Limiting
- No strict limits
- Recommended: 0.5-1 second delay
- Large requests: Use bulk download

---

### 4. Fire Information for Resource Management System (FIRMS)

#### Overview
- **Provider**: NASA / University of Maryland
- **URL**: https://firms.modaps.eosdis.nasa.gov/
- **API Endpoint**: https://firms.modaps.eosdis.nasa.gov/api/area/
- **Cost**: Free with registration (API key required)
- **Status**: **PROPOSED - Not yet integrated**

#### Value Proposition

**Why add FIRMS?**
1. **Real-time**: Active fire detection from MODIS/VIIRS satellites
2. **Historical**: Fire archive back to 2000
3. **High Resolution**: 375m-1km spatial resolution
4. **Brazil Focus**: Critical for sugarcane (pre-harvest burning, wildfires)
5. **Quantitative**: Fire count, radiative power, not just binary classification

#### Data Provided

**Fire Detection**:
- `latitude`, `longitude`: Fire location
- `brightness`: Fire radiative power (MW)
- `confidence`: Detection confidence (0-100%)
- `acq_date`, `acq_time`: Detection date/time
- `frp`: Fire radiative power (indicator of intensity)

**Historical Statistics**:
- Fire frequency by grid cell
- Seasonal patterns
- Fire season timing

#### Proposed Integration

**Use Cases**:
1. **Wildfire Risk Enhancement**: Replace ThinkHazard binary with quantitative fire density
2. **Seasonal Analysis**: Identify high-fire-risk months for each location
3. **Trend Analysis**: Increasing or decreasing fire activity
4. **Validation**: Check if ThinkHazard "high" wildfire aligns with FIRMS data

**Scoring Enhancement**:
```python
# Current: Binary from ThinkHazard
wildfire_risk = thinkh azard_level  # VLO, LOW, MED, HIG

# Enhanced: Fire density from FIRMS
fires_per_year = count_firms_fires(location, years=2015-2023)
if fires_per_year > 50:
    wildfire_risk_score = 5
elif fires_per_year > 20:
    wildfire_risk_score = 3
elif fires_per_year > 5:
    wildfire_risk_score = 1
```

#### API Example
```
GET https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/VIIRS_NOAA20_NRT/-50,-25,-40,-15/10/2023-01-01
```

Parameters:
- `API_KEY`: User registration key
- `VIIRS_NOAA20_NRT`: Satellite/sensor
- Bounding box: longitude/latitude
- Last 10 days

#### Implementation Plan

1. User registers for API key at https://firms.modaps.eosdis.nasa.gov/api/
2. Add API key to `config.py`
3. Create `fetch_firms_fire_data()` function
4. Calculate historical fire density for each location
5. Integrate into hazard severity scoring

---

### 5. Global Flood Awareness System (GloFAS)

#### Overview
- **Provider**: European Centre for Medium-Range Weather Forecasts (ECMWF) / Copernicus
- **URL**: https://www.globalfloods.eu/
- **Data Access**: Copernicus Climate Data Store (CDS)
- **Cost**: Free with registration
- **Status**: **PROPOSED - Not yet integrated**

#### Value Proposition

**Why add GloFAS?**
1. **Quantitative**: Return period maps, not just classifications
2. **High Resolution**: ~5-10km spatial resolution
3. **Forecast Capability**: Real-time flood forecasts (not just historical)
4. **Physically-Based**: Hydrological modeling, not just historical statistics
5. **Climate Change**: Projections of future flood risk

#### Data Provided

**Flood Hazard Maps**:
- Return period: 2, 5, 10, 20, 50, 100, 500 year floods
- Inundation depth (meters)
- Flow velocity
- Affected area extent

**Coverage**:
- Global at 0.1° × 0.1° resolution
- Focus on river flooding (not coastal)

#### Proposed Integration

**Use Cases**:
1. **Enhanced Flood Scoring**: Use return period instead of binary classification
2. **Location Specificity**: Identify which specific fields are at risk
3. **Scenario Planning**: "What if" analysis for different flood magnitudes

**Scoring Enhancement**:
```python
# Current: ThinkHazard classification
flood_risk = "HIG"  # Return period <25 years

# Enhanced: GloFAS quantitative
return_period_10yr = get_glofas_flood_depth(location, return_period=10)
if return_period_10yr > 1.5:  # meters
    flood_risk_score = 5  # Severe flooding
elif return_period_10yr > 0.5:
    flood_risk_score = 3  # Moderate flooding
```

#### Data Access

**Copernicus Climate Data Store**:
1. Register at https://cds.climate.copernicus.eu/
2. Install `cdsapi` Python package
3. Download GloFAS reanalysis or forecasts
4. Extract data for Brazilian locations

**Alternative**: Web API (if available)

---

### 6. Copernicus Climate Data Store (CDS)

#### Overview
- **Provider**: European Union Copernicus Programme
- **URL**: https://cds.climate.copernicus.eu/
- **API**: `cdsapi` Python package
- **Cost**: Free with registration
- **Status**: **PROPOSED - Not yet integrated**

#### Value Proposition

**Why add Copernicus?**
1. **ERA5 Reanalysis**: Best-available historical climate data (1979-present)
2. **High Resolution**: 0.25° × 0.25° (~25km)
3. **Hourly Data**: Sub-daily temporal resolution
4. **Soil Moisture**: Direct measurement, not derived
5. **Validation**: Gold standard for validating climate models

#### Data Provided

**ERA5 Reanalysis Variables**:
- Temperature (2m, surface, soil)
- Precipitation (total, convective)
- Soil moisture (multiple layers)
- Evapotranspiration
- Solar radiation
- Wind (multiple heights)

**Derived Agricultural Indicators**:
- **SPI** (Standardized Precipitation Index): Drought indicator
- **SPEI** (Standardized Precipitation-Evapotranspiration Index): Water balance
- Soil water stress
- Heat stress indices

#### Proposed Integration

**Use Cases**:
1. **Historical Validation**: Validate CCKP projections against ERA5 observations
2. **Drought Indices**: SPI/SPEI more sophisticated than simple precipitation
3. **Soil Moisture**: Direct indicator of plant water stress
4. **Heat Stress**: Combine temperature + humidity for physiological stress

**Implementation**:
```python
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': ['2m_temperature', 'total_precipitation', 'volumetric_soil_water_layer_1'],
        'year': ['2000', '2010', '2020'],
        'month': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
        'time': '00:00',
        'area': [-5, -74, -34, -34],  # Brazil bounding box
        'format': 'netcdf',
    },
    'brazil_era5.nc')
```

---

## Data Integration Architecture

### Current Architecture

```
┌─────────────────────┐
│  User Configuration │
│   (config.py)       │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Risk Data Collector │
│ (risk_data_         │
│  collector.py)      │
└──────────┬──────────┘
           │
           ├────────────┐
           v            v
    ┌─────────┐   ┌──────────┐
    │  CCKP   │   │ThinkHazard│
    │   API   │   │   API     │
    └─────────┘   └──────────┘
           │            │
           └────┬───────┘
                v
         ┌─────────────┐
         │  Risk Data  │
         │  DataFrame  │
         └─────────────┘
                │
                v
         ┌─────────────┐
         │   Analysis  │
         │   Engine    │
         └─────────────┘
```

### Proposed Enhanced Architecture

```
┌─────────────────────┐
│  User Configuration │
│   (config.py)       │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Risk Data Collector │
│  (Enhanced)         │
└──────────┬──────────┘
           │
           ├────────┬──────────┬──────────┬──────────┐
           v        v          v          v          v
       ┌──────┐ ┌────┐   ┌──────┐  ┌──────┐  ┌──────┐
       │ CCKP │ │TH! │   │NASA  │  │FIRMS │  │GloFAS│
       │      │ │    │   │POWER │  │      │  │      │
       └──────┘ └────┘   └──────┘  └──────┘  └──────┘
           │        │        │         │         │
           └────────┴────┬───┴─────────┴─────────┘
                         v
                  ┌─────────────┐
                  │    Data     │
                  │ Integration │
                  │  & Quality  │
                  │  Assessment │
                  └─────────────┘
                         │
                         v
                  ┌─────────────┐
                  │  Enhanced   │
                  │  Risk Data  │
                  │  DataFrame  │
                  └─────────────┘
                         │
                         v
                  ┌─────────────┐
                  │  Analysis   │
                  │   Engine    │
                  │  (Enhanced) │
                  └─────────────┘
```

### Data Flow

1. **Configuration**: User specifies locations and parameters
2. **Data Collection**: Parallel API calls to all sources
3. **Data Integration**: Merge data by location
4. **Quality Assessment**: Check completeness, flag gaps
5. **Risk Calculation**: Apply enhanced scoring algorithms
6. **Confidence Scoring**: Assess data quality per location
7. **Results**: Enhanced risk dataframe with confidence indicators

---

## Data Quality Assessment

### Quality Dimensions

1. **Completeness**: Are all variables available?
2. **Timeliness**: How recent is the data?
3. **Spatial Resolution**: Does resolution match needs?
4. **Temporal Resolution**: Adequate time periods?
5. **Validation**: Is data cross-checked?

### Quality Scoring

**Proposed Confidence Score** (0-100%):

```python
def calculate_confidence_score(data_availability):
    score = 0
    
    # CCKP climate data
    if data_availability['cckp']['tas']:
        score += 20
    if data_availability['cckp']['tasmax']:
        score += 10
    if data_availability['cckp']['pr']:
        score += 20
    
    # ThinkHazard data
    if data_availability['thinkhazard']['flood']:
        score += 10
    if data_availability['thinkhazard']['drought']:
        score += 10
    
    # NASA POWER (when implemented)
    if data_availability.get('nasa_power', {}).get('cdd'):
        score += 15
    
    # FIRMS (when implemented)
    if data_availability.get('firms', {}).get('fire_density'):
        score += 15
    
    return score
```

**Confidence Categories**:
- **High (80-100%)**: All key data sources available
- **Medium (50-79%)**: Core data available, some gaps
- **Low (<50%)**: Significant data gaps

### Handling Missing Data

**Strategies**:
1. **Spatial Interpolation**: Use nearby locations
2. **Fallback to Coarser Resolution**: State instead of municipality
3. **Alternative Sources**: If one API fails, use another
4. **Flag Uncertainly**: Clearly mark estimates vs observations

---

## Summary Comparison

| Data Source | Resolution | Coverage | Cost | Status | Priority |
|-------------|------------|----------|------|--------|----------|
| **CCKP** | 25km / State | Global | Free | ✅ Integrated | Essential |
| **ThinkHazard** | District | Global | Free | ✅ Integrated | Essential |
| **NASA POWER** | 50km | Global | Free | 🔄 Proposed | High |
| **FIRMS** | 375m-1km | Global | Free* | 🔄 Proposed | Medium |
| **GloFAS** | 5-10km | Global | Free* | 🔄 Proposed | Medium |
| **Copernicus CDS** | 25km | Global | Free* | 🔄 Proposed | Low |

*Requires registration

### Recommendation Priority

**Phase 1** (Immediate):
- ✅ CCKP (implemented)
- ✅ ThinkHazard (implemented)

**Phase 2** (High Value):
- 🔄 NASA POWER for drought/heat indices
- 🔄 FIRMS for quantitative wildfire risk

**Phase 3** (Advanced):
- 🔄 GloFAS for detailed flood modeling
- 🔄 Copernicus for validation and soil moisture

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Next Review**: Quarterly or when new data sources are added

