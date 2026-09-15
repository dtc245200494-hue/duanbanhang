"""Order and OrderItem models module."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Order(Base):
    """Order entity containing customer, user and delivery information."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    shipping_address = Column(Text, nullable=False)
    note = Column(Text, nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(
        String(30),
        default="pending",
        nullable=False,
        index=True,
    )  # pending, confirmed, shipping, completed, cancelled
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    store = relationship("Store", back_populates="orders")
    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """Order line item representing ordered quantity from a specific batch."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id = Column(
        Integer,
        ForeignKey("product_batches.id"),
        nullable=True,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_item_quantity_positive"),
    )

    # Relationships
    order = relationship("Order", back_populates="items")
    batch = relationship("ProductBatch", back_populates="order_items")
