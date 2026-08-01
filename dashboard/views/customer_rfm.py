"""
Customer Analytics, RFM Segmentation & Cohort Retention View.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components import render_rfm_scatter, render_cohort_heatmap
from dashboard.components.charts import update_dark_layout
from utils.rfm_analytics import RFMAnalytics

def render_customer_rfm_view(df_master: pd.DataFrame, rfm_df: pd.DataFrame):
    """Renders Customer Analytics & RFM Segmentation Page."""
    st.markdown('<div class="section-header">Customer Lifetime Value & RFM Segmentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Recency, Frequency, and Monetary (RFM) modeling, cohort retention decay, and churn risk scoring.</div>', unsafe_allow_html=True)

    if df_master.empty:
        st.warning("⚠️ No orders found matching the selected date range and global filters. Please select dates between 2021 and 2024 or click 'Reset Global Filters'.")
        return

    # 1. RFM Segment Distribution Cards
    seg_counts = rfm_df["rfm_segment"].value_counts().reset_index()
    seg_counts.columns = ["rfm_segment", "customer_count"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Customer Segment Breakdown")
        fig_seg = px.bar(
            seg_counts.sort_values("customer_count", ascending=True),
            x="customer_count",
            y="rfm_segment",
            orientation="h",
            color="customer_count",
            color_continuous_scale="Purples",
            labels={"customer_count": "Customers", "rfm_segment": "Segment"}
        )
        fig_seg = update_dark_layout(fig_seg, title="Customer Segment Breakdown", height=380)
        st.plotly_chart(fig_seg, use_container_width=True)

    with col2:
        # Scatter Plot
        fig_scatter = render_rfm_scatter(rfm_df)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # 2. Cohort Retention Heatmap
    st.markdown("### Customer Acquisition Cohort Retention (%) Matrix")
    rfm_engine = RFMAnalytics()
    _, retention_matrix = rfm_engine.compute_cohort_matrix(df_master)

    fig_cohort = render_cohort_heatmap(retention_matrix)
    st.plotly_chart(fig_cohort, use_container_width=True)

    st.markdown("---")

    # 3. High-Value Customer Leaderboard
    st.markdown("### High-Value Customer Leaderboard (Top 25)")
    top_cust = rfm_df.sort_values("monetary", ascending=False).head(25)
    
    st.dataframe(
        top_cust[[
            "customer_id", "state", "rfm_segment", "recency_days",
            "frequency", "monetary", "aov", "clv_estimate"
        ]].rename(columns={
            "customer_id": "Customer ID",
            "state": "State",
            "rfm_segment": "RFM Segment",
            "recency_days": "Recency (Days)",
            "frequency": "Total Orders",
            "monetary": "Lifetime Spend ($)",
            "aov": "AOV ($)",
            "clv_estimate": "Predicted CLV ($)"
        }),
        use_container_width=True,
        hide_index=True
    )
