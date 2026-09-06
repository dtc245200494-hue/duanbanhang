from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    import_price = Column(Float, nullable=False, default=0)
    sell_price = Column(Float, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active", index=True)
    description = Column(Text, default="")

    category = relationship("Category", backref="products")

    @property
    def category_name(self):
        return self.category.name if self.category else None
