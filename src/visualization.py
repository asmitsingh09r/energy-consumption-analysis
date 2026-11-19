"""Create the energy analysis charts required by the project brief."""

from pathlib import Path

import matplotlib.pyplot as plt

from src.analysis import detect_anomalies


def save_all_charts(dataframe, output_folder):
    """Save ten analysis charts as PNG files."""
    data = detect_anomalies(dataframe)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    def save_plot(figure, filename):
        figure.tight_layout()
        figure.savefig(output_folder / filename, dpi=150)
        plt.close(figure)
        print(f"Chart saved: {output_folder / filename}")

    # 1. Energy usage over time
    figure, axis = plt.subplots(figsize=(12, 5))
    axis.plot(data["Timestamp"], data["Energy_Usage_kWh"], linewidth=0.8)
    axis.set(title="Energy Consumption Over Time",
             xlabel="Date and time", ylabel="Energy (kWh)")
    axis.grid(True, alpha=0.3)
    save_plot(figure, "01_energy_over_time.png")

    # 2. Actual readings compared with the 7-day rolling average
    figure, axis = plt.subplots(figsize=(12, 5))
    axis.plot(data["Timestamp"], data["Energy_Usage_kWh"],
              label="Actual", linewidth=0.7, alpha=0.55)
    axis.plot(data["Timestamp"], data["Rolling_7_Day"],
              label="7-day rolling average", linewidth=1.5)
    axis.set(title="Hourly Usage and 7-Day Rolling Average",
             xlabel="Date and time", ylabel="Energy (kWh)")
    axis.legend()
    axis.grid(True, alpha=0.3)
    save_plot(figure, "02_rolling_average.png")

    # 3 and 4. Monthly total and average usage
    month_stats = data.groupby("Month")["Energy_Usage_kWh"].agg(
        Total="sum", Average="mean"
    )

    figure, axis = plt.subplots(figsize=(10, 5))
    month_stats["Total"].plot(kind="bar", ax=axis)
    axis.set(title="Total Energy Usage by Month",
             xlabel="Month", ylabel="Total energy (kWh)")
    save_plot(figure, "03_monthly_total.png")

    figure, axis = plt.subplots(figsize=(10, 5))
    month_stats["Average"].plot(kind="bar", ax=axis)
    axis.set(title="Average Hourly Usage by Month",
             xlabel="Month", ylabel="Average energy (kWh)")
    save_plot(figure, "04_monthly_average.png")

    # 5. Average usage by hour of day
    hourly_average = data.groupby("Hour")["Energy_Usage_kWh"].mean()
    figure, axis = plt.subplots(figsize=(10, 5))
    hourly_average.plot(kind="bar", ax=axis)
    axis.set(title="Average Energy Usage by Hour",
             xlabel="Hour of day", ylabel="Average energy (kWh)")
    save_plot(figure, "05_average_by_hour.png")

    # 6. Weekday versus weekend usage
    day_type_average = data.groupby("Day_Type")["Energy_Usage_kWh"].mean()
    figure, axis = plt.subplots(figsize=(7, 5))
    day_type_average.plot(kind="bar", ax=axis)
    axis.set(title="Weekday vs Weekend Average Usage",
             xlabel="Day type", ylabel="Average energy (kWh)")
    save_plot(figure, "06_weekday_vs_weekend.png")

    # 7. Distribution of energy readings
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.hist(data["Energy_Usage_kWh"], bins=30, edgecolor="black")
    axis.set(title="Distribution of Energy Consumption",
             xlabel="Energy (kWh)", ylabel="Number of readings")
    save_plot(figure, "07_usage_distribution.png")

    # 8. Temperature versus energy usage (temperature is in this dataset)
    if "Temperature" in data.columns:
        temperature = data["Temperature"].astype(float)
        figure, axis = plt.subplots(figsize=(9, 5))
        axis.scatter(temperature, data["Energy_Usage_kWh"], alpha=0.45)
        axis.set(title="Temperature vs Energy Consumption",
                 xlabel="Temperature", ylabel="Energy (kWh)")
        save_plot(figure, "08_temperature_vs_usage.png")

    # 9. Energy readings with z-score anomalies highlighted
    anomalies = data[data["Anomaly"] == "Anomaly"]
    figure, axis = plt.subplots(figsize=(12, 5))
    axis.plot(data["Timestamp"], data["Energy_Usage_kWh"],
              label="Readings", linewidth=0.8)
    axis.scatter(anomalies["Timestamp"], anomalies["Energy_Usage_kWh"],
                 color="red", label="Z-score anomaly", zorder=3)
    axis.set(title="Energy Consumption Anomalies (Z-score)",
             xlabel="Date and time", ylabel="Energy (kWh)")
    axis.legend()
    axis.grid(True, alpha=0.3)
    save_plot(figure, "09_anomalies_over_time.png")

    # 10. Number of anomalies per month
    anomaly_counts = (
        data.assign(Is_Anomaly=data["Anomaly"] == "Anomaly")
        .groupby("Month")["Is_Anomaly"]
        .sum()
    )
    figure, axis = plt.subplots(figsize=(9, 5))
    anomaly_counts.plot(kind="bar", ax=axis)
    axis.set(title="Statistical Anomaly Count by Month",
             xlabel="Month", ylabel="Number of anomalies")
    save_plot(figure, "10_anomalies_by_month.png")