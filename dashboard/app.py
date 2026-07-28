"""
End-to-End E-Commerce Analytics SaaS Dashboard Application.
Main entry point for Streamlit application.
"""

import os
import sys
import streamlit as st
import pandas as pd

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.views import (
    render_executive_kpi_view,
    render_sales_analytics_view,
    render_customer_rfm_view,
    render_product_inventory_view,
    render_sql_studio_view,
    render_ml_forecasting_view,
    render_business_insights_view
)

# 1. Streamlit Page Config
st.set_page_config(
    page_title="ApexAnalytics | E-Commerce Sales SaaS Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject CSS Styles
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 3. Data Loader with Caching
@st.cache_data(ttl=3600)
def load_dashboard_data():
    fact_path = "data/processed/master_fact_table.csv"
    daily_path = "data/processed/daily_sales_series.csv"
    rfm_path = "data/processed/rfm_customer_segments.csv"
    prod_path = "data/processed/cleaned_products.csv"

    if not os.path.exists(fact_path):
        from seed_data import main as run_seed
        run_seed()

    df_master = pd.read_csv(fact_path)
    daily_df = pd.read_csv(daily_path)
    rfm_df = pd.read_csv(rfm_path)
    df_products = pd.read_csv(prod_path)

    df_master["order_date"] = pd.to_datetime(df_master["order_date"], format="mixed", errors="coerce")
    daily_df["date"] = pd.to_datetime(daily_df["date"], format="mixed", errors="coerce")

    return df_master, daily_df, rfm_df, df_products

try:
    df_master, daily_df, rfm_df, df_products = load_dashboard_data()
except Exception as e:
    st.error(f"Error loading dashboard data: {e}. Generating new seed data...")
    from seed_data import main as run_seed
    run_seed()
    df_master, daily_df, rfm_df, df_products = load_dashboard_data()

# 4. Sidebar Navigation & Global Filters
st.sidebar.markdown("## ⚡ **ApexAnalytics**")
st.sidebar.markdown("<span style='color:#64748b; font-size:0.8rem;'>E-COMMERCE SAAS PLATFORM</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation Selector
page = st.sidebar.radio(
    "NAVIGATION MODULES",
    [
        "📊 Executive KPI Overview",
        "📈 Sales & Payment Analytics",
        "👥 Customer RFM & Cohorts",
        "📦 Product & Inventory Analytics",
        "💻 Interactive SQL Studio",
        "🤖 ML Revenue Forecasting",
        "💡 Strategic Business Insights"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ GLOBAL FILTERS")

# Global Date Range Filter
min_date = df_master["order_date"].min().date()
max_date = df_master["order_date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Order Date Range:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Global Department Filter
departments = ["All"] + sorted(df_master["department"].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("Department:", departments)

# Apply Global Filters to DataFrames
filtered_master = df_master[
    (df_master["order_date"].dt.date >= start_date) &
    (df_master["order_date"].dt.date <= end_date)
]

if selected_dept != "All":
    filtered_master = filtered_master[filtered_master["department"] == selected_dept]

filtered_daily = daily_df[
    (daily_df["date"].dt.date >= start_date) &
    (daily_df["date"].dt.date <= end_date)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filtered_master):,}** filtered order items across **{filtered_master['order_id'].nunique():,}** orders.")

# 5. Render Selected Page View
if page == "📊 Executive KPI Overview":
    render_executive_kpi_view(filtered_master, filtered_daily, rfm_df)
elif page == "📈 Sales & Payment Analytics":
    render_sales_analytics_view(filtered_master, filtered_daily)
elif page == "👥 Customer RFM & Cohorts":
    render_customer_rfm_view(filtered_master, rfm_df)
elif page == "📦 Product & Inventory Analytics":
    render_product_inventory_view(filtered_master, df_products)
elif page == "💻 Interactive SQL Studio":
    render_sql_studio_view()
elif page == "🤖 ML Revenue Forecasting":
    render_ml_forecasting_view(filtered_daily)
elif page == "💡 Strategic Business Insights":
    render_business_insights_view(filtered_master, rfm_df)
