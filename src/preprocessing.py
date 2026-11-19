
"""
Data preprocessing module.

Provides reusable functions for cleaning and preparing
raw energy consumption data for analysis.
"""

import logging

import pandas as pd


logger = logging.getLogger(__name__)


def handle_missing_values(dataframe):
    """
    Handle missing values in numerical and categorical columns.

    Numerical columns are filled with their median.
    Categorical columns are filled with their mode.

    Args:
        dataframe (pd.DataFrame): Input dataset.

    Returns:
        pd.DataFrame: Dataset with missing values handled.
    """

    if dataframe.empty:
        raise ValueError("Cannot preprocess an empty dataset.")

    cleaned_data = dataframe.copy()

    for column in cleaned_data.columns:

        missing_count = cleaned_data[column].isna().sum()

        if missing_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned_data[column]):

            median_value = cleaned_data[column].median()

            cleaned_data[column] = (
                cleaned_data[column].fillna(median_value)
            )

        else:

            mode_values = cleaned_data[column].mode()

            if not mode_values.empty:
                cleaned_data[column] = (
                    cleaned_data[column].fillna(mode_values.iloc[0])
                )

        logger.info(
            "Handled %s missing values in column '%s'",
            missing_count,
            column
        )

    return cleaned_data


def remove_duplicates(dataframe):
    """
    Remove duplicate records from the dataset.

    Args:
        dataframe (pd.DataFrame): Input dataset.

    Returns:
        pd.DataFrame: Dataset without duplicate records.
    """

    original_count = len(dataframe)

    cleaned_data = dataframe.drop_duplicates().copy()

    removed_count = original_count - len(cleaned_data)

    logger.info("Removed %s duplicate records.", removed_count)

    return cleaned_data


def convert_date_columns(dataframe, date_columns):
    """
    Convert specified columns into datetime format.

    Args:
        dataframe (pd.DataFrame): Input dataset.
        date_columns (list): Names of date columns.

    Returns:
        pd.DataFrame: Dataset with converted date columns.
    """

    cleaned_data = dataframe.copy()

    for column in date_columns:

        if column not in cleaned_data.columns:
            raise ValueError(
                f"Date column '{column}' does not exist."
            )

        cleaned_data[column] = pd.to_datetime(
            cleaned_data[column],
            errors="coerce"
        )

        logger.info("Converted column '%s' to datetime.", column)

    return cleaned_data


def preprocess_data(dataframe, date_columns=None):
    """
    Execute the complete preprocessing pipeline.

    Args:
        dataframe (pd.DataFrame): Raw dataset.
        date_columns (list, optional): Date columns to convert.

    Returns:
        pd.DataFrame: Cleaned dataset.
    """

    if dataframe.empty:
        raise ValueError("Input dataset is empty.")

    logger.info("Starting data preprocessing.")

    cleaned_data = dataframe.copy()

    cleaned_data = remove_duplicates(cleaned_data)

    if date_columns:
        cleaned_data = convert_date_columns(
            cleaned_data,
            date_columns
        )

    cleaned_data = handle_missing_values(cleaned_data)

    logger.info("Data preprocessing completed successfully.")

    return cleaned_data
