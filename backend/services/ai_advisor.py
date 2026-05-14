"""
AI advisor using Groq — gives practical, grounded recommendations.
Uses llama-3.3-70b for best quality within Groq free tier.
"""
from datetime import datetime
from groq import Groq
from backend.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are a practical gold buying advisor for small goldsmith shops in India. 
You help jewellers decide WHEN and HOW MUCH gold to buy based on their orders and market data.

Your advice style:
- Plain language, like advice from a trusted friend who knows markets
- Specific and actionable — not vague platitudes
- Honest about uncertainty — never pretend to predict the future
- Focus on protecting the goldsmith's money, not making speculative profits
- Always separate urgent needs from optional purchases
- Recommend batching orders when it saves money
- Never use financial jargon; talk in rupees and grams

You are NOT a trading oracle. You help small businesses make smarter day-to-day buying decisions.
Keep responses to 5–7 sentences. Be direct."""

def build_context(price_data: dict, orders: list, risk_data: dict, custom_context: str = "") -> str:
    pending = [o for o in orders if o.get("status") == "pending"]
    urgent = [o for o in pending if o.get("urgency") == "urgent"]
    normal = [o for o in pending if o.get("urgency") == "normal"]
    flexible = [o for o in pending if o.get("urgency") == "flexible"]

    order_lines = []
    for o in pending[:8]:  # limit context
        due = o.get("due_date", "")
        due_str = f", due {due[:10]}" if due else ""
        order_lines.append(
            f"  - {o['customer_name']}: {o['item_description']} — {o['gold_grams']}g ({o['karat']}k), {o['urgency']}{due_str}"
        )

    return f"""Today's gold market snapshot (India):
- Current price: ₹{price_data.get('current_price', 0):,.0f}/gram (22k)
- 10-day average: ₹{price_data.get('avg_10d', 0):,.0f}/gram
- 30-day average: ₹{price_data.get('avg_30d', 0):,.0f}/gram
- 7-day price swing (volatility): ±₹{price_data.get('volatility_7d', 0):,.0f}/gram
- Price vs 10-day avg: {risk_data.get('current_vs_avg', 0):+.1f}%
- Market risk level: {risk_data.get('risk_level', 'unknown').upper()}

Pending orders right now:
{chr(10).join(order_lines) if order_lines else '  No pending orders.'}

Summary:
- Urgent orders: {len(urgent)} orders, {sum(o['gold_grams'] for o in urgent):.0f}g total
- Normal orders: {len(normal)} orders, {sum(o['gold_grams'] for o in normal):.0f}g total  
- Flexible orders: {len(flexible)} orders, {sum(o['gold_grams'] for o in flexible):.0f}g total
- Total gold needed: {sum(o['gold_grams'] for o in pending):.0f}g

{f'Additional context: {custom_context}' if custom_context else ''}

Give a practical recommendation on: (1) whether to buy today or wait, (2) exactly how many grams and which orders, (3) one specific tip for this week."""


async def get_ai_recommendation(price_data: dict, orders: list, risk_data: dict, custom_context: str = "") -> dict:
    """Call Groq API and return recommendation."""
    now = datetime.utcnow()

    if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
        # Return a rule-based fallback so app still works without API key
        advice = risk_data.get("advice", "")
        batch = risk_data.get("batch_suggestion", "")
        risk = risk_data.get("risk_level", "moderate")
        pg = risk_data.get("pending_grams", 0)
        ug = risk_data.get("urgent_grams", 0)

        fallback_text = (
            f"{advice} "
            f"{batch} "
            f"Current risk level is {risk}. "
        )
        if pg > ug:
            fallback_text += (
                f"You have {pg:.0f}g total pending — consider whether any non-urgent orders can wait a few more days. "
                "Track the 10-day average daily; when price dips below it, that is usually your best window."
            )
        fallback_text += " (Note: Add your GROQ_API_KEY in .env for AI-powered recommendations.)"
        return {
            "recommendation": fallback_text.strip(),
            "generated_at": now,
            "model_used": "rule-based fallback"
        }

    try:
        client = Groq(api_key=settings.groq_api_key)
        context = build_context(price_data, orders, risk_data, custom_context)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            max_tokens=400,
            temperature=0.4,   # lower = more consistent, grounded
        )
        text = response.choices[0].message.content.strip()
        model = response.model

        return {
            "recommendation": text,
            "generated_at": now,
            "model_used": model,
        }

    except Exception as e:
        return {
            "recommendation": (
                f"{risk_data.get('advice', 'Unable to generate AI recommendation at this time.')} "
                f"(AI service error: {str(e)[:80]})"
            ),
            "generated_at": now,
            "model_used": "error-fallback"
        }
