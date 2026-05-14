import streamlit as st
from frontend.components.ui import (
    page_header, advice_box, risk_gauge, price_trend_chart,
    format_inr, badge, GOLD, TEXT_MUTED, GOLD_LIGHT, GREEN, RED, AMBER
)
from frontend.utils import api


def show():
    page_header("Dashboard", "Today's gold market + your shop at a glance")

    # ── Load data ─────────────────────────────────────────────────────────
    with st.spinner("Loading market data..."):
        history = api.get_price_history(days=30)
        risk = api.get_risk_analysis()
        orders = api.get_orders(status="pending")

    # ── Error guard ───────────────────────────────────────────────────────
    if not history or "error" in history:
        st.error(f"⚠️ Could not load data: {history.get('error', 'Unknown error') if history else 'No response'}")
        st.info("Make sure the FastAPI backend is running: `uvicorn backend.main:app --reload`")
        return

    cur = history["current_price"]
    avg10 = history["avg_10d"]
    avg30 = history["avg_30d"]
    change_pct = history["change_today_pct"]
    vol = history["volatility_7d"]
    h14 = history["high_14d"]
    l14 = history["low_14d"]

    # ── Top metrics row ───────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    delta_color = "normal" if change_pct >= 0 else "inverse"
    c1.metric("22k Gold (per gram)", f"₹{cur:,.0f}", f"{change_pct:+.2f}% today")
    c2.metric("10-day average", f"₹{avg10:,.0f}", f"{((cur-avg10)/avg10)*100:+.1f}% vs now")
    c3.metric("30-day average", f"₹{avg30:,.0f}")
    c4.metric("14-day high / low", f"₹{h14:,.0f}", f"Low ₹{l14:,.0f}")
    c5.metric("7-day volatility", f"±₹{vol:,.0f}", "per gram swing")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main two-column layout ────────────────────────────────────────────
    left, right = st.columns([1.1, 1.9], gap="large")

    with left:
        # Risk gauge
        st.markdown("#### Buy Risk Meter")
        if risk and "error" not in risk:
            level = risk["risk_level"]
            score = risk["risk_score"]
            level_color = {"low": GREEN, "moderate": AMBER, "high": RED}.get(level, AMBER)
            st.plotly_chart(risk_gauge(score, level), use_container_width=True)
            st.markdown(
                f'<div style="text-align:center; margin-top:-12px; margin-bottom:12px;">'
                f'<span style="color:{level_color}; font-size:15px; font-weight:600;">'
                f'{level.upper()} RISK</span> — {score:.0f}/100</div>',
                unsafe_allow_html=True,
            )
            advice_box(risk["advice"], risk["advice_type"])
        else:
            st.warning("Could not load risk analysis.")

        # Pending orders summary
        st.markdown("#### Pending Orders")
        if orders and "error" not in orders:
            pending = [o for o in orders if o["status"] == "pending"]
            if pending:
                total_g = sum(o["gold_grams"] for o in pending)
                urgent_g = sum(o["gold_grams"] for o in pending if o["urgency"] == "urgent")
                st.markdown(
                    f'<div class="gold-card">'
                    f'<div class="gold-card-title">total needed</div>'
                    f'<div style="font-size:28px; font-weight:600; color:{GOLD_LIGHT};">{total_g:.1f}g</div>'
                    f'<div style="font-size:13px; color:{TEXT_MUTED}; margin-top:4px;">'
                    f'{len(pending)} orders &nbsp;·&nbsp; '
                    f'<span style="color:#F08080;">{urgent_g:.1f}g urgent</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                # Order mini-list
                for o in pending[:5]:
                    bdg = badge(o["urgency"], o["urgency"])
                    st.markdown(
                        f'<div style="display:flex; justify-content:space-between; '
                        f'align-items:center; padding:7px 0; '
                        f'border-bottom:1px solid #1E1A10; font-size:13px;">'
                        f'<div><div style="color:{GOLD_LIGHT};">{o["item_description"][:32]}</div>'
                        f'<div style="color:{TEXT_MUTED}; font-size:11px;">{o["customer_name"]}</div></div>'
                        f'<div style="text-align:right;">'
                        f'<div style="color:{GOLD_LIGHT}; font-weight:600;">{o["gold_grams"]}g</div>'
                        f'{bdg}</div></div>',
                        unsafe_allow_html=True,
                    )
                if len(pending) > 5:
                    st.caption(f"+{len(pending)-5} more — see Order Manager")

                if risk and risk.get("batch_suggestion"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="advice-wait">💡 {risk["batch_suggestion"]}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No pending orders. Add orders in Order Manager.")
        else:
            st.warning("Could not load orders.")

    with right:
        # Price trend chart
        tab1, tab2, tab3 = st.tabs(["14-day trend", "30-day trend", "7-day trend"])
        prices = history.get("prices", [])

        with tab1:
            st.plotly_chart(price_trend_chart(prices, 14), use_container_width=True)
        with tab2:
            st.plotly_chart(price_trend_chart(prices, 30), use_container_width=True)
        with tab3:
            st.plotly_chart(price_trend_chart(prices, 7), use_container_width=True)

        # Price context box
        dev = ((cur - avg10) / avg10) * 100
        context_color = RED if dev > 2 else (GREEN if dev < -1 else AMBER)
        st.markdown(
            f'<div class="gold-card" style="margin-top:8px;">'
            f'<div class="gold-card-title">price context</div>'
            f'<div style="font-size:14px; line-height:1.8; color:{TEXT_MUTED};">'
            f'Current price is <span style="color:{context_color}; font-weight:600;">'
            f'{dev:+.1f}%</span> vs 10-day average. &nbsp;'
            f'14-day range: ₹{l14:,.0f} – ₹{h14:,.0f}. &nbsp;'
            f'Week volatility: ±₹{vol:,.0f}/gram. &nbsp;'
            f'The lower the price sits within the 14-day range, the lower your buying risk.'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # Quick refresh
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns([2, 1])
        with col_b:
            if st.button("🔄 Refresh prices"):
                with st.spinner("Fetching latest price..."):
                    result = api.refresh_price()
                if result and "error" not in result:
                    st.success(f"Updated: ₹{result['price_22k']:,.0f}/g (22k)")
                    st.rerun()
                else:
                    st.warning("Could not fetch live price. Using stored data.")
