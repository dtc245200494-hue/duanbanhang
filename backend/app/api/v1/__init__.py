"""API v1 router aggregator module."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.stores import router as stores_router
from app.api.v1.products import router as products_router
from app.api.v1.batches import router as batches_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.ai_discount import router as ai_discount_router
from app.api.v1.ai_recommendations import router as ai_recommendations_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(stores_router)
api_router.include_router(products_router)
api_router.include_router(batches_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(ai_discount_router)
api_router.include_router(ai_recommendations_router)
