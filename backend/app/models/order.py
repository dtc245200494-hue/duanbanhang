from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_amount = Column(Float, nullable=False, default=0)
    discount = Column(Float, nullable=False, default=0)
    final_amount = Column(Float, nullable=False, default=0)
    payment_method = Column(String(20), nullable=False, default="cash")
    status = Column(String(20), nullable=False, default="completed", index=True)
    note = Column(String(500), default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    customer = relationship("Customer")
    user = relationship("User")
    details = relationship("OrderDetail", backref="order", cascade="all, delete-orphan")
