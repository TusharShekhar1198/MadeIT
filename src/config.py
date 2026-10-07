from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = ROOT / "models"

RAW_FILE = RAW_DIR / "online_retail.xlsx"
TRANSACTIONS_FILE = PROCESSED_DIR / "transactions.parquet"
FEATURES_FILE = PROCESSED_DIR / "customer_features.parquet"
METRICS_FILE = REPORTS_DIR / "model_metrics.json"

for directory in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR, FIGURES_DIR, MODELS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

