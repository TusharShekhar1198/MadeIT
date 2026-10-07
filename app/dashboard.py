import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit executes this file with app/ on sys.path; expose the project root
# so the sibling src package is available both locally and in Streamlit Cloud.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import FEATURES_FILE, METRICS_FILE, TRANSACTIONS_FILE
from src.auth import authenticate, register

st.set_page_config(page_title="MadeIT Insights", page_icon="◆", layout="wide", initial_sidebar_state="expanded")


def login_screen() -> None:
    st.title("MadeIT Insights")
    st.caption("Retail intelligence. Made actionable.")
    sign_in, create_account = st.tabs(["Sign in", "Create account"])
    with sign_in:
        with st.form("local_login"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", type="primary")
        if submitted:
            user = authenticate(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            st.error("Incorrect email or password.")
        if google_oauth_configured():
            st.divider()
            st.caption("Or use your organization account")
            if st.button("Continue with Google", use_container_width=True):
                st.login("google")
        else:
            st.info("Google sign-in needs Google Cloud credentials. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, then add your client ID and secret.")
    with create_account:
        with st.form("registration"):
            name = st.text_input("Name")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password (10+ characters)", type="password", key="register_password")
            submitted = st.form_submit_button("Create account", type="primary")
        if submitted:
            ok, message = register(name, email, password)
            (st.success if ok else st.error)(message)


def google_oauth_configured() -> bool:
    try:
        return "auth" in st.secrets and "google" in st.secrets["auth"]
    except Exception:
        return False


if st.user.get("is_logged_in", False):
    st.session_state.user = {
        "id": st.user.get("sub", st.user.get("email", "google-user")),
        "email": st.user.get("email", ""),
        "name": st.user.get("name", st.user.get("email", "Google user")),
        "provider": "google",
    }
if "user" not in st.session_state:
    login_screen()
    st.stop()

with st.sidebar:
    st.markdown("## MadeIT")
    st.caption("INSIGHTS")
    page = st.radio("Navigation", ["Overview", "Sales", "Stores", "Products", "Inventory", "Customers", "Promotions", "Returns", "Forecasting", "AI Analyst"], label_visibility="collapsed")
    st.divider()
    st.success(f"Signed in as {st.session_state.user['name']}")
    if st.button("Sign out"):
        if st.session_state.user.get("provider") == "google":
            st.logout()
        del st.session_state.user
        st.rerun()

st.title("MadeIT Insights")
st.caption("Retail intelligence. Made actionable. • UCI Online Retail • Dec 2010–Dec 2011")

if not TRANSACTIONS_FILE.exists() or not FEATURES_FILE.exists():
    st.error("Data has not been prepared. Run `python -m src.ingest` and `python -m src.pipeline`.")
    st.stop()

@st.cache_data
def load_data(): return pd.read_parquet(TRANSACTIONS_FILE), pd.read_parquet(FEATURES_FILE)

transactions, customers = load_data()
country = st.sidebar.selectbox("Country", ["All"] + sorted(transactions.country.unique().tolist()))
if country != "All": transactions = transactions[transactions.country == country]

revenue = transactions.revenue.sum()
orders = transactions.invoice_no.nunique()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"£{revenue:,.0f}")
col2.metric("Orders", f"{orders:,}")
col3.metric("Active customers", f"{transactions.customer_id.nunique():,}")
col4.metric("Average order value", f"£{revenue / orders:,.2f}")

if page == "Overview":
    st.subheader("Executive overview")
    st.info("Decision context is based on completed, identified online transactions. This source does not include physical stores, cost, inventory, promotions, or returns, so MadeIT does not fabricate those measures.")
    monthly = transactions.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))
    st.line_chart(monthly.set_index("month").revenue, color="#1d4ed8")
elif page == "Sales":
    monthly = transactions.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))
    st.subheader("Revenue and order trend")
    st.line_chart(monthly.set_index("month").revenue, color="#2563eb")
    st.dataframe(monthly, use_container_width=True, hide_index=True)
elif page == "Products":
    top_products = transactions.groupby("description", as_index=False).agg(revenue=("revenue", "sum"), units=("quantity", "sum")).nlargest(15, "revenue")
    st.subheader("Top products by revenue")
    st.bar_chart(top_products.set_index("description").revenue, color="#0f766e")
    st.dataframe(top_products, use_container_width=True, hide_index=True)
elif page in {"Stores", "Inventory", "Promotions", "Returns"}:
    st.subheader(f"{page} intelligence")
    st.warning(f"This module needs {page.lower()} operational data that is not present in the current public source. It is intentionally unavailable rather than filled with synthetic KPI cards.")
    st.markdown("**Required data contract:** stable identifiers, dates, quantity/value measures, and the related store, product, supplier, promotion, or return dimensions.")
elif page == "Customers":
    st.subheader("RFM segments")
    segment = customers.groupby("rfm_segment", as_index=False).agg(customers=("customer_id", "count"), avg_revenue=("monetary", "mean"), observed_repeat_rate=("repeat_purchase", "mean"))
    st.bar_chart(segment.set_index("rfm_segment").customers, color="#7c3aed")
    st.dataframe(segment.style.format({"avg_revenue": "£{:,.2f}", "observed_repeat_rate": "{:.1%}"}), use_container_width=True, hide_index=True)
    st.caption("Repeat-purchase label: customer activity in the final 90 days of the dataset; RFM features use the preceding period only.")
elif page == "Forecasting":
    st.subheader("Forecasting readiness")
    st.info("The current dataset has historical revenue and can support an interpretable moving-average forecast. Store-level and inventory-demand forecasts require the operational store and inventory data specified for the full platform.")
    monthly = transactions.groupby("month", as_index=False).revenue.sum()
    monthly["three_month_moving_average"] = monthly.revenue.rolling(3, min_periods=1).mean()
    st.line_chart(monthly.set_index("month")[["revenue", "three_month_moving_average"]])
elif page == "AI Analyst":
    st.subheader("Repeat-purchase prediction")
    if METRICS_FILE.exists():
        metrics = json.loads(METRICS_FILE.read_text())
        st.caption(f"Held-out test set: {metrics['test_size']:,} customers | Positive rate: {metrics['positive_rate']:.1%}")
        table = pd.DataFrame(metrics["models"]).T[["precision", "recall", "f1", "roc_auc", "average_precision"]]
        st.dataframe(table.style.format("{:.4f}"), use_container_width=True)
        st.subheader("Random Forest feature importance")
        st.bar_chart(pd.Series(metrics["random_forest_feature_importance"]), color="#dc2626")
    else:
        st.info("Run `python -m src.train` to calculate and display actual model metrics.")

st.divider()
st.caption("Source: UCI Machine Learning Repository — Online Retail dataset. Dashboard excludes cancelled, non-positive, duplicate, and anonymous transactions.")
