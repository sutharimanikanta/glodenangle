from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from backend.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class GoldPrice(Base):
    __tablename__ = "gold_prices"
    id = Column(Integer, primary_key=True, index=True)
    price_per_gram = Column(Float, nullable=False)       # INR per gram 24k
    price_22k = Column(Float, nullable=False)            # INR per gram 22k
    price_18k = Column(Float, nullable=False)            # INR per gram 18k
    source = Column(String(50), default="api")           # api | manual | demo
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    item_description = Column(String(200), nullable=False)
    gold_grams = Column(Float, nullable=False)
    karat = Column(Integer, default=22)
    urgency = Column(String(20), default="normal")       # urgent | normal | flexible
    due_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")       # pending | purchased | completed
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    grams_bought = Column(Float, nullable=False)
    price_per_gram = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    karat = Column(Integer, default=22)
    notes = Column(Text, default="")
    purchased_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
