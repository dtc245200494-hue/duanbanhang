"""Product Pydantic v2 schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base schema for product data."""

    name: str = Field(..., max_length=200, description="Tên sản phẩm")
    sku: Optional[str] = Field(None, max_length=50, description="Mã SKU")
    original_price: Decimal = Field(..., gt=0, description="Giá niêm yết gốc")
    image_url: Optional[str] = Field(None, description="URL ảnh sản phẩm")
    category_id: Optional[int] = Field(None, description="ID danh mục sản phẩm")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    store_id: int = Field(..., description="ID của cửa hàng sở hữu")


class ProductUpdate(BaseModel):
    """Schema for updating product info."""

    name: Optional[str] = Field(None, max_length=200)
    sku: Optional[str] = Field(None, max_length=50)
    original_price: Optional[Decimal] = Field(None, gt=0)
    image_url: Optional[str] = None
    category_id: Optional[int] = None


class ProductOut(ProductBase):
    """Schema for returning product details."""

    id: int
    store_id: int
    category_name: Optional[str] = None
    created_at: datetime
    total_stock: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
