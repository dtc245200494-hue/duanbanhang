"""Product batch model module for near-expiry and FEFO inventory tracking."""

from datetime import date
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class ProductBatch(Base):
    """Product batch entity representing individual inventory batches with expiry dates."""

    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_code = Column(String(50), nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=False, index=True)
    discount_rate = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="active", nullable=False, index=True)

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="check_stock_quantity_non_negative"),
    )

    # Relationships
    product = relationship("Product", back_populates="batches")
    order_items = relationship("OrderItem", back_populates="batch")
    recommendations = relationship(
        "AIDiscountRecommendation",
        back_populates="batch",
        cascade="all, delete-orphan",
    )

    @property
    def days_until_expiry(self) -> int:
        """Calculate number of days remaining until expiry."""
        today = date.today()
        return (self.expiry_date - today).days

    @property
    def effective_unit_price(self) -> Decimal:
        """Calculate effective unit price based on original product price and discount rate."""
        if not self.product:
            return Decimal("0.00")
        original = Decimal(str(self.product.original_price))
        rate = Decimal(str(self.discount_rate or 0)) / Decimal("100")
        discounted = original * (Decimal("1.00") - rate)
        return round(discounted, 2)
