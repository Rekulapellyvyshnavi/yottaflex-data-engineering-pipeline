"""Read Parquet batches from an input directory."""
from pathlib import Path
import pandas as pd


def read_parquet_files(input_dir):
    root = Path(input_dir)
    return [(path, pd.read_parquet(path)) for path in sorted(root.glob("*.parquet"))]
