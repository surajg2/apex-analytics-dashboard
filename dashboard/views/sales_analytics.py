"""
Exploratory Sales & Regional Analytics View.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.charts import update_dark_layout, PRIMARY_CYAN, SECONDARY_PURPLE, ACCENT_GREEN

def render_sales_analytics_view(df_master: pd.DataFrame, daily_df: pd.DataFrame):
    """Renders Sales & Regional Analytics Page."""
    st.markdown('<div class="section-header">Exploratory Sales & Payment Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Deep-dive into sales seasonality, day-of-week purchase velocity, payment dynamics, and shipping SLAs.</div>', unsafe_allow_html=True)

    valid_df = df_master[df_master["order_status"] != "Cancelled"].copy()
    valid_df["order_date"] = pd.to_datetime(valid_df["order_date"], format="mixed", errors="coerce")

    # 1. Monthly Revenue & MoM Growth Combo Chart
    valid_df["year_month"] = valid_df["order_date"].dt.to_period("M").astype(str)
    monthly = valid_df.groupby("year_month").agg({
        "net_amount": "sum",
        "order_id": "nunique"
    }).reset_index()

    monthly["mom_growth"] = monthly["net_amount"].pct_change() * 100

    fig_mom = go.Figure()
    fig_mom.add_trace(go.Bar(
        x=monthly["year_month"],
        y=monthly["net_amount"],
        name="Net Revenue ($)",
        marker_color="rgba(56, 189, 248, 0.75)",
        hovertemplate="Month: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>"
    ))

    fig_mom.add_trace(go.Scatter(
        x=monthly["year_month"],
        y=monthly["mom_growth"],
        name="MoM Growth (%)",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#f43f5e", width=3),
        hovertemplate="Month: %{x}<br>MoM Growth: %{y:.1f}%<extra></extra>"
    ))

    fig_mom.update_layout(
        yaxis2=dict(
            title="MoM Growth Rate (%)",
            overlaying="y",
            side="right",
            showgrid=False,
            font=dict(color="#f43f5e")
        )
    )
    fig_mom = update_dark_layout(fig_mom, title="Monthly Revenue Trajectory & MoM Growth Rate (%)", height=400)
    st.plotly_chart(fig_mom, use_container_width=True)

    # 2. Row 2: Day of Week Heatmap & Payment Method Breakdown
    col1, col2 = st.columns(2)

    with col1:
        # Day of Week vs Month Heatmap
        valid_df["day_name"] = valid_df["order_date"].dt.day_name()
        valid_df["month_name"] = valid_df["order_date"].dt.strftime("%b")
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        pivot_dow = valid_df.pivot_table(
            index="day_name", columns="month_name", values="net_amount", aggfunc="sum"
        ).reindex(dow_order)

        fig_heat = px.imshow(
            pivot_dow,
            labels=dict(x="Month", y="Day of Week", color="Revenue ($)"),
            color_continuous_scale="Plasma",
            text_auto=".0f"
        )
        fig_heat = update_dark_layout(fig_heat, title="Purchasing Seasonality Heatmap (Day vs Month)", height=380)
        st.plotly_chart(fig_heat, use_container_width=True)

    with col2:
        # Payment Method Distribution Donut
        pay_df = valid_df.groupby("payment_method")["net_amount"].sum().reset_index()
        fig_pay = px.pie(
            pay_df,
            names="payment_method",
            values="net_amount",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Darkmint_r
        )
        fig_pay.update_traces(textposition="inside", textinfo="percent+label")
        fig_pay = update_dark_layout(fig_pay, title="Revenue Share by Payment Method", height=380)
        st.plotly_chart(fig_pay, use_container_width=True)

    # 3. Row 3: Shipping Lead Times & SLA Compliance
    st.markdown("### Shipping & Logistics SLA Performance")
    col3, col4 = st.columns(2)

    with col3:
        # Delivery delay distribution boxplot by state
        fig_box = px.box(
            valid_df[valid_df["delivery_delay_days"].notnull()],
            x="state",
            y="delivery_delay_days",
            color="state",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_box = update_dark_layout(fig_box, title="Delivery Delay Variance (Days) Across States", height=360)
        st.plotly_chart(fig_box, use_container_width=True)

    with col4:
        # Customer review score distribution by delivery delay
        valid_df["delivery_status_label"] = np.where(valid_df["is_delivery_delayed"] == 1, "Delayed Delivery", "On-Time / Early")
        rev_sla = valid_df.groupby(["delivery_status_label", "review_score"])["order_id"].nunique().reset_index()

        fig_rev = px.bar(
            rev_sla,
            x="review_score",
            y="order_id",
            color="delivery_status_label",
            barmode="group",
            labels={"order_id": "Review Count", "review_score": "Star Rating (1-5)"},
            color_discrete_map={"Delayed Delivery": "#ef4444", "On-Time / Early": "#10b981"}
        )
        fig_rev = update_dark_layout(fig_rev, title="Customer Rating Score vs Delivery SLA Compliance", height=360)
        st.plotly_chart(fig_rev, use_container_width=True)
