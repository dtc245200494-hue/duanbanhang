# BÁO CÁO BÀI KIỂM TRA THƯỜNG XUYÊN 3 (TX3)
## TÍCH HỢP, THỬ NGHIỆM VÀ TỐI ƯU HÓA TRỢ LÝ TRÍ TUỆ NHÂN TẠO (AI)

- **Học phần:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)
- **Nhóm sinh viên:** Nhóm 03
- **Thành viên thực hiện:**
  - **Hoàng Trang Hiên** (Trưởng nhóm — Phân tích yêu cầu SRS, Thiết kế Kiến trúc & UML, Kỹ nghệ Prompt AI, Guardrails PII, Kịch bản Demo & Tổng hợp báo cáo)
  - **Nguyễn Viết Cường** (Lập trình viên chính — Phát triển Backend FastAPI, Frontend React 18, Tích hợp OpenAI/Gemini API, Xử lý giao dịch kho & Bộ kiểm thử Pytest)
- **Học kỳ:** 2026_2027_1
- **Giảng viên hướng dẫn:** ThS. Nguyễn Tuấn Anh (0912662003)
- **Cơ sở đào tạo:** Đại học Công nghệ Thông tin & Truyền thông (ICTU)
---

## 1. Tích hợp chức năng AI vào hệ thống
Hệ thống không gọi AI tách rời mà tích hợp sâu vào quy trình nghiệp vụ bán hàng thực tế:
1. **AI Tư vấn sản phẩm (`/api/ai/consult`):** Trợ lý bán hàng tự động đọc kho dữ liệu sản phẩm đang kinh doanh và còn tồn kho (`stock > 0`) để đưa ra gợi ý sát với nhu cầu của khách hàng.
2. **AI Phân tích báo cáo (`/api/ai/report`):** Nhận dữ liệu tổng hợp từ doanh thu, chi tiết bán hàng trong một khoảng thời gian và sinh nhận định kinh doanh tổng thể.
3. **AI Hỏi đáp kinh doanh (`/api/ai/qa`):** Đóng vai trò cố vấn tài chính/bán hàng, trả lời các câu hỏi quản lý dựa trên bối cảnh dữ liệu thật.

---

## 2. Kết nối API và Mô hình AI đúng chuẩn
- **Mô hình sử dụng:** OpenAI `gpt-4o-mini` (cung cấp qua OpenAI Python SDK v1.x).
- **Cấu hình môi trường:**
  - Khai báo qua file `.env`: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`.
  - Hỗ trợ thay đổi model hoặc chuyển sang các nhà cung cấp tương thích OpenAI (như Gemini OpenAI-compatible endpoint, Groq, Ollama) mà không cần sửa code.
- **Bảo mật:** API Key được lưu giữ ở Server Backend, không bao giờ để lộ xuống Client.

---

## 3. Thiết kế Prompt có hệ thống (Prompt Architecture)
Các mẫu prompt được tách riêng thành các tệp tin trong thư mục `prompts/`:
- `prompts/product_consultant.txt`: Mẫu prompt tư vấn bán hàng.
- `prompts/sales_report.txt`: Mẫu prompt phân tích báo cáo kinh doanh.
- `prompts/sales_qa.txt`: Mẫu prompt hỏi đáp nghiệp vụ.

Hệ thống cung cấp hàm nạp và thay thế biến template `load_prompt(name, **kwargs)` trong [ai_service.py](../backend/app/services/ai_service.py).

---

## 4. Tối ưu hóa Prompt qua 3 vòng thử nghiệm (Prompt Evolution)

Trong thư mục `prompts/versions/`, nhóm đã lưu trữ và đánh giá chi tiết quá trình cải tiến Prompt qua 3 phiên bản:

| Phiên bản | Nội dung Prompt | Vấn đề phát sinh | Kết quả đánh giá & Giải pháp |
| :--- | :--- | :--- | :--- |
| **V1 (Sơ khai)** | *"Bạn là trợ lý tư vấn sản phẩm. Khách cần: {{customer_request}}. Danh sách sản phẩm: {{product_table}}. Hãy gợi ý sản phẩm phù hợp."* | - AI tự "bịa" thêm các sản phẩm ngoài thị trường (ảo giác - hallucination).<br>- Gợi ý cả sản phẩm có số lượng tồn kho = 0. | **Chưa đạt:** Thiếu ràng buộc dữ liệu nghiêm ngặt. |
| **V2 (Cải tiến)** | Thêm các dòng: *"Chỉ tư vấn dựa trên dữ liệu sản phẩm được cung cấp. TUYỆT ĐỐI không gợi ý sản phẩm hết hàng. Hãy gợi ý tối đa 3 sản phẩm và giải thích ngắn gọn."* | - Đã giới hạn sản phẩm hết hàng.<br>- Tuy nhiên khi khách hỏi sản phẩm cửa hàng không có, AI vẫn cố gắng gán ghép sản phẩm không liên quan. | **Khá:** Giảm thiểu ảo giác nhưng cần quy định rõ câu trả lời khi không có hàng. |
| **V3 (Chuẩn hóa - Hiện tại)** | Bổ sung 4 quy tắc rõ ràng:<br>1. Chỉ tư vấn dựa trên dữ liệu được cung cấp.<br>2. Không đề xuất sản phẩm ngoài danh sách.<br>3. Không gợi ý sản phẩm hết hàng.<br>4. Nếu không có sản phẩm phù hợp, nói rõ *"hiện không có sản phẩm phù hợp"*. | - AI trả lời chính xác, giải thích ngắn gọn, từ chối lịch sự khi cửa hàng không có mặt hàng đáp ứng nhu cầu. | **Đạt xuất sắc:** Đáp ứng đầy đủ yêu cầu nghiệp vụ thực tế. |

---

## 5. Sử dụng Dữ liệu hệ thống trong chức năng AI (Data Grounding)
- **Lọc dữ liệu chính xác:** Trước khi đưa vào prompt, Backend thực hiện truy vấn SQLAlchemy:
  ```python
  products = db.query(Product).filter(
      Product.status == "active",
      Product.stock > 0
  ).order_by(Product.sell_price.asc()).all()
  ```
- Nhờ vậy, AI hoàn toàn không có cơ hội tiếp cận hoặc đề xuất những sản phẩm đã ngừng kinh doanh hoặc hết hàng.
- Với tính năng phân tích báo cáo, dữ liệu doanh thu tổng hợp thực tế theo ngày/tháng được truyền vào làm ngữ cảnh.

---

## 6. Hiển thị kết quả AI trên giao diện người dùng
- Trang `AIChat.jsx` được thiết kế dạng 3 Tabs trực quan:
  1. **Tab Tư vấn sản phẩm:** Có nút gửi nhanh các câu hỏi mẫu (Ví dụ: "Khách cần tai nghe dưới 500k", "Tìm điện thoại pin trâu tầm giá 5-7 triệu").
  2. **Tab Phân tích báo cáo:** Cho phép chọn khoảng ngày và bấm "Phân tích số liệu".
  3. **Tab Hỏi đáp kinh doanh:** Đặt câu hỏi tùy ý về tình hình bán lẻ.
- Kết quả được format trực quan, rõ ràng, có trạng thái "Đang suy nghĩ..." khi chờ phản hồi.

---

## 7. Xử lý lỗi và Các giới hạn AI (Fault Tolerance & Rate Limiting)
Hệ thống cài đặt đầy đủ các cơ chế phòng vệ tại [ai_service.py](../backend/app/services/ai_service.py):
1. **Che giấu dữ liệu nhạy cảm (Data Masking):**
   ```python
   def mask_sensitive(text: str) -> str:
       # Che giấu số điện thoại khách hàng thành [SĐT-ĐÃ-ẨN]
       return re.sub(r'(?:0|\+84)[1-9][0-9]{8,9}', '[SĐT-ĐÃ-ẨN]', text)
   ```
2. **Giới hạn tần suất gọi AI (Rate Limiter):** Giới hạn `12 lần gọi/phút`. Nếu vượt quá sẽ trả về mã lỗi HTTP `429 Too Many Requests`.
3. **Kiểm soát Timeout:** Thiết lập `timeout = 30.0s` khi gọi OpenAI API, tránh nghẽn luồng xử lý.
4. **Xử lý thiếu API Key:** Trả về mã lỗi `503 Service Unavailable` kèm thông báo hướng dẫn bổ sung khóa trong `.env` thay vì làm ứng dụng bị lỗi.

---

## 8. Kiểm thử Hệ thống và Chức năng AI (Testing Suite)
Dự án được bao phủ bởi **45 Test Cases** tự động với Pytest:
- `backend/tests/test_ai.py` (7 tests): Kiểm tra tư vấn chỉ gợi ý hàng còn kho, kiểm tra che giấu SĐT, kiểm tra Rate Limiter 429, kiểm tra thiếu API Key 503, kiểm tra phân tích báo cáo.
- `backend/tests/test_auth.py` (7 tests): Đăng nhập, phân quyền, token hết hạn.
- `backend/tests/test_products.py` (7 tests): CRUD, lọc tồn kho thấp, chặn xóa khi không có quyền.
- `backend/tests/test_orders.py` (8 tests): Tạo đơn, trừ kho, hủy đơn hoàn kho, kiểm tra tính toán tiền.
- `backend/tests/test_inventory.py` (5 tests): Cập nhật kho, nhập hàng.
- `backend/tests/test_reports.py` (11 tests): Báo cáo doanh thu, top sản phẩm, xuất Excel/PDF/CSV.

> **Kết quả kiểm thử thực tế:** `45 passed in 1.41s` (100% Passed).

---

## 9. Minh chứng Review Code & Cải thiện chất lượng bằng AI
- **Vấn đề ban đầu:** Hàm gọi OpenAI không có giới hạn số lần gọi, có nguy cơ bị spam làm tăng chi phí API và nghẽn hệ thống.
- **Prompt yêu cầu AI Review:** *"Hãy review đoạn code gọi OpenAI trong ai_service.py và đề xuất cơ chế rate limiter dạng in-memory đơn giản và hiệu quả trong Python."*
- **Đề xuất từ AI:** Cung cấp hàm `_check_rate_limit()` sử dụng danh sách timestamp trượt trong 60 giây.
- **Triển khai thực tế:** Nhóm đã áp dụng giải pháp này vào [ai_service.py](../backend/app/services/ai_service.py) và viết unit test `test_rate_limit_returns_429` để xác thực.

---

## 10. Trải nghiệm người dùng khi sử dụng AI
- Luồng tương tác tự nhiên, phản hồi nhanh chóng, hỗ trợ nhân viên bán hàng chốt đơn hiệu quả mà không làm xáo trộn quy trình tạo hóa đơn truyền thống.
