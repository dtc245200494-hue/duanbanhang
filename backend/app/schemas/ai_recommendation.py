"""AI Discount Recommendation Pydantic v2 schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AIRecommendationBase(BaseModel):
    """Base schema for AI dynamic clearance proposal."""

    batch_id: int = Field(..., description="ID của lô hàng")
    recommended_discount: int = Field(..., ge=0, le=100, description="Mức chiết khấu AI đề xuất (%)")
    reason: str = Field(..., description="Lý do gợi ý từ AI")


class AIRecommendationCreate(AIRecommendationBase):
    """Schema for persisting an AI recommendation."""

    pass


class AIRecommendationApproval(BaseModel):
    """Schema for approving or rejecting an AI proposal."""

    action: str = Field(..., pattern="^(approve|reject)$", description="'approve' hoặc 'reject'")


class AIRecommendationOut(AIRecommendationBase):
    """Schema for returning recommendation details with audit information."""

    id: int
    status: str
    approved_by: Optional[int] = None
    approver_name: Optional[str] = None
    created_at: datetime
    batch_code: Optional[str] = None
    product_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
