"""
Custom HTML/CSS UI Card Components for Executive Dashboard.
"""

import streamlit as st

# Vector SVG trend icons
SVG_TREND_UP = """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>"""
SVG_TREND_DOWN = """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="17 7 17 17 7 17"></polyline></svg>"""

def render_metric_card(title: str, value: str, delta: str = None, is_positive: bool = True):
    """Renders a modern Glassmorphism KPI card with SVG trend indicators."""
    badge_html = ""
    if delta:
        badge_class = "badge-positive" if is_positive else "badge-negative"
        trend_svg = SVG_TREND_UP if is_positive else SVG_TREND_DOWN
        badge_html = f'<div class="metric-badge {badge_class}" title="{delta}">{trend_svg}<span>{delta}</span></div>'

    card_html = f"""
    <div class="metric-card">
        <div class="metric-title" title="{title}">{title}</div>
        <div class="metric-value" title="{value}">{value}</div>
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
