# Energy Consumption and Utility Usage Analysis

A Python project for analyzing hourly energy usage, identifying consumption patterns, finding statistically unusual readings, and creating reports and visualizations.

**Data note:** The included dataset is synthetic practice data. It does not represent real meter readings or a real facility.

## Project objectives

- Calculate total, average, median, minimum, and maximum energy usage.
- Summarize usage by day, week, and month.
- Identify peak usage hours, days, and months.
- Compare weekday and weekend consumption.
- Calculate a 7-day rolling average for hourly readings.
- Flag statistical anomalies using a z-score threshold of 3.
- Estimate monthly energy costs when tariff data is available.
- Explore the relationship between temperature and energy usage.
- Create charts, summary tables, and written findings.

## Dataset

The generator creates 60 days of hourly sample readings (1,440 records) in `data/raw/energy_consumption.csv`.

The dataset includes date, time, energy usage, meter, location, equipment, temperature, day type, tariff, and a synthetic unusual-reading indicator.

The analysis also creates a separate `Anomaly` label using the z-score method. An anomaly is a reading to investigate; it is not automatically an error.

## Setup

From the project folder, run these commands in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the project

Generate the sample dataset:

```powershell
python generate_sample_data.py
```

Run the analysis and create its output files:

```powershell
python main.py
```

Launch the interactive dashboard:

```powershell
streamlit run app.py
```

The deployed dashboard is available at:  
https://energy-consumption-analysis-09.streamlit.app/

## Cleaning and analysis notes

- Invalid timestamps and missing or non-numeric energy values are dropped during preparation.
- Duplicate readings for the same meter and timestamp keep the first record.
- Negative readings are retained and reported for investigation.
- Missing hourly intervals are counted, not filled in.
- The 7-day rolling average uses 168 hourly readings.
- Statistical anomalies are flagged when the absolute z-score is greater than 3.

## Outputs

The project creates:

- `data/processed/cleaned_energy_data.csv` — prepared readings with time features and anomaly results.
- `outputs/monthly_energy_report.csv` — monthly totals, averages, peak and minimum readings, and anomaly counts.
- `outputs/energy_summary_report.txt` — KPIs, monthly and weekly summaries, and business findings.
- `outputs/data_quality_summary.txt` — data-quality check counts and handling notes.
- `outputs/01_energy_over_time.png` through `outputs/10_anomalies_by_month.png` — Matplotlib visualizations.

## Visualizations

The generated charts cover:

1. Energy use over time.
2. Actual readings and the 7-day rolling average.
3. Monthly total usage.
4. Monthly average usage.
5. Average usage by hour.
6. Weekday versus weekend usage.
7. Energy usage distribution.
8. Temperature versus energy usage.
9. Anomalies over time.
10. Anomaly counts by month.

## Project structure

- `generate_sample_data.py` — creates the synthetic CSV.
- `main.py` — runs preparation, analysis, chart creation, and reporting.
- `app.py` — displays the Streamlit dashboard.
- `config.py` — defines project folders and paths.
- `src/analysis.py` — analysis calculations and anomaly detection.
- `src/data_loader.py` — loads the CSV.
- `src/preprocessing.py` — reusable preprocessing functions.
- `src/visualization.py` — creates the Matplotlib charts.
- `src/reporting.py` — writes the summary report.
- `tests/` — preprocessing checks.
- `requirements.txt` — Python package requirements.