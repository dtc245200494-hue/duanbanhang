"""Store model module."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Store(Base):
    """Store entity representing retail branches."""

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_stores")
    products = relationship(
        "Product", back_populates="store", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="store")
