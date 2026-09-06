from datetime import datetime

import pytest

TODAY = datetime.now().strftime("%Y-%m-%d")


@pytest.fixture(scope="module")
def report_product(client, admin_hdr, accessory_category_id):
    res = client.post(
        "/api/products",
        json={
            "code": "RPT-P",
            "name": "Tai nghe Report Test",
            "category_id": accessory_category_id,
            "sell_price": 100000,
            "stock": 100,
            "status": "active",
        },
        headers=admin_hdr,
    )
    assert res.status_code == 201
    return res.json()


@pytest.fixture(scope="module")
def two_orders_today(client, owner_hdr, report_product):
    pid = report_product["id"]
    r1 = client.post(
        "/api/orders",
        json={"items": [{"product_id": pid, "quantity": 3}], "discount": 0, "payment_method": "cash"},
        headers=owner_hdr,
    )
    r2 = client.post(
        "/api/orders",
        json={"items": [{"product_id": pid, "quantity": 2}], "discount": 50000, "payment_method": "banking"},
        headers=owner_hdr,
    )
    assert r1.status_code == 201 and r2.status_code == 201, (r1.text, r2.text)
    return [r1.json(), r2.json()]


class TestRevenueReports:
    def test_revenue_by_day(self, client, owner_hdr, two_orders_today):
        res = client.get(
            f"/api/reports/revenue?group_by=day&date_from={TODAY}&date_to={TODAY}",
            headers=owner_hdr,
        )
        assert res.status_code == 200
        rows = [r for r in res.json() if r["label"] == TODAY]
        assert rows, "Phải có dòng doanh thu cho hôm nay"
        row = rows[0]
        assert row["revenue"] >= 250000
        assert row["orders"] >= 2

    def test_revenue_by_month(self, client, owner_hdr, two_orders_today):
        month = TODAY[:7]
        res = client.get(f"/api/reports/revenue?group_by=month&date_from={month}-01", headers=owner_hdr)
        assert res.status_code == 200
        labels = [r["label"] for r in res.json()]
        assert month in labels

    def test_top_products(self, client, owner_hdr, two_orders_today, report_product):
        res = client.get("/api/reports/top-products?limit=5", headers=owner_hdr)
        assert res.status_code == 200
        top = res.json()
        assert top[0]["code"] == report_product["code"]
        assert top[0]["quantity"] == 5

    def test_slow_products_include_zero_sales(self, client, owner_hdr):
        res = client.get("/api/reports/slow-products?limit=50", headers=owner_hdr)
        assert res.status_code == 200
        zeros = [r for r in res.json() if r["quantity"] == 0]
        assert zeros

    def test_revenue_by_category(self, client, owner_hdr, two_orders_today):
        res = client.get("/api/reports/by-category", headers=owner_hdr)
        assert res.status_code == 200
        cats = {c["category"]: c for c in res.json()}
        assert "Phụ kiện" in cats
        assert cats["Phụ kiện"]["revenue"] >= 250000


class TestExports:
    def test_export_csv_sales(self, client, owner_hdr):
        res = client.get(
            f"/api/reports/export?type=sales&format=csv&date_from={TODAY}&date_to={TODAY}",
            headers=owner_hdr,
        )
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/csv")
        body = res.content.decode("utf-8-sig")
        assert "Thời gian" in body

    def test_export_excel_orders(self, client, owner_hdr):
        res = client.get(
            f"/api/reports/export?type=orders&format=excel&date_from={TODAY}&date_to={TODAY}",
            headers=owner_hdr,
        )
        assert res.status_code == 200
        assert "spreadsheetml" in res.headers["content-type"]
        assert len(res.content) > 100

    def test_export_pdf_inventory(self, client, owner_hdr):
        res = client.get("/api/reports/export?type=inventory&format=pdf", headers=owner_hdr)
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"
        assert res.content[:4] == b"%PDF"

    def test_export_invalid_format_422(self, client, owner_hdr):
        res = client.get("/api/reports/export?type=sales&format=json", headers=owner_hdr)
        assert res.status_code == 422


class TestDashboard:
    def test_dashboard_totals(self, client, owner_hdr, two_orders_today):
        res = client.get("/api/dashboard", headers=owner_hdr)
        assert res.status_code == 200
        data = res.json()
        assert data["total_revenue"] > 0
        assert data["total_orders"] >= 2
        assert data["total_products"] >= 10
        assert isinstance(data["top_products"], list)
        assert isinstance(data["low_stock_products"], list)

    def test_dashboard_requires_auth(self, client):
        assert client.get("/api/dashboard").status_code == 401
