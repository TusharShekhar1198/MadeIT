# MadeIT Insights

**Retail intelligence. Made actionable.**

[Live dashboard](https://madeit-insights.streamlit.app) · [Architecture](ARCHITECTURE.md)

MadeIT Insights is an analytics and decision-intelligence workspace built on the public [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail). It turns transaction-level e-commerce data into executive KPIs, sales and product views, RFM customer segments, and repeat-purchase predictions.

## Highlights

- Analyzes **392,692 cleaned transactions**, **4,338 identified customers**, and **£8.89M** in observed revenue.
- Cleans duplicates, cancelled invoices, invalid dates, anonymous customers, and non-positive quantity/price records with pandas and NumPy.
- Builds leakage-aware customer features and RFM segments: At Risk, Potential, Loyal, and Champions.
- Evaluates Logistic Regression and Random Forest repeat-purchase models on a held-out set. Random Forest: **F1 0.6882**, **ROC-AUC 0.7285**.
- Provides a Streamlit dashboard, PostgreSQL loader/SQL queries, optional FastAPI prediction endpoint, and Google OAuth-ready authentication.

## Current dashboard

| Area | What it provides |
| --- | --- |
| Overview | Revenue, orders, active customers, average order value, and revenue trend |
| Sales | Monthly revenue and order analysis |
| Products | Revenue and unit performance by product description |
| Customers | RFM customer-segment counts, value, and observed repeat rate |
| Forecasting | Interpretable three-month moving-average baseline |
| AI Analyst | Held-out model metrics and Random Forest feature importance |

Stores, inventory, promotions, and returns are intentionally labelled as unavailable: the public source does not contain the operational dimensions needed to calculate those measures honestly.

## Architecture

```mermaid
flowchart LR
    UCI["UCI Online Retail workbook"] --> ING["Ingestion\nsrc/ingest.py"]
    ING --> PIPE["Cleaning, EDA, RFM & features\nsrc/pipeline.py"]
    PIPE --> TX["transactions.parquet"]
    PIPE --> CF["customer_features.parquet"]
    CF --> TRAIN["Model training\nsrc/train.py"]
    TRAIN --> MODELS["Joblib models + metrics JSON"]
    TX --> UI["Streamlit dashboard\napp/dashboard.py"]
    CF --> UI
    MODELS --> UI
    TX --> PG["Optional PostgreSQL loader\nsrc/load_postgres.py"]
    CF --> PG
    PG --> SQL["Analytical SQL\nsql/analytics.sql"]
    MODELS --> API["Optional FastAPI API\napp/api.py"]
    USER["User"] --> AUTH["Local PBKDF2 account\nor Google OIDC"] --> UI
```

Read the [full architecture](ARCHITECTURE.md) for components, data flow, authentication, deployment, and production considerations.

## Local setup

```bash
git clone https://github.com/TusharShekhar1198/MadeIT.git
cd MadeIT
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.ingest
python -m src.pipeline
python -m src.train
streamlit run app/dashboard.py
```

Run tests with:

```bash
pytest -q
```

## PostgreSQL and API

```bash
cp .env.example .env
docker compose up -d db
python -m src.load_postgres
psql "$DATABASE_URL" -f sql/analytics.sql
uvicorn app.api:app --reload
```

`POST /predict` accepts the behavioral features used during model training and returns probabilities from both classifiers.

## Google sign-in

The dashboard supports Google OpenID Connect through Streamlit. Create a Google OAuth web client and configure the exact redirect URI for your environment.

| Environment | Redirect URI |
| --- | --- |
| Local | `http://localhost:8501/oauth2callback` |
| Hosted | `https://madeit-insights.streamlit.app/oauth2callback` |

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` locally, or paste its values into Streamlit Community Cloud **Settings → Secrets**. Never commit client secrets.

## Deployment

The dashboard is deployed from `app/dashboard.py` on Streamlit Community Cloud. The repository includes the prepared parquet files, trained models, and model metrics so the dashboard works without running the training pipeline during startup. Update `requirements.txt` and push to `main` to trigger a rebuild.

## Data and model notes

- The raw UCI workbook is not committed; run `python -m src.ingest` to retrieve it.
- The repeat-purchase label is activity in the final 90 days of the dataset; model features use the preceding history window.
- Current local email/password accounts use SQLite and are suitable for development only. Google identity is handled through Streamlit OIDC. Use managed PostgreSQL or an identity provider for durable production user/role storage.
- This project does not claim profit, store, inventory, promotion, supplier, or return metrics because the source data does not provide them.
