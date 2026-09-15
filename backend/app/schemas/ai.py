"""AI Discount Recommendation Pydantic schemas."""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class AIDiscountRequest(BaseModel):
    """Input parameters for AI discount evaluation."""

    batch_id: int = Field(..., description="ID lô hàng cần đánh giá")
    average_daily_sales: Optional[float] = Field(
        None, ge=0, description="Tốc độ bán trung bình (sản phẩm/ngày)"
    )
    competitor_price: Optional[Decimal] = Field(
        None, gt=0, description="Giá thị trường/đối thủ cạnh tranh nếu có"
    )
    custom_instruction: Optional[str] = Field(
        None, description="Yêu cầu đặc biệt cho AI (ví dụ: cần đẩy nhanh trong 2 ngày)"
    )


class AIDiscountResponse(BaseModel):
    """Output results of AI discount proposal."""

    batch_id: int
    batch_code: Optional[str]
    product_name: str
    original_price: Decimal
    days_until_expiry: int
    stock_quantity: int
    suggested_discount_rate: int = Field(
        ..., ge=0, le=100, description="Tỷ lệ giảm giá đề xuất (%)"
    )
    suggested_price: Decimal = Field(
        ..., description="Đơn giá đề xuất sau khi áp dụng giảm giá"
    )
    urgency_level: str = Field(
        ..., description="Mức độ khẩn cấp: critical (<3 ngày), high (<7 ngày), moderate, low"
    )
    reasoning: str = Field(
        ..., description="Giải thích lý do đề xuất chiết khấu cho chủ cửa hàng"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Độ tin cậy của thuật toán đề xuất"
    )
    engine_used: str = Field(
        ..., description="Tên engine xử lý: 'openai_gpt' hoặc 'rule_based_fallback'"
    )
    prompt_version: str = Field(..., description="Phiên bản prompt được áp dụng")
