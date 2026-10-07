"""Render EDA figures from the prepared transaction and customer data."""
import pandas as pd

from src.config import FEATURES_FILE, TRANSACTIONS_FILE
from src.pipeline import make_eda


if __name__ == "__main__":
    make_eda(pd.read_parquet(TRANSACTIONS_FILE), pd.read_parquet(FEATURES_FILE))
    print("Wrote EDA figures to reports/figures.")
