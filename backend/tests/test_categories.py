"""Unit tests for product categories."""

from app.models.category import Category
from app.models.product import Product


def test_category_creation_and_product_relation(db_session):
    """Test creating category and linking products."""
    cat = Category(name="Đồ uống đóng chai", description="Nước giải khát, nước ép")
    db_session.add(cat)
    db_session.commit()

    prod = db_session.query(Product).first()
    prod.category_id = cat.id
    db_session.commit()

    db_session.refresh(cat)
    assert len(cat.products) == 1
    assert cat.products[0].name == prod.name
