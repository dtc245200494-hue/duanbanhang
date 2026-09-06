from typing import List, Optional

from pydantic import BaseModel

from app.schemas.product import ProductOut


class RevenueRow(BaseModel):
    label: str
    orders: int
    revenue: float


class CategoryRevenueRow(BaseModel):
    category: str
    quantity: int
    revenue: float


class TopProductRow(BaseModel):
    product_id: int
    code: str
    name: str
    quantity: int
    revenue: float


class DashboardOut(BaseModel):
    total_revenue: float
    total_orders: int
    today_revenue: float
    month_revenue: float
    month_orders: int
    total_products: int
    active_products: int
    total_customers: int
    low_stock_count: int
    top_products: List[TopProductRow]
    low_stock_products: List[ProductOut]
