"""Shared UI helpers and gold-themed CSS for all pages."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

GOLD = "#C8942A"
GOLD_LIGHT = "#F5D98C"
GOLD_DARK = "#8B6510"
BG_DARK = "#0F0E0A"
BG_CARD = "#1A1812"
BG_CARD2 = "#221F15"
TEXT_MAIN = "#F0E6C8"
TEXT_MUTED = "#9E8E6A"
GREEN = "#2E8B57"
RED = "#C0392B"
AMBER = "#D4920A"


GOLD_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: {TEXT_MAIN};
}}

.stApp {{
    background-color: {BG_DARK};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: #130F08;
    border-right: 1px solid #2A2415;
}}
section[data-testid="stSidebar"] .stMarkdown p {{
    color: {TEXT_MUTED};
    font-size: 13px;
}}

/* Metric cards */
[data-testid="metric-container"] {{
    background: {BG_CARD};
    border: 1px solid #2A2415;
    border-radius: 10px;
    padding: 14px 18px;
}}
[data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED} !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
[data-testid="stMetricValue"] {{
    color: {GOLD_LIGHT} !important;
    font-size: 26px !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 13px !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, {GOLD_DARK}, {GOLD});
    color: #0F0E0A;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    padding: 8px 20px;
    transition: opacity 0.2s;
}}
.stButton > button:hover {{
    opacity: 0.88;
    color: #0F0E0A;
    border: none;
}}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div {{
    background: {BG_CARD2} !important;
    color: {TEXT_MAIN} !important;
    border: 1px solid #2A2415 !important;
    border-radius: 8px !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent;
    border-bottom: 1px solid #2A2415;
    gap: 0;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {TEXT_MUTED};
    border-bottom: 2px solid transparent;
    font-size: 14px;
    padding: 8px 20px;
}}
.stTabs [aria-selected="true"] {{
    color: {GOLD} !important;
    border-bottom-color: {GOLD} !important;
    background: transparent !important;
}}

/* Custom cards */
.gold-card {{
    background: {BG_CARD};
    border: 1px solid #2A2415;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
}}
.gold-card-title {{
    color: {TEXT_MUTED};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}}

/* Advice boxes */
.advice-buy {{
    background: #0D2618;
    border: 1px solid #1E5C38;
    border-left: 4px solid {GREEN};
    border-radius: 8px;
    padding: 14px 18px;
    color: #7ECFA0;
    font-size: 14px;
    line-height: 1.6;
}}
.advice-wait {{
    background: #1C1408;
    border: 1px solid #4A3410;
    border-left: 4px solid {AMBER};
    border-radius: 8px;
    padding: 14px 18px;
    color: #E8B84B;
    font-size: 14px;
    line-height: 1.6;
}}
.advice-caution {{
    background: #1A0A0A;
    border: 1px solid #4A1A1A;
    border-left: 4px solid {RED};
    border-radius: 8px;
    padding: 14px 18px;
    color: #E87070;
    font-size: 14px;
    line-height: 1.6;
}}
.advice-ai {{
    background: #0F0E1A;
    border: 1px solid #2A2440;
    border-left: 4px solid #7A6FD4;
    border-radius: 8px;
    padding: 16px 20px;
    color: #C4BFEE;
    font-size: 14px;
    line-height: 1.7;
}}

/* Badge pills */
.badge-urgent {{
    background: #4A1515; color: #F08080;
    border: 1px solid #7A2020;
    padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;
}}
.badge-normal {{
    background: #1A2A10; color: #80C070;
    border: 1px solid #2A4A18;
    padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;
}}
.badge-flexible {{
    background: #101A2A; color: #70A0C0;
    border: 1px solid #183040;
    padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;
}}

/* Tables */
.stDataFrame {{ background: {BG_CARD}; border-radius: 10px; }}
[data-testid="stDataFrame"] {{ background: transparent; }}

/* Hide Streamlit branding */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Page title */
.page-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: {GOLD_LIGHT};
    margin-bottom: 4px;
}}
.page-subtitle {{
    font-size: 14px;
    color: {TEXT_MUTED};
    margin-bottom: 24px;
}}

/* Risk meter */
.risk-container {{
    background: {BG_CARD};
    border: 1px solid #2A2415;
    border-radius: 12px;
    padding: 20px 24px;
}}
</style>
"""


def apply_theme():
    st.markdown(GOLD_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">✦ {title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def advice_box(text: str, advice_type: str):
    css_class = {
        "buy": "advice-buy",
        "wait": "advice-wait",
        "caution": "advice-caution",
    }.get(advice_type, "advice-wait")
    icon = {"buy": "✅", "wait": "⏸", "caution": "⚠️"}.get(advice_type, "ℹ️")
    st.markdown(f'<div class="{css_class}">{icon} {text}</div>', unsafe_allow_html=True)


def badge(text: str, urgency: str):
    css = {"urgent": "badge-urgent", "normal": "badge-normal", "flexible": "badge-flexible"}.get(urgency, "badge-normal")
    return f'<span class="{css}">{text.upper()}</span>'


def risk_gauge(score: float, level: str) -> go.Figure:
    color = {"low": GREEN, "moderate": AMBER, "high": RED}.get(level, AMBER)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"color": color, "size": 36}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_MUTED, "tickfont": {"color": TEXT_MUTED, "size": 10}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": BG_CARD2,
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35], "color": "#0D2618"},
                {"range": [35, 60], "color": "#1C1408"},
                {"range": [60, 100], "color": "#1A0A0A"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=10),
        height=200,
        font={"color": TEXT_MUTED},
    )
    return fig


def price_trend_chart(prices_data: list, days: int = 14) -> go.Figure:
    if not prices_data:
        return go.Figure()
    df = pd.DataFrame(prices_data)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df = df.sort_values("recorded_at").tail(days)
    avg = df["price_22k"].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["recorded_at"], y=df["price_22k"],
        mode="lines+markers",
        line=dict(color=GOLD, width=2),
        marker=dict(color=GOLD, size=5),
        name="22k price",
        hovertemplate="₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(
        y=avg, line_dash="dot", line_color=TEXT_MUTED,
        annotation_text=f"  avg ₹{avg:,.0f}", annotation_font_color=TEXT_MUTED
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=240,
        showlegend=False,
        xaxis=dict(showgrid=False, color=TEXT_MUTED, tickfont=dict(size=11)),
        yaxis=dict(
            showgrid=True, gridcolor="#1E1A10", color=TEXT_MUTED,
            tickformat="₹,.0f", tickfont=dict(size=11)
        ),
        hovermode="x unified",
    )
    return fig


def format_inr(amount: float) -> str:
    """Format number as Indian rupees with comma separation."""
    if amount >= 1_00_000:
        return f"₹{amount/1_00_000:.2f}L"
    elif amount >= 1_000:
        return f"₹{amount:,.0f}"
    return f"₹{amount:.2f}"
