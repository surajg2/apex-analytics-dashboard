"""
Interactive Machine Learning Sales & Demand Forecasting View.
"""

import streamlit as st
import pandas as pd
import pickle
import os
import plotly.express as px
from dashboard.components import render_metric_card, render_forecast_chart
from dashboard.components.charts import update_dark_layout
from utils.forecasting_engine import SalesForecaster

def render_ml_forecasting_view(daily_df: pd.DataFrame):
    """Renders ML Sales & Demand Forecasting View."""
    st.markdown('<div class="section-header">Supervised ML Sales & Revenue Forecasting</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Predict future daily revenue trajectory, holiday demand surges, and confidence bands using machine learning algorithms.</div>', unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        model_choice = st.selectbox(
            "Select Forecasting Model:",
            ["gradient_boosting", "random_forest", "ridge"],
            format_func=lambda x: f"🤖 {x.replace('_', ' ').title()}"
        )
    with col_ctrl2:
        forecast_days = st.slider("Forecast Horizon (Days):", min_value=14, max_value=90, value=60, step=7)

    # Train / load forecaster
    forecaster = SalesForecaster(model_type=model_choice)
    eval_res = forecaster.train_and_eval(daily_df, test_days=30)
    future_df = forecaster.predict_future(daily_df, forecast_horizon_days=forecast_days)

    # 1. Model Evaluation Metrics
    st.markdown("### Model Evaluation & Holdout Test Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Root Mean Sq Error", f"${eval_res['metrics']['RMSE']:.2f}", "Holdout RMSE", is_positive=True)
    with m2:
        render_metric_card("Mean Absolute Error", f"${eval_res['metrics']['MAE']:.2f}", "Holdout MAE", is_positive=True)
    with m3:
        render_metric_card("MAPE (%)", f"{eval_res['metrics']['MAPE_pct']:.1f}%", "Mean Abs % Error", is_positive=eval_res['metrics']['MAPE_pct'] < 15)
    with m4:
        r2_val = eval_res['metrics']['R2_Score']
        render_metric_card("R² Score", f"{r2_val:.4f}", "Variance Explained", is_positive=r2_val > 0.70)

    st.markdown("---")

    # 2. Plotly Forecast Line Chart
    fig_forecast = render_forecast_chart(daily_df, future_df)
    st.plotly_chart(fig_forecast, use_container_width=True)

    st.markdown("---")

    # 3. Feature Importance & Forecast Projections Table
    col_fi, col_tbl = st.columns([1, 1])

    with col_fi:
        st.markdown("### Top Predictive Features")
        fi_dict = eval_res["feature_importance"]
        if fi_dict:
            fi_df = pd.DataFrame(list(fi_dict.items()), columns=["feature", "importance"])
            fig_fi = px.bar(
                fi_df.sort_values("importance", ascending=True),
                x="importance",
                y="feature",
                orientation="h",
                color="importance",
                color_continuous_scale="Purples"
            )
            fig_fi = update_dark_layout(fig_fi, title="", height=320)
            st.plotly_chart(fig_fi, use_container_width=True)

    with col_tbl:
        st.markdown("### Predicted Revenue Projections (Next 14 Days)")
        st.dataframe(
            future_df.head(14).rename(columns={
                "date": "Forecast Date",
                "forecast_revenue": "Predicted Revenue ($)",
                "lower_bound": "Lower Bound ($)",
                "upper_bound": "Upper Bound ($)"
            }),
            use_container_width=True,
            hide_index=True
        )
