from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# ─── Gold Price ───────────────────────────────────────────────────────────────

class GoldPriceOut(BaseModel):
    id: int
    price_per_gram: float
    price_22k: float
    price_18k: float
    source: str
    recorded_at: datetime

    class Config:
        from_attributes = True

class PriceHistoryOut(BaseModel):
    prices: List[GoldPriceOut]
    avg_10d: float
    avg_30d: float
    high_14d: float
    low_14d: float
    volatility_7d: float
    change_today_pct: float
    current_price: float

# ─── Orders ──────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    item_description: str = Field(..., min_length=1, max_length=200)
    gold_grams: float = Field(..., gt=0, le=10000)
    karat: int = Field(22, ge=18, le=24)
    urgency: str = Field("normal", pattern="^(urgent|normal|flexible)$")
    due_date: Optional[datetime] = None
    notes: Optional[str] = ""

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    item_description: Optional[str] = None
    gold_grams: Optional[float] = None
    karat: Optional[int] = None
    urgency: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class OrderOut(BaseModel):
    id: int
    customer_name: str
    item_description: str
    gold_grams: float
    karat: int
    urgency: str
    due_date: Optional[datetime]
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ─── Purchases ───────────────────────────────────────────────────────────────

class PurchaseCreate(BaseModel):
    grams_bought: float = Field(..., gt=0)
    price_per_gram: float = Field(..., gt=0)
    karat: int = Field(22, ge=18, le=24)
    notes: Optional[str] = ""

class PurchaseOut(BaseModel):
    id: int
    grams_bought: float
    price_per_gram: float
    total_cost: float
    karat: int
    notes: str
    purchased_at: datetime

    class Config:
        from_attributes = True

# ─── Risk Analysis ───────────────────────────────────────────────────────────

class RiskAnalysisOut(BaseModel):
    risk_score: float          # 0-100
    risk_level: str            # low | moderate | high
    current_vs_avg: float      # % above/below 10d avg
    advice: str
    advice_type: str           # buy | wait | caution
    pending_grams: float
    urgent_grams: float
    batch_suggestion: str

# ─── What-if Calculator ──────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    grams: float = Field(..., gt=0)
    expected_change_pct: float = Field(..., ge=-10, le=10)
    days_to_wait: int = Field(..., ge=0, le=30)
    current_price: Optional[float] = None

class WhatIfOut(BaseModel):
    buy_now_cost: float
    future_price: float
    future_cost: float
    cost_difference: float
    verdict: str
    verdict_type: str   # buy_now | wait | neutral

# ─── AI Recommendation ───────────────────────────────────────────────────────

class AIRecommendationRequest(BaseModel):
    include_orders: bool = True
    custom_context: Optional[str] = ""

class AIRecommendationOut(BaseModel):
    recommendation: str
    generated_at: datetime
    model_used: str

# ─── Preferences ─────────────────────────────────────────────────────────────

class PreferenceSet(BaseModel):
    key: str
    value: str
