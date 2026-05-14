import streamlit as st
from datetime import datetime
from frontend.components.ui import (
    page_header, GOLD, GOLD_LIGHT, TEXT_MUTED, BG_CARD
)
from frontend.utils import api


def show():
    page_header("AI Advisor", "Plain-language recommendation based on today's data and your order book")

    st.markdown(
        f'<div style="font-size:13px; color:{TEXT_MUTED}; max-width:660px; '
        f'margin-bottom:20px; line-height:1.7;">'
        "The advisor looks at today's gold price, your pending orders, and recent volatility — "
        "then gives you a practical, honest recommendation. "
        "It won't tell you what price gold will be tomorrow. "
        "It will tell you what makes sense to do <em>today</em>, given what you have in front of you."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Context snapshot ──────────────────────────────────────────────────
    col1, col2 = st.columns([1.4, 1])

    with col1:
        with st.spinner("Loading market snapshot..."):
            history = api.get_price_history(days=14)
            risk = api.get_risk_analysis()
            orders = api.get_orders(status="pending")

        if history and "error" not in history:
            cur = history["current_price"]
            avg10 = history["avg_10d"]
            dev = ((cur - avg10) / avg10) * 100
            vol = history["volatility_7d"]
            change = history["change_today_pct"]

            st.markdown("#### Today's snapshot")
            m1, m2, m3 = st.columns(3)
            m1.metric("22k price", f"₹{cur:,.0f}", f"{change:+.2f}%")
            m2.metric("vs 10-day avg", f"{dev:+.1f}%")
            m3.metric("Risk level", (risk or {}).get("risk_level", "—").upper())

            pending = [o for o in (orders or []) if o.get("status") == "pending"]
            if pending:
                total_g = sum(o["gold_grams"] for o in pending)
                urgent_g = sum(o["gold_grams"] for o in pending if o["urgency"] == "urgent")
                st.markdown(
                    f'<div class="gold-card" style="margin-top:12px;">'
                    f'<div class="gold-card-title">pending orders</div>'
                    f'<div style="color:{GOLD_LIGHT}; font-size:15px; font-weight:600;">'
                    f'{len(pending)} orders — {total_g:.1f}g total</div>'
                    f'<div style="color:{TEXT_MUTED}; font-size:13px; margin-top:4px;">'
                    f'Urgent: {urgent_g:.1f}g &nbsp;·&nbsp; Can wait: {total_g-urgent_g:.1f}g</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col2:
        st.markdown("#### Optional context")
        custom_context = st.text_area(
            "Add context for the advisor (optional)",
            placeholder=(
                "e.g. 'A big wedding order is coming next week' or "
                "'I heard prices will rise due to the festival season' or "
                "'I can only afford to spend ₹50,000 right now'"
            ),
            height=130,
            label_visibility="collapsed"
        )

    # ── Generate button ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        generate = st.button("✦ Get today's recommendation", use_container_width=True)

    if generate or st.session_state.get("ai_result"):
        if generate:
            with st.spinner("Thinking through your situation..."):
                result = api.get_ai_recommendation(custom_context=custom_context)
            st.session_state["ai_result"] = result
            st.session_state["ai_time"] = datetime.now().strftime("%H:%M:%S")
        else:
            result = st.session_state.get("ai_result")

        if result and "error" not in result:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Recommendation")
            model = result.get("model_used", "AI")
            time_str = st.session_state.get("ai_time", "")
            st.markdown(
                f'<div style="font-size:11px; color:{TEXT_MUTED}; margin-bottom:8px;">'
                f'Generated at {time_str} &nbsp;·&nbsp; Model: {model}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="advice-ai">{result["recommendation"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Regenerate", key="regen"):
                if "ai_result" in st.session_state:
                    del st.session_state["ai_result"]
                st.rerun()
        elif result:
            st.error(f"Could not get recommendation: {result.get('error', 'Unknown error')}")

    # ── Disclaimer ────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:12px; color:{TEXT_MUTED}; '
        f'border-top: 1px solid #2A2415; padding-top: 12px; max-width:660px; line-height:1.7;">'
        "This advisor uses available market data and your order book to give context-aware suggestions. "
        "It does not predict future gold prices. "
        "Final buying decisions always rest with you — use this as one input, not the only one."
        "</div>",
        unsafe_allow_html=True,
    )
