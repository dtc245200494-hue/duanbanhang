# 💳 BỘ PROMPT: QUẢN LÝ GIAO DỊCH THANH TOÁN (PAYMENTS MANAGEMENT)

> **Chức năng:** Quản lý giao dịch thu chi thanh toán gắn liền với từng đơn hàng, hỗ trợ đa dạng phương thức (COD, MoMo, VNPAY, Chuyển khoản ngân hàng), theo dõi trạng thái đối soát thu tiền.  
> **Tác nhân:** Thu ngân / Quản lý cửa hàng (Store Manager), Quản trị viên (Admin).  
> **Bảng CSDL liên quan:** `payments`, `orders`.

---

## 📌 1. Prompt Thiết Kế Model Thanh Toán (Payment Model)

### 🎯 Mục tiêu:
Thiết kế bảng `payments` đảm bảo tính toàn vẹn tài chính, liên kết chặt chẽ với bảng `orders`.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Cơ sở dữ liệu và FinTech Backend. Hãy viết SQLAlchemy 2.0 Model cho bảng `payments`:

1. Các trường dữ liệu:
   - `id`: Khóa chính Integer tự tăng.
   - `order_id`: Khóa ngoại liên kết `orders.id` (ondelete="CASCADE").
   - `payment_method`: Phương thức thanh toán (String 50, các giá trị hợp lệ: "COD", "momo", "vnpay", "bank_transfer", "card").
   - `amount`: Số tiền thanh toán (Numeric(12, 2), không null, >= 0).
   - `status`: Trạng thái giao dịch (String 20: "pending" - Chờ thu tiền, "paid" - Đã thanh toán, "failed" - Thất bại).
   - `paid_at`: Thời gian hoàn tất quyết toán (DateTime, nullable).
   - `created_at`: Thời gian khởi tạo bản ghi thanh toán.

2. Ràng buộc quan hệ:
   - `order`: Relationship liên kết ngược về bảng `Order`.

Đảm bảo tuân thủ PEP 8 và có docstring mô tả chi tiết quy trình tài chính.
```

---

## 📌 2. Prompt Xây Dựng RESTful API Router (Payments API)

### 🎯 Mục tiêu:
Cung cấp các endpoint xem lịch sử giao dịch và xác nhận đã thu tiền.

### 💬 Prompt gửi AI:
```text
Hãy viết router FastAPI `api/v1/payments.py`:

1. `GET /api/v1/payments`:
   - Yêu cầu xác thực tài khoản qua Bearer token.
   - Nếu là Quản lý hoặc Admin: Trả về toàn bộ danh sách giao dịch thanh toán của hệ thống.
   - Nếu là Khách hàng: Chỉ trả về giao dịch thuộc các đơn hàng của chính khách hàng đó.
   - Sắp xếp giảm dần theo `created_at` (mới nhất lên đầu).

2. `PATCH /api/v1/payments/{id}/status`:
   - Input: `status` mới ("paid", "failed").
   - Yêu cầu quyền: `["admin", "store_manager"]`.
   - Logic: Nếu chuyển thành "paid", tự động gán `paid_at = utcnow()`. Đồng thời nếu đơn hàng tương ứng đang ở trạng thái 'pending', tự động chuyển đơn hàng thành 'confirmed'.
   - Trả về bản ghi giao dịch đã cập nhật.
```

---

## 📌 3. Prompt Thiết Kế Giao Diện Bảng Đối Soát Thanh Toán (Payments UI)

### 🎯 Mục tiêu:
Bảng hiển thị lịch sử giao dịch rõ ràng, có huy hiệu phương thức thanh toán và nút "Xác Nhận Thu" 1-chạm cho thu ngân.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML, CSS và JS cho tab Giao Dịch Thanh Toán (Payments Tab):

1. Giao diện (HTML & CSS):
   - Tiêu đề có icon SVG CreditCard (`<svg class="svg-icon" ...>`).
   - Bảng dữ liệu giao dịch:
     + Mã GD: Hiển thị `#PAY-{id}` in đậm màu xanh ngọc.
     + Mã Đơn: Liên kết đơn hàng `#ORDER-{order_id}`.
     + Phương thức: Badge màu cyan hiển thị MOMO, VNPAY, COD, BANK_TRANSFER.
     + Số tiền: In đậm định dạng tiền tệ VNĐ.
     + Trạng thái: Badge màu sắc phân biệt có chấm phát sáng (vàng: Chờ thu tiền, xanh lá: Đã thanh toán, đỏ: Thất bại).
     + Thời gian quyết toán: Ngày giờ thanh toán hoặc `-` nếu chưa thanh toán.
     + Thao tác: Nếu chưa thanh toán -> Hiển thị nút bấm màu xanh lá "✓ Xác Nhận Thu". Nếu đã thanh toán -> Hiển thị text mờ "Đã quyết toán".

2. JavaScript Xử lý:
   - Hàm `markPaymentPaid(paymentId)`: Gửi PATCH cập nhật `status = 'paid'`, hiển thị toast thông báo và cập nhật lại bảng.
```

---

## 📌 4. Prompt Viết Kiểm Thử Tự Động Pytest (Payment Tests)

### 🎯 Mục tiêu:
Kiểm thử tự động sinh bản ghi thanh toán khi tạo đơn hàng và kiểm thử chuyển trạng thái giao dịch.

### 💬 Prompt gửi AI:
```text
Hãy viết unit test Pytest tại `backend/tests/test_payments.py`:
- `test_order_creates_payment_record`: Tạo một đơn hàng mới với phương thức 'momo' và tổng tiền 50.000đ -> Kiểm tra bảng `payments` tự động có đúng 1 bản ghi liên kết tới `order_id`, số tiền bằng 50.000đ và trạng thái ban đầu là 'pending'.
```
