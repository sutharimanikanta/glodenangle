from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.database import get_db, Order, GoldPrice
from backend.models.schemas import (
    RiskAnalysisOut, WhatIfRequest, WhatIfOut,
    AIRecommendationRequest, AIRecommendationOut,
    PurchaseCreate, PurchaseOut
)
from backend.models.database import Purchase
from backend.services.risk_engine import calculate_risk, calculate_whatif
from backend.services.ai_advisor import get_ai_recommendation
from backend.routers.prices import get_price_history, get_current_price
from datetime import datetime

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/risk", response_model=RiskAnalysisOut)
async def get_risk_analysis(db: AsyncSession = Depends(get_db)):
    """Compute current risk score based on price + pending orders."""
    history = await get_price_history(days=30, db=db)
    pending_result = await db.execute(
        select(Order).where(Order.status == "pending")
    )
    pending = pending_result.scalars().all()

    result = calculate_risk(
        current_price=history.current_price,
        avg_10d=history.avg_10d,
        avg_30d=history.avg_30d,
        volatility_7d=history.volatility_7d,
        pending_orders=pending,
    )
    return RiskAnalysisOut(**result)


@router.post("/whatif", response_model=WhatIfOut)
async def what_if_calculator(payload: WhatIfRequest, db: AsyncSession = Depends(get_db)):
    """Calculate cost impact of buying now vs waiting."""
    if payload.current_price:
        current_price = payload.current_price
    else:
        current = await get_current_price(db=db)
        current_price = current.price_22k

    result = calculate_whatif(
        grams=payload.grams,
        current_price=current_price,
        expected_change_pct=payload.expected_change_pct,
        days_to_wait=payload.days_to_wait,
    )
    return WhatIfOut(**result)


@router.post("/recommend", response_model=AIRecommendationOut)
async def ai_recommendation(
    payload: AIRecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered recommendation using Groq."""
    history = await get_price_history(days=30, db=db)
    risk = await get_risk_analysis(db=db)

    orders_data = []
    if payload.include_orders:
        result = await db.execute(select(Order).where(Order.status == "pending"))
        orders = result.scalars().all()
        orders_data = [
            {
                "customer_name": o.customer_name,
                "item_description": o.item_description,
                "gold_grams": o.gold_grams,
                "karat": o.karat,
                "urgency": o.urgency,
                "due_date": str(o.due_date) if o.due_date else None,
                "status": o.status,
            }
            for o in orders
        ]

    price_data = {
        "current_price": history.current_price,
        "avg_10d": history.avg_10d,
        "avg_30d": history.avg_30d,
        "volatility_7d": history.volatility_7d,
        "change_today_pct": history.change_today_pct,
    }
    risk_data = risk.model_dump()

    result = await get_ai_recommendation(
        price_data=price_data,
        orders=orders_data,
        risk_data=risk_data,
        custom_context=payload.custom_context or "",
    )
    return AIRecommendationOut(**result)


@router.post("/purchase", response_model=PurchaseOut, status_code=201)
async def log_purchase(payload: PurchaseCreate, db: AsyncSession = Depends(get_db)):
    """Log a gold purchase."""
    purchase = Purchase(
        grams_bought=payload.grams_bought,
        price_per_gram=payload.price_per_gram,
        total_cost=round(payload.grams_bought * payload.price_per_gram, 2),
        karat=payload.karat,
        notes=payload.notes or "",
    )
    db.add(purchase)
    await db.commit()
    await db.refresh(purchase)
    return purchase
