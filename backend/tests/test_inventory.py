"""Unit tests for InventoryService and FEFO allocation."""

import pytest
from app.models.product import Product
from app.models.batch import ProductBatch
from app.services.inventory_service import InventoryService


def test_fefo_allocation_single_batch(db_session):
    """Test FEFO takes from the earliest expiry batch first."""
    prod = db_session.query(Product).first()

    # We need 6 items. Batch 1 has 10 (expires in 2 days).
    allocations = InventoryService.allocate_fefo_stock(
        db=db_session, product_id=prod.id, quantity_needed=6
    )

    assert len(allocations) == 1
    batch, qty = allocations[0]
    assert batch.batch_code == "B1"
    assert qty == 6
    assert batch.stock_quantity == 4
    assert batch.status == "active"


def test_fefo_allocation_split_batches(db_session):
    """Test FEFO splits across multiple batches when earliest batch is exhausted."""
    prod = db_session.query(Product).first()

    # We need 15 items. B1 has 10, B2 has 20. Total needed 15 -> 10 from B1, 5 from B2.
    allocations = InventoryService.allocate_fefo_stock(
        db=db_session, product_id=prod.id, quantity_needed=15
    )

    assert len(allocations) == 2
    b1, qty1 = allocations[0]
    b2, qty2 = allocations[1]

    assert b1.batch_code == "B1"
    assert qty1 == 10
    assert b1.stock_quantity == 0
    assert b1.status == "sold_out"

    assert b2.batch_code == "B2"
    assert qty2 == 5
    assert b2.stock_quantity == 15
    assert b2.status == "active"


def test_fefo_allocation_insufficient_stock(db_session):
    """Test that requesting more than total stock raises ValueError."""
    prod = db_session.query(Product).first()

    with pytest.raises(ValueError) as exc_info:
        InventoryService.allocate_fefo_stock(
            db=db_session, product_id=prod.id, quantity_needed=50
        )
    assert "không đủ tồn kho" in str(exc_info.value)
