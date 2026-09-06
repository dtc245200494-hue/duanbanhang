from typing import List, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    code: str
    name: str
    category_id: Optional[int] = None
    import_price: float = Field(default=0, ge=0)
    sell_price: float = Field(default=0, ge=0)
    stock: int = Field(default=0, ge=0)
    status: str = "active"
    description: str = ""


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    import_price: Optional[float] = None
    sell_price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    description: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    category_name: Optional[str] = None

    model_config = {"from_attributes": True}
