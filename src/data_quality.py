"""Write a standalone data-quality report without regenerating models or charts."""
import json
import pandas as pd

from src.config import RAW_FILE, REPORTS_DIR
from src.pipeline import clean_transactions


if __name__ == "__main__":
    _, report = clean_transactions(pd.read_excel(RAW_FILE))
    (REPORTS_DIR / "data_quality.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
