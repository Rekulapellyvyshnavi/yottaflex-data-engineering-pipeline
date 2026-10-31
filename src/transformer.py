"""Standardize accepted records."""
import pandas as pd


def transform(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["category"] = result["category"].astype("string").str.strip().str.lower()
    result["amount"] = result["amount"].round(2)
    for column in ("region", "source_system"):
        if column not in result.columns:
            result[column] = "unknown"
        else:
            result[column] = result[column].fillna("unknown").astype("string").str.strip().str.lower()
    return result
