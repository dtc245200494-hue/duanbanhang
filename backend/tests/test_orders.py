import pytest


@pytest.fixture(scope="module")
def order_product(client, admin_hdr, accessory_category_id):
    res = client.post(
        "/api/products",
        json={
            "code": "ORD-T1",
            "name": "Tai nghe Order Test",
            "category_id": accessory_category_id,
            "sell_price": 350000,
            "stock": 10,
            "status": "active",
        },
        headers=admin_hdr,
    )
    assert res.status_code == 201, res.text
    return res.json()


def _create_order(client, hdr, product_id, quantity, discount=0, customer_id=None):
    payload = {
        "items": [{"product_id": product_id, "quantity": quantity}],
        "discount": discount,
        "payment_method": "cash",
    }
    if customer_id:
        payload["customer_id"] = customer_id
    return client.post("/api/orders", json=payload, headers=hdr)


class TestOrders:
    def test_create_order_success_math_and_stock(self, client, owner_hdr, order_product):
        res = _create_order(client, owner_hdr, order_product["id"], 2, discount=50000)
        assert res.status_code == 201, res.text
        order = res.json()
        assert order["total_amount"] == 700000
        assert order["discount"] == 50000
        assert order["final_amount"] == 650000
        detail = client.get(f"/api/products/{order_product['id']}", headers=owner_hdr).json()
        assert detail["stock"] == 8

    def test_cancel_restores_stock(self, client, owner_hdr, order_product):
        res = _create_order(client, owner_hdr, order_product["id"], 1)
        assert res.status_code == 201
        oid = res.json()["id"]
        cancel = client.post(f"/api/orders/{oid}/cancel", headers=owner_hdr)
        assert cancel.status_code == 200
        assert cancel.json()["status"] == "cancelled"
        stock = client.get(f"/api/products/{order_product['id']}", headers=owner_hdr).json()["stock"]
        assert stock == 8

    def test_cancel_twice_rejected(self, client, owner_hdr, order_product):
        res = _create_order(client, owner_hdr, order_product["id"], 1)
        oid = res.json()["id"]
        client.post(f"/api/orders/{oid}/cancel", headers=owner_hdr)
        again = client.post(f"/api/orders/{oid}/cancel", headers=owner_hdr)
        assert again.status_code == 400

    def test_insufficient_stock_rejected(self, client, owner_hdr, order_product):
        res = _create_order(client, owner_hdr, order_product["id"], 999)
        assert res.status_code == 400
        assert "không đủ tồn kho" in res.json()["detail"]

    def test_inactive_product_rejected(self, client, admin_hdr, owner_hdr):
        p = client.post(
            "/api/products",
            json={"code": "ORD-T2", "name": "SP ngừng KD", "sell_price": 100000, "stock": 5, "status": "inactive"},
            headers=admin_hdr,
        ).json()
        res = _create_order(client, owner_hdr, p["id"], 1)
        assert res.status_code == 400

    def test_discount_cannot_exceed_total(self, client, owner_hdr, order_product):
        res = _create_order(client, owner_hdr, order_product["id"], 1, discount=99999999)
        assert res.status_code == 201
        assert res.json()["final_amount"] >= 0

    def test_list_orders_filter_status(self, client, owner_hdr):
        res = client.get("/api/orders?status=cancelled", headers=owner_hdr)
        assert res.status_code == 200
        statuses = {o["status"] for o in res.json()}
        assert statuses == {"cancelled"}

    def test_empty_items_rejected(self, client, owner_hdr):
        res = client.post("/api/orders", json={"items": []}, headers=owner_hdr)
        assert res.status_code == 422

    def test_duplicate_items_stock_check(self, client, owner_hdr, order_product):
        # order_product stock is 8 now (10 initial - 2 in first test)
        # Requesting 2 lines of 5 each (total 10 > 8) should be rejected
        payload = {
            "items": [
                {"product_id": order_product["id"], "quantity": 5},
                {"product_id": order_product["id"], "quantity": 5},
            ],
            "payment_method": "cash",
        }
        res = client.post("/api/orders", json=payload, headers=owner_hdr)
        assert res.status_code == 400
        assert "không đủ tồn kho" in res.json()["detail"]
