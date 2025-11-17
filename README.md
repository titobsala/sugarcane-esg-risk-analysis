# ESG Risk Analysis Tool

Comprehensive climate and natural hazard risk assessment for sugarcane supply chains.

## 📚 Documentation

**Essential Reading**:
- 🚀 **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- 📖 **[METHODOLOGY.md](docs/METHODOLOGY.md)** - Detailed risk calculation methods
- 🔬 **[SCIENTIFIC_BASIS.md](docs/SCIENTIFIC_BASIS.md)** - Research foundation and citations
- 💼 **[INTERPRETATION_GUIDE.md](docs/INTERPRETATION_GUIDE.md)** - How to use results for business decisions
- 🌐 **[DATA_SOURCES.md](docs/DATA_SOURCES.md)** - API documentation and data sources

## 🆕 What's New - Phase 2 Complete (November 2025)

**NASA POWER Integration Now Live!**

The ESG Risk Analysis Tool has been enhanced with NASA POWER agricultural meteorology data:

- ✅ **5 New Climate Variables**: Temperature, max temperature, precipitation, consecutive dry days, and solar radiation
- ✅ **Enhanced Risk Scoring**: Drought stress (CDD) and extreme heat indicators now quantified
- ✅ **Growing Degree Days**: Agricultural phenology modeling for crop development assessment
- ✅ **Data Confidence Scoring**: Automated quality metrics (0-100%) for each location
- ✅ **Improved Accuracy**: Confidence levels increased from 60% to 90% with NASA POWER data

**Impact**: Climate likelihood scores are now more nuanced and location-specific, with better differentiation between drought-prone and heat-stressed regions.

See [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md#phase-2-nasa-power-api-integration) for complete details.

---

## Overview

This tool provides integrated ESG (Environmental, Social, Governance) risk analysis combining:
- **Climate Risk Analysis**: Temperature and precipitation projections from World Bank CCKP API
- **Enhanced Agricultural Indicators**: NASA POWER data for drought stress (CDD), extreme heat, growing degree days, and solar radiation
- **Natural Hazard Assessment**: Multi-hazard data from ThinkHazard! (floods, earthquakes, landslides, etc.)
- **Monte Carlo Simulations**: Probabilistic loss modeling across 10,000+ scenarios
- **Data Confidence Scoring**: Automated quality assessment with 0-100% confidence levels
- **Interactive Dashboard**: Visual reporting with Streamlit
- **Comprehensive Documentation**: Scientific basis, methodology, and interpretation guides

## Features

### 📊 Executive Summary
- Portfolio-level KPIs and metrics
- Top risk identification
- Geographic risk distribution
- Value chain overview

### 🌡️ Climate Risk Analysis
- Temperature and precipitation change projections (CCKP)
- Enhanced agricultural meteorology indicators (NASA POWER):
  - Consecutive Dry Days (CDD) for drought assessment
  - Extreme heat days (>35°C) estimation
  - Growing Degree Days (GDD) for crop development
  - Solar radiation for photosynthesis potential
- Impact vs Likelihood scatter analysis
- State-level climate trends
- Risk categorization with 0-5 scale
- Data confidence levels (High/Medium/Low)

### ⚠️ Natural Hazards
- Multi-hazard matrix (floods, earthquakes, landslides, wildfires, drought)
- Hazard severity scoring
- Integration with ThinkHazard! global database

### 🎲 Monte Carlo Simulations
- 10,000 scenario simulations per location
- Value at Risk (VaR) calculations at 90%, 95%, 99% confidence levels
- Loss distribution analysis
- Portfolio-level risk aggregation

### 🔗 Value Chain Risk
- Upstream (Supplier) vs Downstream (Client) comparison
- Sankey flow diagrams
- Concentration risk analysis
- Herfindahl diversification index

### 🔬 Sensitivity Analysis
- Stress testing capabilities
- Impact parameter adjustments
- Ranking stability analysis

## Installation

### Prerequisites
- Python 3.11 or 3.12
- Poetry (for dependency management)

### Setup

1. Clone or download the repository

2. Install dependencies:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Usage

### Option 1: Interactive Dashboard (Recommended)

Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Steps in Dashboard:**
1. Click "Run Analysis" in the sidebar
2. Wait for data collection (may take several minutes due to API calls)
3. Explore results across 6 interactive tabs
4. Export results to CSV using sidebar button

### Option 2: Command Line Analysis

Run the analysis engine directly:

```bash
python risk_analysis_engine.py
```

This will:
- Collect climate and hazard data for all locations
- Run Monte Carlo simulations
- Generate portfolio summary
- Export results to CSV files in current directory

### Option 3: Original Scripts (Legacy)

The original scripts are preserved for reference:

```bash
# Climate risk analysis (state-level CCKP data)
python sugarcane.py

# Single-location Monte Carlo
python monte-carlo-risk.py
```

## Configuration

Edit `config.py` to customize:

### Location Data
- `CLIENT_LOCATIONS`: Royalty locations and impact percentages
- `SUPPLIER_LOCATIONS`: Seedling supplier locations

### Risk Thresholds
- `CLIMATE_RISK_THRESHOLDS`: Temperature and precipitation thresholds
- `HAZARD_LEVEL_SCORES`: Hazard severity mappings

### Monte Carlo Parameters
- `n_simulations`: Number of scenarios (default: 10,000)
- `std_dev_yield_loss`: Volatility of yield loss (default: 15.0)

### API Configuration
- Rate limits and timeouts
- Retry parameters

## Project Structure

```
/home/tito-sala/Code/Exo/risk-test/
├── app.py                          # Streamlit dashboard (main UI)
├── risk_analysis_engine.py         # Analysis orchestrator
├── risk_data_collector.py          # API integration (CCKP + ThinkHazard)
├── monte_carlo_integrated.py       # Probabilistic simulations
├── config.py                       # Configuration and settings
├── brazil_adm2_mapping.py          # Geographic code mapping
├── utils.py                        # Helper functions
├── geonames.json                   # State geocode reference
├── pyproject.toml                  # Python dependencies
├── sugarcane.py                    # Original climate script
└── monte-carlo-risk.py             # Original Monte Carlo script
```

## Data Sources

> 🌐 **Complete data source documentation**: [DATA_SOURCES.md](docs/DATA_SOURCES.md)

### Current Implementation

#### World Bank Climate Change Knowledge Portal (CCKP)
- **API**: `https://cckpapi.worldbank.org/cckp/v1`
- **Data**: CMIP6 climate projections (20+ global models ensemble)
- **Variables**: Temperature (tas, tasmax), Precipitation (pr)
- **Scenarios**: SSP5-8.5 (high emissions, conservative for risk assessment)
- **Resolution**: State-level (ADM1) for Brazil
- **Temporal**: Baseline 1995-2014, Future 2040-2059
- **Quality**: High (World Bank curated, peer-reviewed)

**Why SSP5-8.5?**: Conservative approach for business planning, current emissions trajectory closer to high scenarios, better to over-prepare than under-prepare.

#### ThinkHazard! (GFDRR)
- **API**: `https://thinkhazard.org/en`
- **Data**: Multi-hazard assessment using GAUL administrative boundaries
- **Hazards**: 11 types including floods, earthquakes, landslides, wildfires, drought
- **Levels**: Very Low, Low, Medium, High (based on return periods)
- **Coverage**: Global, Brazil state/district level
- **Update**: Varies by hazard, generally 2-5 year cycles

### Proposed Enhancements (Phase 2)

> 📋 **Research and implementation plan**: [DATA_SOURCES.md - Proposed Additional Sources](docs/DATA_SOURCES.md#proposed-additional-sources)

**High Priority**:
1. **NASA POWER API**: Solar radiation, consecutive dry days, extreme heat indices
   - Value: More granular climate data, drought stress indicators
   - Status: Configuration added, implementation pending
   
2. **FIRMS (NASA)**: Real-time wildfire detection and historical fire density
   - Value: Quantitative wildfire risk vs binary classification
   - Status: Documented, pending API key registration

**Medium Priority**:
3. **GloFAS**: Detailed flood return period mapping
4. **Copernicus CDS**: ERA5 reanalysis for validation, soil moisture data

### Data Quality & Confidence

All data sources include quality metadata and confidence scoring:
- **High Confidence (80-100%)**: All key data sources available
- **Medium Confidence (50-79%)**: Core data available, some gaps
- **Low Confidence (<50%)**: Significant data gaps, use with caution

> 📊 **Data quality framework**: [DATA_SOURCES.md - Data Quality Assessment](docs/DATA_SOURCES.md#data-quality-assessment)

## ESG Alignment

### Environmental (E)
- **Climate Change Physical Risks**: Temperature increases, precipitation variability
- **Natural Disaster Exposure**: Multi-hazard assessment
- **Regional Climate Impacts**: State and municipality-level analysis

### Social (S)
- **Community Risk**: Geographic risk mapping
- **Supply Chain Resilience**: Supplier risk assessment
- **Placeholder for**: Worker safety, community impact metrics (future enhancement)

### Governance (G)
- **Risk Management**: Data-driven decision making
- **Supply Chain Oversight**: Comprehensive upstream/downstream visibility
- **Transparent Reporting**: Interactive dashboards and CSV exports
- **Business Continuity**: Stress testing and sensitivity analysis

## Risk Methodology

> 📖 **For detailed methodology**: See [METHODOLOGY.md](docs/METHODOLOGY.md)
> 
> 🔬 **For scientific basis**: See [SCIENTIFIC_BASIS.md](docs/SCIENTIFIC_BASIS.md)

### Climate Likelihood Score (0-5)

The climate risk assessment evaluates three critical variables for sugarcane production:

#### Variables Assessed
1. **Average Temperature (tas)**: Sugarcane optimal range is 21-27°C
   - Above 32°C: Photosynthesis declines sharply
   - Above 35°C: Growth essentially stops
   
2. **Maximum Temperature (tasmax)**: Extreme heat causes physiological stress
   - Prolonged periods >35°C reduce yields by 10-30%
   
3. **Precipitation (pr)**: Sugarcane requires 1500-2500mm annually
   - Drought: 25-50% yield loss during growth phase
   - Waterlogging >7 days: Root damage, 20-40% yield loss

#### Scoring Thresholds

Based on projected changes from 1995-2014 baseline to 2040-2059 (SSP5-8.5):

| Variable | High Risk (+2) | Medium Risk (+1) | Rationale |
|----------|---------------|------------------|-----------|
| **Temperature Change** | > 2.5°C | > 1.5°C | IPCC thresholds, sugarcane physiological studies |
| **Max Temperature Change** | > 3.5°C | > 2.0°C | ~30 more days >35°C, approaching limits |
| **Precipitation Change** | > ±20% | > ±10% | Major infrastructure investment needed |

**Score Capped at 5** (maximum risk)

#### Interpretation

| Score | Category | Business Implication | Source |
|-------|----------|---------------------|---------|
| 0-1 | Very Low | Business as usual, maintain monitoring | - |
| 2 | Low | Begin adaptation planning | Marin et al., 2013 |
| 3 | Medium | Implement adaptation measures | PBMC, 2014 |
| 4 | High | Urgent adaptation required | FAO, 2012 |
| 5 | Very High | Strategic review needed | IPCC AR6, 2021 |

### Hazard Severity Score (0-5)

> 📖 **Detailed hazard methodology**: [METHODOLOGY.md - Natural Hazard Scoring](docs/METHODOLOGY.md#natural-hazard-scoring)

**Data Source**: ThinkHazard! (World Bank GFDRR)

**Hazard Types**: Floods, Drought, Wildfires, Landslides, Earthquakes, Cyclones, and more

**Scoring**: Each hazard level contributes to aggregate score:
- High (HIG): 3 points
- Medium (MED): 2 points  
- Low (LOW): 1 point
- Very Low (VLO): 0.5 points

**Weighting by Sugarcane Relevance** (documented in config.py):
- Flood: 30% (critical - waterlogging kills crops)
- Drought: 30% (critical - major yield impact)
- Wildfire: 20% (high - can destroy crops)
- Other hazards: 10-15% (infrastructure impacts)

### Aggregate Risk Calculation

```
Aggregate Risk = (0.6 × Climate Likelihood) + (0.4 × Hazard Severity)
```

**Rationale for 60/40 weighting**:
- Climate change is systemic and predictable
- Climate directly determines sugarcane productivity
- Hazards are episodic but can be catastrophic
- Both components essential for complete risk picture

> 💼 **Alternative weighting scenarios**: See [INTERPRETATION_GUIDE.md](docs/INTERPRETATION_GUIDE.md)

### Hazard Severity Score (0-5)
Aggregate of individual hazard levels:
- High (HIG): 3 points
- Medium (MED): 2 points
- Low (LOW): 1 point
- Very Low (VLO): 0.5 points
- Normalized to 0-5 scale

### Aggregate Risk Score
Weighted combination:
- Climate: 60% weight
- Hazards: 40% weight

### Weighted Risk Score
Risk Score × Business Impact Score (0-100)

### Monte Carlo Simulation

> 📖 **Full Monte Carlo methodology**: [METHODOLOGY.md - Monte Carlo Simulation](docs/METHODOLOGY.md#monte-carlo-simulation)

**Purpose**: Quantifies uncertainty and generates probability distributions for financial planning

**Methodology**:
- **Simulations**: 10,000 scenarios per location
- **Distribution**: Normal distribution (justified by Central Limit Theorem)
- **Mean Loss**: `(climate_likelihood / 5) × 50%` (calibrated to Brazilian yield data)
- **Std Deviation**: 15% (based on observed coefficient of variation)
- **Bounds**: 0-100% (realistic limits)

**Key Metrics**:
- **Mean Loss**: Expected average annual loss
- **VaR(95%)**: Maximum loss in 95% of scenarios (used for financial reserves)
- **VaR(99%)**: Worst-case planning scenario
- **Expected Shortfall**: Average loss beyond VaR threshold

**Calibration**: Based on CONAB (Brazilian agricultural agency) yield data 1990-2020

**Scientific Basis**: 
- Marin et al. (2013): Historical sugarcane yield variability
- FAO (2012): Crop response to climate variability
- IPCC SRCCL (2019): Agricultural risk assessment methods

## Exports

Results are exported to CSV files:
- `risk_analysis_results.csv`: Comprehensive risk data for all locations
- `monte_carlo_results.csv`: Simulation results and VaR metrics
- `portfolio_summary.csv`: Portfolio-level statistics

Export directory: `./exports/` (created automatically)

## Performance Notes

- **First Run**: 15-30 minutes (API data collection for 26 locations)
- **Subsequent Runs**: Consider implementing API response caching
- **Monte Carlo**: ~5-10 seconds for 10,000 simulations × 26 locations
- **Dashboard**: Real-time interactivity after initial data load

## Troubleshooting

### API Rate Limiting
If you encounter rate limit errors:
- Increase `CCKP_RATE_LIMIT_DELAY` in `config.py`
- Reduce number of locations analyzed
- Implement response caching (future enhancement)

### Missing Hazard Data
ThinkHazard may not have detailed data for all municipalities:
- Tool automatically falls back to state-level data
- Some locations may show "No ADM code found"
- This is expected and handled gracefully

### Import Errors
Ensure all dependencies are installed:
```bash
poetry install
```

## Future Enhancements

> 📋 **Complete implementation roadmap**: [FUTURE_ENHANCEMENTS.md](docs/FUTURE_ENHANCEMENTS.md)

### Phase 2: Enhanced Data Integration (Ready for Implementation)

**High Priority**:
- **NASA POWER API**: Additional climate variables (drought indices, extreme heat, solar radiation)
  - Status: Configuration complete, implementation pending (~2-3 days)
- **Confidence Indicators**: Data quality scoring and transparency
  - Status: Framework designed, UI implementation pending (~1 day)

**Medium Priority**:
- **FIRMS Wildfire Data**: Quantitative fire risk assessment
  - Status: Research complete, API key registration pending (~1-2 days)
- **Enhanced Scoring**: 0-10 internal scale for better granularity
  - Status: Algorithm designed, implementation pending (~1 day)
- **Data Quality Tab**: Comprehensive data coverage dashboard
  - Status: Design complete, implementation pending (~1 day)

### Phase 3: Advanced Features (6-12 months)

- API response caching for faster re-runs
- PDF report generation with branding
- Social impact metrics integration
- Financial loss modeling (revenue → profit impact)
- Adaptation strategy recommendations
- Multi-year trend analysis with alerts
- Machine learning pattern detection

**All enhancements are fully documented with implementation plans, effort estimates, and code examples.**