from datetime import datetime, timedelta

import streamlit as st

from frontend.components.ui import (
    AMBER,
    GOLD,
    GOLD_LIGHT,
    RED,
    TEXT_MUTED,
    badge,
    page_header,
)
from frontend.utils import api


def show():
    page_header(
        "Order Manager",
        "Track customer orders — know exactly how much gold you need and when",
    )

    orders_data = api.get_orders()
    if not orders_data or "error" in orders_data:
        st.error("Could not load orders. Is the backend running?")
        return

    pending = [o for o in orders_data if o["status"] == "pending"]
    purchased = [o for o in orders_data if o["status"] == "purchased"]
    completed = [o for o in orders_data if o["status"] == "completed"]

    # ── Summary strip ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pending orders", len(pending))
    c2.metric("Gold needed (pending)", f"{sum(o['gold_grams'] for o in pending):.1f}g")
    c3.metric("Urgent orders", len([o for o in pending if o["urgency"] == "urgent"]))
    c4.metric("Completed", len(completed))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Add new order ─────────────────────────────────────────────────────
    with st.expander("➕ Add new customer order", expanded=False):
        with st.form("add_order_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer = st.text_input("Customer name *")
                description = st.text_input(
                    "Item description *", placeholder="e.g. Gold necklace set"
                )
                grams = st.number_input(
                    "Gold required (grams) *",
                    min_value=0.1,
                    max_value=10000.0,
                    value=10.0,
                    step=0.5,
                )
            with col2:
                karat = st.selectbox("Karat", [22, 18, 24, 14], index=0)
                urgency = st.selectbox(
                    "Urgency",
                    ["normal", "urgent", "flexible"],
                    help="urgent=needed today/tomorrow, normal=few days, flexible=can wait",
                )
                due_date = st.date_input(
                    "Due date", value=datetime.now().date() + timedelta(days=5)
                )
            notes = st.text_area("Notes (optional)", height=60)

            if st.form_submit_button("Add Order", use_container_width=True):
                if not customer or not description:
                    st.error("Customer name and description are required.")
                else:
                    result = api.create_order(
                        {
                            "customer_name": customer,
                            "item_description": description,
                            "gold_grams": grams,
                            "karat": karat,
                            "urgency": urgency,
                            "due_date": datetime.combine(
                                due_date, datetime.min.time()
                            ).isoformat(),
                            "notes": notes,
                        }
                    )
                    if result and "error" not in result:
                        st.success(f"Order added: {description} for {customer}")
                        st.rerun()
                    else:
                        st.error(
                            f"Failed to add order: {result.get('error', 'Unknown') if result else 'No response'}"
                        )

    # ── Orders table ──────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(
        [
            f"Pending ({len(pending)})",
            f"Purchased ({len(purchased)})",
            f"Completed ({len(completed)})",
        ]
    )

    def render_orders(order_list, show_actions=True):
        if not order_list:
            st.info("No orders in this category.")
            return

        for o in order_list:
            due_str = ""
            if o.get("due_date"):
                due_dt = datetime.fromisoformat(o["due_date"].replace("Z", ""))
                days_left = (due_dt.date() - datetime.now().date()).days
                if days_left < 0:
                    due_str = (
                        f'<span style="color:{RED};">overdue {abs(days_left)}d</span>'
                    )
                elif days_left == 0:
                    due_str = f'<span style="color:{RED};">due today</span>'
                elif days_left <= 2:
                    due_str = f'<span style="color:{AMBER};">{days_left}d left</span>'
                else:
                    due_str = (
                        f'<span style="color:{TEXT_MUTED};">{days_left}d left</span>'
                    )

            bdg = badge(o["urgency"], o["urgency"])
            notes_html = (
                f'<div style="font-size:11px; color:{TEXT_MUTED};">{o["notes"]}</div>'
                if o.get("notes")
                else ""
            )

            col_info, col_action = (
                st.columns([4, 1]) if show_actions else (st.columns([1])[0], None)
            )
            with col_info:
                st.markdown(
                    f'<div class="gold-card" style="margin-bottom:8px;">'
                    f'<div style="display:flex; justify-content:space-between; align-items:flex-start;">'
                    f"<div>"
                    f'<div style="font-size:15px; font-weight:600; color:{GOLD_LIGHT};">'
                    f"{o['item_description']}</div>"
                    f'<div style="font-size:13px; color:{TEXT_MUTED}; margin-top:2px;">'
                    f"{o['customer_name']} &nbsp;·&nbsp; {o['karat']}k &nbsp;·&nbsp; "
                    f'<strong style="color:{GOLD};">{o["gold_grams"]}g</strong>'
                    f"</div>"
                    f"{notes_html}"
                    f"</div>"
                    f'<div style="text-align:right;">{bdg}<br>'
                    f'<span style="font-size:12px;">{due_str}</span></div>'
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

            if show_actions and col_action:
                with col_action:
                    st.markdown("<br>", unsafe_allow_html=True)
                    action = st.selectbox(
                        "Action",
                        ["—", "Mark purchased", "Mark completed", "Delete"],
                        key=f"action_{o['id']}",
                        label_visibility="collapsed",
                    )
                    if action == "Mark purchased":
                        api.update_order(o["id"], {"status": "purchased"})
                        st.rerun()
                    elif action == "Mark completed":
                        api.update_order(o["id"], {"status": "completed"})
                        st.rerun()
                    elif action == "Delete":
                        api.delete_order(o["id"])
                        st.rerun()

    with tab1:
        # Batching insight
        if len(pending) > 1:
            normal_orders = [o for o in pending if o["urgency"] == "normal"]
            if len(normal_orders) > 1:
                batch_g = sum(o["gold_grams"] for o in normal_orders)
                st.markdown(
                    f'<div class="advice-wait" style="margin-bottom:14px;">💡 '
                    f"<strong>Batching tip:</strong> You have {len(normal_orders)} normal orders "
                    f"totalling {batch_g:.1f}g. Buy them together in one go to avoid multiple "
                    f"market exposures and save on transaction friction.</div>",
                    unsafe_allow_html=True,
                )
        render_orders(pending, show_actions=True)

    with tab2:
        render_orders(purchased, show_actions=False)

    with tab3:
        render_orders(completed, show_actions=False)
