"""MadeIT Insights Streamlit experience."""
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.auth import authenticate, register
from src.config import FEATURES_FILE, METRICS_FILE, TRANSACTIONS_FILE

st.set_page_config(page_title="MadeIT Insights", page_icon="✦", layout="wide", initial_sidebar_state="expanded")


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root { --ink:#0e1018; --night:#14131a; --yellow:#f6d83e; --cream:#f8f7f3; --muted:#72727b; --line:#e7e5df; --green:#17a673; }
        .stApp { background: var(--cream); color:var(--ink); font-family:'Manrope',sans-serif; }
        #MainMenu, footer, header {visibility:hidden;} .block-container {padding:1.25rem 2.1rem 2.4rem; max-width:1500px;}
        [data-testid='stSidebar'] { background:#111117; border-right:0; }
        [data-testid='stSidebar'] * { color:#f4f3ef !important; }
        [data-testid='stSidebar'] .stRadio label { border-radius:10px; padding:8px 10px; margin:2px 0; font-size:.9rem; }
        [data-testid='stSidebar'] .stRadio label:hover { background:#27252d; }
        [data-testid='stSidebar'] [data-baseweb='radio'] > div { background:var(--yellow)!important; }
        .brand {font-size:1.45rem;font-weight:800;letter-spacing:-.07em;margin:4px 0 0}.brand b{color:var(--yellow)}
        .eyebrow {font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.12em;color:#87838d;font-size:.69rem;font-weight:500;}
        .hero {background:radial-gradient(circle at 85% 10%,#ffe982 0,transparent 19%),linear-gradient(125deg,#15141a 0%,#25222c 100%);color:white;border-radius:24px;padding:32px 34px;margin:4px 0 22px;position:relative;overflow:hidden;min-height:170px;}
        .hero:after {content:'';position:absolute;width:310px;height:310px;border:1px solid rgba(246,216,62,.45);border-radius:50%;right:-115px;bottom:-230px;animation:ring 8s linear infinite;}
        @keyframes ring {to {transform:rotate(360deg) scale(1.1)}}
        .hero h1{font-size:2.35rem;line-height:1.04;letter-spacing:-.065em;margin:.45rem 0 .65rem;font-weight:800;max-width:650px}.hero p{max-width:630px;color:#cfccd5;font-size:.98rem;line-height:1.65;margin:0}.hero-mark{position:absolute;right:34px;top:28px;color:var(--yellow);font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.12em;}
        .kpi {background:#fff;border:1px solid var(--line);border-radius:16px;padding:17px 18px;min-height:112px;transition:transform .25s ease,box-shadow .25s ease;}
        .kpi:hover {transform:translateY(-3px);box-shadow:0 14px 30px rgba(19,18,25,.08)} .kpi-label{font-size:.75rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.08em}.kpi-value{font-size:1.65rem;font-weight:800;letter-spacing:-.055em;margin-top:10px}.kpi-sub{font-size:.74rem;color:#77737c;margin-top:5px}
        .section-title{font-size:1.28rem;font-weight:800;letter-spacing:-.04em;margin:8px 0 2px}.section-copy{font-size:.88rem;color:var(--muted);margin:0 0 14px}.panel{background:#fff;border:1px solid var(--line);border-radius:16px;padding:15px 18px;margin:3px 0 18px}.signal{background:#15141a;color:#f9f8f3;border-radius:16px;padding:18px;min-height:128px}.signal strong{font-size:1rem;display:block;margin:9px 0 6px}.signal p{font-size:.81rem;color:#c6c2cc;margin:0;line-height:1.5}.signal-yellow{background:var(--yellow);color:#1d1c20}.signal-yellow p{color:#3b3822}.signal-green{background:#daf3e9;color:#163d2d}.signal-green p{color:#35604e}
        .data-note{border-left:3px solid var(--yellow);padding:10px 13px;background:#fffdf0;border-radius:0 10px 10px 0;color:#514d39;font-size:.85rem;margin-bottom:18px}.auth-shell{max-width:1180px;margin:8vh auto 0}.auth-hero{background:linear-gradient(135deg,#15141a 0%,#302c3b 100%);padding:48px;border-radius:28px;color:#fff;position:relative;overflow:hidden;min-height:530px}.auth-hero:after{content:'✦';font-size:20rem;color:rgba(246,216,62,.15);position:absolute;right:-20px;bottom:-105px;line-height:1;animation:float 6s ease-in-out infinite}.auth-hero:before{content:'';width:300px;height:300px;border:1px solid rgba(246,216,62,.35);border-radius:50%;position:absolute;right:-125px;top:-125px;animation:ring 10s linear infinite}.auth-hero h1{font-size:3.3rem;letter-spacing:-.09em;line-height:.98;margin:14px 0}.auth-hero p{color:#d4d0da;max-width:455px;line-height:1.7;position:relative;z-index:1}.auth-stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;position:absolute;bottom:34px;left:48px;right:48px;z-index:1}.auth-stat{padding:13px 14px;border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.06);border-radius:12px;backdrop-filter:blur(8px)}.auth-stat strong{font-size:1.1rem;display:block;color:var(--yellow);margin-bottom:3px}.auth-stat span{font-size:.72rem;color:#d2cfd7}.auth-card{background:#fff;border:1px solid var(--line);border-radius:24px;padding:28px;min-height:530px;box-shadow:0 24px 55px rgba(22,20,28,.08)}.auth-card-title{font-size:1.65rem;font-weight:800;letter-spacing:-.06em;margin:8px 0 5px}.auth-card-copy{font-size:.86rem;color:var(--muted);line-height:1.55;margin-bottom:18px}.security-line{display:flex;align-items:center;gap:8px;font-size:.73rem;color:#77737c;margin-top:18px}.security-dot{width:8px;height:8px;background:var(--green);border-radius:50%;box-shadow:0 0 0 4px #e4f8ef}@keyframes float{50%{transform:translateY(-12px) rotate(8deg)}}.stButton>button{border-radius:10px;border:0;background:#15141a;color:#fff;font-weight:700;padding:.55rem 1rem}.stButton>button:hover{background:#f6d83e;color:#16151b;border:0}.stTabs [data-baseweb='tab-list']{gap:22px;border-bottom:1px solid var(--line)}.stTabs [data-baseweb='tab']{font-weight:700;color:#77737c;padding:9px 1px}.stTabs [aria-selected='true']{color:#15141a!important;border-bottom:3px solid var(--yellow)!important}.stDataFrame{border:1px solid var(--line);border-radius:12px;overflow:hidden}
        </style>
        """,
        unsafe_allow_html=True,
    )


def google_oauth_configured() -> bool:
    try:
        return "auth" in st.secrets and "google" in st.secrets["auth"]
    except Exception:
        return False


def metric(label: str, value: str, detail: str) -> None:
    st.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-sub'>{detail}</div></div>", unsafe_allow_html=True)


def heading(title: str, copy: str) -> None:
    st.markdown(f"<div class='section-title'>{title}</div><p class='section-copy'>{copy}</p>", unsafe_allow_html=True)


def login_screen() -> None:
    st.markdown("<div class='auth-shell'>", unsafe_allow_html=True)
    story, access = st.columns([1.08, .92], gap="large")
    with story:
        st.markdown("""<div class='auth-hero'><div class='eyebrow' style='color:#f6d83e'>Retail decision intelligence / v1.0</div><h1>Find the signal.<br><span style='color:#f6d83e'>Move with confidence.</span></h1><p>MadeIT brings revenue, product, customer, and predictive intelligence into one focused workspace for sharper retail decisions.</p><div class='auth-stat-grid'><div class='auth-stat'><strong>392K+</strong><span>cleaned transactions analyzed</span></div><div class='auth-stat'><strong>0.73</strong><span>Random Forest ROC-AUC</span></div><div class='auth-stat'><strong>RFM</strong><span>customer intelligence built in</span></div><div class='auth-stat'><strong>LIVE</strong><span>decision-ready dashboard</span></div></div></div>""", unsafe_allow_html=True)
    with access:
        st.markdown("<div class='auth-card'><div class='eyebrow'>Secure workspace access</div><div class='auth-card-title'>Welcome to MadeIT.</div><p class='auth-card-copy'>Sign in to explore the retail performance workspace and predictive decision layer.</p>", unsafe_allow_html=True)
        sign_in, create_account = st.tabs(["Sign in", "Create account"])
        with sign_in:
            with st.form("local_login"):
                email = st.text_input("Work email", key="login_email", placeholder="you@company.com")
                password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                submitted = st.form_submit_button("Enter workspace →", type="primary", use_container_width=True)
            if submitted:
                user = authenticate(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                st.error("We could not verify that email and password.")
            if google_oauth_configured():
                st.divider()
                if st.button("Continue with Google", use_container_width=True):
                    st.login("google")
            else:
                st.caption("Google sign-in is available when OIDC is configured for this environment.")
        with create_account:
            with st.form("registration"):
                name = st.text_input("Full name")
                email = st.text_input("Work email", key="register_email", placeholder="you@company.com")
                password = st.text_input("Password (10+ characters)", type="password", key="register_password")
                submitted = st.form_submit_button("Create workspace account →", type="primary", use_container_width=True)
            if submitted:
                ok, message = register(name, email, password)
                (st.success if ok else st.error)(message)
        st.markdown("<div class='security-line'><span class='security-dot'></span> Protected access · Your credentials are never displayed.</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


inject_theme()
if st.user.get("is_logged_in", False):
    st.session_state.user = {"id": st.user.get("sub", st.user.get("email", "google-user")), "email": st.user.get("email", ""), "name": st.user.get("name", st.user.get("email", "Google user")), "provider": "google"}
if "user" not in st.session_state:
    login_screen()
    st.stop()

with st.sidebar:
    st.markdown("<div class='brand'>Made<b>IT</b></div><div class='eyebrow' style='margin-top:5px'>Insights workspace</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigation", ["Overview", "Sales", "Stores", "Products", "Inventory", "Customers", "Promotions", "Returns", "Forecasting", "AI Analyst"], label_visibility="collapsed")
    st.divider()
    st.markdown(f"<div class='eyebrow'>Signed in</div><div style='font-weight:700;margin-top:5px'>{st.session_state.user['name']}</div>", unsafe_allow_html=True)
    if st.button("Sign out", use_container_width=True):
        if st.session_state.user.get("provider") == "google":
            st.logout()
        del st.session_state.user
        st.rerun()

if not TRANSACTIONS_FILE.exists() or not FEATURES_FILE.exists():
    st.error("Prepared analytics artifacts are unavailable. Run the pipeline before starting the dashboard.")
    st.stop()


@st.cache_data
def load_data():
    return pd.read_parquet(TRANSACTIONS_FILE), pd.read_parquet(FEATURES_FILE)


transactions, customers = load_data()
country = st.sidebar.selectbox("Market", ["All markets"] + sorted(transactions.country.unique().tolist()))
if country != "All markets":
    transactions = transactions[transactions.country == country]

revenue = transactions.revenue.sum()
orders = transactions.invoice_no.nunique()
monthly = transactions.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("invoice_no", "nunique"))

if page == "Overview":
    st.markdown("<section class='hero'><div class='hero-mark'>LIVE INTELLIGENCE / 01</div><div class='eyebrow' style='color:#f6d83e'>Executive overview</div><h1>Every retail signal.<br>One decisive view.</h1><p>See the commercial pulse, isolate opportunity, and move from transaction data to the next best business question.</p></section>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("Revenue", f"£{revenue:,.0f}", "Completed transactions")
    with c2: metric("Orders", f"{orders:,}", "Unique completed invoices")
    with c3: metric("Active customers", f"{transactions.customer_id.nunique():,}", "Identified purchasers")
    with c4: metric("Order value", f"£{revenue / orders:,.2f}", "Revenue per invoice")
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.85, 1])
    with left:
        heading("Revenue momentum", "Monthly completed-sales trend across the selected market.")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.line_chart(monthly.set_index("month").revenue, color="#f0c90e", height=270)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        heading("Signals to investigate", "Data-backed prompts for the next review.")
        top_product = transactions.groupby("description").revenue.sum().idxmax()
        repeat_rate = customers.repeat_purchase.mean()
        st.markdown(f"<div class='signal'><div class='eyebrow' style='color:#f6d83e'>Product leader</div><strong>{top_product[:45]}</strong><p>Highest observed revenue contribution in the selected data.</p></div><br><div class='signal signal-yellow'><div class='eyebrow'>Retention signal</div><strong>{repeat_rate:.0%} observed repeat rate</strong><p>Customer activity in the final 90 days of the data period.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='data-note'>MadeIT shows only source-supported measures. Store, inventory, promotion, and return modules require additional operational data.</div>", unsafe_allow_html=True)
elif page == "Sales":
    heading("Sales performance", "Follow monthly revenue and order movement to identify where to investigate further.")
    a, b = st.columns([2, 1])
    with a:
        st.markdown("<div class='panel'>", unsafe_allow_html=True); st.line_chart(monthly.set_index("month")[["revenue", "orders"]], height=330); st.markdown("</div>", unsafe_allow_html=True)
    with b:
        latest = monthly.iloc[-1]
        st.markdown(f"<div class='signal signal-green'><div class='eyebrow'>Latest observed month</div><strong>{latest.month}</strong><p>£{latest.revenue:,.0f} revenue from {int(latest.orders):,} orders.</p></div>", unsafe_allow_html=True)
    st.dataframe(monthly.style.format({"revenue": "£{:,.2f}", "orders": "{:,.0f}"}), use_container_width=True, hide_index=True)
elif page == "Products":
    heading("Product intelligence", "Rank product descriptions by commercial contribution and unit velocity.")
    products = transactions.groupby("description", as_index=False).agg(revenue=("revenue", "sum"), units=("quantity", "sum")).nlargest(15, "revenue")
    st.markdown("<div class='panel'>", unsafe_allow_html=True); st.bar_chart(products.set_index("description").revenue, color="#f0c90e", height=360); st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(products.style.format({"revenue": "£{:,.2f}", "units": "{:,.0f}"}), use_container_width=True, hide_index=True)
elif page == "Customers":
    heading("Customer intelligence", "RFM segments reveal which customers to retain, develop, or re-engage.")
    segment = customers.groupby("rfm_segment", as_index=False).agg(customers=("customer_id", "count"), avg_revenue=("monetary", "mean"), observed_repeat_rate=("repeat_purchase", "mean"))
    st.markdown("<div class='panel'>", unsafe_allow_html=True); st.bar_chart(segment.set_index("rfm_segment").customers, color="#f0c90e", height=300); st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(segment.style.format({"avg_revenue": "£{:,.2f}", "observed_repeat_rate": "{:.1%}"}), use_container_width=True, hide_index=True)
    st.caption("RFM features are derived before the final 90-day repeat-purchase observation window.")
elif page == "Forecasting":
    heading("Forecasting baseline", "An interpretable moving-average view establishes a transparent demand baseline.")
    monthly["three_month_moving_average"] = monthly.revenue.rolling(3, min_periods=1).mean()
    st.markdown("<div class='panel'>", unsafe_allow_html=True); st.line_chart(monthly.set_index("month")[["revenue", "three_month_moving_average"]], height=350); st.markdown("</div>", unsafe_allow_html=True)
    st.info("Store-level and inventory-demand forecasts need store and inventory history, which is not available in the current public dataset.")
elif page == "AI Analyst":
    heading("Predictive decision layer", "Compare repeat-purchase models and inspect the behavioral signals they use.")
    if METRICS_FILE.exists():
        metrics = json.loads(METRICS_FILE.read_text())
        one, two, three = st.columns(3)
        with one: metric("Test customers", f"{metrics['test_size']:,}", "Held-out evaluation set")
        with two: metric("Best F1", f"{metrics['models']['random_forest']['f1']:.4f}", "Random Forest")
        with three: metric("Best ROC-AUC", f"{metrics['models']['random_forest']['roc_auc']:.4f}", "Random Forest")
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(metrics["models"]).T[["precision", "recall", "f1", "roc_auc", "average_precision"]].style.format("{:.4f}"), use_container_width=True)
        heading("What influences repeat purchase?", "Random Forest feature importance from the held-out evaluation pipeline.")
        st.markdown("<div class='panel'>", unsafe_allow_html=True); st.bar_chart(pd.Series(metrics["random_forest_feature_importance"]), color="#f0c90e", height=280); st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Model artifacts are not available. Run `python -m src.train` to calculate them.")
else:
    heading(f"{page} intelligence", "This workspace is ready for the next operational data feed.")
    st.markdown("<div class='hero'><div class='eyebrow' style='color:#f6d83e'>Data contract required</div><h1>Build this view on real operations data.</h1><p>MadeIT does not simulate enterprise KPIs. Add stable operational identifiers, timestamps, quantities, and linked dimensions before enabling this decision module.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='data-note'>Required inputs vary by module: stores need store/location dimensions; inventory needs stock and movement records; promotions need campaign/control assignment; returns need return events and reasons.</div>", unsafe_allow_html=True)
