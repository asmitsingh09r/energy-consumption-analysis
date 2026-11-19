"""Analysis functions for energy consumption data."""

import pandas as pd


def prepare_energy_data(dataframe):
    """Clean core fields and add time features for analysis."""
    required = ["Date", "Time", "Energy_Usage_kWh"]
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = dataframe.copy()
    data["Timestamp"] = pd.to_datetime(
        data["Date"].astype(str) + " " + data["Time"].astype(str),
        errors="coerce",
    )
    data["Energy_Usage_kWh"] = pd.to_numeric(
        data["Energy_Usage_kWh"], errors="coerce"
    )

    # Drop rows that cannot be used for time-based energy analysis.
    data = data.dropna(subset=["Timestamp", "Energy_Usage_kWh"])

    # If a meter has duplicate timestamps, keep its first reading.
    duplicate_columns = ["Timestamp"]
    if "Meter_ID" in data.columns:
        duplicate_columns.insert(0, "Meter_ID")
    data = data.drop_duplicates(subset=duplicate_columns)

    data = data.sort_values("Timestamp").reset_index(drop=True)
    data["Hour"] = data["Timestamp"].dt.hour
    data["Day_Name"] = data["Timestamp"].dt.day_name()
    data["Day_Type"] = data["Timestamp"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )
    data["Month"] = data["Timestamp"].dt.to_period("M").astype(str)

    # Hourly data: 168 readings represent a 7-day rolling average.
    data["Rolling_7_Day"] = data["Energy_Usage_kWh"].rolling(
        window=168, min_periods=24
    ).mean()

    return data


def calculate_kpis(dataframe):
    """Calculate overall consumption statistics."""
    data = prepare_energy_data(dataframe)
    energy = data["Energy_Usage_kWh"]

    return {
        "total_kWh": energy.sum(),
        "average_kWh": energy.mean(),
        "median_kWh": energy.median(),
        "minimum_kWh": energy.min(),
        "maximum_kWh": energy.max(),
        "standard_deviation_kWh": energy.std(),
        "number_of_readings": len(energy),
    }


def detect_anomalies(dataframe, threshold=3):
    """Flag readings whose absolute z-score exceeds the threshold."""
    data = prepare_energy_data(dataframe)
    energy = data["Energy_Usage_kWh"]
    standard_deviation = energy.std()

    if pd.isna(standard_deviation) or standard_deviation == 0:
        data["Z_Score"] = 0.0
        data["Anomaly"] = "Normal"
    else:
        data["Z_Score"] = (energy - energy.mean()) / standard_deviation
        data["Anomaly"] = data["Z_Score"].abs().gt(threshold).map(
            {True: "Anomaly", False: "Normal"}
        )

    return data


def daily_summary(dataframe):
    """Summarize total, average, maximum, and minimum use per day."""
    data = prepare_energy_data(dataframe)
    data["Date"] = data["Timestamp"].dt.date

    return (
        data.groupby("Date")["Energy_Usage_kWh"]
        .agg(Total_kWh="sum", Average_kWh="mean",
             Maximum_kWh="max", Minimum_kWh="min")
        .reset_index()
    )


def weekly_summary(dataframe):
    """Summarize consumption by calendar week."""
    data = prepare_energy_data(dataframe)
    data["Week"] = data["Timestamp"].dt.to_period("W").astype(str)

    return (
        data.groupby("Week")["Energy_Usage_kWh"]
        .agg(Total_kWh="sum", Average_kWh="mean")
        .reset_index()
    )


def monthly_summary(dataframe):
    """Summarize consumption and statistical anomalies by month."""
    data = detect_anomalies(dataframe)

    return (
        data.groupby("Month")
        .agg(
            Total_kWh=("Energy_Usage_kWh", "sum"),
            Average_kWh=("Energy_Usage_kWh", "mean"),
            Peak_kWh=("Energy_Usage_kWh", "max"),
            Minimum_kWh=("Energy_Usage_kWh", "min"),
            Anomaly_Count=("Anomaly", lambda values: (values == "Anomaly").sum()),
        )
        .reset_index()
    )


def weekday_weekend_summary(dataframe):
    """Compare consumption on weekdays and weekends."""
    data = prepare_energy_data(dataframe)

    return (
        data.groupby("Day_Type")["Energy_Usage_kWh"]
        .agg(Average_kWh="mean", Total_kWh="sum", Peak_kWh="max")
        .reset_index()
    )


def hourly_summary(dataframe):
    """Calculate average consumption for each hour of the day."""
    data = prepare_energy_data(dataframe)

    return (
        data.groupby("Hour")["Energy_Usage_kWh"]
        .mean()
        .sort_values(ascending=False)
        .rename("Average_kWh")
        .reset_index()
    )


def peak_usage_periods(dataframe):
    """Find the highest-use hour, day, and month."""
    data = prepare_energy_data(dataframe)
    data["Date_Only"] = data["Timestamp"].dt.date

    daily_totals = data.groupby("Date_Only")["Energy_Usage_kWh"].sum()
    monthly_totals = data.groupby("Month")["Energy_Usage_kWh"].sum()
    hourly_averages = data.groupby("Hour")["Energy_Usage_kWh"].mean()

    return {
        "peak_average_hour": int(hourly_averages.idxmax()),
        "highest_consumption_day": str(daily_totals.idxmax()),
        "highest_consumption_month": str(monthly_totals.idxmax()),
    }


def get_unusual_readings(dataframe):
    """Return statistical anomalies using the z-score rule."""
    data = detect_anomalies(dataframe)
    return data[data["Anomaly"] == "Anomaly"].copy()
def data_quality_summary(dataframe):
    """Count common data-quality issues without hiding them."""
    data = dataframe.copy()

    timestamps = pd.to_datetime(
        data["Date"].astype(str) + " " + data["Time"].astype(str),
        errors="coerce",
    )
    energy = pd.to_numeric(data["Energy_Usage_kWh"], errors="coerce")

    duplicate_columns = ["Timestamp"]
    if "Meter_ID" in data.columns:
        duplicate_columns.insert(0, "Meter_ID")

    checked = data.assign(Timestamp=timestamps).dropna(subset=["Timestamp"])
    duplicate_count = int(
        checked.duplicated(subset=duplicate_columns).sum()
    )

    # For hourly data, count missing hourly timestamps between readings.
    missing_hours = 0
    groups = (
        checked.groupby("Meter_ID")
        if "Meter_ID" in checked.columns
        else [("all", checked)]
    )

    for _, group in groups:
        observed = pd.DatetimeIndex(group["Timestamp"].drop_duplicates())
        if len(observed) > 1:
            expected = pd.date_range(
                observed.min(), observed.max(), freq="h"
            )
            missing_hours += len(expected.difference(observed))

    return {
        "Invalid timestamps": int(timestamps.isna().sum()),
        "Missing or non-numeric energy values": int(energy.isna().sum()),
        "Duplicate meter timestamps": duplicate_count,
        "Negative energy readings": int((energy < 0).sum()),
        "Missing hourly intervals": int(missing_hours),
    }