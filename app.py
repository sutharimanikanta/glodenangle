"""
Gold Buy Advisor — Main Streamlit Application
Run: streamlit run app.py
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Gold Buy Advisor",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.components.ui import apply_theme, GOLD, TEXT_MUTED, GOLD_LIGHT
apply_theme()

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-size:22px; font-weight:700; color:{GOLD_LIGHT}; '
        f'margin-bottom:2px;">✦ Gold Buy Advisor</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:12px; color:{TEXT_MUTED}; margin-bottom:24px;">'
        "Decision support for small goldsmith shops</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "Navigate",
        ["Dashboard", "Order Manager", "What-If Calculator", "AI Advisor", "Purchase Log"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown(
        f'<div style="font-size:11px; color:{TEXT_MUTED}; line-height:1.7;">'
        "This tool helps you make <strong>informed</strong> buying decisions — "
        "not predictions. Always use your own judgment."
        "</div>",
        unsafe_allow_html=True,
    )

# ── Route to page ────────────────────────────────────────────────────────────
if page == "Dashboard":
    from frontend.pages.dashboard import show
    show()
elif page == "Order Manager":
    from frontend.pages.orders import show
    show()
elif page == "What-If Calculator":
    from frontend.pages.whatif import show
    show()
elif page == "AI Advisor":
    from frontend.pages.advisor import show
    show()
elif page == "Purchase Log":
    from frontend.pages.purchases import show
    show()
