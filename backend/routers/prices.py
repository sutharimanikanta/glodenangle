from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta
from typing import List

from backend.models.database import get_db, GoldPrice
from backend.models.schemas import GoldPriceOut, PriceHistoryOut
from backend.services.gold_price import fetch_live_price, get_demo_price, generate_demo_history

router = APIRouter(prefix="/api/prices", tags=["prices"])


async def _get_or_seed_prices(db: AsyncSession) -> None:
    """Ensure at least 30 days of price history exists (seeds demo data if empty)."""
    result = await db.execute(select(func.count()).select_from(GoldPrice))
    count = result.scalar()
    if count < 5:
        demo = generate_demo_history(30)
        for d in demo:
            db.add(GoldPrice(**d))
        await db.commit()


@router.get("/current", response_model=GoldPriceOut)
async def get_current_price(db: AsyncSession = Depends(get_db)):
    """Get the most recent price. Fetches live if the last record is >1h old."""
    await _get_or_seed_prices(db)

    result = await db.execute(
        select(GoldPrice).order_by(desc(GoldPrice.recorded_at)).limit(1)
    )
    latest = result.scalar_one_or_none()
    threshold = datetime.utcnow() - timedelta(hours=1)

    if not latest or latest.recorded_at < threshold:
        live = await fetch_live_price()
        data = live if live else get_demo_price(0)
        new_price = GoldPrice(**data)
        db.add(new_price)
        await db.commit()
        await db.refresh(new_price)
        return new_price

    return latest


@router.post("/refresh", response_model=GoldPriceOut)
async def force_refresh_price(db: AsyncSession = Depends(get_db)):
    """Force-fetch a fresh price from the API."""
    live = await fetch_live_price()
    data = live if live else get_demo_price(0)
    new_price = GoldPrice(**data)
    db.add(new_price)
    await db.commit()
    await db.refresh(new_price)
    return new_price


@router.get("/history", response_model=PriceHistoryOut)
async def get_price_history(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get price history with computed statistics."""
    await _get_or_seed_prices(db)
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(GoldPrice)
        .where(GoldPrice.recorded_at >= since)
        .order_by(GoldPrice.recorded_at.asc())
    )
    prices_orm = result.scalars().all()

    if not prices_orm:
        raise HTTPException(status_code=404, detail="No price history found.")

    prices_22k = [p.price_22k for p in prices_orm]
    current_price = prices_22k[-1]

    # 10-day avg
    r10 = await db.execute(
        select(GoldPrice)
        .where(GoldPrice.recorded_at >= datetime.utcnow() - timedelta(days=10))
        .order_by(desc(GoldPrice.recorded_at))
    )
    p10 = [p.price_22k for p in r10.scalars().all()]
    avg_10d = sum(p10) / len(p10) if p10 else current_price

    # 30-day avg
    avg_30d = sum(prices_22k) / len(prices_22k)

    # 14-day high/low
    r14 = await db.execute(
        select(GoldPrice)
        .where(GoldPrice.recorded_at >= datetime.utcnow() - timedelta(days=14))
    )
    p14 = [p.price_22k for p in r14.scalars().all()]
    high_14d = max(p14) if p14 else current_price
    low_14d = min(p14) if p14 else current_price

    # 7-day volatility (std-dev proxy: half of range)
    r7 = await db.execute(
        select(GoldPrice)
        .where(GoldPrice.recorded_at >= datetime.utcnow() - timedelta(days=7))
    )
    p7 = [p.price_22k for p in r7.scalars().all()]
    volatility_7d = (max(p7) - min(p7)) / 2 if len(p7) > 1 else 0.0

    # Change vs yesterday
    yesterday_cutoff = datetime.utcnow() - timedelta(days=1)
    r_yd = await db.execute(
        select(GoldPrice)
        .where(GoldPrice.recorded_at >= yesterday_cutoff)
        .order_by(GoldPrice.recorded_at.asc())
        .limit(1)
    )
    yesterday = r_yd.scalar_one_or_none()
    if yesterday and yesterday.price_22k > 0:
        change_today_pct = ((current_price - yesterday.price_22k) / yesterday.price_22k) * 100
    else:
        change_today_pct = 0.0

    return PriceHistoryOut(
        prices=[GoldPriceOut.model_validate(p) for p in prices_orm],
        avg_10d=round(avg_10d, 2),
        avg_30d=round(avg_30d, 2),
        high_14d=round(high_14d, 2),
        low_14d=round(low_14d, 2),
        volatility_7d=round(volatility_7d, 2),
        change_today_pct=round(change_today_pct, 2),
        current_price=round(current_price, 2),
    )
