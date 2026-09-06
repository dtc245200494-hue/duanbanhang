import pytest


@pytest.fixture(scope="module")
def inv_product(client, admin_hdr):
    res = client.post(
        "/api/products",
        json={"code": "INV-T1", "name": "Sản phẩm tồn kho test", "sell_price": 100000, "stock": 8},
        headers=admin_hdr,
    )
    assert res.status_code == 201
    return res.json()


class TestInventory:
    def test_purchase_receipt_increases_stock(self, client, owner_hdr, inv_product):
        res = client.post(
            "/api/purchases",
            json={"product_id": inv_product["id"], "quantity": 5, "import_price": 60000, "supplier": "NCC A"},
            headers=owner_hdr,
        )
        assert res.status_code == 201, res.text
        receipt = res.json()
        assert receipt["total_amount"] == 300000
        assert receipt["code"].startswith("PR-")

        stock = client.get(f"/api/products/{inv_product['id']}", headers=owner_hdr).json()["stock"]
        assert stock == 13

    def test_inventory_endpoint_reflects(self, client, owner_hdr, inv_product):
        res = client.get("/api/inventory?keyword=INV-T1", headers=owner_hdr)
        assert res.status_code == 200
        rows = res.json()
        assert len(rows) == 1
        assert rows[0]["quantity"] == 13

    def test_delete_receipt_reverts_stock(self, client, admin_hdr, owner_hdr, inv_product):
        receipts = client.get(
            f"/api/purchases?product_id={inv_product['id']}", headers=admin_hdr
        ).json()
        target = receipts[0]
        res = client.delete(f"/api/purchases/{target['id']}", headers=admin_hdr)
        assert res.status_code == 200
        stock = client.get(f"/api/products/{inv_product['id']}", headers=owner_hdr).json()["stock"]
        assert stock == 8

    def test_low_stock_appears_in_inventory(self, client, admin_hdr, inv_product):
        client.put(f"/api/products/{inv_product['id']}", json={"stock": 4}, headers=admin_hdr)
        res = client.get("/api/inventory", headers=admin_hdr)
        rows = {r["code"]: r for r in res.json()}
        assert rows["INV-T1"]["low"] is True

    def test_anonymous_cannot_create_receipt(self, client):
        res = client.post(
            "/api/purchases",
            json={"product_id": 1, "quantity": 1, "import_price": 1000},
        )
        assert res.status_code == 401
