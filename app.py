"""Interactive dashboard for synthetic energy consumption data."""

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "raw" / "energy_consumption.csv"

st.set_page_config(page_title="Energy Consumption Analysis", layout="wide")
st.title("Energy Consumption Analysis")
st.caption("Practice dashboard using synthetic data, not real meter readings.")


if not DATA_FILE.exists():
    st.error(f"Dataset not found: {DATA_FILE}")
    st.info("Run `python generate_sample_data.py` from the project folder first.")
    st.stop()

data = pd.read_csv(DATA_FILE)

required_columns = [
    "Date",
    "Time",
    "Energy_Usage_kWh",
    "Is_Unusual_Reading",
]
missing_columns = [
    column for column in required_columns if column not in data.columns
]

if missing_columns:
    st.error(f"CSV is missing these columns: {', '.join(missing_columns)}")
    st.stop()

data["Energy_Usage_kWh"] = pd.to_numeric(
    data["Energy_Usage_kWh"], errors="coerce"
)
data["Timestamp"] = pd.to_datetime(
    data["Date"].astype(str) + " " + data["Time"].astype(str),
    errors="coerce",
)
data["Is_Unusual_Reading"] = (
    data["Is_Unusual_Reading"].astype(str).str.lower() == "true"
)
data = data.dropna(subset=["Timestamp", "Energy_Usage_kWh"])

if data.empty:
    st.error("The CSV does not contain any usable energy readings.")
    st.stop()

total_usage = data["Energy_Usage_kWh"].sum()
average_usage = data["Energy_Usage_kWh"].mean()
peak_usage = data["Energy_Usage_kWh"].max()
unusual_count = int(data["Is_Unusual_Reading"].sum())

metric_columns = st.columns(4)
metric_columns[0].metric("Total usage", f"{total_usage:,.1f} kWh")
metric_columns[1].metric("Average per hour", f"{average_usage:.2f} kWh")
metric_columns[2].metric("Peak hourly usage", f"{peak_usage:.2f} kWh")
metric_columns[3].metric("Flagged readings", unusual_count)

st.subheader("Hourly energy usage")
hourly_chart = data.set_index("Timestamp")[["Energy_Usage_kWh"]]
st.line_chart(hourly_chart, y="Energy_Usage_kWh")

st.subheader("Daily energy consumption")
daily_data = (
    data.groupby(data["Timestamp"].dt.date)["Energy_Usage_kWh"]
    .sum()
    .rename("Daily_kWh")
    .rename_axis("Date")
    .reset_index()
)
st.bar_chart(daily_data, x="Date", y="Daily_kWh")

st.subheader("Flagged unusual readings")
unusual_data = data[data["Is_Unusual_Reading"]].copy()
if unusual_data.empty:
    st.write("No readings are flagged.")
else:
    st.dataframe(
        unusual_data[
            ["Date", "Time", "Energy_Usage_kWh", "Is_Unusual_Reading"]
        ],
        hide_index=True,
    )

with st.expander("View all readings"):
    st.dataframe(data, hide_index=True)