"""Generate a clearly labeled synthetic hourly energy dataset."""

import csv
import math
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path


# Using the same seed produces the same dataset each time.
RANDOM_SEED = 42
NUMBER_OF_DAYS = 60
START_DATE = date(2025, 1, 1)

OUTPUT_FILE = (
    Path(__file__).parent
    / "data"
    / "raw"
    / "energy_consumption.csv"
)

random.seed(RANDOM_SEED)


def main():
    """Create the output folder and write the synthetic CSV file."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    start_datetime = datetime.combine(START_DATE, time.min)

    for hour_number in range(NUMBER_OF_DAYS * 24):
        timestamp = start_datetime + timedelta(hours=hour_number)
        hour = timestamp.hour
        weekday = timestamp.weekday()

        # Usage is lower overnight, rises during the day, and peaks in
        # the afternoon. Weekdays are generally busier than weekends.
        daily_pattern = 1.0 + 0.45 * math.sin(
            2 * math.pi * (hour - 8) / 24
        )
        daily_pattern = max(0.35, daily_pattern)

        weekly_pattern = 1.15 if weekday < 5 else 0.78
        temperature = (
            18
            + 9 * math.sin(2 * math.pi * (hour - 7) / 24)
            + random.uniform(-2.5, 2.5)
        )

        # Warmer hours add some cooling demand.
        temperature_effect = 1 + max(0, temperature - 22) * 0.025
        random_variation = random.uniform(0.85, 1.15)

        usage = (
            8.0
            * daily_pattern
            * weekly_pattern
            * temperature_effect
            * random_variation
        )
        unusual_reading = False

        # Add a small number of flagged high or low readings.
        if hour_number in (137, 589, 1004, 1318):
            usage *= 2.8
            unusual_reading = True
        elif hour_number == 846:
            usage *= 0.12
            unusual_reading = True

        day_type = "Weekend" if weekday >= 5 else "Weekday"
        tariff = 0.12 if 0 <= hour < 6 else 0.20 if 17 <= hour < 22 else 0.16

        rows.append(
            {
                "Date": timestamp.strftime("%Y-%m-%d"),
                "Time": timestamp.strftime("%H:%M"),
                "Energy_Usage_kWh": round(usage, 3),
                "Meter_ID": "MTR-001",
                "Location": "Main Building",
                "Equipment": "Whole Building Meter",
                "Temperature": round(temperature, 1),
                "Day_Type": day_type,
                "Tariff_Per_Unit": tariff,
                "Is_Unusual_Reading": unusual_reading,
            }
        )

    fieldnames = [
        "Date",
        "Time",
        "Energy_Usage_kWh",
        "Meter_ID",
        "Location",
        "Equipment",
        "Temperature",
        "Day_Type",
        "Tariff_Per_Unit",
        "Is_Unusual_Reading",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Synthetic sample data created successfully.")
    print(f"Records written: {len(rows)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()