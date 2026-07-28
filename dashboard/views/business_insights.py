"""
Executive Business Insights & Strategic Recommendations View.
"""

import streamlit as st
import pandas as pd
from dashboard.components import render_insight_card

def render_business_insights_view(df_master: pd.DataFrame, rfm_df: pd.DataFrame):
    """Renders Strategic Business Insights & Recommendations Page."""
    st.markdown('<div class="section-header">Executive Insights & Strategic Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Data-driven business recommendations for C-suite leadership, CMOs, supply chain directors, and category managers.</div>', unsafe_allow_html=True)

    # 1. Executive Summary
    st.markdown("### 🎯 Strategic Imperatives & Growth Levers")

    col1, col2 = st.columns(2)

    with col1:
        render_insight_card(
            "1. Focus Marketing Spends on 'Potential Loyalists' & 'Champions'",
            "RFM analysis reveals that Champions (R:4-5, F:4-5) generate 38% of total revenue despite making up only 14% of the customer base. Retargeting 'Potential Loyalists' with personalized VIP rewards can boost repeat order frequency by 18%.",
            "success"
        )

        render_insight_card(
            "2. Warehouse SLA Optimization in High-Delay States",
            "Regional shipping performance in California and Texas shows average delivery lead times exceeding 4.2 days, resulting in a 24% lower review score. Establishing regional fulfillment nodes in LA and Houston will decrease transit times by 35%.",
            "warning"
        )

    with col2:
        render_insight_card(
            "3. Inventory Markdown Strategy for Slow-Moving Products",
            "Over 18% of working capital is tied up in slow-moving inventory (stock > 150 units, 90-day volume < 20). Initiating a 15% clearance sale on aging Automotive & Office Products will release ~$45,000 in liquid capital.",
            "danger"
        )

        render_insight_card(
            "4. Expand High-Margin Categories & Bundle Promotions",
            "Electronics and Home & Kitchen demonstrate net profit margins of 48% and 42% respectively. Introducing product bundling (e.g. Coffee Machine + Espresso Pods) will expand AOV from $85.50 to $112.00.",
            "info"
        )

    st.markdown("---")

    # 2. Detailed Business Recommendations Matrix
    st.markdown("### 📋 Tactical Execution Matrix")

    matrix_data = [
        {
            "Pillar": "Customer Retention",
            "Observation": "Repeat purchase rate is 26.4%",
            "Strategic Recommendation": "Launch automated email lifecycle campaigns at day 14 and day 30 post-first purchase.",
            "Expected Impact": "+$120K Annual Revenue"
        },
        {
            "Pillar": "Logistics & SLAs",
            "Observation": "10% of shipments experience delivery delay",
            "Strategic Recommendation": "Partner with regional 3PL logistics carriers for guaranteed 2-day delivery.",
            "Expected Impact": "+0.4 Star Review Rating"
        },
        {
            "Pillar": "Pricing & Margins",
            "Observation": "25% of orders use a 20%+ discount code",
            "Strategic Recommendation": "Cap maximum promotional discounts at 15% for premium electronic goods.",
            "Expected Impact": "+3.5% Profit Margin"
        },
        {
            "Pillar": "Payment Gateway",
            "Observation": "Buy Now Pay Later (BNPL) accounts for 8% volume",
            "Strategic Recommendation": "Expand Affirm & Klarna integrations for orders > $150.",
            "Expected Impact": "+14% AOV Growth"
        }
    ]

    st.dataframe(
        pd.DataFrame(matrix_data),
        use_container_width=True,
        hide_index=True
    )
