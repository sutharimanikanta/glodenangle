from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.models.database import init_db
from backend.routers import prices, orders, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Gold Buy Advisor API",
    description="Decision-support backend for small goldsmith shops",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router)
app.include_router(orders.router)
app.include_router(analysis.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Gold Buy Advisor API"}
