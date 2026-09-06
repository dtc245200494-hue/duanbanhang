from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    items: List[OrderItemIn] = Field(min_length=1)
    discount: float = Field(default=0, ge=0)
    payment_method: str = "cash"
    note: str = ""


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderOut(BaseModel):
    id: int
    code: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str
    total_amount: float
    discount: float
    final_amount: float
    payment_method: str
    status: str
    note: str = ""
    items: List[OrderItemOut] = []
