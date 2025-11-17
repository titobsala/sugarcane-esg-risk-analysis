# Risk Interpretation Guide

## For Business Decision Makers

This guide helps you understand what the risk scores mean and how to use them for business decisions.

---

## Quick Reference: Risk Scores

### Climate Likelihood Score (0-5)

| Score | Label | What It Means | Action Required |
|-------|-------|---------------|-----------------|
| **0-1** | 🟢 Very Low | Minimal climate change expected | Monitor regularly, business as usual |
| **2** | 🟡 Low | Noticeable but manageable changes | Begin adaptation planning, research new varieties |
| **3** | 🟠 Medium | Significant climate challenges ahead | Implement adaptation measures, invest in irrigation/drainage |
| **4** | 🔴 High | Major climate risks | Urgent action required, consider diversification |
| **5** | 🔴 Very High | Severe climate disruption | Strategic review needed, high-risk location |

### What the Numbers Mean

**Score 2 Example**: São Paulo might see:
- +1.8°C average temperature by 2050
- 10-15% change in rainfall patterns
- **Impact**: Need drought-resistant varieties, adjust planting calendar

**Score 4 Example**: Interior locations might face:
- +2.8°C temperature increase
- 25% reduction in rainfall OR flooding increase
- **Impact**: Major infrastructure investment needed (irrigation, drainage)

---

## Understanding the Dashboard

### Tab 1: Executive Summary

**Key Metrics to Watch**:

1. **Portfolio VaR (95%)**
   - **What it is**: Maximum expected loss in 95% of scenarios
   - **Example**: VaR = 8% means "95% chance losses are ≤8% of royalties"
   - **Use it for**: Setting financial reserves, insurance decisions
   
2. **High Risk Locations**
   - **What it is**: Count of locations with aggregate risk ≥4
   - **Action threshold**: >20% of portfolio → Need risk reduction strategy
   
3. **Total Weighted Risk**
   - **What it is**: Sum of all (Risk × Impact) scores
   - **Trend**: Track quarterly to see if portfolio risk is increasing

**Decision Framework**:
```
IF High Risk Locations > 5 AND Portfolio VaR > 10%
THEN → Urgent: Convene risk committee, develop mitigation plan

IF High Risk Locations 2-5
THEN → Moderate: Increase monitoring, pilot adaptation projects

IF High Risk Locations 0-1
THEN → Low: Maintain current risk management
```

---

### Tab 2: Climate Risk Analysis

**Understanding the Scatter Plot** (Impact vs Likelihood):

```
        High Impact
             |
  ⚠️ CRITICAL|  🚨 URGENT
    MONITOR  |  ACTION
  -----------+-----------
    ✅ LOW   |  ⚡ WATCH
    PRIORITY |  CLOSELY
             |
        Low Impact
```

**Quadrant Interpretation**:
- **Top Right** (High Impact, High Likelihood): Your #1 priorities
- **Top Left** (High Impact, Low Likelihood): Monitor closely, prepare contingency
- **Bottom Right** (Low Impact, High Likelihood): Accept risk or minor adjustments
- **Bottom Left** (Low Impact, Low Likelihood): Minimal concern

**Temperature Projections**:
- **< +1.5°C**: Manageable with minor adjustments
- **+1.5 to +2.5°C**: Significant adaptation required
- **> +2.5°C**: Fundamental changes to operations needed

**Sugarcane Tolerances**:
- Optimal growth: 21-27°C
- Stress begins: >30°C
- Severe stress: >35°C (growth stops)

**Precipitation Changes**:
- **-10% to +10%**: Manageable with good practices
- **-20% or less**: Major drought risk → irrigation essential
- **+20% or more**: Flooding risk → drainage investment needed

---

### Tab 3: Natural Hazards

**Hazard Priority Matrix** (for Sugarcane):

| Hazard | Impact on Operations | Priority | Mitigation Options |
|--------|---------------------|----------|-------------------|
| **Floods** | Crop destruction, harvest delays | 🔴 Critical | Drainage, field location, insurance |
| **Drought** | Yield reduction 25-50% | 🔴 Critical | Irrigation, water storage, varieties |
| **Wildfires** | Total crop loss in affected areas | 🟠 High | Firebreaks, monitoring, controlled burns |
| **Landslides** | Road/infrastructure damage | 🟡 Medium | Route planning, alternative access |
| **Earthquakes** | Processing facility damage | 🟢 Low | Building codes, insurance |

**When to Act**:
- **High Level Flood/Drought**: Mandatory risk mitigation
- **Medium Level**: Monitor and prepare response plans
- **Low Level**: Basic preparedness sufficient

**Multi-Hazard Locations**:
- 3+ hazards at Medium/High → Comprehensive risk management plan required
- Consider whether location is economically viable long-term

---

### Tab 4: Monte Carlo Simulations

**Understanding Value at Risk (VaR)**:

**VaR (95%) = 8%** means:
- ✅ In 95 out of 100 years, losses will be ≤8%
- ⚠️ In 5 out of 100 years, losses will be >8%
- 📊 Plan for the 95% case, prepare for the 5% case

**Using VaR for Business Decisions**:

1. **Financial Reserves**:
   ```
   Reserve = VaR(95%) × Annual Royalty Revenue
   Example: VaR(95%) = 8%, Revenue = $10M → Reserve = $800K
   ```

2. **Insurance Coverage**:
   ```
   Insure losses between VaR(95%) and VaR(99%)
   Retain risk below VaR(95%)
   ```

3. **Risk Tolerance**:
   ```
   Conservative: Set reserves at VaR(99%)
   Moderate: VaR(95%)
   Aggressive: VaR(90%)
   ```

**Distribution Shape Matters**:
- **Narrow distribution** (low std dev): Predictable risk
- **Wide distribution** (high std dev): Uncertain outcomes → need bigger reserves

**Loss Exceedance Curves**:
- Shows probability of exceeding any loss level
- **Use**: "What's the chance of losing >10%?" → Read from curve

---

### Tab 5: Value Chain Risk

**Concentration Risk**:

**Herfindahl Index** interpretation:
- **0.00 - 0.10**: Highly diversified ✅
- **0.10 - 0.20**: Moderate concentration ⚠️
- **0.20 - 0.40**: High concentration 🔴
- **> 0.40**: Dangerous concentration 🚨

**Example**:
```
Herfindahl = 0.25
Equivalent to having just 4 equal-sized clients (1/0.25 = 4)
→ Risk: Loss of 1-2 clients is catastrophic
→ Action: Diversify client base
```

**Upstream vs Downstream Risk**:
- **Higher Supplier Risk**: Supply disruption affects all clients
- **Higher Client Risk**: Revenue concentration, but supply intact

**Decision Matrix**:
```
IF Supplier Risk > Client Risk
THEN → Diversify supplier base, dual sourcing

IF Client Risk > Supplier Risk
THEN → Diversify client portfolio, long-term contracts

IF Both High
THEN → Comprehensive supply chain resilience program
```

---

### Tab 6: Sensitivity Analysis

**What Stress Testing Shows**:
- How stable are your risk rankings?
- What if your top client grows to 20% of business?
- Which locations are "on the edge" of risk categories?

**Interpreting Results**:

**Scenario 1: Ranking Stays Same**
```
Top risk remains #1 even with +50% impact
→ Robust identification, focus mitigation here
```

**Scenario 2: Ranking Changes**
```
Different location becomes #1 under stress
→ Portfolio sensitive to assumptions
→ Action: Stress test regularly, flexible planning
```

**Business Use Cases**:
1. **Growth Planning**: "If we expand client X, what's our risk exposure?"
2. **Contract Negotiations**: "Is this client worth the risk?"
3. **Budget Allocation**: "Which risk mitigation gives best ROI?"

---

## Actionable Decision Framework

### Immediate Actions (Next 30 Days)

**If you see**:
- ✅ 5+ locations with aggregate risk ≥4
- ✅ Portfolio VaR(95%) >10%
- ✅ Herfindahl Index >0.25

**Then do**:
1. Schedule executive risk review meeting
2. Identify top 3 risk locations
3. Request detailed site assessments
4. Review insurance coverage adequacy

### Short-Term Actions (3-6 Months)

**For High-Risk Locations**:
1. Conduct detailed vulnerability assessment
2. Develop location-specific adaptation plans
3. Budget for risk mitigation investments
4. Explore risk transfer options (insurance, contracts)

**Portfolio-Level**:
1. Diversification strategy if Herfindahl >0.20
2. Establish climate risk monitoring dashboard
3. Include climate risk in supplier/client due diligence

### Medium-Term Actions (1-2 Years)

**Adaptation Investments**:
- **Drought Risk**: Irrigation systems, water storage
- **Flood Risk**: Drainage infrastructure, field elevation
- **Heat Risk**: Shade structures, new varieties
- **Fire Risk**: Firebreaks, monitoring systems

**Strategic Decisions**:
- Phase out highest-risk locations (score 5)
- Grow business in lower-risk regions (score 0-2)
- Negotiate long-term contracts tied to climate performance

### Long-Term Strategy (3-5 Years)

**Climate Resilience Program**:
1. **Research & Development**: Climate-adapted varieties
2. **Infrastructure**: Major water management systems
3. **Diversification**: Geographic and crop diversification
4. **Insurance**: Portfolio-level parametric insurance
5. **Monitoring**: Real-time climate and hazard monitoring

---

## Red Flags: When to Escalate

🚨 **Immediate Escalation Required**:
- Single location represents >25% of business AND has risk score ≥4
- Portfolio VaR(99%) >20% of annual revenue
- 3+ consecutive quarters of increasing aggregate risk
- Major hazard event (flood, drought) affecting top 5 locations

⚠️ **Management Attention Needed**:
- Aggregate risk trending upward >10% per year
- New high-risk location enters portfolio
- VaR(95%) exceeds available financial reserves
- Supplier concentration index >0.30

---

## Common Questions

**Q: What's an acceptable level of risk?**
A: Depends on your risk appetite, but guidelines:
- Conservative: VaR(95%) <5%, <3 high-risk locations
- Moderate: VaR(95%) <10%, <5 high-risk locations
- Growth-focused: VaR(95%) <15%, monitor closely

**Q: Should I exit a location with risk score 5?**
A: Not necessarily. Consider:
- Can risk be mitigated? (irrigation, insurance)
- What's the business impact? (if <5%, may be acceptable)
- Are there alternatives? (diversification options)
- Time horizon: Exit over 3-5 years, not immediately

**Q: How often should I run this analysis?**
A: 
- **Quarterly**: Track VaR and top risks
- **Annually**: Full analysis with updated data
- **Ad-hoc**: Before major decisions (new contracts, investments)

**Q: My results don't match my experience. Why?**
A: Possible reasons:
- Local conditions differ from state-level data
- You've already adapted (tool assumes no adaptation)
- Short-term weather vs long-term climate
- Tool is forward-looking (2040-2059), not current

**Q: What if I disagree with the risk scores?**
A: Tool is meant to inform, not dictate. Combine with:
- Local knowledge from farm managers
- Historical yield data from your operations
- Expert agronomist opinions
- Consider adjusting weights in config.py

---

## Integration with ESG Reporting

### TCFD Alignment

**Strategy**: Use this tool to identify climate risks in business strategy
**Risk Management**: Monte Carlo results quantify financial impact
**Metrics & Targets**: Track VaR and high-risk location count quarterly
**Scenario Analysis**: Sensitivity tab shows stressed scenarios

### CDP Climate Disclosure

**C2.3 (Climate Risks)**: Reference the methodology and risk scores
**C2.4 (Financial Impact)**: Use Monte Carlo VaR estimates
**C3.1 (Adaptation)**: Cite mitigation actions for high-risk locations

---

## Limitations to Remember

**This Tool Does NOT**:
- ❌ Predict specific events or timing
- ❌ Account for adaptation you've already done
- ❌ Include economic factors (prices, costs)
- ❌ Model social impacts (labor, community)
- ❌ Guarantee outcomes (probabilistic, not deterministic)

**This Tool DOES**:
- ✅ Identify relative risk across locations
- ✅ Quantify uncertainty through probabilities
- ✅ Provide consistent, data-driven framework
- ✅ Support strategic decision-making
- ✅ Meet ESG reporting requirements

---

## Getting More Help

**For Technical Questions**:
- See `METHODOLOGY.md` for calculation details
- See `DATA_SOURCES.md` for data provenance

**For Business Strategy**:
- Consult with climate risk advisory firms
- Engage agronomists for location-specific advice
- Work with insurance brokers for risk transfer

**To Customize the Tool**:
- Edit `config.py` for different weights or thresholds
- See README for configuration options

---

**Remember**: This tool provides information to support decisions, not make them for you. Combine quantitative analysis with qualitative judgment, local knowledge, and expert advice.

**Document Version**: 1.0  
**Last Updated**: 2025  
**For Questions**: Contact ESG risk analysis team

