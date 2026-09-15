"""ProductBatch Pydantic v2 schemas."""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BatchBase(BaseModel):
    """Base schema for product batch."""

    batch_code: Optional[str] = Field(None, max_length=50, description="Mã lô hàng")
    stock_quantity: int = Field(..., ge=0, description="Số lượng tồn kho của lô")
    expiry_date: date = Field(..., description="Ngày hết hạn sử dụng")
    discount_rate: int = Field(
        default=0, ge=0, le=100, description="Tỷ lệ giảm giá (%) do AI hoặc rule đề xuất"
    )
    status: str = Field(
        default="active", description="Trạng thái: active, sold_out, expired"
    )


class BatchCreate(BatchBase):
    """Schema for creating a batch."""

    product_id: int = Field(..., description="ID sản phẩm tương ứng")


class BatchUpdate(BaseModel):
    """Schema for updating batch attributes."""

    batch_code: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    discount_rate: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = None


class BatchDiscountUpdate(BaseModel):
    """Schema specifically for applying AI or manual discount rate."""

    discount_rate: int = Field(..., ge=0, le=100, description="Tỷ lệ giảm giá mới (%)")


class BatchOut(BatchBase):
    """Schema for returning batch details."""

    id: int
    product_id: int
    days_until_expiry: int
    effective_unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class BatchExpiringOut(BatchOut):
    """Detailed schema for expiring batches with product metadata."""

    product_name: str
    product_sku: Optional[str] = None
    original_price: Decimal
    store_name: Optional[str] = None
