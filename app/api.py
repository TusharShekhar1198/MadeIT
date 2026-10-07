from pathlib import Path
import sys

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MODELS_DIR
from src.train import FEATURE_COLUMNS

app = FastAPI(title="MadeIT Insights Prediction API", version="1.0.0")

class CustomerFeatures(BaseModel):
    recency_days: float = Field(ge=0)
    frequency: float = Field(ge=0)
    monetary: float = Field(ge=0)
    avg_order_value: float = Field(ge=0)
    quantity: float = Field(ge=0)
    unique_products: float = Field(ge=0)
    countries: float = Field(ge=0)
    customer_tenure_days: float = Field(ge=0)

@app.get("/health")
def health(): return {"status": "ok", "models_ready": all((MODELS_DIR / f"{name}.joblib").exists() for name in ("logistic_regression", "random_forest"))}

@app.post("/predict")
def predict(features: CustomerFeatures):
    paths = {"logistic_regression": MODELS_DIR / "logistic_regression.joblib", "random_forest": MODELS_DIR / "random_forest.joblib"}
    if not all(path.exists() for path in paths.values()):
        raise HTTPException(status_code=503, detail="Models unavailable. Run python -m src.train first.")
    row = pd.DataFrame([features.model_dump()], columns=FEATURE_COLUMNS)
    probabilities = {name: round(float(joblib.load(path).predict_proba(row)[0, 1]), 4) for name, path in paths.items()}
    return {"repeat_purchase_probability": probabilities}
