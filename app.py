import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cold Mill Dashboard", layout="wide")

# -----------------------------
# USERS
# -----------------------------
USERS = {
    "admin": "master",
    "engineer": "steel123"
}

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# LOGIN PAGE
# -----------------------------
if not st.session_state.logged_in:

    st.title("🔒 Cold Mill Dashboard Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login = st.form_submit_button("Login")

        if login:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")

    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("User")

st.sidebar.write(f"👤 {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# -----------------------------
# TITLE
# -----------------------------
st.title("🏭 Cold Mill Processing Line Dashboard")

# -----------------------------
# SAMPLE DATA
# -----------------------------
np.random.seed(1)

dates = pd.date_range("2026-01-01", periods=120)

df = pd.DataFrame({

    "Date": np.random.choice(dates, 300),

    "Shift": np.random.choice(["A","B","C"],300),

    "Coil_ID": np.random.randint(1000,1100,300),

    "Width_mm": np.random.randint(900,1600,300),

    "Thickness_mm": np.round(np.random.normal(1.5,0.05,300),3),

    "Target_Thickness_mm":1.5,

    "Production_tons":np.random.randint(15,30,300),

    "Downtime_minutes":np.random.randint(0,60,300),

    "Delay_Agency":np.random.choice(
        ["Mechanical","Electrical","Operator","Material","Quality"],300
    ),

    "Delay_Reason":np.random.choice(
        ["Roll change","Strip break","Sensor fault","Coil jam","Setup delay"],300
    ),

    "Setup_Time_min":np.random.randint(10,45,300),

    "Operator":np.random.choice(
        ["John","Mike","Ravi","Chen","Luis"],300
    )

})

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 KPI Overview","⚙️ Downtime Analysis","🔍 Coil Drilldown","📋 Data"]
)

# -----------------------------
# KPI TAB
# -----------------------------
with tab1:

    st.subheader("Production KPIs")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "Total Production (tons)",
        int(df["Production_tons"].sum())
    )

    col2.metric(
        "Average Setup Time",
        f"{df['Setup_Time_min'].mean():.1f} min"
    )

    col3.metric(
        "Total Downtime",
        f"{df['Downtime_minutes'].sum()} min"
    )

    thickness_dev = abs(df["Thickness_mm"]-df["Target_Thickness_mm"]).mean()

    col4.metric(
        "Thickness Deviation",
        f"{thickness_dev:.3f} mm"
    )

    st.subheader("Production Trend")

    prod_trend = df.groupby("Date")["Production_tons"].sum()

    st.line_chart(prod_trend)

# -----------------------------
# DOWNTIME TAB
# -----------------------------
with tab2:

    col1,col2 = st.columns(2)

    with col1:

        st.subheader("Downtime by Agency")

        agency_data = df.groupby("Delay_Agency")["Downtime_minutes"].sum()

        fig,ax = plt.subplots(figsize=(4,4))

        ax.pie(
            agency_data,
            labels=agency_data.index,
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title("Downtime Distribution")

        st.pyplot(fig)

    with col2:

        st.subheader("Downtime Pareto (Reason)")

        reason_data = (
            df.groupby("Delay_Reason")["Downtime_minutes"]
            .sum()
            .sort_values(ascending=False)
        )

        fig,ax = plt.subplots(figsize=(6,4))

        reason_data.plot(kind="bar",ax=ax)

        ax.set_ylabel("Downtime Minutes")

        st.pyplot(fig)

# -----------------------------
# COIL DRILLDOWN
# -----------------------------
with tab3:

    st.subheader("Coil Drilldown Report")

    coil_list = sorted(df["Coil_ID"].unique())

    selected_coil = st.selectbox(
        "Select Coil",
        coil_list
    )

    coil_data = df[df["Coil_ID"]==selected_coil]

    st.write("### Coil Setup Details")

    st.dataframe(
        coil_data[
            [
                "Date",
                "Shift",
                "Operator",
                "Width_mm",
                "Thickness_mm",
                "Target_Thickness_mm",
                "Setup_Time_min"
            ]
        ]
    )

    st.subheader("Thickness Test Graph")

    fig,ax = plt.subplots(figsize=(7,4))

    ax.plot(
        coil_data.index,
        coil_data["Thickness_mm"],
        marker="o",
        label="Measured"
    )

    ax.axhline(
        coil_data["Target_Thickness_mm"].iloc[0],
        color="red",
        linestyle="--",
        label="Target"
    )

    ax.set_xlabel("Sample")

    ax.set_ylabel("Thickness (mm)")

    ax.legend()

    st.pyplot(fig)

# -----------------------------
# DATA TAB
# -----------------------------
with tab4:

    st.subheader("Raw Production Data")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "cold_mill_report.csv",
        "text/csv"
    )
