"""Payment transaction model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Payment(Base):
    """Payment transaction entity for customer orders."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_method = Column(
        String(50),
        nullable=False,
        default="COD",
    )  # COD, bank_transfer, momo, vnpay, card
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(
        String(30),
        default="pending",
        nullable=False,
        index=True,
    )  # pending, paid, failed
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payments")
