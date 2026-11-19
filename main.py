"""Run the energy data preparation and analysis workflow."""

from config import (
    OUTPUT_DIR,
    PROCESSED_DATA_PATH,
    create_project_directories,
)
from src.analysis import (
    calculate_kpis,
    data_quality_summary,
    detect_anomalies,
    get_unusual_readings,
    hourly_summary,
    monthly_summary,
    peak_usage_periods,
    weekday_weekend_summary,
    weekly_summary,
)
from src.data_loader import load_data
from src.reporting import save_summary_report
from src.visualization import save_all_charts


def main():
    create_project_directories()

    try:
        raw_data = load_data()
        quality = data_quality_summary(raw_data)
        print("\nData quality checks")
        for check, count in quality.items():
            print(f"{check}: {count}")

        quality_lines = [
            "DATA QUALITY CHECKS",
            *[f"{check}: {count}" for check, count in quality.items()],
            "",
            "Invalid timestamp or energy rows are dropped during preparation.",
            "Duplicate meter timestamps keep their first reading.",
            "Negative readings are retained for investigation.",
            "Missing hourly intervals are counted, not filled in.",
        ]
        quality_path = OUTPUT_DIR / "data_quality_summary.txt"
        quality_path.write_text("\n".join(quality_lines), encoding="utf-8")
        print(f"Data quality summary saved to: {quality_path}")
        analyzed_data = detect_anomalies(raw_data)

        analyzed_data.to_csv(PROCESSED_DATA_PATH, index=False)
        print(f"Cleaned dataset saved to: {PROCESSED_DATA_PATH}")

        print("\nOverall statistics")
        for name, value in calculate_kpis(analyzed_data).items():
            print(f"{name.replace('_', ' ').title()}: {value:.2f}")

        print("\nWeekly summary")
        print(weekly_summary(analyzed_data).to_string(index=False))

        monthly = monthly_summary(analyzed_data)
        print("\nMonthly summary")
        print(monthly.to_string(index=False))
        monthly.to_csv(OUTPUT_DIR / "monthly_energy_report.csv", index=False)

        print("\nWeekday vs weekend")
        print(weekday_weekend_summary(analyzed_data).to_string(index=False))

        print("\nAverage usage by hour, highest first")
        print(hourly_summary(analyzed_data).head().to_string(index=False))

        print("\nPeak usage periods")
        for name, value in peak_usage_periods(analyzed_data).items():
            print(f"{name.replace('_', ' ').title()}: {value}")

        unusual = get_unusual_readings(analyzed_data)
        print(f"\nStatistical anomalies found: {len(unusual)}")
        print(
            unusual[
                ["Timestamp", "Energy_Usage_kWh", "Z_Score", "Anomaly"]
            ].to_string(index=False)
        )

        save_all_charts(analyzed_data, OUTPUT_DIR)
        save_summary_report(
            analyzed_data,
            OUTPUT_DIR / "energy_summary_report.txt",
        )

    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nCould not complete the analysis: {error}")


if __name__ == "__main__":
    main()