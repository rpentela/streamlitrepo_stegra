# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Cold Mill Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("🏭 Cold Mill Process Dashboard")
st.markdown("Professional interactive dashboard for production line monitoring, trends, and KPIs.")

# -----------------------------
# Example Data Generation
# -----------------------------
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
shifts = ['A', 'B', 'C']

data = {
    'Date': np.repeat(dates, 3),
    'Shift': shifts * len(dates),
    'Production_tons': np.random.randint(80, 120, len(dates)*3),
    'Scrap_tons': np.random.randint(0, 5, len(dates)*3),
    'Downtime_minutes': np.random.randint(0, 60, len(dates)*3),
    'Efficiency_%': np.random.randint(75, 100, len(dates)*3)
}

df = pd.DataFrame(data)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")
date_filter = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
shift_filter = st.sidebar.multiselect("Select Shift(s)", options=shifts, default=shifts)

filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_filter[0])) &
    (df['Date'] <= pd.to_datetime(date_filter[1])) &
    (df['Shift'].isin(shift_filter))
]

# -----------------------------
# Tabs for different views
# -----------------------------
tab1, tab2, tab3 = st.tabs(["KPIs", "Trends", "Data Table"])

# -----------------------------
# Tab 1: KPIs
# -----------------------------
with tab1:
    st.subheader("🔑 Key Performance Indicators")
    total_prod = filtered_df['Production_tons'].sum()
    total_scrap = filtered_df['Scrap_tons'].sum()
    avg_eff = filtered_df['Efficiency_%'].mean()
    total_downtime = filtered_df['Downtime_minutes'].sum()/60  # hours

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Production (tons)", f"{total_prod:,.0f}", delta=f"{total_prod - df['Production_tons'].sum():,.0f}")
    col2.metric("Total Scrap (tons)", f"{total_scrap:,.1f}")
    
    # colored KPI for efficiency
    eff_color = "normal"
    if avg_eff < 80:
        eff_color = "danger"
    elif avg_eff < 90:
        eff_color = "warning"
    
    col3.metric("Average Efficiency (%)", f"{avg_eff:.1f}", delta_color=eff_color)
    col4.metric("Total Downtime (hrs)", f"{total_downtime:.1f}")

# -----------------------------
# Tab 2: Trends
# -----------------------------
with tab2:
    st.subheader("📈 Production & Scrap Trends")

    # Side-by-side charts
    col1, col2 = st.columns(2)

    # Production Trend
    prod_trend = filtered_df.groupby('Date')['Production_tons'].sum().reset_index()
    col1.line_chart(prod_trend.rename(columns={'Date':'index'}).set_index('Date'))

    # Scrap Trend
    scrap_trend = filtered_df.groupby('Date')['Scrap_tons'].sum().reset_index()
    col2.bar_chart(scrap_trend.rename(columns={'Date':'index'}).set_index('Date'))

    # Efficiency Boxplot by Shift
    st.subheader("Shift-wise Efficiency Distribution")
    fig, ax = plt.subplots(figsize=(8,3))
    sns.boxplot(x='Shift', y='Efficiency_%', data=filtered_df, palette='Blues', ax=ax)
    ax.set_title("Efficiency by Shift")
    st.pyplot(fig)

    # Downtime Heatmap
    st.subheader("Downtime Distribution")
    downtime_pivot = filtered_df.pivot_table(index='Date', columns='Shift', values='Downtime_minutes')
    fig2, ax2 = plt.subplots(figsize=(10,3))
    sns.heatmap(downtime_pivot, annot=True, fmt=".0f", cmap="Reds", cbar_kws={'label':'Minutes'}, ax=ax2)
    st.pyplot(fig2)

# -----------------------------
# Tab 3: Data Table
# -----------------------------
with tab3:
    st.subheader("📋 Filtered Data Table")
    st.dataframe(filtered_df)

    # CSV download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='cold_mill_report.csv',
        mime='text/csv'
    )
