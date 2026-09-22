# ⏳ BỘ PROMPT: QUẢN LÝ LÔ HÀNG & THUẬT TOÁN XUẤT KHO FEFO (FIRST EXPIRED, FIRST OUT)

> **Chức năng:** Quản lý từng lô hàng cụ thể, theo dõi ngày hết hạn (`expiry_date`), tỷ lệ chiết khấu hiện hành của lô và thuật toán phân bổ kho FEFO tự động.  
> **Tác nhân:** Quản lý cửa hàng (Store Manager), Khách mua hàng (hưởng giá ưu đãi lô cận date).  
> **Bảng CSDL liên quan:** `product_batches`, `products`, `order_items`.

---

## 📌 1. Prompt Thiết Kế Model Lô Hàng (ProductBatch Model)

### 🎯 Mục tiêu:
Thiết kế bảng `product_batches` lưu trữ chi tiết hạn dùng, tồn kho theo lô, giá bán thực tế sau chiết khấu và số ngày còn lại đến hạn.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Backend cấp cao phụ trách hệ thống Bán lẻ & Quản lý chuỗi cung ứng thực phẩm tươi sống.
Hãy thiết kế bảng `product_batches` (Lô hàng sản phẩm) bằng SQLAlchemy 2.0:

1. Các trường dữ liệu:
   - `id`: Khóa chính Integer tự tăng.
   - `product_id`: Khóa ngoại liên kết `products.id` (ondelete="CASCADE").
   - `batch_code`: Mã số lô sản xuất/nhập kho (String 100, unique index).
   - `stock_quantity`: Số lượng hàng thực tế còn trong lô (Integer, default 0, constraint >= 0).
   - `expiry_date`: Ngày hết hạn sử dụng (Date, không null).
   - `discount_rate`: Tỷ lệ giảm giá hiện hành áp dụng cho lô hàng này (Integer, từ 0 đến 100, default 0).
   - `status`: Trạng thái lô hàng (String 20: "active", "clearance", "expired").
   - `created_at`: Ngày nhập lô hàng.

2. Các thuộc tính tính toán động (Hybrid Properties):
   - `days_until_expiry`: Số ngày còn lại tính từ ngày hiện tại đến `expiry_date`.
   - `effective_unit_price`: Đơn giá thực tế sau khi áp dụng chiết khấu: `original_price * (1 - discount_rate / 100)`.
   - `is_expired`: Boolean xác định lô đã quá hạn sử dụng hay chưa.

Viết code rõ ràng, có xử lý múi giờ và kiểm tra điều kiện dữ liệu hợp lệ.
```

---

## 📌 2. Prompt Viết Thuật Toán Xuất Kho FEFO (FEFO Inventory Service)

### 🎯 Mục tiêu:
Thuật toán xuất kho tự động: Khi có đơn hàng, hệ thống tự động tìm và trừ tồn kho từ các lô có `expiry_date` gần nhất còn hàng (`stock_quantity > 0`). Nếu đơn hàng mua nhiều hơn số lượng của 1 lô, thuật toán tự động tách (split) ra nhiều lô kế tiếp. Khi đơn bị hủy (`cancelled`), tồn kho từng lô phải được hoàn trả chính xác.

### 💬 Prompt gửi AI:
```text
Hãy viết lớp dịch vụ `InventoryService` phụ trách thuật toán xuất kho FEFO tại `backend/app/services/inventory_service.py`:

Yêu cầu cụ thể:
1. Hàm `allocate_fefo_batches(db: Session, product_id: int, requested_quantity: int) -> list[dict]`:
   - Bước 1: Truy vấn danh sách lô hàng của `product_id` có `status == 'active'` và `stock_quantity > 0`.
   - Bước 2: Sắp xếp danh sách lô hàng tăng dần theo `expiry_date` (First Expired First Out).
   - Bước 3: Tính toán tổng tồn kho của tất cả các lô khả dụng. Nếu tổng tồn kho < `requested_quantity`, bắn ngoại lệ ValueError("Số lượng tồn kho không đủ để đáp ứng").
   - Bước 4: Lặp qua từng lô:
     + Lấy số lượng có thể xuất từ lô hiện tại: `take = min(batch.stock_quantity, remaining_needed)`.
     + Trừ trực tiếp `batch.stock_quantity -= take`.
     + Nếu `batch.stock_quantity == 0`, cập nhật trạng thái nếu cần.
     + Lưu thông tin phân bổ: `batch_id`, `batch_code`, `quantity`, `effective_price`.
     + Giảm `remaining_needed -= take`.
     + Dừng vòng lặp khi `remaining_needed == 0`.
   - Trả về danh sách chi tiết các lô được phân bổ.

2. Hàm `restore_fefo_batches(db: Session, order_items: list[OrderItem])`:
   - Hoàn trả lại chính xác số lượng sản phẩm vào từng `batch_id` tương ứng khi đơn hàng chuyển sang trạng thái "cancelled".

3. Hàm `refresh_batch_statuses(db: Session) -> int`:
   - Quét toàn bộ lô hàng, nếu `days_until_expiry <= 0` thì chuyển status thành "expired" và set `discount_rate = 100`.
   - Nếu `days_until_expiry <= 7` và `status == 'active'`, chuyển status thành "clearance".
```

---

## 📌 3. Prompt Xây Dựng RESTful API Lô Cận Date (Batches API)

### 🎯 Mục tiêu:
API cung cấp danh sách lô hàng cận date được sắp xếp theo mức độ khẩn cấp (ngày hết hạn tăng dần).

### 💬 Prompt gửi AI:
```text
Hãy viết router FastAPI `api/v1/batches.py`:
1. `GET /api/v1/batches/expiring?days=15`:
   - Lấy danh sách tất cả các lô hàng có số ngày còn lại đến hạn `days_until_expiry <= days` và còn tồn kho (`stock_quantity > 0`).
   - Sắp xếp tăng dần theo `expiry_date`.
   - Trả về danh sách chứa: batch_code, product_name, stock_quantity, expiry_date, days_until_expiry, effective_unit_price, discount_rate.

2. `POST /api/v1/batches/`:
   - Thêm lô hàng mới cho sản phẩm (product_id, batch_code, stock_quantity, expiry_date, discount_rate).
   - Quyền hạn yêu cầu: `["admin", "store_manager"]`.

3. `PATCH /api/v1/batches/{id}/discount`:
   - Cập nhật thủ công tỷ lệ giảm giá cho lô hàng (`discount_rate` từ 0 đến 100%).
```

---

## 📌 4. Prompt Thiết Kế Giao Diện Bảng Lô Cận Date & Đèn Báo Động

### 🎯 Mục tiêu:
Giao diện hiển thị trực quan các lô cận date, có bộ lọc theo số ngày và đèn tín hiệu nhấp nháy đỏ cho các lô khẩn cấp ≤ 3 ngày.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML, CSS và JavaScript cho màn hình Lô Cận Date (Expiring Batches Tab):

1. Giao diện (HTML/CSS):
   - Thanh công cụ phía trên với dropdown lọc:
     + 🚨 Cực kỳ khẩn cấp (≤ 3 ngày)
     + ⚠️ Khẩn cấp cao (≤ 7 ngày)
     + ⏳ Cảnh báo vừa (≤ 15 ngày)
     + 📅 Toàn bộ trong tháng (≤ 30 ngày)
   - Bảng dữ liệu:
     + Cột Mức Khẩn Cấp: Nếu <= 3 ngày hiển thị badge màu đỏ có chấm phát sáng nhấp nháy (`badge-critical` với `status-dot pulse`). Nếu <= 7 ngày hiển thị badge màu hổ phách (`badge-warning`).
     + Cột Đơn Giá Bán: Nếu có chiết khấu, hiển thị giá gốc gạch ngang và giá mới màu xanh lá nổi bật kèm pill `-X%`.
     + Cột Trí Tuệ Nhân Tạo: Có 2 nút bấm với icon SVG: "🤖 AI Phân tích" (mở Modal AI) và "⚡ Áp dụng nhanh" (chạy nhanh quy tắc xả hàng).
```

---

## 📌 5. Prompt Viết Kiểm Thử Tự Động Thuật Toán FEFO (Pytest)

### 🎯 Mục tiêu:
Viết 3 test case kiểm thử xuất kho đơn lô, đa lô (split) và xử lý lỗi khi thiếu hàng.

### 💬 Prompt gửi AI:
```text
Hãy viết bộ unit test Pytest tại `backend/tests/test_inventory.py`:
1. `test_fefo_allocation_single_batch`: Tạo sản phẩm với 2 lô (Lô 1 hạn ngày mai còn 10 sp, Lô 2 hạn 10 ngày sau còn 20 sp). Đặt mua 5 sp -> Xác nhận hệ thống chỉ lấy đúng từ Lô 1, Lô 1 còn lại 5 sp, Lô 2 giữ nguyên 20 sp.
2. `test_fefo_allocation_split_batches`: Tiếp tục với kịch bản trên, đặt mua 12 sp (vượt quá 5 sp còn lại của Lô 1) -> Xác nhận thuật toán tự động tách: lấy hết 5 sp của Lô 1 (Lô 1 về 0) và lấy tiếp 7 sp của Lô 2 (Lô 2 còn 13 sp).
3. `test_fefo_allocation_insufficient_stock`: Đặt mua số lượng vượt quá tổng tồn kho của tất cả các lô -> Xác nhận hàm ném lỗi ngoại lệ và không có số lượng lô nào bị trừ sai.
```
