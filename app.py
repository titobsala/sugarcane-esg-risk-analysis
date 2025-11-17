"""
ESG Risk Analysis Dashboard
Streamlit application for interactive risk visualization and reporting
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Local imports
import config
import risk_analysis_engine as engine
import monte_carlo_integrated as mc
import utils

# Page configuration
st.set_page_config(
    page_title="ESG Risk Analysis",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .high-risk {
        color: #d62728;
        font-weight: bold;
    }
    .medium-risk {
        color: #ff7f0e;
        font-weight: bold;
    }
    .low-risk {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'analysis_run' not in st.session_state:
    st.session_state.analysis_run = False
if 'risk_data' not in st.session_state:
    st.session_state.risk_data = None
if 'mc_results' not in st.session_state:
    st.session_state.mc_results = None
if 'portfolio_summary' not in st.session_state:
    st.session_state.portfolio_summary = None


def run_analysis():
    """Run the complete risk analysis"""
    with st.spinner("Collecting risk data from APIs..."):
        # Collect risk data
        risk_data = engine.collect_all_risk_data()
        st.session_state.risk_data = risk_data
    
    with st.spinner("Running Monte Carlo simulations..."):
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current, total, location):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Simulating {location}... ({current}/{total})")
        
        # Run Monte Carlo
        mc_results = engine.run_monte_carlo_analysis(
            risk_data,
            progress_callback=progress_callback
        )
        st.session_state.mc_results = mc_results
        
        progress_bar.empty()
        status_text.empty()
    
    with st.spinner("Calculating portfolio metrics..."):
        # Calculate summary
        portfolio_summary = engine.calculate_portfolio_summary(risk_data, mc_results)
        st.session_state.portfolio_summary = portfolio_summary
    
    st.session_state.analysis_run = True
    st.success("Analysis complete!")


def render_sidebar():
    """Render sidebar with controls"""
    st.sidebar.title("🌱 ESG Risk Analysis")
    st.sidebar.markdown("### Sugarcane Supply Chain")
    st.sidebar.markdown("---")
    
    # Run analysis button
    if st.sidebar.button("🔄 Run Analysis", type="primary", width='stretch'):
        run_analysis()
    
    if st.session_state.analysis_run:
        st.sidebar.success("✅ Analysis Complete")
        
        # Filters
        st.sidebar.markdown("### Filters")
        
        # Risk threshold filter
        risk_threshold = st.sidebar.slider(
            "Min Risk Score",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5
        )
        
        # Location type filter
        location_types = st.sidebar.multiselect(
            "Location Type",
            options=["Client (Royalty)", "Supplier (Seedling)"],
            default=["Client (Royalty)", "Supplier (Seedling)"]
        )
        
        # Export options
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Export")
        
        if st.sidebar.button("📥 Export to CSV"):
            engine.export_results_to_csv(
                st.session_state.risk_data,
                st.session_state.mc_results,
                st.session_state.portfolio_summary,
                output_dir="exports"
            )
            st.sidebar.success("Exported to exports/ folder")
        
        return risk_threshold, location_types
    
    else:
        st.sidebar.info("Click 'Run Analysis' to begin")
        return 0.0, ["Client (Royalty)", "Supplier (Seedling)"]


def render_executive_summary():
    """Render Executive Summary tab"""
    st.header("📊 Executive Summary")
    
    if not st.session_state.analysis_run:
        st.info("Please run the analysis first using the sidebar button.")
        return
    
    summary = st.session_state.portfolio_summary
    risk_data = st.session_state.risk_data
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Locations",
            summary['total_locations'],
            delta=None
        )
    
    with col2:
        st.metric(
            "High Risk Locations",
            summary['high_aggregate_risk_count'],
            delta=None
        )
    
    with col3:
        st.metric(
            "Portfolio VaR (95%)",
            f"{summary.get('total_var_95', 0):.2f}%",
            delta=None,
            help="Value at Risk: Expected maximum loss in 95% of scenarios"
        )
    
    with col4:
        st.metric(
            "Avg Aggregate Risk",
            f"{summary['avg_aggregate_risk']:.2f}/5",
            delta=None
        )
    
    with col5:
        # Data quality metric
        avg_confidence = summary.get('avg_confidence_score', 0)
        confidence_emoji = "🟢" if avg_confidence >= 80 else "🟡" if avg_confidence >= 50 else "🔴"
        st.metric(
            "Data Confidence",
            f"{confidence_emoji} {avg_confidence:.0f}%",
            delta=None,
            help="Average data quality score across all locations (NASA POWER enhanced)"
        )
    
    st.markdown("---")
    
    # Two columns for visualizations
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Value Chain Risk Distribution")
        
        # Pie chart for client vs supplier risk
        value_chain_data = pd.DataFrame({
            'Type': ['Clients', 'Suppliers'],
            'Weighted Risk': [
                summary['client_total_weighted_risk'],
                summary['supplier_total_weighted_risk']
            ]
        })
        
        fig = px.pie(
            value_chain_data,
            values='Weighted Risk',
            names='Type',
            title='Risk Distribution: Clients vs Suppliers',
            color_discrete_sequence=['#ff7f0e', '#2ca02c']
        )
        st.plotly_chart(fig, width='stretch')
    
    with col_right:
        st.subheader("Risk Category Distribution")
        
        # Bar chart for risk categories
        risk_categories = risk_data['aggregate_category'].value_counts()
        
        fig = px.bar(
            x=risk_categories.index,
            y=risk_categories.values,
            title='Number of Locations by Risk Category',
            labels={'x': 'Risk Category', 'y': 'Count'},
            color=risk_categories.index,
            color_discrete_map={
                'High': config.RISK_COLORS['high'],
                'Medium': config.RISK_COLORS['medium'],
                'Low': config.RISK_COLORS['low'],
                'Very Low': config.RISK_COLORS['very_low']
            }
        )
        st.plotly_chart(fig, width='stretch')
    
    # Top Risks Table
    st.subheader("🎯 Top 5 Highest Risk Locations")
    
    top_risks = risk_data.nlargest(5, 'aggregate_weighted_risk')[[
        'location', 'type', 'state', 'climate_likelihood', 
        'hazard_severity', 'aggregate_risk', 'aggregate_weighted_risk'
    ]].copy()
    
    top_risks.columns = ['Location', 'Type', 'State', 'Climate Risk', 
                         'Hazard Risk', 'Aggregate Risk', 'Weighted Risk Score']
    
    st.dataframe(
        top_risks.style.background_gradient(
            subset=['Weighted Risk Score'],
            cmap='Reds'
        ),
        width='stretch'
    )
    
    # Data Quality Overview
    st.subheader("📊 Data Quality Overview - NASA POWER Impact")
    
    if 'confidence_score' in risk_data.columns:
        col_q1, col_q2, col_q3 = st.columns(3)
        
        high_conf = summary.get('high_confidence_count', 0)
        medium_conf = summary.get('medium_confidence_count', 0)
        low_conf = summary.get('low_confidence_count', 0)
        
        with col_q1:
            st.metric(
                "🟢 High Confidence",
                f"{high_conf} locations",
                help="Locations with ≥80% data confidence (full NASA POWER data)"
            )
        
        with col_q2:
            st.metric(
                "🟡 Medium Confidence",
                f"{medium_conf} locations",
                help="Locations with 50-79% data confidence"
            )
        
        with col_q3:
            st.metric(
                "🔴 Low Confidence",
                f"{low_conf} locations",
                help="Locations with <50% data confidence"
            )
        
        # Show confidence distribution
        confidence_dist = risk_data['confidence_level'].value_counts()
        fig_conf = px.pie(
            values=confidence_dist.values,
            names=confidence_dist.index,
            title='Data Confidence Distribution Across Portfolio',
            color=confidence_dist.index,
            color_discrete_map={
                'High': '#2ca02c',
                'Medium': '#ff7f0e',
                'Low': '#d62728'
            }
        )
        st.plotly_chart(fig_conf, use_container_width=True)
        
        st.info("""
        **🛰️ NASA POWER Enhancement**: Locations with NASA POWER data (temperature, precipitation, 
        consecutive dry days, extreme heat, solar radiation) achieve 80-90% confidence scores, 
        providing more reliable risk assessments with agricultural-specific indicators.
        """)
    
    st.markdown("---")
    
    # Geographic Distribution
    st.subheader("🗺️ Geographic Risk Distribution")
    
    # Group by state
    state_risks = risk_data.groupby('state').agg({
        'aggregate_weighted_risk': 'sum',
        'location': 'count'
    }).reset_index()
    state_risks.columns = ['State', 'Total Weighted Risk', 'Location Count']
    state_risks = state_risks.sort_values('Total Weighted Risk', ascending=False)
    
    fig = px.bar(
        state_risks,
        x='State',
        y='Total Weighted Risk',
        title='Total Risk by State',
        color='Total Weighted Risk',
        color_continuous_scale='Reds',
        text='Location Count'
    )
    fig.update_traces(texttemplate='%{text} locations', textposition='outside')
    st.plotly_chart(fig, width='stretch')


def render_climate_risk():
    """Render Climate Risk Analysis tab"""
    st.header("🌡️ Climate Risk Analysis")
    
    if not st.session_state.analysis_run:
        st.info("Please run the analysis first using the sidebar button.")
        return
    
    risk_data = st.session_state.risk_data
    
    # NASA POWER Enhancement Notice
    st.success("""
    **🛰️ Enhanced with NASA POWER Agricultural Meteorology Data**  
    Climate risk assessment now includes: Consecutive Dry Days (drought), Extreme Heat Days, 
    Growing Degree Days (crop development), and Solar Radiation (photosynthesis potential).
    """)
    
    # Climate risk scatter plot
    st.subheader("Impact vs Likelihood Analysis")
    
    fig = px.scatter(
        risk_data,
        x='climate_likelihood',
        y='impact_score',
        size='climate_weighted_risk',
        color='type',
        hover_data=['location', 'state', 'climate_category'],
        title='Climate Risk: Impact vs Likelihood',
        labels={
            'climate_likelihood': 'Climate Likelihood (0-5)',
            'impact_score': 'Business Impact Score',
            'type': 'Location Type'
        },
        color_discrete_map={
            'Client (Royalty)': '#ff7f0e',
            'Supplier (Seedling)': '#2ca02c'
        }
    )
    
    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=1.25, y=75, text="High Impact<br>Low Likelihood", showarrow=False, opacity=0.5)
    fig.add_annotation(x=3.75, y=75, text="High Impact<br>High Likelihood", showarrow=False, opacity=0.5)
    fig.add_annotation(x=1.25, y=25, text="Low Impact<br>Low Likelihood", showarrow=False, opacity=0.5)
    fig.add_annotation(x=3.75, y=25, text="Low Impact<br>High Likelihood", showarrow=False, opacity=0.5)
    
    st.plotly_chart(fig, width='stretch')
    
    # Climate changes by state
    st.subheader("Projected Climate Changes by State")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature changes
        temp_data = []
        for _, row in risk_data.iterrows():
            if row['climate_changes'] and 'temp_change' in row['climate_changes']:
                temp_data.append({
                    'State': row['state'],
                    'Temperature Change (°C)': row['climate_changes']['temp_change']
                })
        
        if temp_data:
            temp_df = pd.DataFrame(temp_data).groupby('State').mean().reset_index()
            temp_df = temp_df.sort_values('Temperature Change (°C)', ascending=False)
            
            fig = px.bar(
                temp_df,
                x='State',
                y='Temperature Change (°C)',
                title='Projected Temperature Increase by State (2040-2059)',
                color='Temperature Change (°C)',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Precipitation changes
        precip_data = []
        for _, row in risk_data.iterrows():
            if row['climate_changes'] and 'precip_change_pct' in row['climate_changes']:
                precip_data.append({
                    'State': row['state'],
                    'Precipitation Change (%)': row['climate_changes']['precip_change_pct']
                })
        
        if precip_data:
            precip_df = pd.DataFrame(precip_data).groupby('State').mean().reset_index()
            precip_df = precip_df.sort_values('Precipitation Change (%)')
            
            fig = px.bar(
                precip_df,
                x='State',
                y='Precipitation Change (%)',
                title='Projected Precipitation Change by State (2040-2059)',
                color='Precipitation Change (%)',
                color_continuous_scale='RdBu_r'
            )
            st.plotly_chart(fig, width='stretch')
    
    # NASA POWER Indicators Section
    st.markdown("---")
    st.subheader("🛰️ NASA POWER Agricultural Indicators")
    
    # Extract NASA POWER data
    nasa_data_available = False
    nasa_indicators = []
    
    for _, row in risk_data.iterrows():
        if row['climate_changes'] and isinstance(row['climate_changes'], dict):
            changes = row['climate_changes']
            if 'consecutive_dry_days' in changes or 'extreme_heat_days' in changes:
                nasa_data_available = True
                
                # Determine drought risk level
                cdd = changes.get('consecutive_dry_days', 0)
                drought_risk = "🔴 HIGH" if cdd > 30 else "🟡 MEDIUM" if cdd > 20 else "🟢 LOW"
                
                # Determine heat stress level
                heat_days = changes.get('extreme_heat_days', 0)
                heat_risk = "🔴 HIGH" if heat_days > 50 else "🟡 MEDIUM" if heat_days > 30 else "🟢 LOW"
                
                # GDD status
                gdd = changes.get('growing_degree_days', 0)
                gdd_status = "🟢 OPTIMAL" if 4000 <= gdd <= 6000 else "🟡 SUBOPTIMAL"
                
                # Solar radiation status
                solar = changes.get('solar_radiation', 0)
                solar_status = "🟢 EXCELLENT" if solar >= 18 else "🟡 ADEQUATE" if solar >= 15 else "🔴 LOW"
                
                nasa_indicators.append({
                    'Location': row['location'],
                    'State': row['state'],
                    'Confidence': f"{row.get('confidence_score', 0):.0f}%",
                    'CDD (days)': f"{cdd:.1f}",
                    'Drought Risk': drought_risk,
                    'Extreme Heat Days': f"{heat_days:.0f}",
                    'Heat Stress': heat_risk,
                    'GDD': f"{gdd:.0f}",
                    'GDD Status': gdd_status,
                    'Solar (MJ/m²/day)': f"{solar:.2f}",
                    'Solar Status': solar_status
                })
    
    if nasa_data_available and nasa_indicators:
        st.markdown("""
        **Agricultural Meteorology Indicators** - Derived from NASA POWER satellite data (2000-2020 baseline):
        - **CDD**: Consecutive Dry Days - indicates drought stress potential
        - **Extreme Heat Days**: Days with temperature >35°C - indicates heat stress
        - **GDD**: Growing Degree Days - optimal range for sugarcane is 4000-6000
        - **Solar Radiation**: Photosynthesis potential - optimal >18 MJ/m²/day
        """)
        
        nasa_df = pd.DataFrame(nasa_indicators)
        
        # Create tabs for different views
        tab_table, tab_drought, tab_heat, tab_gdd, tab_solar = st.tabs([
            "📋 Full Table", 
            "🌵 Drought Risk", 
            "🌡️ Heat Stress", 
            "🌱 Growing Conditions",
            "☀️ Solar Radiation"
        ])
        
        with tab_table:
            st.dataframe(nasa_df, use_container_width=True, hide_index=True)
            
            # Download button
            csv = nasa_df.to_csv(index=False)
            st.download_button(
                label="📥 Download NASA POWER Data",
                data=csv,
                file_name="nasa_power_indicators.csv",
                mime="text/csv"
            )
        
        with tab_drought:
            # Drought risk chart
            nasa_df_sorted = nasa_df.copy()
            nasa_df_sorted['CDD_numeric'] = nasa_df_sorted['CDD (days)'].astype(float)
            nasa_df_sorted = nasa_df_sorted.sort_values('CDD_numeric', ascending=False)
            
            fig_drought = px.bar(
                nasa_df_sorted.head(15),
                x='Location',
                y='CDD_numeric',
                color='Drought Risk',
                title='Top 15 Locations by Drought Risk (Consecutive Dry Days)',
                labels={'CDD_numeric': 'Consecutive Dry Days'},
                color_discrete_map={
                    '🔴 HIGH': '#d62728',
                    '🟡 MEDIUM': '#ff7f0e',
                    '🟢 LOW': '#2ca02c'
                }
            )
            fig_drought.add_hline(y=30, line_dash="dash", line_color="red", 
                                 annotation_text="HIGH risk threshold (30 days)")
            fig_drought.add_hline(y=20, line_dash="dash", line_color="orange",
                                 annotation_text="MEDIUM risk threshold (20 days)")
            st.plotly_chart(fig_drought, use_container_width=True)
        
        with tab_heat:
            # Heat stress chart
            nasa_df_sorted = nasa_df.copy()
            nasa_df_sorted['Heat_numeric'] = nasa_df_sorted['Extreme Heat Days'].astype(float)
            nasa_df_sorted = nasa_df_sorted.sort_values('Heat_numeric', ascending=False)
            
            fig_heat = px.bar(
                nasa_df_sorted.head(15),
                x='Location',
                y='Heat_numeric',
                color='Heat Stress',
                title='Top 15 Locations by Heat Stress (Days >35°C per year)',
                labels={'Heat_numeric': 'Extreme Heat Days'},
                color_discrete_map={
                    '🔴 HIGH': '#d62728',
                    '🟡 MEDIUM': '#ff7f0e',
                    '🟢 LOW': '#2ca02c'
                }
            )
            fig_heat.add_hline(y=50, line_dash="dash", line_color="red",
                              annotation_text="HIGH risk threshold (50 days)")
            fig_heat.add_hline(y=30, line_dash="dash", line_color="orange",
                              annotation_text="MEDIUM risk threshold (30 days)")
            st.plotly_chart(fig_heat, use_container_width=True)
        
        with tab_gdd:
            # Growing degree days chart
            nasa_df_temp = nasa_df.copy()
            nasa_df_temp['GDD_numeric'] = nasa_df_temp['GDD'].astype(float)
            
            fig_gdd = px.scatter(
                nasa_df_temp,
                x='Location',
                y='GDD_numeric',
                color='GDD Status',
                size='GDD_numeric',
                title='Growing Degree Days by Location (Base Temperature: 10°C)',
                labels={'GDD_numeric': 'Growing Degree Days'},
                color_discrete_map={
                    '🟢 OPTIMAL': '#2ca02c',
                    '🟡 SUBOPTIMAL': '#ff7f0e'
                }
            )
            fig_gdd.add_hrect(y0=4000, y1=6000, fillcolor="green", opacity=0.1,
                             annotation_text="Optimal range for sugarcane", annotation_position="top left")
            st.plotly_chart(fig_gdd, use_container_width=True)
            
            st.info("""
            **Growing Degree Days (GDD)** measure heat accumulation for crop development.
            Sugarcane optimal range: 4000-6000 degree-days annually.
            - Too low: Slower growth, extended maturation
            - Too high: Increased stress, reduced sucrose accumulation
            """)
        
        with tab_solar:
            # Solar radiation chart
            nasa_df_temp = nasa_df.copy()
            nasa_df_temp['Solar_numeric'] = nasa_df_temp['Solar (MJ/m²/day)'].astype(float)
            nasa_df_temp = nasa_df_temp.sort_values('Solar_numeric', ascending=True)
            
            fig_solar = px.bar(
                nasa_df_temp,
                x='Location',
                y='Solar_numeric',
                color='Solar Status',
                title='Solar Radiation by Location (Annual Average)',
                labels={'Solar_numeric': 'Solar Radiation (MJ/m²/day)'},
                color_discrete_map={
                    '🟢 EXCELLENT': '#2ca02c',
                    '🟡 ADEQUATE': '#ff7f0e',
                    '🔴 LOW': '#d62728'
                }
            )
            fig_solar.add_hline(y=18, line_dash="dash", line_color="green",
                               annotation_text="Optimal (>18 MJ/m²/day)")
            fig_solar.add_hline(y=15, line_dash="dash", line_color="orange",
                               annotation_text="Adequate threshold (15 MJ/m²/day)")
            st.plotly_chart(fig_solar, use_container_width=True)
            
            st.info("""
            **Solar Radiation** is critical for photosynthesis and sugar accumulation.
            Higher radiation = better productivity (up to thermal limits).
            - Excellent: >18 MJ/m²/day
            - Adequate: 15-18 MJ/m²/day
            - Low: <15 MJ/m²/day (may limit yields)
            """)
    
    else:
        st.warning("NASA POWER data not yet available for this analysis. Re-run with NASA_POWER_ENABLED=True.")
    
    st.markdown("---")
    
    # Detailed data table
    st.subheader("Detailed Climate Risk Data")
    
    # Include confidence if available
    if 'confidence_score' in risk_data.columns:
        climate_table = risk_data[[
            'location', 'type', 'state', 'climate_likelihood', 
            'confidence_level', 'confidence_score',
            'climate_category', 'impact_score', 'climate_weighted_risk'
        ]].copy()
        
        climate_table.columns = [
            'Location', 'Type', 'State', 'Climate Likelihood',
            'Data Quality', 'Confidence %',
            'Risk Category', 'Impact Score', 'Weighted Risk'
        ]
    else:
        climate_table = risk_data[[
            'location', 'type', 'state', 'climate_likelihood', 
            'climate_category', 'impact_score', 'climate_weighted_risk'
        ]].copy()
        
        climate_table.columns = [
            'Location', 'Type', 'State', 'Climate Likelihood',
            'Risk Category', 'Impact Score', 'Weighted Risk'
        ]
    
    st.dataframe(
        climate_table.style.background_gradient(
            subset=['Climate Likelihood', 'Weighted Risk'],
            cmap='Reds'
        ),
        width='stretch'
    )
    
    # Download button
    csv = climate_table.to_csv(index=False)
    st.download_button(
        label="📥 Download Climate Risk Data",
        data=csv,
        file_name="climate_risk_data.csv",
        mime="text/csv"
    )


def render_natural_hazards():
    """Render Natural Hazards tab"""
    st.header("⚠️ Natural Hazards Analysis")
    
    if not st.session_state.analysis_run:
        st.info("Please run the analysis first using the sidebar button.")
        return
    
    risk_data = st.session_state.risk_data
    
    st.markdown("""
    This analysis integrates natural hazard data from **ThinkHazard!** (World Bank GFDRR).
    Hazards include: Floods, Earthquakes, Landslides, Wildfires, Droughts, and more.
    """)
    
    # Aggregate hazard statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Avg Hazard Severity",
            f"{risk_data['hazard_severity'].mean():.2f}/5"
        )
    
    with col2:
        high_hazard_count = len(risk_data[risk_data['hazard_severity'] >= 4])
        st.metric(
            "High Hazard Locations",
            high_hazard_count
        )
    
    with col3:
        st.metric(
            "Total Hazard Weighted Risk",
            f"{risk_data['hazard_weighted_risk'].sum():.2f}"
        )
    
    # Hazard matrix
    st.subheader("Multi-Hazard Matrix")
    
    # Extract hazard data
    hazard_types = set()
    for hazards in risk_data['hazards']:
        if isinstance(hazards, dict):
            hazard_types.update(hazards.keys())
    
    if hazard_types:
        hazard_matrix_data = []
        for _, row in risk_data.iterrows():
            hazard_row = {'Location': row['location'], 'Type': row['type']}
            if isinstance(row['hazards'], dict):
                for haz_type in hazard_types:
                    level = row['hazards'].get(haz_type, 'N/A')
                    score = utils.convert_hazard_level_to_score(level) if level != 'N/A' else 0
                    hazard_row[utils.get_hazard_name(haz_type)] = score
            hazard_matrix_data.append(hazard_row)
        
        hazard_matrix_df = pd.DataFrame(hazard_matrix_data)
        
        # Create heatmap
        hazard_cols = [col for col in hazard_matrix_df.columns if col not in ['Location', 'Type']]
        
        fig = px.imshow(
            hazard_matrix_df[hazard_cols].values,
            x=hazard_cols,
            y=hazard_matrix_df['Location'],
            color_continuous_scale='Reds',
            title='Hazard Severity Matrix (0=None, 3=High)',
            labels={'color': 'Severity Score'}
        )
        fig.update_xaxes(side="bottom")
        fig.update_layout(height=600)
        st.plotly_chart(fig, width='stretch')
        
        # Hazard distribution
        st.subheader("Hazard Type Distribution")
        
        hazard_counts = {}
        for hazards in risk_data['hazards']:
            if isinstance(hazards, dict):
                for haz_type, level in hazards.items():
                    if haz_type not in hazard_counts:
                        hazard_counts[haz_type] = {'HIG': 0, 'MED': 0, 'LOW': 0, 'VLO': 0}
                    if level in hazard_counts[haz_type]:
                        hazard_counts[haz_type][level] += 1
        
        if hazard_counts:
            hazard_dist_data = []
            for haz_type, levels in hazard_counts.items():
                for level, count in levels.items():
                    if count > 0:
                        hazard_dist_data.append({
                            'Hazard': f"{utils.get_hazard_icon(haz_type)} {utils.get_hazard_name(haz_type)}",
                            'Level': level,
                            'Count': count
                        })
            
            if hazard_dist_data:
                hazard_dist_df = pd.DataFrame(hazard_dist_data)
                
                fig = px.bar(
                    hazard_dist_df,
                    x='Hazard',
                    y='Count',
                    color='Level',
                    title='Distribution of Hazard Levels Across Portfolio',
                    color_discrete_map={
                        'HIG': config.RISK_COLORS['high'],
                        'MED': config.RISK_COLORS['medium'],
                        'LOW': config.RISK_COLORS['low'],
                        'VLO': config.RISK_COLORS['very_low']
                    },
                    barmode='stack'
                )
                st.plotly_chart(fig, width='stretch')
    else:
        st.warning("No hazard data available. This may indicate API issues or missing ADM codes.")
    
    # Detailed hazard table
    st.subheader("Detailed Hazard Data by Location")
    
    hazard_table = risk_data[[
        'location', 'type', 'state', 'hazard_severity',
        'hazard_category', 'hazard_weighted_risk'
    ]].copy()
    
    hazard_table.columns = [
        'Location', 'Type', 'State', 'Hazard Severity',
        'Risk Category', 'Weighted Risk'
    ]
    
    st.dataframe(
        hazard_table.style.background_gradient(
            subset=['Hazard Severity', 'Weighted Risk'],
            cmap='Reds'
        ),
        width='stretch'
    )


def render_monte_carlo():
    """Render Monte Carlo Simulations tab"""
    st.header("🎲 Monte Carlo Risk Simulations")
    
    if not st.session_state.analysis_run:
        st.info("Please run the analysis first using the sidebar button.")
        return
    
    mc_results = st.session_state.mc_results
    risk_data = st.session_state.risk_data
    
    st.markdown(f"""
    Probabilistic analysis of potential losses across {config.MONTE_CARLO_CONFIG['n_simulations']:,} simulated scenarios.
    Each simulation models yield loss based on climate risk and business impact.
    """)
    
    # Portfolio-level metrics
    st.subheader("Portfolio Risk Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Mean Loss",
            f"{mc_results['mean_loss'].sum():.2f}%",
            help="Average expected loss across all locations"
        )
    
    with col2:
        st.metric(
            "Portfolio VaR (95%)",
            f"{mc_results['var_95'].sum():.2f}%",
            help="Maximum loss in 95% of scenarios"
        )
    
    with col3:
        st.metric(
            "Portfolio VaR (99%)",
            f"{mc_results['var_99'].sum():.2f}%",
            help="Maximum loss in 99% of scenarios"
        )
    
    with col4:
        st.metric(
            "Max Single Location Risk",
            f"{mc_results['var_95'].max():.2f}%",
            help="Highest VaR(95%) from single location"
        )
    
    # VaR comparison chart
    st.subheader("Value at Risk (VaR) by Location")
    
    mc_sorted = mc_results.nlargest(15, 'var_95')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='VaR 90%',
        x=mc_sorted['location'],
        y=mc_sorted['var_90'],
        marker_color='#ff7f0e'
    ))
    
    fig.add_trace(go.Bar(
        name='VaR 95%',
        x=mc_sorted['location'],
        y=mc_sorted['var_95'],
        marker_color='#d62728'
    ))
    
    fig.add_trace(go.Bar(
        name='VaR 99%',
        x=mc_sorted['location'],
        y=mc_sorted['var_99'],
        marker_color='#8b0000'
    ))
    
    fig.update_layout(
        title='Top 15 Locations by Value at Risk',
        xaxis_title='Location',
        yaxis_title='Loss (% of Total Royalties)',
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Interactive location selector
    st.subheader("Detailed Simulation Results")
    
    selected_location = st.selectbox(
        "Select a location for detailed analysis:",
        options=mc_results['location'].tolist()
    )
    
    selected_mc = mc_results[mc_results['location'] == selected_location].iloc[0]
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Distribution histogram
        simulated_losses = np.array(selected_mc['simulated_losses'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=simulated_losses,
            nbinsx=50,
            name='Simulated Losses',
            marker_color='#1f77b4',
            opacity=0.7
        ))
        
        # Add mean line
        fig.add_vline(
            x=selected_mc['mean_loss'],
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {selected_mc['mean_loss']:.2f}%"
        )
        
        # Add VaR 95 line
        fig.add_vline(
            x=selected_mc['var_95'],
            line_dash="dash",
            line_color="orange",
            annotation_text=f"VaR(95%): {selected_mc['var_95']:.2f}%"
        )
        
        fig.update_layout(
            title=f'Loss Distribution: {selected_location}',
            xaxis_title='Loss (% of Total Royalties)',
            yaxis_title='Frequency',
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col_right:
        # Summary statistics
        st.markdown("**Summary Statistics**")
        
        stats_df = mc.create_mc_summary_stats(selected_mc.to_dict())
        st.dataframe(stats_df, width='stretch', hide_index=True)
    
    # Loss exceedance curve
    st.subheader("Loss Exceedance Curves")
    
    fig = go.Figure()
    
    # Plot curves for top 5 risks
    top_risks = mc_results.nlargest(5, 'var_95')
    
    for _, row in top_risks.iterrows():
        losses, exceedance = mc.generate_loss_exceedance_curve(row.to_dict())
        
        fig.add_trace(go.Scatter(
            x=losses,
            y=exceedance * 100,  # Convert to percentage
            mode='lines',
            name=row['location']
        ))
    
    fig.update_layout(
        title='Loss Exceedance Probability (Top 5 Risks)',
        xaxis_title='Loss (% of Total Royalties)',
        yaxis_title='Exceedance Probability (%)',
        height=500
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Full results table
    st.subheader("Complete Monte Carlo Results")
    
    mc_table = mc_results[[
        'location', 'climate_likelihood', 'impact_percent',
        'mean_loss', 'std_dev', 'var_90', 'var_95', 'var_99'
    ]].copy()
    
    mc_table.columns = [
        'Location', 'Climate Risk', 'Impact %',
        'Mean Loss %', 'Std Dev %', 'VaR 90%', 'VaR 95%', 'VaR 99%'
    ]
    
    st.dataframe(
        mc_table.style.background_gradient(
            subset=['VaR 95%', 'VaR 99%'],
            cmap='Reds'
        ).format({
            'Climate Risk': '{:.1f}',
            'Impact %': '{:.2%}',
            'Mean Loss %': '{:.2f}',
            'Std Dev %': '{:.2f}',
            'VaR 90%': '{:.2f}',
            'VaR 95%': '{:.2f}',
            'VaR 99%': '{:.2f}'
        }),
        width='stretch'
    )


def render_value_chain():
    """Render Value Chain Risk tab"""
    st.header("🔗 Value Chain Risk Analysis")
    
    if not st.session_state.analysis_run:
        st.info("Please run the analysis first using the sidebar button.")
        return
    
    risk_data = st.session_state.risk_data
    mc_results = st.session_state.mc_results
    
    st.markdown("""
    Analyzing risk across the supply chain:
    - **Upstream (Suppliers)**: Seedling providers
    - **Downstream (Clients)**: Royalty locations
    """)
    
    # Split data
    clients = risk_data[risk_data['type'] == 'Client (Royalty)']
    suppliers = risk_data[risk_data['type'] == 'Supplier (Seedling)']
    
    # High-level comparison
    st.subheader("Upstream vs Downstream Risk Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌱 Upstream (Suppliers)")
        st.metric("Number of Suppliers", len(suppliers))
        st.metric("Avg Climate Risk", f"{suppliers['climate_likelihood'].mean():.2f}/5")
        st.metric("Avg Aggregate Risk", f"{suppliers['aggregate_risk'].mean():.2f}/5")
        st.metric("Total Weighted Risk", f"{suppliers['aggregate_weighted_risk'].sum():.2f}")
        
        if len(mc_results) > 0:
            supplier_mc = mc_results[mc_results['location'].isin(suppliers['location'])]
            st.metric("Total VaR (95%)", f"{supplier_mc['var_95'].sum():.2f}%")
    
    with col2:
        st.markdown("### 💰 Downstream (Clients)")
        st.metric("Number of Clients", len(clients))
        st.metric("Avg Climate Risk", f"{clients['climate_likelihood'].mean():.2f}/5")
        st.metric("Avg Aggregate Risk", f"{clients['aggregate_risk'].mean():.2f}/5")
        st.metric("Total Weighted Risk", f"{clients['aggregate_weighted_risk'].sum():.2f}")
        
        if len(mc_results) > 0:
            client_mc = mc_results[mc_results['location'].isin(clients['location'])]
            st.metric("Total VaR (95%)", f"{client_mc['var_95'].sum():.2f}%")
    
    # Sankey diagram
    st.subheader("Risk Flow Through Value Chain")
    
    # Prepare Sankey data
    # Nodes: Suppliers -> States -> Clients
    suppliers_list = suppliers['location'].tolist()
    clients_list = clients['location'].tolist()
    states = risk_data['state'].unique().tolist()
    
    all_nodes = suppliers_list + states + clients_list
    node_indices = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Links
    sources = []
    targets = []
    values = []
    colors = []
    
    # Suppliers to States
    for _, supplier in suppliers.iterrows():
        sources.append(node_indices[supplier['location']])
        targets.append(node_indices[supplier['state']])
        values.append(supplier['aggregate_weighted_risk'])
        colors.append('rgba(44, 160, 44, 0.4)')  # Green for suppliers
    
    # States to Clients
    for _, client in clients.iterrows():
        sources.append(node_indices[client['state']])
        targets.append(node_indices[client['location']])
        values.append(client['aggregate_weighted_risk'])
        colors.append('rgba(255, 127, 14, 0.4)')  # Orange for clients
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=['#2ca02c'] * len(suppliers_list) + 
                  ['#1f77b4'] * len(states) + 
                  ['#ff7f0e'] * len(clients_list)
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])
    
    fig.update_layout(
        title="Risk Flow: Suppliers → States → Clients",
        font_size=10,
        height=600
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Detailed breakdowns
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Supplier Risk Ranking")
        
        supplier_table = suppliers.nlargest(10, 'aggregate_weighted_risk')[[
            'location', 'state', 'aggregate_risk', 'aggregate_weighted_risk'
        ]].copy()
        
        supplier_table.columns = ['Location', 'State', 'Risk Score', 'Weighted Risk']
        
        st.dataframe(
            supplier_table.style.background_gradient(
                subset=['Weighted Risk'],
                cmap='Greens'
            ),
            width='stretch',
            hide_index=True
        )
    
    with col_right:
        st.subheader("Client Risk Ranking")
        
        client_table = clients.nlargest(10, 'aggregate_weighted_risk')[[
            'location', 'state', 'aggregate_risk', 'aggregate_weighted_risk'
        ]].copy()
        
        client_table.columns = ['Location', 'State', 'Risk Score', 'Weighted Risk']
        
        st.dataframe(
            client_table.style.background_gradient(
                subset=['Weighted Risk'],
                cmap='Oranges'
            ),
            width='stretch',
            hide_index=True
        )
    
    # Concentration risk analysis
    st.subheader("Concentration Risk Analysis")
    
    st.markdown("""
    **Herfindahl Index**: Measures concentration of business impact across locations.
    - Values closer to 0 indicate high diversification
    - Values closer to 1 indicate high concentration (higher risk)
    """)
    
    # Calculate Herfindahl for clients
    client_impacts = clients['impact_percent'].values
    herfindahl_clients = np.sum(client_impacts ** 2)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Client Herfindahl Index",
            f"{herfindahl_clients:.3f}",
            help="Concentration of business across clients"
        )
    
    with col2:
        diversification = 1 - herfindahl_clients
        st.metric(
            "Diversification Score",
            f"{diversification:.3f}",
            help="Higher is better (more diversified)"
        )
    
    with col3:
        equivalent_n = 1 / herfindahl_clients if herfindahl_clients > 0 else 0
        st.metric(
            "Equivalent # of Equal Clients",
            f"{equivalent_n:.1f}",
            help="Portfolio behaves like this many equal-weighted clients"
        )


def render_sensitivity_analysis():
    """Render Sensitivity Analysis tab"""
    st.header("🔬 Sensitivity Analysis")
    
    if not st.session_state.analysis_run:
        st.info("Please run the analysis first using the sidebar button.")
        return
    
    risk_data = st.session_state.risk_data
    
    st.markdown("""
    Test how sensitive your risk profile is to changes in key assumptions.
    Adjust parameters below to see how risk rankings change.
    """)
    
    # Stress test controls
    st.subheader("Stress Test Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stress_factor = st.slider(
            "Impact Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.5,
            step=0.1,
            help="Multiply the top risk's business impact by this factor"
        )
    
    with col2:
        # Select location to stress
        clients = risk_data[risk_data['type'] == 'Client (Royalty)']
        selected_client = st.selectbox(
            "Select Client to Stress Test",
            options=clients['location'].tolist(),
            index=0
        )
    
    # Run stress test
    if st.button("Run Stress Test", type="primary"):
        with st.spinner("Running stress test..."):
            stressed_df, analysis = engine.run_sensitivity_analysis(
                risk_data,
                stress_factor=stress_factor
            )
            
            # Store in session state
            st.session_state.stressed_df = stressed_df
            st.session_state.sensitivity_analysis = analysis
    
    # Display results if available
    if 'stressed_df' in st.session_state and 'sensitivity_analysis' in st.session_state:
        analysis = st.session_state.sensitivity_analysis
        stressed_df = st.session_state.stressed_df
        
        st.markdown("---")
        st.subheader("Stress Test Results")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Stressed Location",
                analysis['top_client_name']
            )
        
        with col2:
            delta_impact = analysis['stressed_impact'] - analysis['baseline_impact']
            st.metric(
                "Impact Change",
                f"{analysis['stressed_impact']:.2f}",
                delta=f"+{delta_impact:.2f}"
            )
        
        with col3:
            delta_risk = analysis['stressed_weighted_risk'] - analysis['baseline_weighted_risk']
            st.metric(
                "Weighted Risk Change",
                f"{analysis['stressed_weighted_risk']:.2f}",
                delta=f"+{delta_risk:.2f}"
            )
        
        # Ranking comparison
        st.subheader("Risk Ranking: Baseline vs Stressed")
        
        # Top 10 from each scenario
        baseline_top10 = risk_data.nlargest(10, 'aggregate_weighted_risk')[
            ['location', 'aggregate_weighted_risk']
        ].copy()
        baseline_top10.columns = ['Location', 'Baseline Risk']
        baseline_top10['Baseline Rank'] = range(1, len(baseline_top10) + 1)
        
        stressed_top10 = stressed_df.nlargest(10, 'aggregate_weighted_risk')[
            ['location', 'aggregate_weighted_risk']
        ].copy()
        stressed_top10.columns = ['Location', 'Stressed Risk']
        stressed_top10['Stressed Rank'] = range(1, len(stressed_top10) + 1)
        
        # Merge
        comparison = pd.merge(
            baseline_top10,
            stressed_top10,
            on='Location',
            how='outer'
        )

        # Convert to display-friendly format (avoid mixed data types for Arrow serialization)
        comparison_display = comparison.copy()
        for col in comparison_display.columns:
            if col != 'Location':
                comparison_display[col] = comparison_display[col].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '-'
                )

        st.dataframe(comparison_display, width='stretch', hide_index=True)
        
        # Visual comparison
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Baseline',
            x=baseline_top10['Location'],
            y=baseline_top10['Baseline Risk'],
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            name='Stressed',
            x=stressed_top10['Location'],
            y=stressed_top10['Stressed Risk'],
            marker_color='#d62728'
        ))
        
        fig.update_layout(
            title='Top 10 Risks: Baseline vs Stressed Scenario',
            xaxis_title='Location',
            yaxis_title='Weighted Risk Score',
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Analysis insights
        st.subheader("Key Insights")
        
        if analysis['ranking_changed']:
            st.warning(f"""
            ⚠️ **Ranking Changed**: Under stress, {analysis['new_top_risk']} 
            becomes the highest risk, replacing {analysis['top_client_name']}.
            This indicates sensitivity to business concentration assumptions.
            """)
        else:
            st.success(f"""
            ✅ **Ranking Stable**: {analysis['top_client_name']} remains the top risk 
            even under {(stress_factor - 1) * 100:.0f}% stress. This indicates 
            a robust risk identification.
            """)


def main():
    """Main application"""
    
    # Render sidebar
    risk_threshold, location_types = render_sidebar()
    
    # Main content
    st.title("🌱 ESG Risk Analysis Dashboard")
    st.markdown("### Sugarcane Supply Chain - Climate & Natural Hazard Risk Assessment")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Executive Summary",
        "🌡️ Climate Risk",
        "⚠️ Natural Hazards",
        "🎲 Monte Carlo",
        "🔗 Value Chain",
        "🔬 Sensitivity"
    ])
    
    with tab1:
        render_executive_summary()
    
    with tab2:
        render_climate_risk()
    
    with tab3:
        render_natural_hazards()
    
    with tab4:
        render_monte_carlo()
    
    with tab5:
        render_value_chain()
    
    with tab6:
        render_sensitivity_analysis()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Data Sources: World Bank CCKP | ThinkHazard! (GFDRR) | NASA POWER Agricultural Meteorology</p>
        <p>ESG Risk Analysis Tool v2.0 - Enhanced with NASA POWER Integration</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

