# Future Enhancements

## Overview

This document outlines planned improvements to the ESG Risk Analysis Tool. All necessary research and design work has been completed. Implementation is prioritized and ready for development.

---

## Phase 2: Dashboard UI Enhancements

### Status: NASA POWER ✅ Complete | Dashboard UI Pending

### 1. Confidence Indicators & Data Quality Features

**Priority**: HIGH
**Estimated Effort**: 1-2 days
**Status**: Framework ready, UI implementation pending

**Dashboard Enhancements to Implement**:
1. **Confidence Badges**: Add 🟢🟡🔴 confidence indicators to all location tables
2. **Data Quality Tab**: Comprehensive dashboard showing data source status and coverage
3. **Methodology Tooltips**: Interactive help and expandable explanations for all metrics
4. **Enhanced Export**: Additional data format options and filtered exports
5. **UI Polish**: Improved navigation and user experience elements

---

### 2. Enhanced Scoring to 0-10 Scale

**Priority**: MEDIUM  
**Estimated Effort**: 1 day  
**Status**: Algorithm designed, implementation pending

**Rationale**:
- Current 0-5 scale lacks granularity with 8+ risk variables
- 0-10 scale allows better differentiation between locations
- Maintain backward compatibility by normalizing to 0-5 for display

**Implementation**:
```python
def calculate_enhanced_climate_likelihood(geocode):
    """Enhanced scoring with 0-10 internal scale"""
    risk_score = 0  # Now accumulates to 10 max
    
    # Existing variables (3 variables × 2 points = 6 points max)
    # + New variables (4 variables × 1 point = 4 points max)
    # Total: 10 points maximum
    
    # Temperature, tasmax, precipitation (as before)
    risk_score += calculate_temp_risk()      # 0-2
    risk_score += calculate_tasmax_risk()    # 0-2
    risk_score += calculate_precip_risk()    # 0-2
    
    # New from NASA POWER
    risk_score += calculate_cdd_risk()       # 0-1
    risk_score += calculate_heat_days_risk() # 0-1
    risk_score += calculate_gdd_risk()       # 0-1
    risk_score += calculate_solar_risk()     # 0-1
    
    # Normalize to 0-5 for display
    display_score = (risk_score / 10) * 5
    
    return {
        'internal_score': risk_score,  # 0-10 for calculations
        'display_score': round(display_score, 1),  # 0-5 for UI
        'confidence': calculate_confidence(data_available)
    }
```

**Dashboard Updates**: Display shows 0-5, tooltips show 0-10 internal score

---

## Phase 3: Dashboard Enhancements

### Status: Design Complete, Implementation Pending

### 1. Confidence Indicators

**Priority**: HIGH  
**Estimated Effort**: 1 day  
**Status**: Confidence scoring framework in `config.py`, UI pending

**Implementation**:
1. Add `confidence_score` column to risk data DataFrame
2. Calculate per-location based on data availability
3. Display confidence badges in all tables (🟢 High, 🟡 Medium, 🔴 Low)
4. Add confidence filter in sidebar
5. Tooltip explains what affects confidence

**Confidence Calculation** (already in `config.py`):
```python
def calculate_confidence_score(data_availability):
    score = 0
    if data_availability['cckp']['tas']: score += 20
    if data_availability['cckp']['tasmax']: score += 10
    if data_availability['cckp']['pr']: score += 20
    if data_availability['thinkhazard']['flood']: score += 10
    if data_availability['thinkhazard']['drought']: score += 10
    if data_availability['nasa_power']['cdd']: score += 15
    if data_availability['nasa_power']['extreme_heat']: score += 10
    if data_availability['firms']['fire_density']: score += 5
    return score  # 0-100
```

**UI Enhancement**:
- Add badge next to each location: `Location 🟢 95%`
- Filter: "Show only High Confidence (>80%)" checkbox
- Summary: "23/26 locations have high confidence data"

---

### 2. Methodology Links & Tooltips

**Priority**: MEDIUM  
**Estimated Effort**: 1 day  
**Status**: Documentation complete, linking pending

**Implementation**:
1. Add `st.info()` boxes at top of each tab linking to relevant docs
2. Add tooltips to all metrics using `help=` parameter
3. Add "Learn More" buttons with `st.expander()` for methodology
4. Link chart titles to methodology sections

**Example**:
```python
st.metric(
    "Climate Likelihood",
    f"{score}/5",
    help="Based on temperature and precipitation projections. "
         "Click 'Learn More' below for details."
)

with st.expander("📖 How is Climate Likelihood calculated?"):
    st.markdown("""
    This score evaluates three variables:
    1. Temperature change (see [METHODOLOGY.md](docs/METHODOLOGY.md#temperature))
    2. Max temperature change
    3. Precipitation change
    
    Thresholds based on IPCC assessments and sugarcane physiology research.
    """)
```

---

### 3. Data Quality Tab

**Priority**: MEDIUM  
**Estimated Effort**: 1 day  
**Status**: Framework designed, implementation pending

**Tab Content**:

**Section 1: Data Coverage Matrix**
```
Location           | CCKP | ThinkHazard | NASA POWER | FIRMS | Confidence
-------------------|------|-------------|------------|-------|------------
NOVO HORIZONTE/SP  | ✅✅✅ | ✅✅        | ⏳         | ⏳    | 🟡 60%
SÃO PAULO/SP       | ✅✅✅ | ✅✅        | ⏳         | ⏳    | 🟡 60%
...
```

**Section 2: Data Source Status**
- CCKP: ✅ Operational, last updated 2023
- ThinkHazard: ✅ Operational, data vintage varies
- NASA POWER: ⏳ Configured, not yet integrated
- FIRMS: ⏳ Pending API key registration

**Section 3: Known Limitations**
- List of locations with missing data
- Explanation of fallbacks (e.g., state-level when municipality unavailable)
- Data update schedule

**Section 4: Validation Metrics**
- Cross-validation between data sources
- Comparison with historical observations
- Model uncertainty bands

---

## Phase 4: Advanced Features

### Future Enhancements (6-12 months)

### 1. Historical Validation Module

**Purpose**: Validate projections against observed data

**Implementation**:
- Fetch historical weather from NASA POWER (1981-2020)
- Compare CCKP hindcasts to observations
- Calculate bias correction factors
- Display validation statistics in Data Quality tab

### 2. Multi-Year Trend Analysis

**Purpose**: Track how risk evolves over time

**Implementation**:
- Store analysis results in SQLite database
- Track quarterly risk scores
- Display trend charts showing risk evolution
- Alert when risk increases >10% quarter-over-quarter

### 3. Automated PDF Report Generation

**Purpose**: Professional reports for stakeholders

**Implementation**:
- Use `reportlab` or `weasyprint`
- Template-based report with branding
- Include executive summary, key charts, recommendations
- Export button: "Generate PDF Report"

### 4. Email Alerts

**Purpose**: Proactive risk notifications

**Implementation**:
- Configure SMTP settings
- Set alert thresholds (e.g., VaR >15%)
- Weekly summary emails
- Immediate alerts for high-risk changes

### 5. Financial Impact Modeling

**Purpose**: Translate yield loss to revenue/profit

**Implementation**:
- Add revenue and cost parameters to config
- Link yield loss to profit margins
- Calculate financial VaR in currency units
- Integrate with corporate financial models

### 6. Machine Learning Integration

**Purpose**: Pattern detection and prediction

**Implementation**:
- Train models on historical yield vs climate data
- Predict location-specific yield response
- Anomaly detection for unusual risk patterns
- Feature importance analysis

---

## Implementation Priority Matrix

| Enhancement | Business Value | Technical Complexity | Priority | Effort |
|-------------|---------------|---------------------|----------|--------|
| **NASA POWER Integration** | High (better drought/heat data) | Medium | ✅ **COMPLETE** | 2-3 days |
| **Confidence Indicators** | High (data quality transparency) | Low | 🔴 HIGH | 1 day |
| **Enhanced 0-10 Scoring** | Medium (better granularity) | Low | 🟠 MEDIUM | 1 day |
| **Methodology Tooltips** | Medium (user understanding) | Low | 🟠 MEDIUM | 1 day |
| **Data Quality Tab** | Medium (transparency) | Low | 🟠 MEDIUM | 1 day |
| **FIRMS Integration** | Medium (wildfire quantification) | Medium | 🟠 MEDIUM | 1-2 days |
| **PDF Reports** | Low (nice-to-have) | Medium | 🟡 LOW | 2-3 days |
| **Historical Validation** | Low (academic interest) | High | 🟡 LOW | 3-5 days |
| **ML Integration** | Low (experimental) | Very High | 🟡 LOW | 2-3 weeks |

---

## Quick Wins Status

### Phase 2 Completed (November 2025)

1. ✅ **NASA POWER integration** (2-3 days) - **COMPLETED**
   - Full integration with 5 agricultural meteorology variables
   - Enhanced climate scoring with drought and heat stress indicators
   - Data confidence scoring system implemented
   - 90% confidence achieved for locations with full data

### Remaining Quick Wins (Can be done in 1 week)

2. ⏳ Confidence indicators UI display (1 day)
3. ⏳ Methodology tooltips and links (1 day)
4. ⏳ Data Quality tab (1 day)
5. ⏳ Enhanced 0-10 scoring display (1 day)

**Completed**: NASA POWER integration (2-3 days)  
**Remaining**: 4 days of focused development for UI enhancements

---

## Getting Started with Implementation

### For NASA POWER Integration:

1. Review `DATA_SOURCES.md` section on NASA POWER
2. Configuration is already in `config.py` (`NASA_POWER_*` variables)
3. Add function to `risk_data_collector.py`:

```python
def fetch_nasa_power_climatology(lat, lon, variables, start_year=2000, end_year=2020):
    """
    Fetch NASA POWER climatology data
    """
    base_url = config.NASA_POWER_BASE_URL
    params = {
        'parameters': ','.join(variables),
        'community': 'AG',
        'longitude': lon,
        'latitude': lat,
        'start': f'{start_year}0101',
        'end': f'{end_year}1231',
        'format': 'JSON'
    }
    
    response = requests.get(base_url, params=params, timeout=config.NASA_POWER_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    
    # Parse and return
    return parse_nasa_power_response(data)
```

4. Integrate into `calculate_climate_likelihood()` function
5. Update dashboard to display new variables
6. Test with 2-3 locations before full rollout

### For Confidence Indicators:

1. Review `config.py` section on confidence scoring
2. Add to `collect_location_risk_data()`:

```python
# Calculate confidence
confidence_score = calculate_data_confidence(
    has_cckp_temp=True if baseline.get('tas') else False,
    has_cckp_precip=True if baseline.get('pr') else False,
    has_thinkhazard=len(hazards) > 0,
    # Add more as data sources expand
)
result['confidence_score'] = confidence_score
result['confidence_level'] = get_confidence_level(confidence_score)
```

3. Update dashboard tables to show confidence badges
4. Add confidence filter to sidebar

---

## Documentation Status

All enhancement documentation is complete:
- ✅ Methodology fully documented (METHODOLOGY.md)
- ✅ Data sources researched and documented (DATA_SOURCES.md)
- ✅ Scientific basis with citations (SCIENTIFIC_BASIS.md)
- ✅ Business interpretation guide (INTERPRETATION_GUIDE.md)
- ✅ Configuration parameters added (config.py)
- ✅ Implementation roadmap (this document)

**Next Step**: Begin implementation following priority order above.

---

**Document Version**: 1.0  
**Created**: 2025  
**Status**: Ready for Implementation

