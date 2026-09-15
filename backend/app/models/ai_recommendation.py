"""AI Discount Recommendation audit and approval workflow model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class AIDiscountRecommendation(Base):
    """Stores AI-generated dynamic clearance proposals and manager approvals."""

    __tablename__ = "ai_discount_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(
        Integer,
        ForeignKey("product_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recommended_discount = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )  # pending, approved, rejected
    approved_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    batch = relationship("ProductBatch", back_populates="recommendations")
    approver = relationship("User", back_populates="approved_recommendations")
