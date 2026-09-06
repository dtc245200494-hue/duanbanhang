import app.services.ai_service as ai_service


def _capture_generate(monkeypatch, reply="Đây là gợi ý từ AI (giả lập cho test)."):
    calls = {}

    def fake_generate(prompt: str) -> str:
        calls["prompt"] = prompt
        return reply

    monkeypatch.setattr(ai_service, "generate", fake_generate)
    return calls


class TestAIConsultant:
    def test_only_suggests_in_stock_products(self, client, admin_hdr, owner_hdr, monkeypatch, accessory_category_id):
        client.post(
            "/api/products",
            json={"code": "AI-IN", "name": "Tai nghe AI Còn Hàng", "sell_price": 350000,
                  "stock": 5, "status": "active", "category_id": accessory_category_id},
            headers=admin_hdr,
        )
        client.post(
            "/api/products",
            json={"code": "AI-OUT", "name": "Tai nghe AI Het Hang XYZ", "sell_price": 400000,
                  "stock": 0, "status": "active", "category_id": accessory_category_id},
            headers=admin_hdr,
        )
        calls = _capture_generate(monkeypatch)
        res = client.post(
            "/api/ai/consult",
            json={"customer_request": "Khách cần tai nghe dưới 500k, pin lâu"},
            headers=owner_hdr,
        )
        assert res.status_code == 200, res.text
        assert res.json()["answer"]
        prompt = calls["prompt"]
        assert "Tai nghe AI Còn Hàng" in prompt
        assert "Tai nghe AI Het Hang XYZ" not in prompt

    def test_phone_number_is_masked(self, client, owner_hdr, monkeypatch):
        calls = _capture_generate(monkeypatch)
        client.post(
            "/api/ai/consult",
            json={"customer_request": "Gọi lại cho tôi theo số 0912345678 nhé"},
            headers=owner_hdr,
        )
        assert "0912345678" not in calls["prompt"]

    def test_missing_api_key_returns_503(self, client, owner_hdr, monkeypatch):
        monkeypatch.setattr(ai_service, "OPENAI_API_KEY", "")
        res = client.post(
            "/api/ai/consult",
            json={"customer_request": "test"},
            headers=owner_hdr,
        )
        assert res.status_code == 503
        assert ".env" in res.json()["detail"]


class TestAIReportAndQA:
    def test_report_prompt_contains_sales_data(self, client, owner_hdr, monkeypatch):
        calls = _capture_generate(monkeypatch, reply="# Báo cáo doanh thu\\nNhận xét...")
        res = client.post("/api/ai/report", json={}, headers=owner_hdr)
        assert res.status_code == 200
        assert "Tổng doanh thu" in calls["prompt"]

    def test_qa_answers_based_on_data(self, client, owner_hdr, monkeypatch):
        calls = _capture_generate(monkeypatch, reply="Mặt hàng bán chậm là...")
        res = client.post(
            "/api/ai/qa",
            json={"question": "Tháng này mặt hàng nào bán chậm?"},
            headers=owner_hdr,
        )
        assert res.status_code == 200
        prompt = calls["prompt"]
        assert "Tháng này mặt hàng nào bán chậm?" in prompt
        assert "Sản phẩm bán chậm" in prompt

    def test_mask_sensitive_helper(self):
        masked = ai_service.mask_sensitive("SĐT 0912345678 và mail abc@xyz.com")
        assert "0912345678" not in masked
        assert "abc@xyz.com" not in masked

    def test_rate_limit_returns_429(self, client, owner_hdr, monkeypatch):
        monkeypatch.setattr(ai_service, "AI_MAX_CALLS_PER_MINUTE", 0)
        ai_service._call_times.clear()
        res = client.post(
            "/api/ai/qa",
            json={"question": "test rate limit"},
            headers=owner_hdr,
        )
        assert res.status_code == 429
