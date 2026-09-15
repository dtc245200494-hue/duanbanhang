"""Payment Pydantic v2 schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    """Base schema for payments."""

    order_id: int
    payment_method: str = Field("COD", description="COD, bank_transfer, momo, vnpay, card")
    amount: Decimal = Field(..., gt=0)


class PaymentCreate(PaymentBase):
    """Schema for creating a payment record."""

    pass


class PaymentUpdateStatus(BaseModel):
    """Schema for updating payment status."""

    status: str = Field(..., pattern="^(pending|paid|failed)$")


class PaymentOut(PaymentBase):
    """Schema for returning payment details."""

    id: int
    status: str
    paid_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
