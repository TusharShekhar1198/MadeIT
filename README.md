# MadeIT Insights

**Retail intelligence. Made actionable.**

MadeIT Insights is a decision-intelligence workspace for retail leaders and analysts. It begins with a real public e-commerce dataset and exposes what happened across revenue, product demand, and customer behavior, plus a repeat-purchase model.

## Working capabilities

- Local user accounts with salted PBKDF2 password hashing; Google OAuth configuration template included.
- Executive overview with revenue, orders, active customers, and average order value.
- Sales trends, product performance, RFM customer segments, and repeat-purchase model evaluation.
- PostgreSQL loader and analytical SQL.
- FastAPI endpoint for repeat-purchase probabilities.

## Data integrity

The current source is the UCI Online Retail dataset (December 2010–December 2011). It contains online transactions but no physical-store identifiers, cost/profit, inventory, promotions, returns, or supplier data. MadeIT intentionally does not invent those metrics.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.ingest
python -m src.pipeline
python -m src.train
streamlit run app/dashboard.py
```

For Google sign-in, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, add a Google OAuth client ID and secret, and install the listed `Authlib` dependency before starting Streamlit. Register `http://localhost:8501/oauth2callback` as an authorized redirect URI in Google Cloud. Never commit the secrets file.

## Next platform layers

The full enterprise roadmap requires a source with stores, costs, inventory, promotions, returns, and operational dimensions. Once available, those feeds can power store, inventory, promotion, return, anomaly, root-cause, and forecasting modules without misleading users with fabricated measures.
