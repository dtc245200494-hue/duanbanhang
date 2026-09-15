"""Role model module for RBAC (Role-Based Access Control)."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Role(Base):
    """Role entity representing user authorization levels."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # admin, store_manager, customer
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", back_populates="role")
