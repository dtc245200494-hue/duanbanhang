"""User model module representing system accounts with authentication credentials."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User account entity."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="users")
    owned_stores = relationship("Store", back_populates="owner")
    orders = relationship("Order", back_populates="user")
    approved_recommendations = relationship("AIDiscountRecommendation", back_populates="approver")
