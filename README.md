
# 🌍 Global Disaster Intelligence Dashboard


> **A comprehensive data visualization suite analyzing global natural and technological disasters (2018-2024).**

## 📖 Overview

This project provides a multi-dimensional analysis of global disaster events using the **EM-DAT** dataset. It combines rigorous statistical analysis (Jupyter Notebooks) with a production-ready interactive dashboard (Streamlit) to reveal patterns in geographical risk, temporal dynamics, and impact severity.

The system is designed to answer critical questions:
- *Which countries face the highest "Human vs. Economic" trade-off?*
- *Is there a seasonal cycle to specific disaster types?*
- *How do natural hazards compare to technological accidents in frequency?*

## 🚀 Key Features

### 🔹 Interactive Dashboard (`app.py`)
- **3D Orthographic Globe:** Interactive geospatial visualization of event locations.
- **Severity Scoring Engine:** Custom algorithm combining Log(Casualties) and Log(Economic Loss) to identify high-impact events.
- **Seasonal Radar Charts:** Cyclical analysis of disaster frequencies by month.
- **Hierarchical Sunbursts:** Drill-down analysis from Disaster Type → Affected Country.
- **Dynamic Filtering:** Filter by Year, Country, Type, and Severity Threshold.

### 🔹 Analytical Notebooks
- **Time-Series Analysis:** Area charts and trend lines identifying peak activity years.
- **Geospatial Intelligence:** Anti-aliased choropleth maps and comparative density analysis (Natural vs. Technological).
- **Statistical Heatmaps:** Z-Score anomaly detection and Percentage-Share matrices to solve data imbalance issues (e.g., Flood dominance).

## 📂 Project Structure

```bash
global-disaster-data-visualization/
├── data/
│   ├── cleaned_data_final.csv       # Processed dataset used by the app and notebooks
│   └── public_emdat_... .csv        # Raw dataset (used for rich correlation analysis)
├── notebooks/
│   ├── 01_data_preprocessing.ipynb  # Data cleaning, imputation, and feature engineering
│   ├── 02_time_series_analysis.ipynb# Temporal trends, seasonality, and impact analysis
│   ├── 03_geospatial_analysis.ipynb # 3D/2D maps, density analysis, and whitelisted filtering
│   ├── 04_statistical_analysis.ipynb# Correlation matrices, Z-Score trends, and risk heatmaps
│   └── 05_advanced_analysis.ipynb   # Scatter plots and distribution analysis (Boxplots/Histograms)
├── app.py                           # Production-ready Streamlit Dashboard
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

## 🛠️ Installation & Usage

1. **Clone the Repository**
```bash
git clone [https://github.com/solid1010/global-disaster-data-visualization.git](https://github.com/solid1010/global-disaster-data-visualization.git)
cd global-disaster-data-visualization

```


2. **Install Dependencies**
```bash
pip install -r requirements.txt

```


3. **Run the Dashboard**
```bash
streamlit run app.py

```


*The dashboard will open automatically in your default web browser (http://localhost:8501).*

## 📊 Methodology & Metrics

### 1. Severity Score Algorithm

To enable fair comparison between events with high casualties (e.g., Earthquakes) and high economic loss (e.g., Storms in developed nations), we engineered a composite **Severity Score**:

$$ \text{Severity} = \log(1 + \text{Casualties}) + \log(1 + \text{Economic Loss}) $$

*This score is normalized to a 0-100 scale for the dashboard filters.*

### 2. Logarithmic Scaling

Due to the Power Law distribution of disaster impacts (Pareto Principle), we utilize Log-Normal scales in Boxplots, Scatter plots, and Choropleth maps to visualize outliers effectively without losing detail on smaller events.

### 3. "Natural Only" Whitelisting

For geospatial risk profiling, we strictly filter for natural hazards (Floods, Storms, Earthquakes) to avoid skewing geographical data with ubiquitous technological accidents like Road/Traffic crashes.

## 📚 Data Source

* **Dataset:** EM-DAT (The International Disaster Database)
* **Period:** 2018 - 2024
* **Attributes:** Disaster Type, Location, Start/End Dates, Total Deaths, Total Affected, Economic Loss (Adjusted USD).

## 👥 Contributors

* **Alperen Sağlam** - *Data Analysis, Dashboard Development, Geospatial Visualization*
* **İbrahim Bancar** - *Data Analysis, Data Preprocessing, Statistical Analysis*

---


