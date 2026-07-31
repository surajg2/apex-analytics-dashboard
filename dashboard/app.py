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
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject CSS Styles & Dynamic Theme Engine
def apply_theme(theme_choice="🌌 Midnight Slate (Executive Dark)"):
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if "Light" in theme_choice:
        st.markdown("""
        <style>
            :root {
                --bg-main: #f8fafc !important;
                --bg-sidebar: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
                --bg-card: #ffffff !important;
                --border-card: #e2e8f0 !important;
                --text-primary: #0f172a !important;
                --text-secondary: #334155 !important;
                --shadow-card: 0 4px 20px 0 rgba(0, 0, 0, 0.06) !important;
                --accent-blue: #2563eb !important;
                --tab-bg: #f1f5f9 !important;
                --tab-active-bg: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            }
            .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
            .section-header { color: #0f172a !important; }
            .section-subheader { color: #334155 !important; }
            .metric-value { color: #0f172a !important; }
            .metric-title { color: #334155 !important; }
            .dataframe { background-color: #ffffff !important; color: #0f172a !important; }

            /* Plotly Visualization Labels High-Contrast Override in Light Theme */
            .js-plotly-plot .plotly .main-svg text,
            .js-plotly-plot .plotly .gtitle,
            .js-plotly-plot .plotly .xtick text,
            .js-plotly-plot .plotly .ytick text,
            .js-plotly-plot .plotly .legendtext,
            .js-plotly-plot .plotly .annotation-text,
            .js-plotly-plot .plotly .xaxis-title,
            .js-plotly-plot .plotly .yaxis-title,
            .js-plotly-plot .plotly .slicetext {
                fill: #0f172a !important;
                color: #0f172a !important;
                font-weight: 500 !important;
            }
            .js-plotly-plot .plotly .gridlayer path {
                stroke: rgba(15, 23, 42, 0.1) !important;
            }
        </style>
        """, unsafe_allow_html=True)
    elif "Emerald" in theme_choice:
        st.markdown("""
        <style>
            :root {
                --bg-main: #06131a !important;
                --bg-sidebar: linear-gradient(180deg, #0a1f2b 0%, #040d12 100%) !important;
                --bg-card: rgba(10, 31, 43, 0.85) !important;
                --border-card: rgba(16, 185, 129, 0.2) !important;
                --text-primary: #f0fdf4 !important;
                --text-secondary: #a7f3d0 !important;
                --shadow-card: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
                --accent-blue: #10b981 !important;
                --tab-bg: rgba(10, 31, 43, 0.9) !important;
                --tab-active-bg: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
            }
            .stApp { background-color: #06131a !important; color: #f0fdf4 !important; }
            .section-header { color: #f0fdf4 !important; }
            .section-subheader { color: #a7f3d0 !important; }
            .metric-value { color: #f0fdf4 !important; }
            .metric-title { color: #a7f3d0 !important; }
        </style>
        """, unsafe_allow_html=True)

# 3. Data Loader with Caching
@st.cache_data(ttl=3600)
def load_dashboard_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    fact_path = os.path.join(base_dir, "data", "processed", "master_fact_table.csv")
    daily_path = os.path.join(base_dir, "data", "processed", "daily_sales_series.csv")
    rfm_path = os.path.join(base_dir, "data", "processed", "rfm_customer_segments.csv")
    prod_path = os.path.join(base_dir, "data", "processed", "cleaned_products.csv")

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
st.sidebar.markdown("""
<div class="brand-container">
    <div class="brand-icon-box">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3v18h18"></path>
            <path d="M18 17V9"></path>
            <path d="M13 17V5"></path>
            <path d="M8 17v-3"></path>
        </svg>
    </div>
    <div>
        <div class="brand-text">ApexAnalytics</div>
        <div class="brand-sub">E-Commerce SaaS Executive Platform</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Theme Preset Switcher
selected_theme = st.sidebar.selectbox(
    "EXECUTIVE THEME",
    [
        "Midnight Slate (Executive Dark)",
        "Corporate Light (Clean Enterprise)",
        "Emerald Wealth (Financial Pro)"
    ]
)
apply_theme(selected_theme)

st.sidebar.markdown("---")

# Navigation Selector
page = st.sidebar.radio(
    "NAVIGATION MODULES",
    [
        "Executive KPI Overview",
        "Sales & Payment Analytics",
        "Customer RFM & Cohorts",
        "Product & Inventory Analytics",
        "Interactive SQL Studio",
        "ML Revenue Forecasting",
        "Strategic Business Insights"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### GLOBAL FILTERS")

# Global Date Range Filter
min_date = df_master["order_date"].min().date()
max_date = df_master["order_date"].max().date()

# Reset Filters Button
if st.sidebar.button("Reset Global Filters", key="reset_filters"):
    st.session_state["date_filter"] = (min_date, max_date)
    st.session_state["dept_filter"] = "All"
    st.rerun()

default_dates = st.session_state.get("date_filter", (min_date, max_date))

date_range = st.sidebar.date_input(
    "Order Date Range:",
    value=default_dates
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    d1, d2 = date_range
    start_date = min(d1, d2)
    end_date = max(d1, d2)
elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
    start_date = end_date = date_range[0]
else:
    start_date, end_date = min_date, max_date

# Global Department Filter
departments = ["All"] + sorted(df_master["department"].dropna().unique().tolist())
default_dept = st.session_state.get("dept_filter", "All")
dept_idx = departments.index(default_dept) if default_dept in departments else 0
selected_dept = st.sidebar.selectbox("Department:", departments, index=dept_idx)

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
if page == "Executive KPI Overview":
    render_executive_kpi_view(filtered_master, filtered_daily, rfm_df)
elif page == "Sales & Payment Analytics":
    render_sales_analytics_view(filtered_master, filtered_daily)
elif page == "Customer RFM & Cohorts":
    render_customer_rfm_view(filtered_master, rfm_df)
elif page == "Product & Inventory Analytics":
    render_product_inventory_view(filtered_master, df_products)
elif page == "Interactive SQL Studio":
    render_sql_studio_view()
elif page == "ML Revenue Forecasting":
    render_ml_forecasting_view(filtered_daily)
elif page == "Strategic Business Insights":
    render_business_insights_view(filtered_master, rfm_df)
