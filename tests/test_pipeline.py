import pandas as pd

from src.pipeline import clean_transactions


def test_clean_transactions_removes_cancellations_duplicates_and_invalid_rows():
    raw = pd.DataFrame({"InvoiceNo": ["100", "100", "C101", "102", "103"], "StockCode": ["A"] * 5, "Description": ["Item"] * 5, "Quantity": [2, 2, 1, -1, 1], "InvoiceDate": ["2011-01-01"] * 5, "UnitPrice": [3, 3, 3, 3, 0], "CustomerID": [1, 1, 2, 3, 4], "Country": ["UK"] * 5})
    clean, report = clean_transactions(raw)
    assert len(clean) == 1
    assert clean.iloc[0].revenue == 6
    assert report["exact_duplicates_removed"] == 1
