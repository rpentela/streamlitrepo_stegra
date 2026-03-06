# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Cold Mill Dashboard", layout="wide")
st.title("🏭 Cold Mill Process Dashboard")
st.markdown("Example dashboard for production, efficiency, scrap, and trends of a cold mill line.")

# --- Generate Example Data ---
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
shift = ['A', 'B', 'C']
data = {
    'Date': np.repeat(dates, 3),
    'Shift': shift * len(dates),
    'Production_tons': np.random.randint(80, 120, len(dates)*3),
    'Scrap_tons': np.random.randint(0, 5, len(dates)*3),
    'Downtime_minutes': np.random.randint(0, 60, len(dates)*3),
    'Efficiency_%': np.random.randint(75, 100, len(dates)*3)
}

df = pd.DataFrame(data)

# --- KPIs ---
st.subheader("Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Production (tons)", f"{df['Production_tons'].sum():,.0f}")
col2.metric("Total Scrap (tons)", f"{df['Scrap_tons'].sum():,.1f}")
col3.metric("Average Efficiency (%)", f"{df['Efficiency_%'].mean():.1f}%")
col4.metric("Total Downtime (hrs)", f"{df['Downtime_minutes'].sum()/60:.1f}")

# --- Production Trend ---
st.subheader("📈 Production Trend Over Time")
prod_trend = df.groupby('Date')['Production_tons'].sum().reset_index()
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(prod_trend['Date'], prod_trend['Production_tons'], marker='o', color='green')
ax.set_xlabel("Date")
ax.set_ylabel("Production (tons)")
ax.set_title("Daily Total Production")
plt.xticks(rotation=45)
st.pyplot(fig)

# --- Scrap Trend ---
st.subheader("Scrap Trend Over Time")
scrap_trend = df.groupby('Date')['Scrap_tons'].sum().reset_index()
fig2, ax2 = plt.subplots(figsize=(10,4))
ax2.bar(scrap_trend['Date'], scrap_trend['Scrap_tons'], color='red')
ax2.set_xlabel("Date")
ax2.set_ylabel("Scrap (tons)")
ax2.set_title("Daily Scrap")
plt.xticks(rotation=45)
st.pyplot(fig2)

# --- Efficiency Distribution ---
st.subheader("Efficiency Distribution by Shift")
fig3, ax3 = plt.subplots(figsize=(10,4))
sns.boxplot(x='Shift', y='Efficiency_%', data=df, ax=ax3, palette='Blues')
ax3.set_title("Shift-wise Efficiency")
st.pyplot(fig3)

# --- Sidebar Filters ---
st.sidebar.header("Filters")
date_filter = st.sidebar.date_input(
    "Select Date Range",
    [df['Date'].min(), df['Date'].max()]
)
shift_filter = st.sidebar.multiselect(
    "Select Shift(s)",
    options=shift,
    default=shift
)

filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_filter[0])) &
    (df['Date'] <= pd.to_datetime(date_filter[1])) &
    (df['Shift'].isin(shift_filter))
]

st.subheader("Filtered Data Table")
st.dataframe(filtered_df)

st.subheader("Filtered Production Trend")
filtered_prod = filtered_df.groupby('Date')['Production_tons'].sum().reset_index()
fig4, ax4 = plt.subplots(figsize=(10,4))
ax4.plot(filtered_prod['Date'], filtered_prod['Production_tons'], marker='o', color='green')
ax4.set_xlabel("Date")
ax4.set_ylabel("Production (tons)")
ax4.set_title("Filtered Production Trend")
plt.xticks(rotation=45)
st.pyplot(fig4)
