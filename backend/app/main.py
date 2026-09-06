from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.database import Base, engine
from app.routers import (
    ai,
    auth,
    categories,
    customers,
    dashboard,
    orders,
    products,
    purchases,
    reports,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sales Management AI API",
    description="Hệ thống quản lý bán hàng có tích hợp AI - AIA331",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (
    auth,
    users,
    categories,
    products,
    customers,
    orders,
    purchases,
    dashboard,
    reports,
    ai,
):
    app.include_router(module.router)
    if hasattr(module, "inventory_router"):
        app.include_router(module.inventory_router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "service": "sales-management-ai"}


@app.get("/", include_in_schema=False)
def root():
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")
