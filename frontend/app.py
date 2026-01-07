import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# Import GenAI assistant
#from 5_genai_assistant import MobilityGenAIAssistant

# -----------------------------
# CONFIG
# -----------------------------
DATA_PATH = Path("../data/cleaned/cleaned_taxi_data.csv")
OUTPUTS = Path("../outputs")
VIS_DIR = OUTPUTS / "visualizations"
SQL_DIR = OUTPUTS / "sql_results"

st.set_page_config(
    page_title="Urban Mobility Analytics Platform",
    layout="wide"
)

st.title("🚕 Intelligent Urban Mobility Analytics & GenAI Insights")

# -----------------------------
# SIDEBAR
# -----------------------------
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 KPIs & Overview",
        "📈 Visual Analytics",
        "🧮 SQL Insights",
        "⚡ Spark KPIs",
        "🤖 GenAI Chatbot"
    ]
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# =============================
# PAGE 1 — KPI OVERVIEW
# =============================
if page == "📊 KPIs & Overview":
    st.header("📊 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Trips", f"{len(df):,}")
    col2.metric("Total Revenue ($)", f"{df['total_amount'].sum():,.2f}")
    col3.metric("Avg Trip Distance (mi)", f"{df['trip_distance'].mean():.2f}")
    col4.metric("Avg Fare ($)", f"{df['fare_amount'].mean():.2f}")

    st.subheader("📄 Cleaned Data Preview")
    st.dataframe(df.head(100))

# =============================
# PAGE 2 — VISUALS
# =============================
elif page == "📈 Visual Analytics":
    st.header("📈 Mobility Visual Analytics")

    images = list(VIS_DIR.glob("*.png"))
    for img in images:
        st.subheader(img.stem.replace("_", " ").title())
        st.image(str(img), use_column_width=True)

# =============================
# PAGE 3 — SQL RESULTS
# =============================
elif page == "🧮 SQL Insights":
    st.header("🧮 SQL Analytics Results")

    files = list(SQL_DIR.glob("*.csv"))
    selected = st.selectbox("Select SQL Result", files)

    if selected:
        st.dataframe(pd.read_csv(selected))

# =============================
# PAGE 4 — SPARK
# =============================
elif page == "⚡ Spark KPIs":
    st.header("⚡ PySpark Aggregated Outputs")

    parquet_files = list((Path("../data/processed")).glob("*.parquet"))
    st.write("Available Spark Outputs:")
    for f in parquet_files:
        st.write("•", f.name)

# =============================
# PAGE 5 — GENAI CHATBOT
# =============================
