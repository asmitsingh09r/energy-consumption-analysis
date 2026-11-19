
"""
Data loading module.

Responsible for reading the raw energy consumption dataset.
"""

import logging
import pandas as pd

from config import RAW_DATA_PATH


logger = logging.getLogger(__name__)


def load_data(file_path=RAW_DATA_PATH):
    """
    Load energy consumption data from a CSV file.

    Args:
        file_path: Location of the CSV dataset.

    Returns:
        pandas.DataFrame: Loaded dataset.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If the dataset is empty.
    """

    try:
        logger.info("Loading dataset from: %s", file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        dataframe = pd.read_csv(file_path)

        if dataframe.empty:
            raise ValueError("The dataset is empty.")

        logger.info(
            "Dataset loaded successfully. Rows: %s, Columns: %s",
            dataframe.shape[0],
            dataframe.shape[1],
        )

        return dataframe

    except pd.errors.ParserError as error:
        logger.exception("Unable to parse CSV file.")
        raise ValueError("Invalid CSV file format.") from error

    except FileNotFoundError:
        logger.error("Dataset file was not found.")
        raise
