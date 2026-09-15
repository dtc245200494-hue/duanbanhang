"""Product model module."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Product(Base):
    """Product metadata entity."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(50), nullable=True, index=True)
    original_price = Column(Numeric(12, 2), nullable=False)
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    store = relationship("Store", back_populates="products")
    category = relationship("Category", back_populates="products")
    batches = relationship(
        "ProductBatch", back_populates="product", cascade="all, delete-orphan"
    )
