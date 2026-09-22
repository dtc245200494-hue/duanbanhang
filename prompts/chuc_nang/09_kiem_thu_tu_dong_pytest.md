# 🧪 BỘ PROMPT: KIỂM THỬ TỰ ĐỘNG VỚI PYTEST (AUTOMATED TEST SUITE)

> **Chức năng:** Thiết lập môi trường kiểm thử độc lập (In-memory SQLite), xây dựng các Fixture dùng chung và viết bộ kiểm thử tự động toàn diện bao phủ 100% chức năng cốt lõi.  
> **Tác nhân:** QA Engineer, Backend Developer.  
> **Thư mục liên quan:** `backend/tests/`, `pytest.ini`.

---

## 📌 1. Prompt Thiết Lập Fixtures Dùng Chung (`conftest.py`)

### 🎯 Mục tiêu:
Xây dựng cơ chế Mock CSDL độc lập bằng SQLite in-memory, tự động dọn dẹp sau mỗi phiên test, cung cấp `TestClient` và hàm sinh token đăng nhập giả lập.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Đảm bảo Chất lượng Phần mềm (Senior QA / Test Automation Engineer).
Hãy viết file cấu hình kiểm thử `backend/tests/conftest.py` cho dự án FastAPI:

1. Cơ sở dữ liệu kiểm thử (In-memory SQLite):
   - Sử dụng engine `sqlite:///:memory:` tách biệt hoàn toàn với file CSDL thực tế `sales.db`.
   - Fixture `db_session`:
     + Tạo toàn bộ các bảng `Base.metadata.create_all(bind=engine)`.
     + Khởi tạo session, nạp dữ liệu mẫu ban đầu (3 vai trò: admin, store_manager, customer; 1 cửa hàng; 1 tài khoản manager; 1 danh mục; 1 sản phẩm).
     + Yield session cho test case sử dụng.
     + Sau khi test case chạy xong, rollback và drop toàn bộ bảng `Base.metadata.drop_all(bind=engine)`.

2. Fixture `client`:
   - Cung cấp `TestClient(app)` của FastAPI (hoặc `starlette.testclient.TestClient`).
   - Override dependency `get_db` bằng `override_get_db` trả về in-memory session.

3. Fixture tạo Header xác thực:
   - Viết helper hàm `get_auth_headers(user_id: int, role_code: str) -> dict` tự động sinh mã JWT Bearer token hợp lệ để test các API yêu cầu đăng nhập.
```

---

## 📌 2. Prompt Viết Bộ 17 Test Cases Toàn Diện

### 🎯 Mục tiêu:
Bao phủ toàn bộ các luồng: Xác thực, Phân quyền, Danh mục, Lô hàng FEFO, Động cơ AI Fallback, Workflow duyệt giá, Bán hàng POS và Thanh toán.

### 💬 Prompt gửi AI:
```text
Hãy thiết kế và viết toàn bộ các file test case tự động bằng Pytest trong thư mục `backend/tests/`:

1. File `test_auth_rbac.py` (3 test cases):
   - `test_user_registration_and_password_hashing`: Test đăng ký tài khoản mới và kiểm tra mã hóa bcrypt.
   - `test_user_authentication_success_and_jwt`: Test đăng nhập thành công và giải mã JWT token.
   - `test_user_authentication_wrong_password`: Test đăng nhập sai mật khẩu trả về 401.

2. File `test_inventory.py` (3 test cases):
   - `test_fefo_allocation_single_batch`: Test xuất kho khi 1 lô đủ số lượng.
   - `test_fefo_allocation_split_batches`: Test xuất kho tách nhiều lô theo thứ tự ngày hết hạn.
   - `test_fefo_allocation_insufficient_stock`: Test báo lỗi khi không đủ tổng tồn kho.

3. File `test_ai_discount.py` (2 test cases):
   - `test_ai_discount_rule_based_fallback`: Test ma trận suy luận chiết khấu theo số ngày cận date.
   - `test_prompt_template_loader`: Test nạp file template prompt không bị lỗi cú pháp.

4. File `test_recommendation_workflow.py` (2 test cases):
   - `test_ai_recommendation_approval_workflow`: Test duyệt đề xuất làm cập nhật chiết khấu lô hàng.
   - `test_ai_recommendation_rejection`: Test từ chối đề xuất giữ nguyên giá lô hàng.

5. File `test_orders_api.py` (3 test cases):
   - `test_list_expiring_batches_endpoint`: Test API lấy danh sách lô cận date.
   - `test_create_order_with_fefo_endpoint`: Test API tạo đơn hàng trừ kho tự động.
   - `test_cancel_order_restores_stock`: Test API hủy đơn hoàn trả tồn kho về từng lô.

6. File `test_payments.py` (1 test case):
   - `test_order_creates_payment_record`: Test tự động sinh bản ghi thanh toán theo đơn.

7. File `test_categories.py` & `test_models.py` (3 test cases):
   - Test quan hệ giữa Category và Product.
   - Test thuộc tính `effective_unit_price` của ProductBatch.
   - Test xóa cascade chi nhánh và sản phẩm.

Tất cả các test case phải chạy độc lập, không phụ thuộc mạng bên ngoài và hoàn thành dưới 10 giây khi gõ lệnh: `pytest backend/tests -v`.
```
