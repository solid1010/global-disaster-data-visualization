import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Global Disaster Risk Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DATA LOADING (Cache Mechanism)
# ==========================================
@st.cache_data
def load_data():
    # Load cleaned data
    df = pd.read_csv('data/cleaned_data_final.csv') # Verify path matches your structure
    return df

@st.cache_data
def load_map_data():
    # Download map data 
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url)
    return world

df = load_data()
world = load_map_data()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Refine analysis scope.")

# Year Filter
min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_years = st.sidebar.slider("Year Range", min_year, max_year, (min_year, max_year))

# Disaster Type Filter
all_types = sorted(df['disaster_type'].unique())
selected_types = st.sidebar.multiselect("Disaster Type", all_types, default=all_types[:5]) # Default: First 5

# Country Filter
all_countries = ["All World"] + sorted(df['country'].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", all_countries)

# ==========================================
# 4. FILTERING LOGIC
# ==========================================
# Filter data based on user selection
filtered_df = df[
    (df['year'] >= selected_years[0]) & 
    (df['year'] <= selected_years[1])
]

if selected_types:
    filtered_df = filtered_df[filtered_df['disaster_type'].isin(selected_types)]

if selected_country != "All World":
    filtered_df = filtered_df[filtered_df['country'] == selected_country]

# ==========================================
# 5. MAIN DASHBOARD LAYOUT
# ==========================================
st.title("🌍 Global Disaster Risk Monitor (2018-2024)")
st.markdown("This dashboard analyzes the impacts of global natural and technological disasters.")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "📈 Trends & Analysis", "🗺️ Comparative Maps"])

with tab1:
    st.subheader("Global Impact Overview")
    
    # KPI Cards (3 columns side-by-side)
    col1, col2, col3 = st.columns(3)
    
    total_events = len(filtered_df)
    total_deaths = filtered_df['casualties'].sum()
    total_loss = filtered_df['economic_loss_usd'].sum() / 1e9 # Billions USD
    
    col1.metric("Total Events", f"{total_events}", delta_color="off")
    col2.metric("Casualties", f"{total_deaths:,.0f}", delta_color="inverse") # Red for danger
    col3.metric("Economic Loss", f"${total_loss:,.2f} B")

    st.markdown("---")
    
    # MAP PLACEHOLDER
    st.info("📍 Map Visualization Area (Geospatial Analysis Integration)")
    # Bubble Map code from geospatial.ipynb will be migrated here as a function.

with tab2:
    st.subheader("Temporal Trends")
    st.info("📈 Time Series Chart Area")
    # Area Chart code from time_series.ipynb will be migrated here.

with tab3:
    st.subheader("Advanced Risk Analysis")
    st.info("🔥 Heatmap & Comparative Maps Area")
    # Heatmap code from statistical_analysis.ipynb will be migrated here.