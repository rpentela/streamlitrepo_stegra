import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

st.set_page_config(layout="wide")

# ---------------- LOGIN SYSTEM ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():

    st.title("Cold Mill Production Dashboard Login")

    with st.form("login_form"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        submit = st.form_submit_button("Login")

        if submit:
            if user == "admin" and pwd == "master":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- SAMPLE DATA ---------------- #

@st.cache_data
def generate_data():

    np.random.seed(1)

    coils = [f"C{1000+i}" for i in range(50)]

    data = pd.DataFrame({
        "Coil_ID": coils,
        "Thickness": np.random.normal(1.2,0.05,50),
        "Target_Thickness":1.2,
        "Weight_tons":np.random.randint(20,30,50),
        "Yield":np.random.uniform(90,98,50),
        "Scrap":np.random.uniform(0.5,5,50),
        "Shift":np.random.choice(["A","B","C"],50),
        "Production_Time_hr":np.random.uniform(1.2,2.5,50)
    })

    defects = pd.DataFrame({
        "Defect":["Edge Crack","Roll Mark","Scratch","Oil Stain","Gauge Variation"],
        "Count":[23,15,9,12,7]
    })

    downtime = pd.DataFrame({
        "Reason":["Roll Change","Coil Break","Maintenance","Hydraulic Issue","Setup Delay"],
        "Minutes":[120,60,180,50,70]
    })

    thickness_samples = np.random.normal(1.2,0.04,100)

    return data, defects, downtime, thickness_samples

# ---------------- DASHBOARD ---------------- #

def dashboard():

    st.title("Cold Rolling Mill Production Dashboard")

    data, defects, downtime, thickness_samples = generate_data()

    if "selected_coil" not in st.session_state:
        st.session_state.selected_coil = None

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tabs = st.tabs([
        "KPIs",
        "Production",
        "Quality",
        "Downtime",
        "Gauge SPC",
        "AI Monitoring"
    ])

# ---------------- KPI TAB ---------------- #

    with tabs[0]:

        st.subheader("Key Performance Indicators")

        avg_yield = data["Yield"].mean()
        scrap = data["Scrap"].mean()

        utilization = (data["Production_Time_hr"].sum() / (24*3)) * 100

        col1,col2,col3 = st.columns(3)

        col1.metric("Average Yield %",f"{avg_yield:.2f}")
        col2.metric("Average Scrap %",f"{scrap:.2f}")
        col3.metric("Mill Utilization %",f"{utilization:.1f}")

        st.subheader("Shift Performance")

        shift_perf = data.groupby("Shift")["Weight_tons"].sum()

        st.bar_chart(shift_perf)

# ---------------- PRODUCTION TAB ---------------- #

    with tabs[1]:

        st.subheader("Production Data")

        for i,row in data.iterrows():

            col1,col2,col3,col4,col5 = st.columns([2,2,2,2,1])

            col1.write(row["Coil_ID"])
            col2.write(round(row["Thickness"],3))
            col3.write(row["Weight_tons"])
            col4.write(row["Shift"])

            if col5.button("View",key=row["Coil_ID"]):
                st.session_state.selected_coil = row["Coil_ID"]
                st.rerun()

        if st.session_state.selected_coil:

            st.subheader(f"Coil Drilldown : {st.session_state.selected_coil}")

            coil = data[data["Coil_ID"]==st.session_state.selected_coil]

            st.write(coil)

            fig,ax = plt.subplots()

            samples = np.random.normal(coil["Thickness"].values[0],0.02,30)

            ax.plot(samples)

            ax.axhline(coil["Target_Thickness"].values[0],color="red")

            ax.set_title("Thickness Measurement")

            st.pyplot(fig)

# ---------------- QUALITY TAB ---------------- #

    with tabs[2]:

        st.subheader("Quality Defects")

        fig,ax = plt.subplots()

        ax.bar(defects["Defect"],defects["Count"])

        ax.set_title("Defect Distribution")

        st.pyplot(fig)

# ---------------- DOWNTIME TAB ---------------- #

    with tabs[3]:

        st.subheader("Downtime Pareto")

        downtime_sorted = downtime.sort_values(by="Minutes",ascending=False)

        fig,ax = plt.subplots()

        ax.bar(downtime_sorted["Reason"],downtime_sorted["Minutes"])

        ax.set_title("Downtime Pareto")

        st.pyplot(fig)

# ---------------- SPC TAB ---------------- #

    with tabs[4]:

        st.subheader("Gauge Control SPC Chart")

        mean = np.mean(thickness_samples)
        std = np.std(thickness_samples)

        ucl = mean + 3*std
        lcl = mean - 3*std

        fig,ax = plt.subplots()

        ax.plot(thickness_samples)

        ax.axhline(mean)
        ax.axhline(ucl)
        ax.axhline(lcl)

        ax.set_title("SPC Chart")

        st.pyplot(fig)

# ---------------- AI ANOMALY ---------------- #

    with tabs[5]:

        st.subheader("AI Anomaly Detection")

        model = IsolationForest(contamination=0.05)

        X = data[["Thickness","Weight_tons","Yield"]]

        model.fit(X)

        preds = model.predict(X)

        data["Anomaly"] = preds

        anomalies = data[data["Anomaly"]==-1]

        st.write("Detected abnormal coils")

        st.write(anomalies)

# ---------------- MAIN ---------------- #

if not st.session_state.logged_in:
    login()
else:
    dashboard()

