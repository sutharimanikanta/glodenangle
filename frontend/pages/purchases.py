import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from frontend.components.ui import (
    page_header, format_inr, GOLD, GOLD_LIGHT, TEXT_MUTED, BG_CARD2, GREEN, RED
)
from frontend.utils import api


def show():
    page_header("Purchase Log", "Record gold purchases and track your buying history")

    # ── Log a new purchase ────────────────────────────────────────────────
    with st.expander("📝 Log a new gold purchase", expanded=False):
        price_data = api.get_current_price()
        suggested_price = price_data.get("price_22k", 7000.0) if price_data and "error" not in price_data else 7000.0

        with st.form("log_purchase"):
            c1, c2, c3 = st.columns(3)
            with c1:
                grams = st.number_input("Grams bought", min_value=0.1, max_value=10000.0, value=20.0, step=0.5)
            with c2:
                price = st.number_input("Price per gram (₹)", min_value=100.0, max_value=100000.0,
                                        value=float(round(suggested_price)), step=10.0,
                                        help=f"Current market: ₹{suggested_price:,.0f}/g")
            with c3:
                karat = st.selectbox("Karat", [22, 18, 24, 14], index=0)
            notes = st.text_input("Notes (optional)", placeholder="e.g. Bought for Priya's necklace order")

            if st.form_submit_button("Save purchase", use_container_width=True):
                result = api.log_purchase(grams=grams, price_per_gram=price, karat=karat, notes=notes)
                if result and "error" not in result:
                    st.success(
                        f"Logged: {grams}g @ ₹{price:,.0f}/g = {format_inr(grams * price)} total"
                    )
                    st.rerun()
                else:
                    st.error("Failed to log purchase.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Placeholder for purchase history ─────────────────────────────────
    # (The full purchases API endpoint exists; displaying a helpful message here
    #  since we don't have a GET /purchases route in the current scope)

    st.markdown("#### Recent purchases")

    # Demo display to show what logged purchases look like
    demo_purchases = [
        {"date": "2025-05-10", "grams": 18.0, "price_per_g": 7180, "karat": 22, "total": 129240, "notes": "Necklace order — Priya"},
        {"date": "2025-05-07", "grams": 22.5, "price_per_g": 7095, "karat": 22, "total": 159638, "notes": "Festival stock"},
        {"date": "2025-04-29", "grams": 8.0, "price_per_g": 7050, "karat": 18, "total": 56400, "notes": "Ring (Anita)"},
        {"date": "2025-04-21", "grams": 30.0, "price_per_g": 6980, "karat": 22, "total": 209400, "notes": "Batch buy — 3 orders"},
    ]

    for p in demo_purchases:
        col_info, col_cost = st.columns([3, 1])
        with col_info:
            st.markdown(
                f'<div class="gold-card" style="margin-bottom:8px;">'
                f'<div style="display:flex; justify-content:space-between;">'
                f'<div>'
                f'<div style="font-size:14px; font-weight:600; color:{GOLD_LIGHT};">'
                f'{p["grams"]}g @ ₹{p["price_per_g"]:,}/gram ({p["karat"]}k)</div>'
                f'<div style="font-size:12px; color:{TEXT_MUTED}; margin-top:3px;">'
                f'{p["date"]} &nbsp;·&nbsp; {p["notes"]}</div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:16px; font-weight:600; color:{GOLD};">'
                f'{format_inr(p["total"])}</div>'
                f'</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div style="font-size:12px; color:{TEXT_MUTED}; margin-top:8px;">'
        "↑ Demo data shown above. Your logged purchases will appear here."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Spending summary chart ─────────────────────────────────────────────
    st.markdown("<br>#### Spending overview (demo)")
    df = pd.DataFrame(demo_purchases)
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure(go.Bar(
        x=df["date"].dt.strftime("%b %d"),
        y=df["total"],
        marker_color=GOLD,
        text=[format_inr(t) for t in df["total"]],
        textposition="outside",
        textfont=dict(color=GOLD_LIGHT, size=12),
        width=0.5,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        height=220,
        showlegend=False,
        xaxis=dict(showgrid=False, color=TEXT_MUTED),
        yaxis=dict(showgrid=True, gridcolor="#1E1A10", color=TEXT_MUTED, tickformat="₹,.0f"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Stats
    total_spent = sum(p["total"] for p in demo_purchases)
    total_g = sum(p["grams"] for p in demo_purchases)
    avg_price = total_spent / total_g if total_g else 0

    s1, s2, s3 = st.columns(3)
    s1.metric("Total spent (demo)", format_inr(total_spent))
    s2.metric("Total grams", f"{total_g:.1f}g")
    s3.metric("Avg buy price", f"₹{avg_price:,.0f}/g")
