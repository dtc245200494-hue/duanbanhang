"""Store Pydantic v2 schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class StoreBase(BaseModel):
    """Base schema for store data."""

    name: str = Field(..., max_length=150, description="Tên cửa hàng / chi nhánh")
    phone: str = Field(..., max_length=20, description="Số điện thoại liên hệ")
    address: str = Field(..., description="Địa chỉ cửa hàng")
    owner_id: Optional[int] = Field(None, description="ID chủ sở hữu / quản lý")


class StoreCreate(StoreBase):
    """Schema for creating a new store."""

    pass


class StoreUpdate(BaseModel):
    """Schema for updating store info."""

    name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    owner_id: Optional[int] = None


class StoreOut(StoreBase):
    """Schema for returning store details."""

    id: int
    owner_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
