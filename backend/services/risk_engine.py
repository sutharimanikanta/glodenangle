"""
Risk analysis engine for gold buying decisions.
Conservative, rule-based logic — no speculative predictions.
"""
from typing import List
from datetime import datetime, timedelta

def calculate_risk(
    current_price: float,
    avg_10d: float,
    avg_30d: float,
    volatility_7d: float,
    pending_orders: list,
) -> dict:
    """
    Compute a 0–100 risk score based on:
    - How much current price deviates from moving averages
    - Recent volatility
    - Urgency of pending orders (forces hand)
    
    Returns risk_score, risk_level, advice, and batch suggestion.
    """
    # ── Price deviation from 10-day average ──────────────────────────────
    dev_from_10d = ((current_price - avg_10d) / avg_10d) * 100  # % above/below

    # ── Raw risk score components (each 0–100) ───────────────────────────
    # 1. Price position: above avg = riskier to buy
    if dev_from_10d <= -2.0:
        price_risk = 10   # price is well below avg — good time
    elif dev_from_10d <= 0:
        price_risk = 30   # slightly below avg — reasonable
    elif dev_from_10d <= 1.5:
        price_risk = 55   # slightly above avg — neutral-caution
    elif dev_from_10d <= 3.0:
        price_risk = 72   # meaningfully above avg — wait if possible
    else:
        price_risk = 90   # significantly above avg — high risk

    # 2. Volatility risk: higher swings = harder to time
    vol_pct = (volatility_7d / avg_10d) * 100
    if vol_pct < 0.8:
        vol_risk = 20
    elif vol_pct < 1.5:
        vol_risk = 40
    elif vol_pct < 2.5:
        vol_risk = 60
    else:
        vol_risk = 80

    # ── Combined score (price deviation carries more weight) ──────────────
    risk_score = round(0.70 * price_risk + 0.30 * vol_risk, 1)

    # ── Risk level ────────────────────────────────────────────────────────
    if risk_score < 35:
        risk_level = "low"
    elif risk_score < 60:
        risk_level = "moderate"
    else:
        risk_level = "high"

    # ── Order analysis ────────────────────────────────────────────────────
    pending_grams = sum(o.gold_grams for o in pending_orders if o.status == "pending")
    urgent_orders = [o for o in pending_orders if o.urgency == "urgent" and o.status == "pending"]
    normal_orders = [o for o in pending_orders if o.urgency == "normal" and o.status == "pending"]
    flexible_orders = [o for o in pending_orders if o.urgency == "flexible" and o.status == "pending"]
    urgent_grams = sum(o.gold_grams for o in urgent_orders)

    # ── Advice ────────────────────────────────────────────────────────────
    if risk_level == "low":
        if pending_grams > 0:
            advice = (
                f"Good time to buy — price is {abs(dev_from_10d):.1f}% below the 10-day average. "
                f"Consider buying all {pending_grams:.0f}g of pending orders now."
            )
        else:
            advice = (
                f"Price is {abs(dev_from_10d):.1f}% below the 10-day average — "
                "a good window if you have upcoming orders. Consider buying in advance."
            )
        advice_type = "buy"

    elif risk_level == "moderate":
        if urgent_grams > 0:
            advice = (
                f"Price is near average. Buy only the urgent {urgent_grams:.0f}g needed now. "
                "Hold off on the rest and watch for a dip in the next 2–3 days."
            )
        else:
            advice = (
                "Price is close to the 10-day average. No urgent pressure — "
                "wait 1–2 days and watch for a small dip before buying."
            )
        advice_type = "caution"

    else:  # high
        if urgent_grams > 0:
            advice = (
                f"Price is {dev_from_10d:.1f}% above the 10-day average — higher than usual. "
                f"Buy only the urgent {urgent_grams:.0f}g that cannot wait. "
                "Delay other purchases if the customer can allow it."
            )
        else:
            advice = (
                f"Price is {dev_from_10d:.1f}% above the 10-day average. "
                "Avoid buying unless a customer order is urgent. "
                "Historical patterns suggest waiting 3–5 days is worth it at this level."
            )
        advice_type = "wait"

    # ── Batch suggestion ──────────────────────────────────────────────────
    batch_parts = []
    if len(normal_orders) > 1:
        batch_grams = sum(o.gold_grams for o in normal_orders)
        batch_parts.append(
            f"Batch {len(normal_orders)} normal orders ({batch_grams:.0f}g) into a single purchase to save on shop margin."
        )
    if len(flexible_orders) > 0:
        flex_grams = sum(o.gold_grams for o in flexible_orders)
        batch_parts.append(
            f"{len(flexible_orders)} flexible order(s) ({flex_grams:.0f}g) can wait for a better price window."
        )
    if not batch_parts:
        batch_suggestion = "No batching opportunity right now."
    else:
        batch_suggestion = " ".join(batch_parts)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "current_vs_avg": round(dev_from_10d, 2),
        "advice": advice,
        "advice_type": advice_type,
        "pending_grams": pending_grams,
        "urgent_grams": urgent_grams,
        "batch_suggestion": batch_suggestion,
    }


def calculate_whatif(
    grams: float,
    current_price: float,
    expected_change_pct: float,
    days_to_wait: int,
) -> dict:
    """Compute cost comparison for buy-now vs wait scenario."""
    buy_now_cost = round(grams * current_price, 2)
    future_price = round(current_price * (1 + expected_change_pct / 100), 2)
    future_cost = round(grams * future_price, 2)
    cost_difference = round(future_cost - buy_now_cost, 2)

    if cost_difference > 500:
        verdict = f"Buying now saves ₹{abs(cost_difference):,.0f} — price is expected to rise."
        verdict_type = "buy_now"
    elif cost_difference < -500:
        verdict = f"Waiting {days_to_wait} day(s) could save ₹{abs(cost_difference):,.0f} if the price drops as expected."
        verdict_type = "wait"
    else:
        verdict = "Difference is small — buy the urgent orders now and hold the rest."
        verdict_type = "neutral"

    return {
        "buy_now_cost": buy_now_cost,
        "future_price": future_price,
        "future_cost": future_cost,
        "cost_difference": cost_difference,
        "verdict": verdict,
        "verdict_type": verdict_type,
    }
