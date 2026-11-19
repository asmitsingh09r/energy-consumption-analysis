
import pandas as pd

from src.preprocessing import (
    remove_duplicates,
    handle_missing_values,
    preprocess_data
)


def test_remove_duplicates():
    dataframe = pd.DataFrame({
        "energy": [100, 200, 200]
    })

    result = remove_duplicates(dataframe)

    assert len(result) == 2


def test_handle_missing_values():
    dataframe = pd.DataFrame({
        "energy": [100, None, 300]
    })

    result = handle_missing_values(dataframe)

    assert result["energy"].isna().sum() == 0
    assert result["energy"].iloc[1] == 200


def test_preprocess_data():
    dataframe = pd.DataFrame({
        "energy": [100, None, 100, 300]
    })

    result = preprocess_data(dataframe)

    assert len(result) == 3
    assert result["energy"].isna().sum() == 0
