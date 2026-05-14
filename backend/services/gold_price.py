"""
Gold price service — fetches live prices with graceful fallback to demo data.
Sources tried in order:
  1. GoldAPI.io (requires free API key)
  2. Metals.live (no key needed, sometimes rate-limits)
  3. Demo data (always works — used for testing / when keys missing)
"""

import random
from datetime import datetime, timedelta
from typing import Optional

import httpx

from backend.config import get_settings

settings = get_settings()

# ─── Base 24k price in INR (updated manually as fallback seed) ───────────────
# As of mid-2025 approximate range
_BASE_24K_INR = 7500.0  # per gram


def karat_price(price_24k: float, karat: int) -> float:
    """Convert 24k price to any karat."""
    return round(price_24k * karat / 24, 2)


async def fetch_live_price() -> Optional[dict]:
    """Try fetching live gold price. Returns dict or None on failure."""
    # ── Attempt 1: GoldAPI.io ──────────────────────────────────────────────
    if settings.gold_api_key and settings.gold_api_key != "your_goldapi_io_key_here":
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                headers = {
                    "x-access-token": settings.gold_api_key,
                    "Content-Type": "application/json",
                }
                # Fetch USD price and convert to INR
                resp = await client.get(
                    "https://www.goldapi.io/api/XAU/USD", headers=headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    usd_price_per_oz = data.get("price", 0)
                    if usd_price_per_oz and usd_price_per_oz > 100:
                        # Convert USD/oz to INR/gram
                        inr_rate = 83.5  # default USD to INR rate
                        try:
                            fx_resp = await client.get(
                                "https://open.er-api.com/v6/latest/USD", timeout=5
                            )
                            if fx_resp.status_code == 200:
                                inr_rate = (
                                    fx_resp.json().get("rates", {}).get("INR", 83.5)
                                )
                        except Exception:
                            pass

                        # 1 troy ounce = 31.1035 grams
                        price_gram_24k = (usd_price_per_oz * inr_rate) / 31.1035
                        if price_gram_24k > 100:
                            return {
                                "price_per_gram": round(price_gram_24k, 2),
                                "price_22k": karat_price(price_gram_24k, 22),
                                "price_18k": karat_price(price_gram_24k, 18),
                                "source": "goldapi.io",
                            }
        except Exception:
            pass

    # ── Attempt 2: metals.live (free, no key) ─────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get("https://metals.live/api/v1/spot")
            if resp.status_code == 200:
                data = resp.json()
                # metals.live returns USD/troy_oz
                for item in data:
                    if item.get("gold"):
                        usd_oz = item["gold"]
                        # Get USD→INR rate
                        fx_resp = await client.get(
                            "https://open.er-api.com/v6/latest/USD"
                        )
                        inr_rate = 83.5
                        if fx_resp.status_code == 200:
                            inr_rate = fx_resp.json().get("rates", {}).get("INR", 83.5)
                        price_gram_24k = (usd_oz * inr_rate) / 31.1035
                        return {
                            "price_per_gram": round(price_gram_24k, 2),
                            "price_22k": karat_price(price_gram_24k, 22),
                            "price_18k": karat_price(price_gram_24k, 18),
                            "source": "metals.live",
                        }
    except Exception:
        pass

    return None  # Will trigger demo data path in router


def get_demo_price(day_offset: int = 0) -> dict:
    """Generate realistic-looking demo price for testing."""
    random.seed(42 + day_offset)
    # Simulate a realistic 30-day price walk
    price = _BASE_24K_INR
    for i in range(30 - day_offset):
        price += random.uniform(-80, 90)
    price = max(6500, min(9000, price))
    return {
        "price_per_gram": round(price, 2),
        "price_22k": karat_price(price, 22),
        "price_18k": karat_price(price, 18),
        "source": "demo",
    }


def generate_demo_history(days: int = 30) -> list[dict]:
    """Generate realistic 30-day price history for demo/seed data."""
    random.seed(99)
    prices = []
    price = _BASE_24K_INR - 300
    now = datetime.utcnow()
    for i in range(days, 0, -1):
        price += random.gauss(10, 55)  # slight upward drift + noise
        price = max(6800, min(9000, price))
        prices.append(
            {
                "price_per_gram": round(price, 2),
                "price_22k": karat_price(price, 22),
                "price_18k": karat_price(price, 18),
                "source": "demo",
                "recorded_at": now - timedelta(days=i),
            }
        )
    return prices
