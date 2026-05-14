import streamlit as st
import plotly.graph_objects as go
from frontend.components.ui import (
    page_header, format_inr, GOLD, TEXT_MUTED, GOLD_LIGHT,
    BG_CARD, BG_CARD2, GREEN, RED, AMBER
)
from frontend.utils import api


def _comparison_chart(buy_now: float, future_cost: float, diff: float) -> go.Figure:
    colors = [GOLD, RED if diff > 0 else GREEN]
    labels = ["Buy now", "If you wait"]
    values = [buy_now, future_cost]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"₹{v:,.0f}" for v in values],
        textposition="outside",
        textfont=dict(color=GOLD_LIGHT, size=13),
        width=0.4,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=260,
        showlegend=False,
        yaxis=dict(
            showgrid=True, gridcolor="#1E1A10",
            color=TEXT_MUTED, tickformat="₹,.0f",
            range=[min(values) * 0.96, max(values) * 1.06]
        ),
        xaxis=dict(showgrid=False, color=TEXT_MUTED),
    )
    return fig


def show():
    page_header("What-If Calculator", "See the real cost impact of buying now vs waiting — in rupees")

    st.markdown(
        f'<div style="font-size:13px; color:{TEXT_MUTED}; max-width:640px; '
        f'margin-bottom:20px; line-height:1.7;">'
        "This tool doesn't predict the future — it shows you what happens to your costs "
        "<em>if</em> the price moves by a certain amount. Use it to understand your risk, "
        "not to make speculative bets."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Get current price ─────────────────────────────────────────────────
    price_data = api.get_current_price()
    current_price = 7243.0  # fallback
    if price_data and "error" not in price_data:
        current_price = price_data["price_22k"]
        st.markdown(
            f'<div style="font-size:13px; color:{TEXT_MUTED}; margin-bottom:16px;">'
            f'Current 22k price: <strong style="color:{GOLD_LIGHT};">₹{current_price:,.0f}/gram</strong>'
            f' &nbsp;(source: {price_data.get("source", "api")})</div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1, 1.2], gap="large")

    with left:
        st.markdown("#### Your inputs")

        grams = st.slider(
            "Grams to buy", min_value=1.0, max_value=500.0, value=38.0, step=1.0,
            help="How many grams you're considering buying"
        )

        change_pct = st.slider(
            "Expected price change (%)", min_value=-8.0, max_value=8.0, value=1.0, step=0.5,
            help="Positive = price goes up if you wait. Negative = price drops. You choose the scenario."
        )

        days = st.slider(
            "Days you'd wait", min_value=0, max_value=14, value=3, step=1,
            help="How many days you're thinking of waiting before buying"
        )

        # Scenario shortcuts
        st.markdown(f'<div style="font-size:12px; color:{TEXT_MUTED}; margin-top:8px;">Quick scenarios:</div>', unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            if st.button("Festival rush\n+3% / 5d", use_container_width=True):
                change_pct = 3.0; days = 5
        with sc2:
            if st.button("Slight dip\n-1.5% / 3d", use_container_width=True):
                change_pct = -1.5; days = 3
        with sc3:
            if st.button("Stable week\n0% / 7d", use_container_width=True):
                change_pct = 0.0; days = 7

    with right:
        # ── Compute ───────────────────────────────────────────────────────
        result = api.get_whatif(grams=grams, change_pct=change_pct, days=days)
        if not result or "error" in result:
            # Fallback local calc
            buy_now = round(grams * current_price, 2)
            future_price = round(current_price * (1 + change_pct / 100), 2)
            future_cost = round(grams * future_price, 2)
            diff = round(future_cost - buy_now, 2)
            verdict_type = "buy_now" if diff > 500 else ("wait" if diff < -500 else "neutral")
            verdict = (
                f"Buying now saves ₹{abs(diff):,.0f}" if verdict_type == "buy_now" else
                f"Waiting {days}d could save ₹{abs(diff):,.0f}" if verdict_type == "wait" else
                "Small difference — buy urgent orders now."
            )
        else:
            buy_now = result["buy_now_cost"]
            future_price = result["future_price"]
            future_cost = result["future_cost"]
            diff = result["cost_difference"]
            verdict = result["verdict"]
            verdict_type = result["verdict_type"]

        # Result cards
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Buy now cost", format_inr(buy_now))
        future_label = f"Price if +{change_pct:+.1f}%" if change_pct != 0 else "Same price"
        rc2.metric(future_label, f"₹{future_price:,.0f}/g")
        diff_sign = f"+{format_inr(diff)}" if diff > 0 else f"-{format_inr(abs(diff))}"
        rc3.metric("Cost difference", diff_sign, delta=None)

        # Bar chart
        st.plotly_chart(_comparison_chart(buy_now, future_cost, diff), use_container_width=True)

        # Verdict
        if verdict_type == "buy_now":
            adv_class, icon = "advice-caution", "⚠️"
        elif verdict_type == "wait":
            adv_class, icon = "advice-buy", "✅"
        else:
            adv_class, icon = "advice-wait", "💡"

        st.markdown(
            f'<div class="{adv_class}">{icon} <strong>Verdict:</strong> {verdict}</div>',
            unsafe_allow_html=True,
        )

        # Cost breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="gold-card">'
            f'<div class="gold-card-title">cost breakdown</div>'
            f'<table style="width:100%; font-size:13px; color:{TEXT_MUTED};">'
            f'<tr><td>Buy now: {grams:.0f}g × ₹{current_price:,.0f}</td>'
            f'<td style="text-align:right; color:{GOLD_LIGHT}; font-weight:600;">{format_inr(buy_now)}</td></tr>'
            f'<tr><td>If you wait {days}d at ₹{future_price:,.0f}/g</td>'
            f'<td style="text-align:right; color:{GOLD_LIGHT}; font-weight:600;">{format_inr(future_cost)}</td></tr>'
            f'<tr style="border-top:1px solid #2A2415;">'
            f'<td style="padding-top:6px;"><strong>Net difference</strong></td>'
            f'<td style="text-align:right; padding-top:6px; color:{"#F08080" if diff > 0 else "#80C080"}; font-weight:600;">'
            f'{diff_sign}</td></tr>'
            f'</table></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:12px; color:{TEXT_MUTED}; max-width:600px;">'
        "⚠️ This calculator uses your assumed price change — not a real forecast. "
        "Gold prices can move unexpectedly. Use this tool to understand risk ranges, "
        "not to bet on specific price movements."
        "</div>",
        unsafe_allow_html=True,
    )
