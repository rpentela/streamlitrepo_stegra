import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

st.set_page_config(layout="wide", page_title="Cold Mill Dashboard")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.main-title{
font-size:32px;
font-weight:700;
color:#1f4e79;
}

.section-title{
font-size:22px;
font-weight:600;
color:#2c7be5;
margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Cold Mill Dashboard Login")
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

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- SAMPLE DATA ----------------
np.random.seed(42)
n = 50
production = pd.DataFrame({
    "Coil_ID": [f"C{1000+i}" for i in range(n)],
    "Thickness": np.round(np.random.normal(1.2,0.05,n),3),
    "Target": 1.2,
    "Weight_tons": np.random.randint(18,28,n),
    "Shift": np.random.choice(["A","B","C"],n),
    "Date": pd.date_range("2025-01-01", periods=n),
    "Quality": np.random.choice(["OK","Minor Defect","Reject"],n,p=[0.8,0.15,0.05])
})
production["Deviation"] = production["Thickness"] - production["Target"]

downtime = pd.DataFrame({
    "Reason": ["Setup Delay","Roll Change","Power","Mechanical","Hydraulic","Operator"],
    "Minutes": [120,80,40,35,20,15]
})

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Filters 🛠")
filter_shift = st.sidebar.multiselect("Select Shift", options=production["Shift"].unique(), default=production["Shift"].unique())
filter_quality = st.sidebar.multiselect("Select Quality", options=production["Quality"].unique(), default=production["Quality"].unique())
filter_date = st.sidebar.date_input("Select Date range", [production["Date"].min(), production["Date"].max()])

filtered_prod = production[
    (production["Shift"].isin(filter_shift) if filter_shift else production["Shift"].notnull()) &
    (production["Quality"].isin(filter_quality) if filter_quality else production["Quality"].notnull()) &
    (production["Date"] >= pd.to_datetime(filter_date[0])) &
    (production["Date"] <= pd.to_datetime(filter_date[1]))
]

if filtered_prod.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">🏭 Cold Mill Processing Dashboard</div>', unsafe_allow_html=True)
if st.sidebar.button("Logout"):
    st.session_state.logged_in=False
    st.rerun()

# ---------------- KPI ----------------
st.markdown('<div class="section-title">📊 KPIs</div>', unsafe_allow_html=True)
yield_rate = (filtered_prod["Quality"]=="OK").mean()*100
scrap_rate = (filtered_prod["Quality"]=="Reject").mean()*100
utilization = np.random.randint(75,92)
col1, col2, col3 = st.columns(3)
col1.metric("✔ Yield %", f"{yield_rate:.1f}%")
col2.metric("♻ Scrap %", f"{scrap_rate:.1f}%")
col3.metric("⚙ Mill Utilization %", f"{utilization}%")
st.divider()

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Production",
    "📉 Downtime",
    "👨‍🏭 Shift Performance",
    "📏 Gauge SPC",
    "🤖 AI Anomaly Detection"
])

# ================= PRODUCTION TAB =================
with tab1:
    st.markdown('<div class="section-title">📦 Production Data</div>', unsafe_allow_html=True)

    for i, row in filtered_prod.iterrows():
        c1,c2,c3,c4,c5 = st.columns([2,2,2,2,1])
        c1.write(row["Coil_ID"])
        c2.write(row["Thickness"])
        c3.write(row["Weight_tons"])
        c4.write(row["Quality"])

        if c5.button("View", key=row["Coil_ID"]):
            st.session_state["coil"] = row["Coil_ID"]
            # Modal popup
            with st.modal(f"🔎 Coil Drilldown: {row['Coil_ID']}", key=row["Coil_ID"]+"_modal"):
                coil_df = production[production["Coil_ID"]==row["Coil_ID"]]
                st.dataframe(coil_df)
                fig, ax = plt.subplots(figsize=(5,2.5))
                test = np.random.normal(coil_df["Thickness"].values[0], 0.02, 30)
                ax.plot(test)
                ax.axhline(coil_df["Target"].values[0], color="green", linestyle="--")
                ax.set_title("Thickness Test Data")
                st.pyplot(fig)

# ================= DOWNTIME TAB =================
with tab2:
    st.markdown('<div class="section-title">📉 Downtime Pareto</div>', unsafe_allow_html=True)
    downtime_sorted = downtime.sort_values("Minutes", ascending=False)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(downtime_sorted["Reason"], downtime_sorted["Minutes"], color="#2c7be5")
    ax.set_ylabel("Minutes")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ================= SHIFT PERFORMANCE =================
with tab3:
    st.markdown('<div class="section-title">👨‍🏭 Shift Performance</div>', unsafe_allow_html=True)
    shift_perf = filtered_prod.groupby("Shift")["Weight_tons"].sum()
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(shift_perf.index, shift_perf.values, color="#ff7f0e")
    ax.set_ylabel("Production (tons)")
    st.pyplot(fig)

# ================= SPC GAUGE =================
with tab4:
    st.markdown('<div class="section-title">📏 Gauge SPC Control</div>', unsafe_allow_html=True)
    if "coil" in st.session_state:
        coil_df = production[production["Coil_ID"]==st.session_state["coil"]]
        thickness = coil_df["Thickness"]
    else:
        thickness = filtered_prod["Thickness"]

    mean = thickness.mean()
    std = thickness.std()
    ucl = mean + 3*std
    lcl = mean - 3*std

    fig, ax = plt.subplots(figsize=(5,2.5))
    ax.plot(thickness.values, marker='o')
    ax.axhline(mean, color="green", label="Mean")
    ax.axhline(ucl, color="red", linestyle="--", label="UCL")
    ax.axhline(lcl, color="red", linestyle="--", label="LCL")
    ax.legend(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)

# ================= AI ANOMALY DETECTION =================
with tab5:
    st.markdown('<div class="section-title">🤖 AI Gauge Anomaly Detection</div>', unsafe_allow_html=True)
    X = filtered_prod[["Thickness"]]
    model = IsolationForest(contamination=0.05)
    filtered_prod["anomaly"] = model.fit_predict(X)
    anomalies = filtered_prod[filtered_prod["anomaly"]==-1]
    normal = filtered_prod[filtered_prod["anomaly"]==1]

    fig, ax = plt.subplots(figsize=(5,3))
    ax.scatter(normal.index, normal["Thickness"], label="Normal")
    ax.scatter(anomalies.index, anomalies["Thickness"], color="red", label="Anomaly")
    ax.legend(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)

    st.write("Detected anomalies:")
    st.dataframe(anomalies)
