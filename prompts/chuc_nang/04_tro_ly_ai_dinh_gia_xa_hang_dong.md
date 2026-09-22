# 🤖 BỘ PROMPT: TRỢ LÝ AI ĐỊNH GIÁ XẢ HÀNG ĐỘNG (DYNAMIC CLEARANCE PRICING ENGINE)

> **Chức năng:** Sử dụng Trí tuệ nhân tạo (OpenAI GPT-4o-mini & Rule-Based Fallback Engine) để phân tích ngữ cảnh kinh doanh, tốc độ bán hàng, giá đối thủ cạnh tranh và hạn dùng còn lại nhằm đề xuất tỷ lệ chiết khấu xả hàng FEFO tối ưu.  
> **Tác nhân:** Quản lý cửa hàng (Store Manager), Quản trị viên (Admin).  
> **Bảng CSDL liên quan:** `product_batches`, `products`, `ai_discount_recommendations`.

---

## 📌 1. Prompt Kỹ Nghệ Prompt Template AI (Prompt Engineering)

### 🎯 Mục tiêu:
Xây dựng prompt template phiên bản hóa (`prompts/versions/v1_discount_recommendation.txt`) có cấu trúc rõ ràng, ép kiểu JSON output nghiêm ngặt để tích hợp trực tiếp vào code backend mà không bị lỗi parse.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Trí tuệ Nhân tạo (AI Prompt Engineer). Hãy viết một Prompt Template chuẩn hóa để tích hợp LLM vào nghiệp vụ Định giá Xả hàng Động (Dynamic Clearance Pricing) cho chuỗi bán lẻ FreshMart:

Yêu cầu về Prompt Template:
1. Định nghĩa Vai trò (Persona):
   - Bạn là Giám đốc Định giá Bán lẻ & Tối ưu Lợi nhuận (Senior Retail Pricing Analyst).
2. Dữ liệu đầu vào (Placeholders):
   - `{product_name}`: Tên sản phẩm.
   - `{original_price}`: Giá niêm yết gốc.
   - `{stock_quantity}`: Số lượng tồn kho của lô hàng.
   - `{days_until_expiry}`: Số ngày còn lại trước khi hết hạn sử dụng.
   - `{average_daily_sales}`: Tốc độ tiêu thụ trung bình (sp/ngày).
   - `{competitor_price}`: Giá bán tham khảo của đối thủ (nếu có).
   - `{custom_instruction}`: Chỉ đạo chiến lược riêng từ Quản lý (ví dụ: "cần giải phóng kho trong 48 giờ").
3. Bộ quy tắc suy luận (Pricing Rules):
   - ≤ 0 ngày: Hết hạn -> Chiết khấu 100% (Thu hồi / Hủy bỏ).
   - 1 - 2 ngày: Cận date khẩn cấp -> Chiết khấu 50% - 70% để xả hàng cấp tốc.
   - 3 - 5 ngày: Tồn kho nguy cơ -> Chiết khấu 30% - 45% kích cầu tiêu dùng nhanh.
   - 6 - 10 ngày: Cảnh báo sớm -> Chiết khấu 15% - 25%.
   - > 14 ngày: Tồn kho an toàn -> Giữ giá niêm yết (0% chiết khấu).
4. Định dạng đầu ra JSON bắt buộc (Không thêm markdown ```json hay văn bản giải thích thừa):
   {
     "suggested_discount_rate": <int từ 0 đến 100>,
     "suggested_price": <float>,
     "urgency_level": "<critical|high|medium|low>",
     "confidence_score": <float từ 0.0 đến 1.0>,
     "reasoning": "<Giải thích ngắn gọn 1-2 câu bằng tiếng Việt về lý do đưa ra mức giá này>"
   }
```

---

## 📌 2. Prompt Xây Dựng Động Cơ Định Giá AI Kèm Fallback Engine (100% Uptime)

### 🎯 Mục tiêu:
Viết dịch vụ `AIDiscountService` có khả năng gọi OpenAI API với cơ chế phòng vệ (Timeout, Rate Limit) và có **Rule-Based Fallback Engine** tự động kích hoạt khi mất mạng hoặc không có API Key, đảm bảo hệ thống bán lẻ hoạt động ổn định 24/7.

### 💬 Prompt gửi AI:
```text
Hãy viết lớp `AIDiscountService` tại `backend/app/services/ai_discount_service.py` bằng Python:

1. Cơ chế hoạt động:
   - Phương thức `evaluate_discount(batch: ProductBatch, average_daily_sales: float, competitor_price: Optional[float], custom_instruction: Optional[str], prompt_version: str = "v1") -> dict`:
     + Bước 1: Kiểm tra cấu hình `settings.OPENAI_API_KEY`.
     + Bước 2: Nếu có API Key, nạp template tương ứng từ thư mục `prompts/versions/{prompt_version}_discount_recommendation.txt`, điền dữ liệu và gửi request đến OpenAI API model `gpt-4o-mini` với `timeout = 3.0s`.
     + Bước 3: Nếu gọi OpenAI thành công, parse JSON kết quả và gắn nhãn `engine_used = "openai_gpt"`.
     + Bước 4: Nếu không có API Key, hoặc gọi OpenAI bị lỗi / quá thời gian (Timeout), hoặc parse JSON thất bại -> Tự động chuyển sang gọi hàm `_rule_based_fallback()`.

2. Hàm Rule-Based Fallback Engine `_rule_based_fallback(...) -> dict`:
   - Phân tích thuần thuật toán dựa trên ma trận `days_until_expiry` và `stock_quantity`:
     + days <= 0: discount 100%, urgency "critical", reason: "Lô hàng đã hết hạn sử dụng, chuyển tiêu hủy theo quy chuẩn."
     + days <= 2: discount 60%, urgency "critical", reason: "Hàng cận date cấp tốc (≤ 2 ngày), giảm giá sâu để kích cầu xả hàng."
     + days <= 4: discount 40%, urgency "high", reason: "Thời hạn còn ngắn (≤ 4 ngày), giảm giá để tăng tốc độ xuất kho."
     + days <= 7: discount 25%, urgency "medium", reason: "Khuyến mại xả hàng định kỳ cho lô sắp hết hạn."
     + days <= 14: discount 10%, urgency "low", reason: "Chiết khấu nhẹ hỗ trợ bán nhanh."
     + Còn lại: discount 0%, urgency "low", reason: "Hạn sử dụng còn an toàn, duy trì giá bán niêm yết."
   - Gắn nhãn `engine_used = "rule_based_fallback"`.
   - Tính toán `suggested_price = original_price * (1 - discount_rate / 100)`.

3. Tự động lưu vết đề xuất vào CSDL:
   - Tạo bản ghi trong bảng `ai_discount_recommendations` với trạng thái `pending` để chờ Quản lý cửa hàng xét duyệt.
```

---

## 📌 3. Prompt Xây Dựng RESTful API Router (AI Discount Endpoints)

### 🎯 Mục tiêu:
Tạo 2 endpoint: Đánh giá đề xuất AI và Áp dụng trực tiếp vào lô hàng.

### 💬 Prompt gửi AI:
```text
Hãy viết router FastAPI `api/v1/ai_discount.py`:

1. `POST /api/v1/ai-discount/evaluate`:
   - Input: Pydantic Schema gồm `batch_id` (int), `average_daily_sales` (float), `competitor_price` (optional float), `custom_instruction` (optional str).
   - Logic: Tìm lô hàng trong DB, gọi `AIDiscountService.evaluate_discount()`.
   - Output: Trả về chi tiết đề xuất (suggested_discount_rate, suggested_price, urgency_level, confidence_score, reasoning, engine_used).

2. `POST /api/v1/ai-discount/{batch_id}/apply`:
   - Tự động chạy đánh giá và cập nhật ngay tỷ lệ `discount_rate` cho lô hàng mà không cần qua modal mô phỏng (dành cho nút "Áp dụng nhanh").
```

---

## 📌 4. Prompt Thiết Kế Giao Diện Modal Mô Phỏng AI (AI Simulation UI)

### 🎯 Mục tiêu:
Modal chạy phân tích AI chuyên nghiệp, có các tham số đầu vào tùy chỉnh, hiển thị kết quả trực quan với chỉ số độ tin cậy và nút xác nhận áp dụng.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML, CSS và JS cho Hộp thoại Phân tích AI (`ai-modal`):

1. Bố cục Modal (HTML & CSS):
   - Tiêu đề modal có icon SVG Sparkles (`<svg class="svg-icon" ...>`) và chữ "AI Dynamic Pricing Engine".
   - Khối tóm tắt lô hàng đang chọn: Mã Lô, Hạn Dùng, Số Lượng Tồn, Giá Hiện Tại.
   - Form thông số mô phỏng:
     + Ô nhập tốc độ bán trung bình (mặc định 3.0 sp/ngày).
     + Ô nhập giá đối thủ cạnh tranh.
     + Ô nhập yêu cầu chiến lược đặc biệt (ví dụ: "Cần bán sạch trong 48h").
     + Dropdown chọn phiên bản Prompt: v1 (Quy tắc bán lẻ) / v2 (Tối ưu biên độ).
   - Nút hành động chính: "🤖 Chạy Phân Tích AI" có hiệu ứng chuyển text thành "Đang phân tích AI..." khi đang gọi API.

2. Khối hiển thị kết quả (`ai-rec-result`):
   - Mức giảm giá đề xuất in chữ lớn màu đỏ (`-50%`).
   - Đơn giá sau giảm in chữ màu xanh ngọc tươi sáng.
   - Các badge: Tên Engine (OpenAI GPT-4 / Rule-Based), Mức độ khẩn cấp (Critical / High), Điểm tin cậy (Confidence).
   - Khối văn bản giải trình lý do (AI Reasoning Text) có dải viền màu tím công nghệ.
   - Nút bấm xác nhận: "✓ Đồng Ý & Áp Dụng Ngay Vào Hệ Thống".
```

---

## 📌 5. Prompt Viết Unit Test Kiểm Thử Động Cơ AI (Pytest)

### 🎯 Mục tiêu:
Kiểm thử bộ suy luận Rule-Based Fallback và kiểm thử bộ nạp prompt template.

### 💬 Prompt gửi AI:
```text
Hãy viết test cases Pytest tại `backend/tests/test_ai_discount.py`:
1. `test_ai_discount_rule_based_fallback`: Tạo 4 lô hàng mẫu với số ngày cận date lần lượt là 0 ngày, 2 ngày, 4 ngày, 15 ngày -> Xác nhận tỷ lệ chiết khấu sinh ra chính xác lần lượt là 100%, 60%, 40%, 0%.
2. `test_prompt_template_loader`: Kiểm tra nạp file template `v1_discount_recommendation.txt` và `v2_discount_recommendation.txt`, xác nhận có thể format đầy đủ các biến placeholder mà không ném KeyError.
```
