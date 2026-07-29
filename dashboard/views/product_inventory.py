"""
Product Performance, Category Margins & Slow-Moving Inventory View.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components.charts import update_dark_layout

def render_product_inventory_view(df_master: pd.DataFrame, df_products: pd.DataFrame):
    """Renders Product Analytics Page."""
    st.markdown('<div class="section-header">Product Performance & Inventory Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Identify high-margin winners, underperforming products, category profitability, and overstocked inventory alerts.</div>', unsafe_allow_html=True)

    if df_master.empty:
        st.warning("⚠️ No orders found matching the selected date range and global filters. Please select dates between 2021 and 2024 or click 'Reset Global Filters'.")
        return

    valid_df = df_master[df_master["order_status"] != "Cancelled"]

    # 1. Product Sales Summary
    prod_summary = valid_df.groupby(["product_id", "product_name", "category_name"]).agg({
        "net_amount": "sum",
        "quantity": "sum",
        "item_profit": "sum"
    }).reset_index()

    prod_summary = prod_summary.merge(df_products[["product_id", "stock_quantity", "cost"]], on="product_id", how="left")
    prod_summary["margin_pct"] = (prod_summary["item_profit"] / prod_summary["net_amount"] * 100).round(2)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top 10 Best-Selling Products")
        top_10 = prod_summary.sort_values("net_amount", ascending=False).head(10)
        fig_top = px.bar(
            top_10.sort_values("net_amount", ascending=True),
            x="net_amount",
            y="product_name",
            orientation="h",
            color="net_amount",
            color_continuous_scale="Teal",
            labels={"net_amount": "Net Revenue ($)", "product_name": "Product Name"}
        )
        fig_top = update_dark_layout(fig_top, title="", height=380)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("### Top 10 High-Margin Winners ($ Profit)")
        top_margin = prod_summary.sort_values("item_profit", ascending=False).head(10)
        fig_profit = px.bar(
            top_margin.sort_values("item_profit", ascending=True),
            x="item_profit",
            y="product_name",
            orientation="h",
            color="margin_pct",
            color_continuous_scale="Viridis",
            labels={"item_profit": "Net Profit ($)", "product_name": "Product Name"}
        )
        fig_profit = update_dark_layout(fig_profit, title="", height=380)
        st.plotly_chart(fig_profit, use_container_width=True)

    st.markdown("---")

    # 2. Category Margin & Volume Matrix
    st.markdown("### Department & Category Profitability Matrix")
    cat_summary = valid_df.groupby("category_name").agg({
        "net_amount": "sum",
        "item_profit": "sum",
        "quantity": "sum"
    }).reset_index()

    cat_summary["margin_pct"] = (cat_summary["item_profit"] / cat_summary["net_amount"] * 100).round(2)

    fig_cat = px.scatter(
        cat_summary,
        x="net_amount",
        y="margin_pct",
        size="quantity",
        color="category_name",
        hover_name="category_name",
        labels={"net_amount": "Total Revenue ($)", "margin_pct": "Profit Margin (%)", "quantity": "Units Sold"}
    )
    fig_cat = update_dark_layout(fig_cat, title="Category Revenue vs Margin % vs Volume", height=380)
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")

    # 3. Slow-Moving & Overstocked Inventory Alerts
    st.markdown("### 🚨 Inventory Health & Overstock Warning Table")
    st.caption("Products with Stock > 120 units and low 90-day sales volume requiring markdown or marketing push.")

    slow_moving = prod_summary[
        (prod_summary["stock_quantity"] > 120) & (prod_summary["quantity"] < 25)
    ].sort_values("stock_quantity", ascending=False)

    if slow_moving.empty:
        slow_moving = prod_summary.sort_values("stock_quantity", ascending=False).head(10)

    st.dataframe(
        slow_moving[[
            "product_id", "product_name", "category_name", "stock_quantity",
            "quantity", "net_amount", "item_profit", "margin_pct"
        ]].rename(columns={
            "product_id": "Product ID",
            "product_name": "Product Title",
            "category_name": "Category",
            "stock_quantity": "Current Stock",
            "quantity": "Units Sold",
            "net_amount": "Revenue ($)",
            "item_profit": "Profit ($)",
            "margin_pct": "Margin (%)"
        }),
        use_container_width=True,
        hide_index=True
    )
