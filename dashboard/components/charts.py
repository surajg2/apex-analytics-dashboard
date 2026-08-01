"""
Plotly Interactive Chart Components styled with Dynamic Day & Night Mode Themes.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def get_active_palette():
    """Retrieves current theme mode and color palette configuration."""
    theme_mode = st.session_state.get("theme_mode", "🌙 Night")
    color_palette = st.session_state.get("color_palette", "💙 Indigo")
    is_light = "Day" in str(theme_mode) or "☀️" in str(theme_mode)

    if "Emerald" in str(color_palette):
        primary = "#059669" if is_light else "#34d399"
        secondary = "#0d9488" if is_light else "#10b981"
        accent = "#0284c7" if is_light else "#38bdf8"
        tree_scale = "Viridis" if is_light else "Emerald"
        map_scale = "Greens" if is_light else "Teal"
    elif "Amethyst" in str(color_palette):
        primary = "#7c3aed" if is_light else "#c084fc"
        secondary = "#e11d48" if is_light else "#f43f5e"
        accent = "#f59e0b" if is_light else "#fbbf24"
        tree_scale = "Purples" if is_light else "Plasma"
        map_scale = "Purples" if is_light else "Magenta"
    else: # Indigo
        primary = "#2563eb" if is_light else "#38bdf8"
        secondary = "#4f46e5" if is_light else "#6366f1"
        accent = "#10b981" if is_light else "#34d399"
        tree_scale = "Blues" if is_light else "Cividis"
        map_scale = "Blues" if is_light else "Blues"

    return {
        "is_light": is_light,
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "tree_scale": tree_scale,
        "map_scale": map_scale
    }

# Exported default palette constants for backwards compatibility
PRIMARY_CYAN = "#38bdf8"
PRIMARY_INDIGO = "#6366f1"
SECONDARY_PURPLE = "#818cf8"
ACCENT_GREEN = "#10b981"
ACCENT_CORAL = "#f43f5e"
DARK_BG = "rgba(15, 23, 42, 0.4)"

def update_dark_layout(fig, title: str = None, height: int = 400):
    """Applies high-end responsive aesthetics to Plotly figures based on active Day/Night theme."""
    pal = get_active_palette()
    is_light = pal["is_light"]

    template = "plotly_white" if is_light else "plotly_dark"
    title_color = "#0f172a" if is_light else "#f8fafc"
    font_color = "#334155" if is_light else "#94a3b8"
    grid_color = "rgba(15, 23, 42, 0.08)" if is_light else "rgba(255, 255, 255, 0.06)"

    fig.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=20, r=20, t=50 if title else 20, b=20),
        title=dict(
            text=title if title else "",
            font=dict(size=16, family="Inter", color=title_color),
            x=0.01, y=0.96
        ) if title else None,
        font=dict(family="Inter", color=font_color),
        xaxis=dict(gridcolor=grid_color, showline=False, tickfont=dict(color=font_color), title_font=dict(color=font_color)),
        yaxis=dict(gridcolor=grid_color, showline=False, tickfont=dict(color=font_color), title_font=dict(color=font_color)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=font_color)
        )
    )
    return fig

def render_revenue_trend_chart(daily_df: pd.DataFrame) -> go.Figure:
    """Line chart showing daily revenue and 7-day moving average."""
    pal = get_active_palette()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=daily_df["revenue"],
        mode="lines",
        name="Daily Revenue",
        line=dict(color=pal["primary"], width=1.5),
        opacity=0.45,
        hovertemplate="Date: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>"
    ))

    # Calculate 7-day Moving Average
    ma_7 = daily_df["revenue"].rolling(7).mean()
    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=ma_7,
        mode="lines",
        name="7-Day Moving Avg",
        line=dict(color=pal["secondary"], width=3),
        hovertemplate="Date: %{x}<br>7D Avg: $%{y:,.2f}<extra></extra>"
    ))

    return update_dark_layout(fig, title="Revenue Performance & Trend (7-Day MA)", height=380)

def render_category_treemap(df_master: pd.DataFrame) -> go.Figure:
    """Treemap of department and category revenue distribution."""
    pal = get_active_palette()
    cat_df = df_master.groupby(["department", "category_name"]).agg({
        "net_amount": "sum",
        "quantity": "sum",
        "item_profit": "sum"
    }).reset_index()

    fig = px.treemap(
        cat_df,
        path=["department", "category_name"],
        values="net_amount",
        color="item_profit",
        color_continuous_scale=pal["tree_scale"],
        hover_data=["quantity"],
        labels={"net_amount": "Revenue ($)", "item_profit": "Profit ($)"}
    )

    fig.update_traces(marker=dict(cornerradius=5))
    return update_dark_layout(fig, title="Category Revenue & Profitability Hierarchy", height=420)

def render_regional_map(state_df: pd.DataFrame) -> go.Figure:
    """US State Choropleth Map or Bar Chart of revenue by state."""
    pal = get_active_palette()
    us_state_to_abbrev = {
        "California": "CA", "New York": "NY", "Texas": "TX", "Florida": "FL",
        "Illinois": "IL", "Washington": "WA", "Massachusetts": "MA", "Georgia": "GA",
        "Colorado": "CO", "Pennsylvania": "PA", "North Carolina": "NC", "Ohio": "OH"
    }

    state_df = state_df.copy()
    state_df["state_code"] = state_df["state"].map(us_state_to_abbrev)

    if state_df["state_code"].notnull().sum() > 0:
        fig = px.choropleth(
            state_df,
            locations="state_code",
            locationmode="USA-states",
            color="state_net_revenue",
            hover_name="state",
            hover_data={"state_net_revenue": ":$,.2f", "total_delivered_orders": ":,"},
            scope="usa",
            color_continuous_scale=pal["map_scale"]
        )
    else:
        fig = px.bar(
            state_df.sort_values("state_net_revenue", ascending=True),
            x="state_net_revenue",
            y="state",
            orientation="h",
            color="state_net_revenue",
            color_continuous_scale=pal["map_scale"]
        )

    return update_dark_layout(fig, title="US Regional Sales Revenue Distribution", height=400)

def render_rfm_scatter(rfm_df: pd.DataFrame) -> go.Figure:
    """Scatter plot of Recency vs Monetary with Segment colors."""
    fig = px.scatter(
        rfm_df,
        x="recency_days",
        y="monetary",
        size="frequency",
        color="rfm_segment",
        hover_name="customer_id",
        hover_data=["rfm_cell", "aov"],
        labels={"recency_days": "Recency (Days)", "monetary": "Monetary ($)", "frequency": "Orders Count"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color="white")))
    return update_dark_layout(fig, title="RFM Customer Segment Distribution", height=420)

def render_cohort_heatmap(retention_matrix: pd.DataFrame) -> go.Figure:
    """Heatmap showing customer cohort retention percentage over time."""
    pal = get_active_palette()
    heat_scale = "Viridis" if pal["is_light"] else "Magma"

    fig = px.imshow(
        retention_matrix,
        labels=dict(x="Months Since Acquisition", y="Acquisition Cohort", color="Retention %"),
        x=retention_matrix.columns,
        y=retention_matrix.index,
        color_continuous_scale=heat_scale,
        text_auto=".1f"
    )

    return update_dark_layout(fig, title="Customer Cohort Retention Rate (%) Matrix", height=450)

def render_forecast_chart(historical_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Line chart displaying historical sales alongside future ML prediction with confidence bounds."""
    pal = get_active_palette()
    fig = go.Figure()

    # Historical Revenue (Last 90 days)
    hist_recent = historical_df.tail(90)
    fig.add_trace(go.Scatter(
        x=hist_recent["date"],
        y=hist_recent["revenue"],
        mode="lines",
        name="Historical Revenue",
        line=dict(color=pal["primary"], width=2.5)
    ))

    # Upper & Lower Confidence Interval Band
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df["date"], forecast_df["date"][::-1]]),
        y=pd.concat([forecast_df["upper_bound"], forecast_df["lower_bound"][::-1]]),
        fill="toself",
        fillcolor="rgba(129, 140, 248, 0.18)" if not pal["is_light"] else "rgba(37, 99, 235, 0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=True,
        name="95% Confidence Interval"
    ))

    # Forecast Predicted Line
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["forecast_revenue"],
        mode="lines+markers",
        name="ML Predicted Forecast",
        line=dict(color=pal["secondary"], width=3, dash="dash"),
        marker=dict(size=4)
    ))

    return update_dark_layout(fig, title="Supervised ML Revenue Forecast with Confidence Bounds", height=420)
