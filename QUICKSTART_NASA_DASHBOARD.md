# NASA POWER Dashboard Quick Start

**Version**: 2.0 Enhanced
**Status**: ✅ Ready to Use

---

## 🚀 Launch Enhanced Dashboard

```bash
poetry shell
streamlit run app.py
```

**What's New**: NASA POWER agricultural indicators with 90% data confidence (vs 60% previously)

---

## 🎯 Key NASA POWER Features

### Executive Summary Tab
- **Data Confidence KPI**: 🟢 High (80-90%) for NASA POWER locations
- **Quality Overview**: Pie chart showing confidence distribution across portfolio

### Climate Risk Tab - NASA POWER Section
**5 Interactive Analysis Tabs**:

| Tab | Purpose | Key Metrics |
|-----|---------|-------------|
| 📋 **Full Table** | Complete dataset | All indicators + CSV export |
| 🌵 **Drought Risk** | Water stress analysis | CDD >20 days = Medium risk |
| 🌡️ **Heat Stress** | Thermal stress analysis | >35°C days >30 = Medium risk |
| 🌱 **Growing Conditions** | Productivity assessment | GDD 4000-6000 = Optimal |
| ☀️ **Solar Radiation** | Photosynthesis potential | >18 MJ/m²/day = Excellent |

### Enhanced Features
- **Confidence Columns**: Data quality scores in all tables
- **Risk Thresholds**: Color-coded indicators (🔴 High, 🟡 Medium, 🟢 Low)
- **Export Options**: CSV download for NASA POWER datasets

---

---

## 📊 Quick Interpretation Guide

### Risk Thresholds
| Indicator | Low Risk | Medium Risk | High Risk |
|-----------|----------|-------------|-----------|
| **Drought (CDD)** | <20 days | 20-30 days | >30 days |
| **Heat Stress** | <30 days >35°C | 30-50 days >35°C | >50 days >35°C |
| **GDD Range** | 4000-6000 | <3500 or >6500 | N/A |
| **Solar Radiation** | >18 MJ/m²/day | 15-18 MJ/m²/day | <15 MJ/m²/day |

### Example: PIRACICABA/SP
```
Climate Score: 2.5/5 (vs 1.0 before)
Confidence: 90% High (vs 60% before)
├─ Drought: 🟡 MEDIUM (28.4 CDD days)
├─ Heat Stress: 🔴 HIGH (~55 extreme days)
├─ Growing Conditions: 🟢 OPTIMAL (3863 GDD)
└─ Solar Radiation: 🟢 EXCELLENT (18.56 MJ/m²/day)
```
**Insight**: Medium drought + High heat stress, but optimal conditions suggest good productivity potential.

---

## 🔍 Analysis Workflow

1. **Check Quality** → Executive Summary → Data Confidence KPI
2. **Identify Risks** → Climate Risk → NASA POWER tabs
3. **Compare Locations** → Full Table for complete overview
4. **Export Data** → CSV download for further analysis

---

## 📥 Export Options

**NASA POWER Data**: Climate Risk → NASA POWER → Full Table → "📥 Download"

**Includes**: Confidence %, drought risk, heat stress, GDD, solar radiation

---

## ⚡ Quick Start

- [x] `NASA_POWER_ENABLED = True` in config.py
- [x] Run `poetry shell && streamlit run app.py`
- [x] Click "Run Analysis" in sidebar
- [x] Explore NASA POWER section in Climate Risk tab

---

## 📚 Documentation

- **Methodology**: `docs/METHODOLOGY.md`
- **Data Sources**: `docs/DATA_SOURCES.md`
- **Implementation**: `docs/IMPLEMENTATION_SUMMARY.md`

---

**Ready to use!** Focus on NASA POWER tabs for agricultural climate intelligence.

