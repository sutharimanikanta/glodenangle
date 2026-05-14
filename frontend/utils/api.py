"""Thin wrapper around the FastAPI backend for Streamlit pages."""
import requests
import os
from typing import Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _get(path: str, params: dict = None) -> Optional[dict]:
    try:
        r = requests.get(f"{BACKEND_URL}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Make sure FastAPI is running on port 8000."}
    except Exception as e:
        return {"error": str(e)}


def _post(path: str, json: dict = None) -> Optional[dict]:
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=json, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend."}
    except Exception as e:
        return {"error": str(e)}


def _patch(path: str, json: dict) -> Optional[dict]:
    try:
        r = requests.patch(f"{BACKEND_URL}{path}", json=json, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _delete(path: str) -> bool:
    try:
        r = requests.delete(f"{BACKEND_URL}{path}", timeout=10)
        return r.status_code == 204
    except Exception:
        return False


# ── Price endpoints ─────────────────────────────────────────────────────────

def get_current_price():
    return _get("/api/prices/current")

def get_price_history(days: int = 30):
    return _get("/api/prices/history", params={"days": days})

def refresh_price():
    return _post("/api/prices/refresh")

# ── Order endpoints ──────────────────────────────────────────────────────────

def get_orders(status: str = None):
    params = {"status": status} if status else None
    return _get("/api/orders/", params=params)

def create_order(data: dict):
    return _post("/api/orders/", json=data)

def update_order(order_id: int, data: dict):
    return _patch(f"/api/orders/{order_id}", json=data)

def delete_order(order_id: int):
    return _delete(f"/api/orders/{order_id}")

# ── Analysis endpoints ────────────────────────────────────────────────────────

def get_risk_analysis():
    return _get("/api/analysis/risk")

def get_whatif(grams: float, change_pct: float, days: int):
    return _post("/api/analysis/whatif", json={
        "grams": grams,
        "expected_change_pct": change_pct,
        "days_to_wait": days,
    })

def get_ai_recommendation(custom_context: str = ""):
    return _post("/api/analysis/recommend", json={
        "include_orders": True,
        "custom_context": custom_context,
    })

def log_purchase(grams: float, price_per_gram: float, karat: int = 22, notes: str = ""):
    return _post("/api/analysis/purchase", json={
        "grams_bought": grams,
        "price_per_gram": price_per_gram,
        "karat": karat,
        "notes": notes,
    })
