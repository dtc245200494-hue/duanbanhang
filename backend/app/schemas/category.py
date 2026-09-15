"""Product Category Pydantic v2 schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base schema for merchandise categories."""

    name: str = Field(..., max_length=100, description="Tên danh mục (Đồ tươi sống, Sữa...)")
    description: Optional[str] = Field(None, description="Mô tả danh mục")


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class CategoryOut(CategoryBase):
    """Schema for returning category details."""

    id: int
    product_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
