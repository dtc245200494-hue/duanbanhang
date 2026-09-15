"""Unit tests for SQLAlchemy models and business properties."""

from datetime import date, timedelta
from decimal import Decimal
import pytest
from app.models.store import Store
from app.models.product import Product
from app.models.batch import ProductBatch


def test_product_batch_properties(db_session):
    """Test days_until_expiry and effective_unit_price calculations."""
    prod = db_session.query(Product).first()
    assert prod is not None

    today = date.today()
    batch = ProductBatch(
        product_id=prod.id,
        batch_code="PROP-TEST",
        stock_quantity=5,
        expiry_date=today + timedelta(days=5),
        discount_rate=20,  # 20% off 30,000 = 24,000
    )
    db_session.add(batch)
    db_session.commit()

    assert batch.days_until_expiry == 5
    assert batch.effective_unit_price == Decimal("24000.00")


def test_cascade_delete_store(db_session):
    """Test that deleting a store cascades to its products and batches."""
    store = db_session.query(Store).first()
    assert store is not None

    db_session.delete(store)
    db_session.commit()

    # Verify products and batches are deleted
    assert db_session.query(Product).count() == 0
    assert db_session.query(ProductBatch).count() == 0
