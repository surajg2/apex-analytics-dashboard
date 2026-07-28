"""
Custom HTML/CSS UI Card Components for Executive Dashboard.
"""

import streamlit as st

def render_metric_card(title: str, value: str, delta: str = None, is_positive: bool = True):
    """Renders a modern Glassmorphism KPI card."""
    badge_html = ""
    if delta:
        badge_class = "badge-positive" if is_positive else "badge-negative"
        arrow = "▲" if is_positive else "▼"
        badge_html = f'<div class="metric-badge {badge_class}">{arrow} {delta}</div>'

    card_html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {badge_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_insight_card(title: str, text: str, card_type: str = "info"):
    """Renders an executive briefing callout card."""
    type_class = ""
    if card_type == "warning":
        type_class = "warning"
    elif card_type == "danger":
        type_class = "danger"
    elif card_type == "success":
        type_class = "success"

    html = f"""
    <div class="insight-card {type_class}">
        <div class="insight-title">{title}</div>
        <div class="insight-text">{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
