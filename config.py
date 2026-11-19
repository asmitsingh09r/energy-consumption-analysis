
"""
Project configuration.

Centralizes directory paths and project settings.
"""

from pathlib import Path

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Output directory
OUTPUT_DIR = BASE_DIR / "outputs"

# Dataset configuration
DATASET_FILENAME = "energy_consumption.csv"
RAW_DATA_PATH = RAW_DATA_DIR / DATASET_FILENAME

# Processed dataset configuration
PROCESSED_DATA_FILENAME = "cleaned_energy_data.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / PROCESSED_DATA_FILENAME

# Project information
PROJECT_NAME = "Energy Consumption Analysis"
PROJECT_VERSION = "1.0.0"


def create_project_directories():
    """Create required project directories if they do not exist."""

    directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        OUTPUT_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
