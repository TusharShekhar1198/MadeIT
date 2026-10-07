"""Cleaning, feature engineering, RFM segmentation, and EDA."""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import FEATURES_FILE, FIGURES_DIR, RAW_FILE, REPORTS_DIR, TRANSACTIONS_FILE


def clean_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw = raw.rename(columns={"InvoiceNo": "invoice_no", "StockCode": "stock_code", "Description": "description", "Quantity": "quantity", "InvoiceDate": "invoice_date", "UnitPrice": "unit_price", "CustomerID": "customer_id", "Country": "country"}).copy()
    report = {"input_rows": len(raw), "missing_customer_id": int(raw.customer_id.isna().sum()), "missing_description": int(raw.description.isna().sum())}
    raw["invoice_date"] = pd.to_datetime(raw["invoice_date"], errors="coerce")
    raw["customer_id"] = pd.to_numeric(raw["customer_id"], errors="coerce").astype("Int64")
    # UCI stock codes mix numeric identifiers and special string codes.
    raw["stock_code"] = raw["stock_code"].astype("string")
    raw["description"] = raw["description"].astype("string")
    raw["is_cancellation"] = raw["invoice_no"].astype(str).str.startswith("C")
    before = len(raw)
    transactions = raw.drop_duplicates().copy()
    report["exact_duplicates_removed"] = before - len(transactions)
    valid = (
        transactions.customer_id.notna()
        & transactions.invoice_date.notna()
        & (transactions.quantity > 0)
        & (transactions.unit_price > 0)
        & ~transactions.is_cancellation
    )
    report["invalid_or_cancelled_rows_removed"] = int((~valid).sum())
    transactions = transactions.loc[valid].copy()
    transactions["revenue"] = transactions.quantity * transactions.unit_price
    transactions["date"] = transactions.invoice_date.dt.date
    transactions["month"] = transactions.invoice_date.dt.to_period("M").astype(str)
    report["clean_rows"] = len(transactions)
    report["unique_customers"] = int(transactions.customer_id.nunique())
    report["date_range"] = [str(transactions.invoice_date.min().date()), str(transactions.invoice_date.max().date())]
    return transactions, report


def build_customer_features(tx: pd.DataFrame) -> pd.DataFrame:
    # Label uses a temporal split: activity in last 90 days after observation cutoff.
    max_date = tx.invoice_date.max().normalize()
    cutoff = max_date - pd.Timedelta(days=90)
    history = tx[tx.invoice_date < cutoff].copy()
    future = tx[tx.invoice_date >= cutoff]
    snapshot = cutoff
    customer = history.groupby("customer_id").agg(
        recency_days=("invoice_date", lambda x: (snapshot - x.max().normalize()).days),
        frequency=("invoice_no", "nunique"),
        monetary=("revenue", "sum"),
        quantity=("quantity", "sum"),
        unique_products=("stock_code", "nunique"),
        countries=("country", "nunique"),
        first_purchase=("invoice_date", "min"),
        last_purchase=("invoice_date", "max"),
    )
    orders = history.groupby(["customer_id", "invoice_no"]).revenue.sum().groupby("customer_id")
    customer["avg_order_value"] = orders.mean()
    customer["customer_tenure_days"] = (snapshot - customer.first_purchase.dt.normalize()).dt.days
    customer = customer.drop(columns=["first_purchase", "last_purchase"])
    customer["repeat_purchase"] = customer.index.isin(future.customer_id.unique()).astype(int)

    # RFM segments based only on observed history, so dashboard and training remain leakage-free.
    for column, ascending in [("recency_days", True), ("frequency", False), ("monetary", False)]:
        customer[f"{column}_score"] = pd.qcut(customer[column].rank(method="first", ascending=ascending), 4, labels=[4, 3, 2, 1]).astype(int)
    score = customer[["recency_days_score", "frequency_score", "monetary_score"]].sum(axis=1)
    customer["rfm_segment"] = pd.cut(score, bins=[0, 5, 8, 10, 12], labels=["At Risk", "Potential", "Loyal", "Champions"], include_lowest=True).astype(str)
    numeric = customer[["recency_days", "frequency", "monetary"]].copy()
    numeric["frequency"] = np.log1p(numeric["frequency"])
    numeric["monetary"] = np.log1p(numeric["monetary"])
    customer["cluster"] = KMeans(n_clusters=4, random_state=42, n_init=20).fit_predict(StandardScaler().fit_transform(numeric))
    return customer.reset_index()


def make_eda(tx: pd.DataFrame, customer: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    monthly = tx.groupby("month", as_index=False).revenue.sum()
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(monthly.month, monthly.revenue, marker="o", color="#2563eb")
    ax.tick_params(axis="x", rotation=45); ax.set(title="Monthly revenue", xlabel="Month", ylabel="Revenue (£)")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "monthly_revenue.png", dpi=160); plt.close(fig)
    products = tx.groupby("description", as_index=False).revenue.sum().nlargest(10, "revenue").sort_values("revenue")
    fig, ax = plt.subplots(figsize=(10, 5)); ax.barh(products.description, products.revenue, color="#0f766e")
    ax.set(title="Top 10 products by revenue", xlabel="Revenue (£)"); fig.tight_layout(); fig.savefig(FIGURES_DIR / "top_products.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4)); sns.countplot(data=customer, x="rfm_segment", order=["At Risk", "Potential", "Loyal", "Champions"], ax=ax, color="#7c3aed")
    ax.set(title="RFM customer segments", xlabel="Segment", ylabel="Customers"); fig.tight_layout(); fig.savefig(FIGURES_DIR / "rfm_segments.png", dpi=160); plt.close(fig)


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError("Run `python -m src.ingest` first.")
    raw = pd.read_excel(RAW_FILE)
    tx, quality = clean_transactions(raw)
    customers = build_customer_features(tx)
    tx.to_parquet(TRANSACTIONS_FILE, index=False)
    customers.to_parquet(FEATURES_FILE, index=False)
    make_eda(tx, customers)
    (REPORTS_DIR / "data_quality.json").write_text(json.dumps(quality, indent=2))
    print(f"Wrote {len(tx):,} clean transactions and {len(customers):,} customer feature rows.")


if __name__ == "__main__":
    main()
