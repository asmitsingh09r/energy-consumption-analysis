"""Create a written energy analysis report with findings."""

from pathlib import Path

import pandas as pd

from src.analysis import (
    calculate_kpis,
    detect_anomalies,
    hourly_summary,
    monthly_summary,
    peak_usage_periods,
    weekday_weekend_summary,
    weekly_summary,
)


def save_summary_report(dataframe, output_path):
    """Save summary tables and business observations to a text file."""
    data = detect_anomalies(dataframe)
    kpis = calculate_kpis(data)
    monthly = monthly_summary(data)
    weekly = weekly_summary(data)
    day_comparison = weekday_weekend_summary(data)
    hourly = hourly_summary(data)
    peaks = peak_usage_periods(data)
    anomalies = data[data["Anomaly"] == "Anomaly"]

    findings = [
        "BUSINESS FINDINGS",
        (
            f"Average hourly usage was {kpis['average_kWh']:.2f} kWh; "
            f"total usage was {kpis['total_kWh']:.2f} kWh."
        ),
        (
            f"The highest average-use hour was "
            f"{int(hourly.iloc[0]['Hour']):02d}:00."
        ),
        (
            f"The highest-use day was {peaks['highest_consumption_day']}; "
            f"the highest-use month was "
            f"{peaks['highest_consumption_month']}."
        ),
        (
            f"The z-score rule flagged {len(anomalies)} readings for "
            "investigation. A statistical anomaly is not automatically an error."
        ),
    ]

    day_averages = day_comparison.set_index("Day_Type")["Average_kWh"]
    if {"Weekday", "Weekend"}.issubset(day_averages.index):
        weekday_avg = day_averages["Weekday"]
        weekend_avg = day_averages["Weekend"]
        if weekday_avg > weekend_avg:
            comparison = "Weekday average use was higher than weekend average use."
        elif weekend_avg > weekday_avg:
            comparison = "Weekend average use was higher than weekday average use."
        else:
            comparison = "Weekday and weekend average use were equal."
        findings.append(comparison)

    report_lines = [
        "ENERGY CONSUMPTION ANALYSIS",
        "Synthetic sample dataset; readings do not represent real meter data.",
        "",
        "OVERALL KPIs",
    ]

    for name, value in kpis.items():
        report_lines.append(f"{name.replace('_', ' ').title()}: {value:.2f}")

    report_lines.extend(["", *findings, "", "WEEKLY SUMMARY"])
    report_lines.append(weekly.to_string(index=False))

    report_lines.extend(["", "MONTHLY SUMMARY"])
    report_lines.append(monthly.to_string(index=False))

    report_lines.extend(["", "WEEKDAY VS WEEKEND"])
    report_lines.append(day_comparison.to_string(index=False))

    if "Tariff_Per_Unit" in data.columns:
        tariff = pd.to_numeric(data["Tariff_Per_Unit"], errors="coerce")
        if tariff.notna().any():
            cost_data = data.assign(
                Estimated_Cost=data["Energy_Usage_kWh"] * tariff
            )
            monthly_cost = cost_data.groupby("Month")["Estimated_Cost"].sum()
            report_lines.extend(["", "ESTIMATED COST BY MONTH"])
            report_lines.append(monthly_cost.to_string())

    if "Temperature" in data.columns:
        temperature = pd.to_numeric(data["Temperature"], errors="coerce")
        valid = temperature.notna() & data["Energy_Usage_kWh"].notna()
        if valid.sum() > 1:
            correlation = temperature[valid].corr(
                data.loc[valid, "Energy_Usage_kWh"]
            )
            report_lines.extend(
                ["", f"Temperature and usage correlation: {correlation:.3f}"]
            )
            report_lines.append(
                "Correlation describes association; it does not prove cause."
            )

    report_lines.extend(
        [
            "",
            "ANOMALY NOTE",
            "Anomalies were flagged when the absolute z-score exceeded 3.",
            "Review unusual readings in context before deciding whether they",
            "represent an error or a real operational event.",
            "",
            "LIMITATION",
            "This is synthetic practice data, so findings are examples rather",
            "than conclusions about an actual building or facility.",
        ]
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Full report saved to: {output_path}")