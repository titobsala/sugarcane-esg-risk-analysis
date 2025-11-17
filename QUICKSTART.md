# Quick Start Guide - ESG Risk Analysis Tool

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /home/tito-sala/Code/Exo/risk-test
poetry install
```

This will install all required packages:
- streamlit (dashboard framework)
- plotly (interactive visualizations)
- pandas, numpy (data processing)
- requests (API calls)
- scipy (statistical functions)
- And more...

### Step 2: Activate Environment

```bash
poetry shell
```

### Step 3: Launch Dashboard

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📊 Using the Dashboard

1. **Click "Run Analysis"** in the sidebar
   - This will collect data from World Bank CCKP API
   - And fetch hazard data from ThinkHazard!
   - Takes 15-30 minutes on first run due to API calls

2. **Explore the 6 Tabs:**
   - 📊 **Executive Summary**: High-level KPIs and top risks
   - 🌡️ **Climate Risk**: Temperature and precipitation projections
   - ⚠️ **Natural Hazards**: Multi-hazard assessment
   - 🎲 **Monte Carlo**: Probabilistic loss simulations
   - 🔗 **Value Chain**: Supplier vs Client risk analysis
   - 🔬 **Sensitivity**: Stress testing and what-if scenarios

3. **Export Results** using the sidebar button

## 💡 Tips

### Faster Development
For development/testing, reduce simulation count in `config.py`:
```python
MONTE_CARLO_CONFIG = {
    'n_simulations': 1000,  # Instead of 10000
    # ...
}
```

### API Rate Limits
If you encounter rate limiting:
- The tool has built-in delays and retries
- Edit `config.py` to increase `CCKP_RATE_LIMIT_DELAY` if needed

### Offline Testing
Once you've run the analysis once, you can add caching to avoid repeated API calls during development.

## 🔧 Alternative Usage

### Command Line (No UI)
```bash
python risk_analysis_engine.py
```

This runs the full analysis and exports CSV files.

### Original Scripts (Legacy)
```bash
# Climate risk only
python sugarcane.py

# Monte Carlo only
python monte-carlo-risk.py
```

## 📁 Output Files

Results are saved to `exports/` directory:
- `risk_analysis_results.csv` - Full risk data
- `monte_carlo_results.csv` - Simulation results
- `portfolio_summary.csv` - Portfolio metrics

## 🐛 Troubleshooting

### ImportError: No module named 'X'
Solution: Run `poetry install` again

### API Errors
- Check internet connection
- World Bank and ThinkHazard APIs may have downtime
- Tool will retry with exponential backoff

### Slow Performance
- First run is slow due to API calls (expected)
- Consider implementing caching for repeated runs
- Reduce number of Monte Carlo simulations for testing

## 📖 Full Documentation

See `README_ESG_TOOL.md` for comprehensive documentation including:
- Detailed methodology
- Configuration options
- ESG alignment
- Data sources
- Risk scoring algorithms

## ✅ Validation

To verify installation:
```bash
python -c "import streamlit, plotly, pandas; print('✓ All dependencies installed')"
```

To test module structure:
```bash
python -c "import config, risk_analysis_engine; print('✓ All modules working')"
```

---

**Ready to analyze sugarcane supply chain risks!** 🌱

