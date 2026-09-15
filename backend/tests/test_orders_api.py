"""Integration tests for Orders and Batches API endpoints."""

from app.models.batch import ProductBatch
from app.models.product import Product


def test_list_expiring_batches_endpoint(client):
    """Test GET /api/v1/batches/expiring returns near-expiry batches."""
    response = client.get("/api/v1/batches/expiring?days=15")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["batch_code"] == "B1"
    assert data[0]["days_until_expiry"] == 2


def test_create_order_with_fefo_endpoint(client, db_session):
    """Test POST /api/v1/orders automatically allocates from earliest expiring batch."""
    prod = db_session.query(Product).first()

    payload = {
        "customer_name": "Test Customer",
        "customer_phone": "0911223344",
        "shipping_address": "123 Test Street, Hanoi",
        "items": [
            {
                "product_id": prod.id,
                "quantity": 5,
            }
        ],
    }

    response = client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Test Customer"
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    # Check that price is discounted 50% from B1: 30000 * 0.5 = 15000
    assert float(data["items"][0]["unit_price"]) == 15000.0
    assert float(data["total_amount"]) == 75000.0


def test_cancel_order_restores_stock(client, db_session):
    """Test cancelling an order restores inventory back to batch."""
    b1 = db_session.query(ProductBatch).filter(ProductBatch.batch_code == "B1").first()
    initial_stock = b1.stock_quantity

    payload = {
        "customer_name": "Restock Test",
        "customer_phone": "0999888777",
        "shipping_address": "456 Test Street",
        "items": [{"batch_id": b1.id, "quantity": 4}],
    }
    create_res = client.post("/api/v1/orders", json=payload)
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    db_session.refresh(b1)
    assert b1.stock_quantity == initial_stock - 4

    # Cancel order
    patch_res = client.patch(
        f"/api/v1/orders/{order_id}/status", json={"status": "cancelled"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "cancelled"

    db_session.refresh(b1)
    assert b1.stock_quantity == initial_stock
