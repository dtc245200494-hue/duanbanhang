class TestProductCRUD:
    def test_create_product(self, client, admin_hdr, accessory_category_id):
        res = client.post(
            "/api/products",
            json={
                "code": "TST-100",
                "name": "Tai nghe Test X",
                "category_id": accessory_category_id,
                "import_price": 220000,
                "sell_price": 350000,
                "stock": 10,
                "status": "active",
                "description": "Pin 20 giờ",
            },
            headers=admin_hdr,
        )
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["code"] == "TST-100"
        assert data["category_name"] == "Phụ kiện"
        assert data["stock"] == 10

    def test_duplicate_code_rejected(self, client, admin_hdr):
        res = client.post(
            "/api/products",
            json={"code": "TST-100", "name": "Trùng mã"},
            headers=admin_hdr,
        )
        assert res.status_code == 400

    def test_search_by_keyword(self, client, owner_hdr):
        res = client.get("/api/products?keyword=TST-100", headers=owner_hdr)
        assert res.status_code == 200
        codes = [p["code"] for p in res.json()]
        assert "TST-100" in codes

    def test_update_product(self, client, admin_hdr):
        products = client.get("/api/products?keyword=TST-100", headers=admin_hdr).json()
        pid = products[0]["id"]
        res = client.put(f"/api/products/{pid}", json={"sell_price": 360000}, headers=admin_hdr)
        assert res.status_code == 200
        assert res.json()["sell_price"] == 360000

    def test_unauthenticated_cannot_delete(self, client, admin_hdr):
        products = client.get("/api/products?keyword=TST-100", headers=admin_hdr).json()
        res = client.delete(f"/api/products/{products[0]['id']}")
        assert res.status_code == 401

    def test_low_stock_filter(self, client, admin_hdr):
        client.post(
            "/api/products",
            json={"code": "TST-101", "name": "SP sắp hết", "stock": 3, "sell_price": 50000},
            headers=admin_hdr,
        )
        res = client.get("/api/products?low_stock=true&status=active", headers=admin_hdr)
        codes = [p["code"] for p in res.json()]
        assert "TST-101" in codes

    def test_delete_unused_product(self, client, admin_hdr):
        created = client.post(
            "/api/products",
            json={"code": "TST-102", "name": "SP xóa được"},
            headers=admin_hdr,
        ).json()
        res = client.delete(f"/api/products/{created['id']}", headers=admin_hdr)
        assert res.status_code == 200
        res = client.get(f"/api/products/{created['id']}", headers=admin_hdr)
        assert res.status_code == 404
