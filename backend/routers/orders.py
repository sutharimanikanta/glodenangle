from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import List

from backend.models.database import get_db, Order
from backend.models.schemas import OrderCreate, OrderUpdate, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


async def _seed_demo_orders(db: AsyncSession):
    from sqlalchemy import func
    result = await db.execute(select(func.count()).select_from(Order))
    count = result.scalar()
    if count == 0:
        from datetime import timedelta
        now = datetime.utcnow()
        demo = [
            Order(customer_name="Priya Sharma", item_description="Gold necklace set (traditional)",
                  gold_grams=18.0, karat=22, urgency="urgent",
                  due_date=now + timedelta(days=1), notes="Wedding order — do not delay"),
            Order(customer_name="Ramesh Gupta", item_description="Bangles pair (plain)",
                  gold_grams=12.0, karat=22, urgency="normal",
                  due_date=now + timedelta(days=4), notes=""),
            Order(customer_name="Anita Patel", item_description="Custom engagement ring",
                  gold_grams=8.0, karat=18, urgency="normal",
                  due_date=now + timedelta(days=6), notes="18k rose gold finish"),
            Order(customer_name="Suresh Kumar", item_description="Temple jewellery earrings",
                  gold_grams=6.5, karat=22, urgency="flexible",
                  due_date=now + timedelta(days=12), notes="Can wait — customer flexible"),
        ]
        for o in demo:
            db.add(o)
        await db.commit()


@router.get("/", response_model=List[OrderOut])
async def list_orders(status: str = None, db: AsyncSession = Depends(get_db)):
    await _seed_demo_orders(db)
    q = select(Order).order_by(desc(Order.created_at))
    if status:
        q = q.where(Order.status == status)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    order = Order(**payload.model_dump())
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}", response_model=OrderOut)
async def update_order(order_id: int, payload: OrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for field, val in payload.model_dump(exclude_none=True).items():
        setattr(order, field, val)
    order.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.delete(order)
    await db.commit()
