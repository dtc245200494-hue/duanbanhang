"""Order and OrderItem Pydantic v2 schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.payment import PaymentOut


class OrderItemBase(BaseModel):
    """Base schema for order item."""

    batch_id: Optional[int] = Field(None, description="ID lô hàng được trừ kho")
    product_id: Optional[int] = Field(None, description="ID sản phẩm (tự động chọn lô FEFO nếu không truyền batch_id)")
    quantity: int = Field(..., gt=0, description="Số lượng đặt mua")


class OrderItemCreate(OrderItemBase):
    """Schema for item input when creating an order."""

    pass


class OrderItemOut(BaseModel):
    """Schema for returning order line item details."""

    id: int
    order_id: int
    batch_id: Optional[int] = None
    batch_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Schema for creating a customer order."""

    store_id: Optional[int] = Field(None, description="ID cửa hàng phụ trách")
    user_id: Optional[int] = Field(None, description="ID tài khoản người mua (nếu có đăng nhập)")
    customer_name: str = Field(..., max_length=100, description="Tên người nhận")
    customer_phone: str = Field(..., max_length=20, description="Số điện thoại nhận hàng")
    shipping_address: str = Field(..., description="Địa chỉ giao hàng")
    note: Optional[str] = Field(None, description="Ghi chú đơn hàng")
    payment_method: Optional[str] = Field("COD", description="Hình thức thanh toán: COD, bank_transfer, momo, vnpay")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Danh sách món hàng trong đơn")


class OrderUpdateStatus(BaseModel):
    """Schema for updating order progress."""

    status: str = Field(
        ...,
        pattern="^(pending|confirmed|shipping|completed|cancelled)$",
        description="Trạng thái mới: pending, confirmed, shipping, completed, cancelled",
    )


class OrderOut(BaseModel):
    """Schema for returning order details with items and payments."""

    id: int
    store_id: Optional[int] = None
    user_id: Optional[int] = None
    customer_name: str
    customer_phone: str
    shipping_address: str
    note: Optional[str] = None
    total_amount: Decimal
    status: str
    created_at: datetime
    items: List[OrderItemOut] = []
    payments: List[PaymentOut] = []

    model_config = ConfigDict(from_attributes=True)
