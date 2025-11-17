# Risk Assessment Methodology

## Table of Contents
1. [Overview](#overview)
2. [Climate Risk Scoring](#climate-risk-scoring)
3. [Natural Hazard Scoring](#natural-hazard-scoring)
4. [Aggregate Risk Calculation](#aggregate-risk-calculation)
5. [Monte Carlo Simulation](#monte-carlo-simulation)
6. [Limitations and Assumptions](#limitations-and-assumptions)

---

## Overview

This document provides a comprehensive explanation of the risk assessment methodology used in the ESG Risk Analysis Tool. The framework evaluates physical climate risks and natural hazards for sugarcane supply chain locations in Brazil, combining multiple data sources to generate actionable risk scores.

### Core Principles

1. **Multi-dimensional Assessment**: Combines climate change projections with natural hazard exposure
2. **Business Impact Integration**: Weights risks by their potential impact on business operations
3. **Probabilistic Modeling**: Uses Monte Carlo simulations to quantify uncertainty
4. **Transparency**: All calculations are documented and reproducible
5. **Actionable Insights**: Translates technical metrics into business decisions

---

## Climate Risk Scoring

### Variables Used

The climate risk assessment focuses on three critical variables for sugarcane production:

#### 1. Average Temperature (tas)
- **Why it matters**: Sugarcane has an optimal growth temperature range of 21-27°C. Temperatures outside this range reduce photosynthetic efficiency and overall yield.
- **Data source**: World Bank CCKP API, CMIP6 ensemble median
- **Baseline**: Historical period 1995-2014
- **Future**: Projected period 2040-2059 under SSP5-8.5 scenario

**Scientific Basis**: 
- Above 32°C: Photosynthesis declines sharply
- Above 35°C: Growth essentially stops
- Below 20°C: Slower growth, extended maturation period

#### 2. Maximum Temperature (tasmax)
- **Why it matters**: Extreme heat events cause immediate physiological stress, reduce sucrose accumulation, and can damage leaves
- **Measurement**: Annual maximum daily temperature
- **Critical threshold**: >35°C causes heat stress

**Scientific Basis**:
- Sugarcane can tolerate brief heat spikes
- Prolonged periods >35°C reduce yields by 10-30%
- Harvest quality (sucrose content) decreases with heat stress

#### 3. Precipitation (pr)
- **Why it matters**: Sugarcane requires 1500-2500mm annual rainfall. Both drought and flooding significantly impact yields
- **Measurement**: Annual total precipitation in millimeters
- **Critical concerns**: 
  - Drought reduces cane weight and sucrose content
  - Excessive rainfall damages roots, increases disease, complicates harvest

**Scientific Basis**:
- Water stress during grand growth phase (4-9 months): 25-50% yield loss
- Waterlogging >7 days: root damage, 20-40% yield loss
- Optimal: 1200-1500mm during growth, dry period for harvest

### Scoring Algorithm

The climate likelihood score ranges from **0 to 5**, calculated as follows:

```python
def calculate_climate_likelihood(baseline, future):
    risk_score = 0
    
    # 1. Temperature Change
    temp_change = future['tas'] - baseline['tas']
    if temp_change > 2.5:  # °C
        risk_score += 2
    elif temp_change > 1.5:
        risk_score += 1
    
    # 2. Maximum Temperature Change
    tasmax_change = future['tasmax'] - baseline['tasmax']
    if tasmax_change > 3.5:  # °C
        risk_score += 2
    elif tasmax_change > 2.0:
        risk_score += 1
    
    # 3. Precipitation Change (%)
    precip_change_pct = ((future['pr'] - baseline['pr']) / baseline['pr']) * 100
    if abs(precip_change_pct) > 20:  # %
        risk_score += 2
    elif abs(precip_change_pct) > 10:
        risk_score += 1
    
    return min(risk_score, 5)  # Cap at 5
```

### Threshold Rationale

#### Temperature Thresholds

**2.5°C / 1.5°C for Average Temperature**
- Based on IPCC climate thresholds and sugarcane physiological studies
- 1.5°C: Noticeable impact on growth cycles, harvest timing shifts
- 2.5°C: Significant yield reduction (15-25%), increased pest pressure
- Sources: 
  - IPCC Special Report on 1.5°C (2018)
  - Sugarcane crop modeling studies (Marin et al., 2013)

**3.5°C / 2.0°C for Maximum Temperature**
- Extreme heat events have disproportionate impact
- 2.0°C increase: ~15 more days >35°C per year
- 3.5°C increase: ~30 more days >35°C per year, approaching physiological limits
- Source: Brazilian agricultural climate studies (EMBRAPA)

#### Precipitation Thresholds

**±20% / ±10% Change**
- Sugarcane can adapt to moderate rainfall variability
- 10% change: Manageable with irrigation/drainage adjustments
- 20% change: Requires major infrastructure investments
- Both drought (-20%) and excess (+20%) are problematic
- Source: FAO irrigation guidelines for sugarcane

### Interpretation

| Score | Category | Interpretation | Business Implication |
|-------|----------|----------------|---------------------|
| 0-1 | Very Low | Minimal climate change impact expected | Business as usual, maintain monitoring |
| 2 | Low | Noticeable changes, manageable | Begin adaptation planning |
| 3 | Medium | Significant changes expected | Implement adaptation measures |
| 4 | High | Major climate challenges | Urgent adaptation required, consider diversification |
| 5 | Very High | Severe climate disruption | High-risk location, strategic review needed |

### Limitations

1. **Spatial Resolution**: State-level data may not capture local microclimates
2. **Single Scenario**: SSP5-8.5 represents a high-emissions pathway; actual outcomes depend on climate policy
3. **Model Uncertainty**: CMIP6 models have varying regional accuracy for Brazil
4. **Non-climate Factors**: Does not account for CO2 fertilization effect (may partially offset temperature increases)
5. **Adaptation**: Assumes current varieties and practices; new cultivars may be more resilient

---

## Natural Hazard Scoring

### Data Source: ThinkHazard!

ThinkHazard! (World Bank GFDRR) provides hazard classifications based on:
- Return period analysis
- Historical event frequency
- Geophysical characteristics
- Infrastructure vulnerability

### Hazard Types Assessed

1. **Floods (FL)** - River and surface flooding
2. **Earthquakes (EQ)** - Seismic activity
3. **Landslides (LS)** - Mass movement hazards
4. **Wildfires (WF)** - Fire risk during dry season
5. **Drought (DR)** - Meteorological and agricultural drought
6. **Cyclones (CY)** - Tropical storm systems
7. **Coastal Floods (CF)** - Storm surge and sea level rise
8. **Urban Floods (UF)** - Drainage system overflow
9. **Tsunamis (TS)** - Ocean-generated waves
10. **Volcanoes (VO)** - Volcanic activity
11. **Extreme Heat (EH)** - Heatwave events

### Hazard Level Mapping

ThinkHazard provides four levels, which we convert to numeric scores:

| ThinkHazard Level | Abbreviation | Score | Return Period | Interpretation |
|-------------------|--------------|-------|---------------|----------------|
| Very Low | VLO | 0.5 | >200 years | Rare events, minimal concern |
| Low | LOW | 1 | 100-200 years | Occasional events, prepare |
| Medium | MED | 2 | 25-100 years | Regular events, plan for |
| High | HIG | 3 | <25 years | Frequent events, critical risk |

### Aggregation Method

The hazard severity score aggregates multiple hazard types:

```python
def calculate_hazard_severity(hazards_dict):
    total_score = 0
    
    for hazard_type, level in hazards_dict.items():
        if level == 'HIG':
            total_score += 3
        elif level == 'MED':
            total_score += 2
        elif level == 'LOW':
            total_score += 1
        elif level == 'VLO':
            total_score += 0.5
    
    # Normalize to 0-5 scale
    # Assuming max 5 hazards at 'HIG' = 15 points
    normalized_score = min(int((total_score / 15) * 5), 5)
    
    return normalized_score
```

### Sugarcane-Specific Hazard Impacts

Not all hazards affect sugarcane equally. Here's why each matters:

#### High Impact Hazards

**Floods (FL)** - Critical
- Waterlogged fields kill roots within 5-7 days
- Soil erosion removes topsoil
- Delays harvest, reducing sucrose content
- Equipment cannot access fields
- **Historical impact**: 20-40% yield loss in affected areas

**Drought (DR)** - Critical
- Reduces cane weight (less water = less biomass)
- Lowers sucrose accumulation
- Increases pest susceptibility
- Irrigation is expensive and not always feasible
- **Historical impact**: 25-50% yield loss in severe droughts

**Wildfires (WF)** - High
- Brazil uses pre-harvest burning (though declining)
- Uncontrolled fires destroy crops completely
- Dry season fires can spread from adjacent areas
- Smoke affects worker health
- **Historical impact**: Total loss in burned areas

#### Moderate Impact Hazards

**Landslides (LS)** - Moderate
- Damages roads and transportation infrastructure
- Affects supply chain, not crops directly
- More relevant for hillside plantations
- **Impact**: Logistical delays, access issues

**Extreme Heat (EH)** - Moderate
- Already captured in climate risk assessment
- Heat stress reduces productivity
- **Impact**: 10-30% yield reduction during heatwaves

#### Low Impact Hazards

**Earthquakes (EQ)** - Low
- Brazil has low seismicity
- Main concern: processing facility damage
- **Impact**: Operational disruption, not agricultural

**Cyclones (CY)** - Low
- Southern Brazil occasionally affected
- Wind damage to standing cane
- **Impact**: 5-15% yield loss if direct hit

### Interpretation

| Score | Category | Interpretation | Business Implication |
|-------|----------|----------------|---------------------|
| 0-1 | Very Low | Minimal multi-hazard exposure | Standard risk management |
| 2 | Low | Some hazard exposure | Basic preparedness measures |
| 3 | Medium | Notable multi-hazard risk | Enhanced monitoring and insurance |
| 4 | High | Multiple hazards at elevated levels | Comprehensive risk management plan |
| 5 | Very High | Severe multi-hazard exposure | Consider risk transfer or diversification |

### Limitations

1. **Administrative Level**: ThinkHazard uses ADM2 (district) level; may not reflect site-specific conditions
2. **Static Assessment**: Does not account for climate change impacts on hazard frequency
3. **Data Gaps**: Some Brazilian municipalities lack detailed hazard mapping
4. **Binary Classification**: Hazard is present or not; doesn't quantify magnitude
5. **Interdependencies**: Doesn't model cascading hazards (e.g., flood → landslide)

---

## Aggregate Risk Calculation

### Weighting Rationale

The aggregate risk combines climate and hazard components with weights:

- **Climate Risk**: 60% weight
- **Hazard Risk**: 40% weight

**Rationale**:

1. **Climate is Systemic**: Climate change affects all locations and is predictable
2. **Climate Drives Yield**: Temperature and water directly determine sugarcane productivity
3. **Hazards are Episodic**: Natural hazards are less frequent but can be catastrophic
4. **Hazards Affect Infrastructure**: Impact extends beyond just crop damage

Formula:
```
Aggregate Risk = (0.6 × Climate Likelihood) + (0.4 × Hazard Severity)
```

### Alternative Weighting Scenarios

Users can adjust weights based on their risk appetite and context:

| Scenario | Climate Weight | Hazard Weight | Use Case |
|----------|----------------|---------------|----------|
| Conservative (default) | 60% | 40% | Balanced long-term view |
| Climate-Focused | 80% | 20% | Long-term planning, sustainability reporting |
| Hazard-Focused | 40% | 60% | Insurance, short-term operational risk |
| Equal Weight | 50% | 50% | Uncertain about priorities |

To modify weights, edit `config.py`:
```python
RISK_WEIGHTS = {
    'climate': 0.6,  # Adjust these values
    'hazard': 0.4,
}
```

### Weighted Risk Score (L × I)

The final risk metric incorporates business impact:

```
Weighted Risk Score = Aggregate Risk × Business Impact Score
```

Where:
- **Aggregate Risk**: 0-5 scale (from above)
- **Business Impact Score**: 0-100 scale (impact_percent × 100)

This means:
- A location with 10% of your business (I=10) and high risk (L=5) → Weighted Score = 50
- A location with 1% of your business (I=1) and high risk (L=5) → Weighted Score = 5

**Interpretation**: Weighted risk score prioritizes locations that are both high-risk AND high-impact to your business.

---

## Monte Carlo Simulation

### Why Monte Carlo?

Traditional risk assessment provides point estimates (e.g., "expected loss = 5%"). Real-world outcomes are uncertain. Monte Carlo simulation:

1. **Quantifies Uncertainty**: Generates probability distributions, not single numbers
2. **Risk Metrics**: Calculates Value at Risk (VaR) and Expected Shortfall
3. **Scenario Analysis**: Explores thousands of possible futures
4. **Decision Support**: Helps set risk tolerances and contingency planning

### Simulation Logic

For each location, we simulate 10,000 scenarios of potential yield loss:

```python
n_simulations = 10,000

for i in range(n_simulations):
    # 1. Calculate mean yield loss based on climate likelihood
    mean_loss_pct = (climate_likelihood / 5.0) * 50%
    # Example: likelihood=3 → mean_loss=30%
    
    # 2. Add uncertainty using normal distribution
    yield_loss_pct = normal_distribution(mean=mean_loss_pct, std_dev=15%)
    
    # 3. Clamp to realistic bounds
    yield_loss_pct = clip(yield_loss_pct, min=0%, max=100%)
    
    # 4. Calculate royalty loss
    royalty_loss = yield_loss_pct * business_impact_percent
    
    store_result(royalty_loss)
```

### Normal Distribution Assumption

**Why Normal?**
- Central Limit Theorem: Many independent factors sum to normal distribution
- Weather variability is approximately normal over seasons
- Yield response to climate is roughly linear in moderate ranges
- Mathematically tractable for analysis

**Limitations**:
- Extreme events (tails) may be underestimated
- Fat-tailed distributions (e.g., Lognormal) might be more accurate for catastrophic scenarios
- Assumes independence between locations (addressed in advanced mode with correlation)

### Parameter Selection

#### Mean Loss Factor
```python
mean_loss_pct = (climate_likelihood / 5.0) * 50%
```

- A climate likelihood of **5/5** implies up to **50% average yield loss** in bad years
- Calibrated to historical sugarcane yield variability in Brazil
- Source: CONAB (Brazilian agricultural agency) yield data 1990-2020

#### Standard Deviation
```python
std_dev = 15%
```

- Represents natural variability around the mean
- Based on observed coefficient of variation in sugarcane yields (~15-20%)
- Allows for both better and worse outcomes than the mean
- Higher std_dev = more uncertainty

**Calibration**: Historical analysis shows:
- Good years: Yields 15-30% above trend
- Bad years: Yields 20-40% below trend
- This range is captured by std_dev=15%

### Value at Risk (VaR)

**Definition**: VaR answers "What is the maximum loss we expect in X% of scenarios?"

VaR Levels:
- **VaR 90%**: Exceeded in worst 10% of scenarios
- **VaR 95%**: Exceeded in worst 5% of scenarios  
- **VaR 99%**: Exceeded in worst 1% of scenarios

**Calculation**:
```python
var_95 = percentile(simulated_losses, 95)
```

**Interpretation**:
- VaR(95%) = 8% means: "In 95% of scenarios, losses are 8% or less"
- Equivalently: "There's a 5% chance of losses exceeding 8%"

**Business Use**:
- Set contingency reserves at VaR(95%) level
- Insurance decisions: Cover losses above VaR(95%)
- Risk tolerance: Define acceptable VaR level

### Expected Shortfall (Conditional VaR)

**Definition**: Average loss in the worst scenarios (beyond VaR threshold)

```python
es_95 = mean(losses where losses > var_95)
```

**Why it matters**:
- VaR tells you the threshold, ES tells you how bad it gets beyond that
- ES is more informative for extreme risk
- Regulators prefer ES over VaR (Basel III)

**Example**:
- VaR(95%) = 8%
- ES(95%) = 12%
- **Meaning**: "In the worst 5% of cases, average loss is 12%"

### Correlated vs Independent Losses

**Independent Simulation** (default):
- Assumes risks at different locations are unrelated
- Conservative for diversification benefits
- Simpler, faster computation

**Correlated Simulation** (advanced):
- Accounts for systemic risks (e.g., El Niño affects all of Brazil)
- Uses correlation matrix (typically 0.2-0.4 for regional climate)
- More realistic but computationally intensive

Formula for correlation:
```python
correlation = 0.3  # 30% correlated
correlated_losses = cholesky_decomposition(correlation_matrix) @ independent_losses
```

### Interpretation Table

| Metric | Typical Range | Interpretation |
|--------|---------------|----------------|
| Mean Loss | 1-8% | Expected average loss per year |
| Median Loss | Slightly < Mean | 50% of scenarios are below this |
| Std Deviation | 2-5% | Volatility / unpredictability |
| VaR(90%) | 3-12% | Losses exceed this in 1 in 10 years |
| VaR(95%) | 4-15% | Losses exceed this in 1 in 20 years |
| VaR(99%) | 5-20% | Worst-case planning scenario |
| Max Loss | Up to 50% | Theoretical worst case (rare) |

---

## Limitations and Assumptions

### Data Limitations

1. **Temporal Resolution**
   - Climate: 20-year periods (coarse for year-to-year variability)
   - Hazards: Static assessment (doesn't show trends)
   - **Impact**: May miss short-term fluctuations

2. **Spatial Resolution**
   - Climate: State-level (coarse for microclimate effects)
   - Hazards: District-level (varies by data availability)
   - **Impact**: Local conditions may differ significantly

3. **Model Uncertainty**
   - CMIP6 models have 20-30% uncertainty in regional projections
   - Ensemble median smooths out extreme scenarios
   - **Impact**: Actual changes may be higher or lower

### Methodological Assumptions

1. **Linear Relationships**
   - Assumes yield loss scales linearly with climate change
   - Reality: Non-linear thresholds exist (e.g., >40°C = total crop failure)
   - **Impact**: May underestimate extreme scenarios

2. **Stationary Relationships**
   - Assumes current climate-yield relationships hold in future
   - Reality: Adaptation, new varieties, changed management
   - **Impact**: Actual impacts may be lower with adaptation

3. **Independence of Factors**
   - Climate and hazards treated separately
   - Reality: Climate change affects hazard frequency (e.g., more droughts)
   - **Impact**: Total risk may be underestimated

4. **No Adaptation**
   - Projects current practices into future
   - Reality: Farmers adapt, companies invest in resilience
   - **Impact**: Worst-case scenario; actual outcomes likely better

### What This Tool Does NOT Tell You

1. **Specific Event Timing**: When a drought will occur, just likelihood
2. **Economic Impacts**: Translates to yield loss, not revenue/profit impact
3. **Adaptation Costs**: Doesn't quantify investment needed to reduce risk
4. **Social Impacts**: Worker safety, community resilience not assessed
5. **Market Dynamics**: Price volatility, demand changes not included
6. **Technological Change**: New varieties, precision agriculture not modeled

### When to Seek Additional Analysis

Consider engaging specialists when:

1. **High Stakes Decisions**: Major investments, site selection, insurance
2. **Detailed Planning**: Need site-specific climate projections
3. **Financial Modeling**: Require revenue/profit impact, not just yield
4. **Regulatory Compliance**: TCFD, CDP reporting with verification
5. **Extreme Scenarios**: Stress testing beyond 95th percentile
6. **Adaptation Planning**: Cost-benefit analysis of resilience measures

### Improving the Assessment

To enhance accuracy:

1. **Local Data**: Incorporate farm-level weather station data
2. **Multiple Scenarios**: Run RCP4.5, SSP1-2.6 in addition to SSP5-8.5
3. **Downscaling**: Use regional climate models for finer resolution
4. **Validation**: Compare projections to historical yield data
5. **Expert Elicitation**: Incorporate agronomist knowledge
6. **Dynamic Modeling**: Use crop simulation models (APSIM, DSSAT)

---

## References and Citations

1. **IPCC (2021)**: Climate Change 2021: The Physical Science Basis
2. **World Bank CCKP**: Climate Change Knowledge Portal methodology
3. **ThinkHazard! (2023)**: GFDRR hazard assessment methodology
4. **Marin et al. (2013)**: "Sugarcane crop simulation model parameterization"
5. **EMBRAPA**: Brazilian Agricultural Research Corporation technical bulletins
6. **FAO (2020)**: Irrigation and Drainage Paper: Sugarcane
7. **CONAB**: Brazilian agricultural statistics (1990-2023)
8. **IPCC SRCCL (2019)**: Special Report on Climate Change and Land

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Next Review**: Annually or upon major methodology changes

