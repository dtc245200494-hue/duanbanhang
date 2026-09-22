# 🛍️ BỘ PROMPT: BÁN HÀNG TẠI QUẦY (POS) & ĐẶT HÀNG TRỰC TUYẾN (ORDERS MANAGEMENT)

> **Chức năng:** Tạo đơn hàng bán lẻ tại quầy hoặc đặt trực tuyến, tích hợp tự động xuất kho FEFO (trừ lô date gần nhất), lưu vết chi tiết từng lô hàng bán ra, tự động khởi tạo giao dịch thanh toán và hỗ trợ hoàn kho khi hủy đơn.  
> **Tác nhân:** Thu ngân / Quản lý cửa hàng (bán hàng POS), Khách hàng (đặt mua trực tuyến).  
> **Bảng CSDL liên quan:** `orders`, `order_items`, `product_batches`, `payments`, `users`, `stores`.

---

## 📌 1. Prompt Thiết Kế Model Đơn Hàng & Chi Tiết Lô Hàng (Orders & OrderItems)

### 🎯 Mục tiêu:
Mô hình hóa bảng `orders` và bảng `order_items` lưu trữ chính xác `batch_id` của từng sản phẩm để theo dõi nguồn gốc và mức giá sau chiết khấu FEFO.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Cơ sở dữ liệu và Backend Python. Hãy thiết kế bảng `orders` và `order_items` bằng SQLAlchemy 2.0:

1. Bảng `orders`:
   - `id`: Khóa chính Integer tự tăng.
   - `store_id`: Khóa ngoại liên kết `stores.id` (chi nhánh xuất kho).
   - `user_id`: Khóa ngoại liên kết `users.id` (khách hàng hoặc thu ngân tạo đơn, nullable).
   - `customer_name`: Tên người nhận hàng (String 255).
   - `customer_phone`: Số điện thoại người nhận (String 20).
   - `shipping_address`: Địa chỉ giao hàng / Nhận tại quầy (String 500).
   - `total_amount`: Tổng tiền đơn hàng sau khi tính toàn bộ chiết khấu (Numeric(12, 2)).
   - `status`: Trạng thái đơn ("pending", "confirmed", "shipping", "completed", "cancelled").
   - `note`: Ghi chú đơn hàng.
   - `created_at`: Thời gian tạo đơn.
   - Quan hệ: `items` (OrderItems), `payments` (Payments).

2. Bảng `order_items`:
   - `id`: Khóa chính tự tăng.
   - `order_id`: Khóa ngoại liên kết `orders.id` (ondelete="CASCADE").
   - `batch_id`: Khóa ngoại liên kết `product_batches.id` (bắt buộc, lưu chính xác lô hàng đã xuất).
   - `product_name`: Tên sản phẩm tại thời điểm bán.
   - `quantity`: Số lượng mua từ lô này (Integer >= 1).
   - `unit_price`: Đơn giá thực tế của sản phẩm từ lô này sau khi trừ chiết khấu lô.
   - `subtotal`: Thành tiền (`quantity * unit_price`).

Ràng buộc toàn vẹn dữ liệu chặt chẽ và đảm bảo tính nhất quán tài chính.
```

---

## 📌 2. Prompt Viết Dịch Vụ Tạo Đơn Hàng & Xuất Kho FEFO (Order Service)

### 🎯 Mục tiêu:
Viết logic tạo đơn hàng trong một Database Transaction duy nhất: phân bổ FEFO từng sản phẩm, tạo các bản ghi `order_items`, tính tổng tiền, tạo bản ghi `payments` và commit an toàn (rollback nếu có lỗi).

### 💬 Prompt gửi AI:
```text
Hãy viết lớp `OrderService` tại `backend/app/services/order_service.py`:

1. Hàm `create_order(db: Session, order_in: OrderCreateRequest, current_user: Optional[User]) -> Order`:
   - Bắt đầu transaction.
   - Khởi tạo `total_amount = 0`.
   - Danh sách các item cần xuất kho: Lặp qua từng món hàng trong `order_in.items`:
     + Gọi `InventoryService.allocate_fefo_batches(db, item.product_id, item.quantity)`.
     + Với mỗi lô được phân bổ, tạo một đối tượng `OrderItem` với `batch_id`, `quantity`, `unit_price = batch.effective_unit_price`.
     + Cộng dồn thành tiền vào `total_amount`.
   - Tạo đối tượng `Order`: gán store_id, user_id (nếu có), customer_name, customer_phone, shipping_address, total_amount, status='pending'.
   - Tạo đối tượng `Payment`: gán order_id, payment_method (COD, momo, vnpay, bank_transfer), amount = total_amount, status = 'pending'.
   - `db.add_all(...)` và `db.commit()`.
   - Trả về đối tượng `Order` hoàn chỉnh kèm items và payments.

2. Hàm `update_order_status(db: Session, order_id: int, new_status: str) -> Order`:
   - Nếu `new_status == 'cancelled'` và đơn hàng trước đó chưa bị hủy: Gọi `InventoryService.restore_fefo_batches()` để hoàn trả tồn kho về từng lô hàng ban đầu.
   - Nếu `new_status == 'completed'`: Cập nhật trạng thái thanh toán tương ứng nếu là COD.
```

---

## 📌 3. Prompt Xây Dựng RESTful API Router (Orders API)

### 🎯 Mục tiêu:
Cung cấp endpoint tạo đơn hàng và quản lý danh sách đơn hàng.

### 💬 Prompt gửi AI:
```text
Hãy viết router FastAPI `api/v1/orders.py`:

1. `POST /api/v1/orders`:
   - Tạo đơn hàng mới từ POS hoặc Giỏ hàng trực tuyến.
   - Validate Pydantic schema: `store_id`, `customer_name`, `customer_phone`, `shipping_address`, `payment_method`, `items: list[{product_id, quantity}]`.
   - Tự động liên kết `user_id` nếu người dùng đã đăng nhập token.

2. `GET /api/v1/orders`:
   - Nếu người gọi là Customer: Chỉ trả về các đơn hàng có `user_id` trùng với tài khoản hiện tại.
   - Nếu người gọi là Admin hoặc Store Manager: Trả về toàn bộ danh sách đơn hàng của hệ thống.
   - Trả về chi tiết items (kèm mã lô đã trừ) và thông tin thanh toán.

3. `PATCH /api/v1/orders/{id}/status`:
   - Cập nhật trạng thái đơn ("confirmed", "shipping", "completed", "cancelled").
   - Yêu cầu quyền `["admin", "store_manager"]`.
```

---

## 📌 4. Prompt Thiết Kế Giao Diện Bán Hàng POS & Hóa Đơn Trực Quan (Live Receipt)

### 🎯 Mục tiêu:
Giao diện POS chia 2 cột hiện đại: Bên trái là Form nhập thông tin, Bên phải là Thẻ hóa đơn bán lẻ xem trước trực tiếp (Live Receipt Preview) cập nhật thời gian thực.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML, CSS và JavaScript cho Màn hình Bán hàng (POS Checkout Tab) theo phong cách Bento Box:

1. Giao diện (HTML & CSS):
   - Bố cục 2 cột (Desktop: 1.15fr và 0.85fr; Mobile: 1 cột):
     + Cột trái: Form thông tin đơn hàng (Chọn chi nhánh, Tên người nhận, Số điện thoại, Địa chỉ, Phương thức thanh toán, Dropdown chọn sản phẩm, Ô nhập số lượng).
     + Cột phải: Thẻ Hóa Đơn Xuất Kho FEFO (`live-receipt-card`) có viền nét đứt (dashed border):
       * Header: "HÓA ĐƠN XUẤT KHO FEFO - SmartRetail FreshMart".
       * Dòng sản phẩm đang chọn, số lượng mua.
       * Dòng huy hiệu chiết khấu: Badge xanh lá "Tự động FEFO".
       * Dòng phương thức thanh toán.
       * Dòng tổng tiền: In đậm màu xanh ngọc tươi sáng.

2. JavaScript Tương tác thời gian thực:
   - Hàm `updatePOSPreview()`: Lắng nghe sự kiện `change` trên dropdown sản phẩm, sự kiện `input` trên ô số lượng, sự kiện `change` trên phương thức thanh toán -> Tự động tính toán và hiển thị ngay thông tin xem trước trên thẻ hóa đơn mà không cần bấm nút.
   - Hàm `handleCreateOrder(e)`: Gửi POST `/api/v1/orders`, nhận response, hiển thị Toast chúc mừng tạo đơn thành công và tự động chuyển sang tab "Đơn Đặt Hàng" để theo dõi.
```

---

## 📌 5. Prompt Viết Unit Test Kiểm Thử Đơn Hàng & Hoàn Kho (Pytest)

### 🎯 Mục tiêu:
Kiểm thử tạo đơn hàng trừ kho FEFO và kiểm thử hủy đơn hàng hoàn trả kho.

### 💬 Prompt gửi AI:
```text
Hãy viết test cases Pytest tại `backend/tests/test_orders_api.py`:
1. `test_create_order_with_fefo_endpoint`: Gọi POST `/api/v1/orders` mua 2 sản phẩm -> Xác nhận API trả về HTTP 200, tạo đúng 1 bản ghi thanh toán tương ứng và tồn kho của lô hàng bị giảm đúng 2 đơn vị.
2. `test_cancel_order_restores_stock`: Chuyển trạng thái đơn hàng sang 'cancelled' -> Xác nhận số lượng tồn kho của lô hàng được cộng bù trở lại đúng bằng số lượng đã mua ban đầu.
```
