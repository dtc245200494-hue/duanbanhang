from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, index=True)
    phone = Column(String(20), default="", index=True)
    email = Column(String(150), default="")
    address = Column(String(255), default="")
    customer_group = Column(String(20), nullable=False, default="normal", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
