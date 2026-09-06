from typing import Optional

from pydantic import BaseModel, Field


class PurchaseReceiptIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    import_price: float = Field(ge=0)
    supplier: str = ""
    note: str = ""


class PurchaseReceiptOut(BaseModel):
    id: int
    code: str
    product_id: int
    product_name: str
    quantity: int
    import_price: float
    total_amount: float
    supplier: str
    note: str = ""
    received_at: str
