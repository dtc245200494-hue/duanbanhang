from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PurchaseReceipt(Base):
    __tablename__ = "purchase_receipts"

    id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    import_price = Column(Float, nullable=False, default=0)
    supplier = Column(String(200), default="")
    note = Column(String(500), default="")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    received_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    product = relationship("Product")
