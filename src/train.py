"""Train comparable, leakage-free repeat-purchase models and save actual metrics."""
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import FEATURES_FILE, METRICS_FILE, MODELS_DIR

FEATURE_COLUMNS = ["recency_days", "frequency", "monetary", "avg_order_value", "quantity", "unique_products", "countries", "customer_tenure_days"]


def evaluate(name: str, pipeline: Pipeline, x_train, x_test, y_train, y_test) -> tuple[Pipeline, dict]:
    pipeline.fit(x_train, y_train)
    probability = pipeline.predict_proba(x_test)[:, 1]
    prediction = (probability >= 0.5).astype(int)
    return pipeline, {
        "precision": round(float(precision_score(y_test, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, prediction, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "average_precision": round(float(average_precision_score(y_test, probability)), 4),
    }


def main() -> None:
    if not FEATURES_FILE.exists():
        raise FileNotFoundError("Run `python -m src.pipeline` first.")
    data = pd.read_parquet(FEATURES_FILE)
    x, y = data[FEATURE_COLUMNS], data.repeat_purchase
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    transformer = ColumnTransformer([("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), FEATURE_COLUMNS)])
    logistic, lr_metrics = evaluate("logistic_regression", Pipeline([("preprocess", transformer), ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42))]), x_train, x_test, y_train, y_test)
    forest, rf_metrics = evaluate("random_forest", Pipeline([("preprocess", transformer), ("model", RandomForestClassifier(n_estimators=500, min_samples_leaf=3, class_weight="balanced", random_state=42, n_jobs=-1))]), x_train, x_test, y_train, y_test)
    importances = forest.named_steps["model"].feature_importances_
    feature_importance = dict(sorted(zip(FEATURE_COLUMNS, map(lambda x: round(float(x), 4), importances)), key=lambda item: item[1], reverse=True))
    metrics = {"task": "repeat purchase in the final 90 days", "n_customers": int(len(data)), "positive_rate": round(float(y.mean()), 4), "test_size": int(len(y_test)), "models": {"logistic_regression": lr_metrics, "random_forest": rf_metrics}, "random_forest_feature_importance": feature_importance}
    METRICS_FILE.write_text(json.dumps(metrics, indent=2))
    joblib.dump(logistic, MODELS_DIR / "logistic_regression.joblib")
    joblib.dump(forest, MODELS_DIR / "random_forest.joblib")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
