import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Global Disaster Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance UI aesthetics
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        div[data-testid="stMetricValue"] {font-size: 1.4rem !important;}
        .stAlert {padding: 0.5rem;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & FEATURE ENGINEERING
# ==========================================
@st.cache_data
def load_data():
    """
    Loads and preprocesses the dataset.
    - Handles date parsing and error correction.
    - Computes 'Severity Score' based on casualties and economic loss.
    """
    try:
        # Check path variations for deployment flexibility
        try:
            df = pd.read_csv('data/cleaned_data_final.csv')
        except FileNotFoundError:
            df = pd.read_csv('../data/cleaned_data_final.csv')
    except Exception as e:
        return None

    # Date Handling: Fill missing months with January
    df['month_clean'] = df['month'].fillna(1).replace(0, 1).astype(int)
    
    # Create datetime object for time-series analysis
    # Coerce errors to NaT (Not a Time)
    df['date'] = pd.to_datetime(
        df['year'].astype(str) + '-' + df['month_clean'].astype(str).str.zfill(2) + '-01', 
        errors='coerce'
    )
    
    # Fill NaT values with the first day of the recorded year
    mask_nat = df['date'].isna()
    df.loc[mask_nat, 'date'] = pd.to_datetime(df.loc[mask_nat, 'year'].astype(str) + '-01-01')

    # Severity Index Calculation (Composite Score)
    # Log-transform inputs to handle power-law distribution
    df['log_casualties'] = np.log1p(df['casualties'])
    df['log_loss'] = np.log1p(df['economic_loss_usd'])
    df['severity_score'] = (df['log_casualties'] + df['log_loss']) 
    
    # Normalize score to 0-100 scale
    max_score = df['severity_score'].max()
    if max_score > 0:
        df['severity_score'] = (df['severity_score'] / max_score) * 100
    else:
        df['severity_score'] = 0
    
    return df

# Load data with error handling
df = load_data()
if df is None:
    st.error("CRITICAL ERROR: Data file not found. Please ensure 'cleaned_data_final.csv' is in the 'data' folder.")
    st.stop()

# ==========================================
# 3. SIDEBAR: ADVANCED FILTERS
# ==========================================
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    # Date Range Slider
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    selected_years = st.slider("📅 Analysis Period", min_year, max_year, (min_year, max_year))

    # Disaster Type Multiselect
    all_types = sorted(df['disaster_type'].unique())
    selected_types = st.multiselect("🌪️ Disaster Types", all_types, default=all_types[:5])

    # Country Select
    all_countries = ["All World"] + sorted(df['country'].unique().tolist())
    selected_country = st.selectbox("📍 Region Focus", all_countries)

    # Severity Threshold Slider
    severity_threshold = st.slider("⚠️ Min. Severity Score", 0, 100, 0, help="Filter out minor events.")
    
    st.markdown("---")
    st.info("**Data Source:** EM-DAT (2018-2024)\n**Version:** 2.1 (Stacked Layout)")

# --- FILTERING LOGIC ---
filtered_df = df[
    (df['year'] >= selected_years[0]) & 
    (df['year'] <= selected_years[1]) &
    (df['severity_score'] >= severity_threshold)
]

if selected_types:
    filtered_df = filtered_df[filtered_df['disaster_type'].isin(selected_types)]

if selected_country != "All World":
    filtered_df = filtered_df[filtered_df['country'] == selected_country]

# ==========================================
# 4. VISUALIZATION FUNCTIONS (PLOTLY)
# ==========================================

def plot_3d_globe(data):
    """Renders an interactive 3D Orthographic Globe."""
    if data.empty: return None
    
    # Filter valid coordinates
    map_data = data.dropna(subset=['latitude', 'longitude'])
    if map_data.empty: return None

    fig = px.scatter_geo(
        map_data,
        lat='latitude', lon='longitude',
        color='disaster_type',
        size='severity_score', 
        hover_name='country',
        hover_data={'year': True, 'casualties': True, 'economic_loss_usd': True},
        projection="orthographic", 
        title=f"Global Risk Globe ({len(map_data)} Events)",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=550)
    return fig

def plot_seasonal_radar(data):
    """Renders a Polar/Radar chart for seasonal analysis."""
    if data.empty: return None
    
    monthly = data.groupby('month').size().reset_index(name='count')
    # Close the loop for radar chart
    monthly = pd.concat([monthly, monthly.iloc[[0]]], ignore_index=True)
    
    month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    monthly['month_name'] = monthly['month'].map(month_map)
    
    fig = px.line_polar(
        monthly, r='count', theta='month_name', line_close=True,
        title="Seasonal Cyclicity (Radar Analysis)", template="plotly_dark", markers=True
    )
    fig.update_traces(fill='toself', line_color='#00CC96')
    return fig

def plot_severity_boxplot(data):
    """Renders Boxplots to show distribution and outliers."""
    if data.empty: return None
    fig = px.box(
        data, x='disaster_type', y='casualties', color='disaster_type',
        log_y=True, title="Severity Distribution & Outliers (Log Scale)",
        template="plotly_dark", points="outliers"
    )
    return fig

def plot_sunburst(data):
    """Renders a Hierarchical Sunburst Chart."""
    if data.empty: return None
    
    # Aggregate for performance
    df_sun = data.groupby(['disaster_type', 'country']).size().reset_index(name='count')
    df_sun = df_sun.sort_values('count', ascending=False).head(100)
    
    fig = px.sunburst(
        df_sun, path=['disaster_type', 'country'], values='count',
        title="Hierarchical Event Distribution (Type > Country)", template="plotly_dark",
        color='count', color_continuous_scale='RdBu_r'
    )
    fig.update_layout(height=600)
    return fig

def plot_correlation_scatter(data):
    """Renders a Log-Log Scatter plot for Impact Analysis."""
    if data.empty: return None
    fig = px.scatter(
        data, x="economic_loss_usd", y="casualties", color="disaster_type",
        size="severity_score", log_x=True, log_y=True, hover_name="country",
        title="Impact Correlation: Casualties vs. Economic Loss", template="plotly_dark",
        labels={"economic_loss_usd": "Economic Loss ($)", "casualties": "Casualties"}
    )
    return fig

# ==========================================
# 5. MAIN DASHBOARD LAYOUT
# ==========================================

st.title("🌍 Global Disaster Intelligence")
st.markdown(f"**Scope:** {selected_years[0]} - {selected_years[1]} | **Total Events:** {len(filtered_df)}")

# --- KPI METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)
total_loss = filtered_df['economic_loss_usd'].sum()
avg_severity = filtered_df['severity_score'].mean()

col1.metric("Total Events", f"{len(filtered_df):,}", delta="Live Data")
col2.metric("Total Casualties", f"{filtered_df['casualties'].sum():,.0f}", delta_color="inverse")
col3.metric("Economic Loss", f"${total_loss/1e9:,.2f} B")
col4.metric("Avg Severity Score", f"{avg_severity:.1f}/100")

st.markdown("---")

# --- ANALYTICAL TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Geospatial Intelligence", 
    "⏱️ Temporal Dynamics", 
    "📊 Comparative Statistics",
    "🔗 Impact Correlations"
])

# TAB 1: GEOSPATIAL (MAP & TABLE)
with tab1:
    # 1. 3D Globe Visualization
    st.plotly_chart(plot_3d_globe(filtered_df), use_container_width=True)
    
    st.markdown("### 🚨 High-Risk Zones Summary")
    # 2. Risk Data Table
    top_risk = filtered_df.groupby('country')[['casualties', 'economic_loss_usd']].sum().sort_values('casualties', ascending=False).head(10)
    st.dataframe(
        top_risk.style.format({"casualties": "{:,.0f}", "economic_loss_usd": "${:,.0f}"}), 
        use_container_width=True
    )
    # Download Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Data (CSV)", data=csv, file_name="disaster_data.csv", mime="text/csv")

# TAB 2: TIME SERIES & SEASONALITY
with tab2:
    col_line, col_radar = st.columns([2, 1])
    with col_line:
        # Time Series (Area Chart)
        valid_dates_df = filtered_df.dropna(subset=['date'])
        
        if not valid_dates_df.empty:
            daily_counts = valid_dates_df.set_index('date').resample('M').size().reset_index(name='count')
            fig_line = px.area(daily_counts, x='date', y='count', title="Activity Timeline (Monthly)", template="plotly_dark")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Insufficient date data for time-series analysis.")
            
    with col_radar:
        # Seasonal Radar Chart
        st.plotly_chart(plot_seasonal_radar(filtered_df), use_container_width=True)

# TAB 3: COMPARATIVE ANALYSIS (STACKED LAYOUT)
with tab3:
    st.markdown("### 📊 Distribution & Hierarchy Analysis")
    
    # 1. Boxplot (Full Width)
    st.plotly_chart(plot_severity_boxplot(filtered_df), use_container_width=True)
    
    st.markdown("---")
    
    # 2. Sunburst (Full Width)
    st.plotly_chart(plot_sunburst(filtered_df), use_container_width=True)

# TAB 4: CORRELATIONS
with tab4:
    st.markdown("### ⚠️ Relationship: Severity vs. Loss vs. Casualties")
    col_scatter, col_metric = st.columns([3, 1])
    with col_scatter:
        st.plotly_chart(plot_correlation_scatter(filtered_df), use_container_width=True)
    with col_metric:
        st.info("💡 **Insight:** Events clustered in the top-right quadrant represent the most catastrophic disasters (High Loss + High Casualties).")
        with st.expander("Methodology Note"):
            st.write("Axes are log-scaled to visualize the wide range of impact magnitudes. Bubble size represents the composite Severity Score.")