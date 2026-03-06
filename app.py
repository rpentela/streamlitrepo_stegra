# app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns




import streamlit as st

# -----------------------------
# User credentials
# -----------------------------
USERS = {
    "admin": "master",
    "colleague1": "pass1",
    "colleague2": "pass2"
}

# -----------------------------
# Session state initialization
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "login_trigger" not in st.session_state:
    st.session_state.login_trigger = False  # new flag to trigger rerun

# -----------------------------
# Login Page
# -----------------------------
if not st.session_state.logged_in:
    st.title("🔒 Cold Mill Dashboard Login")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")

        if submit_btn:
            if username in USERS and password == USERS[username]:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.login_trigger = True  # flag to rerun safely
            else:
                st.error("❌ Invalid username or password")

    # Safe rerun outside form
    if st.session_state.login_trigger:
        st.session_state.login_trigger = False  # reset flag
        st.experimental_rerun()

    st.stop()  # stop execution until login succeeds

# -----------------------------
# Dashboard Content
# -----------------------------
st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")
logout_btn = st.sidebar.button("Logout")
if logout_btn:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()


st.markdown("Welcome! Use the sidebar filters to interact with the dashboard.")
# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Cold Mill Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏭 Cold Mill Process Dashboard")
st.markdown(
    "Interactive dashboard for production, scrap, downtime, and efficiency of a cold mill line."
)

# -----------------------------
# Generate Example Data
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
date_filter = st.sidebar.date_input(
    "Select Date Range",
    [df['Date'].min(), df['Date'].max()]
)
shift_filter = st.sidebar.multiselect(
    "Select Shift(s)",
    options=shifts,
    default=shifts
)

filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_filter[0])) &
    (df['Date'] <= pd.to_datetime(date_filter[1])) &
    (df['Shift'].isin(shift_filter))
]

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["KPIs", "Trends", "Data Table"])

# -----------------------------
# Tab 1: Enhanced KPIs
# -----------------------------
with tab1:
    st.subheader("🔑 Key Performance Indicators")

    # Basic KPIs
    total_prod = filtered_df['Production_tons'].sum()
    total_scrap = filtered_df['Scrap_tons'].sum()
    avg_eff = filtered_df['Efficiency_%'].mean()
    total_downtime = filtered_df['Downtime_minutes'].sum()/60  # hours
    avg_downtime_shift = filtered_df.groupby('Shift')['Downtime_minutes'].mean()/60  # hours
    max_prod_day = filtered_df.groupby('Date')['Production_tons'].sum().idxmax()
    min_eff_day = filtered_df.groupby('Date')['Efficiency_%'].mean().idxmin()

    # KPI Columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Production (tons)", f"{total_prod:,.0f}")
    col2.metric("Total Scrap (tons)", f"{total_scrap:.1f}")

    # Efficiency emoji
    if avg_eff < 80:
        eff_indicator = "🔴"
    elif avg_eff < 90:
        eff_indicator = "🟡"
    else:
        eff_indicator = "🟢"
    col3.metric("Average Efficiency (%)", f"{avg_eff:.1f} {eff_indicator}")

    col4.metric("Total Downtime (hrs)", f"{total_downtime:.1f}")

    # Additional info in next row
    col5, col6, col7 = st.columns(3)
    col5.metric("Average Downtime per Shift (hrs)", f"{avg_downtime_shift.mean():.1f}")
    col6.metric("Max Production Day", f"{max_prod_day.date()}")
    col7.metric("Min Efficiency Day", f"{min_eff_day.date()}")

    # -----------------------------
    # Downtime Pie Chart
    # -----------------------------
    # Downtime Pie Chart (smaller size)
    st.subheader("Downtime Distribution by Shift")
    downtime_by_shift = filtered_df.groupby('Shift')['Downtime_minutes'].sum()
    
    # Set smaller figure size
    fig, ax = plt.subplots(figsize=(4,4))  # smaller than before
    ax.pie(
        downtime_by_shift,
        labels=downtime_by_shift.index,
        autopct="%1.1f%%",
        colors=sns.color_palette("Reds", len(downtime_by_shift)),
        startangle=90
    )
    ax.set_title("Downtime Distribution", fontsize=12)
    st.pyplot(fig, use_container_width=False)  # Prevent it from stretching full width

# -----------------------------
# Tab 2: Trends
# -----------------------------
with tab2:
    st.subheader("📈 Production & Scrap Trends")

    col1, col2 = st.columns(2)

    # Production Trend (line chart)
    prod_trend = filtered_df.groupby('Date')['Production_tons'].sum().reset_index()
    prod_trend.set_index('Date', inplace=True)
    col1.line_chart(prod_trend)

    # Scrap Trend (bar chart)
    scrap_trend = filtered_df.groupby('Date')['Scrap_tons'].sum().reset_index()
    scrap_trend.set_index('Date', inplace=True)
    col2.bar_chart(scrap_trend)

    # Efficiency Boxplot
    st.subheader("Shift-wise Efficiency Distribution")
    fig1, ax1 = plt.subplots(figsize=(8,3))
    sns.boxplot(x='Shift', y='Efficiency_%', data=filtered_df, palette='Blues', ax=ax1)
    ax1.set_title("Efficiency by Shift")
    st.pyplot(fig1)

    

# -----------------------------
# Tab 3: Data Table
# -----------------------------
with tab3:
    st.subheader("📋 Filtered Report")
    st.dataframe(filtered_df)

    # Download CSV
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='cold_mill_report.csv',
        mime='text/csv'
    )













