# 👥 BỘ PROMPT: QUẢN TRỊ NGƯỜI DÙNG & PHÂN QUYỀN HỆ THỐNG (USER MANAGEMENT - ADMIN ONLY)

> **Chức năng:** Giám sát toàn bộ tài khoản người dùng, vai trò (Role), trạng thái kích hoạt và phạm vi phân quyền trong toàn hệ thống chuỗi bán lẻ.  
> **Tác nhân:** Quản trị viên tối cao (Admin Only).  
> **Bảng CSDL liên quan:** `users`, `roles`, `stores`.

---

## 📌 1. Prompt Thiết Kế API Giám Sát Người Dùng Cấp Admin

### 🎯 Mục tiêu:
Cung cấp endpoint trả về danh sách tất cả người dùng trong hệ thống kèm thông tin vai trò, có bảo vệ chặt chẽ bằng dependency `require_role(["admin"])`.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Backend phụ trách Bảo mật và Quản trị Hệ thống. Hãy viết API Router `api/v1/users.py` bằng FastAPI:

1. Yêu cầu bảo mật:
   - Tất cả các endpoint trong router này đều phải đi qua Dependency `require_role(["admin"])`.
   - Nếu tài khoản có vai trò khác (như `store_manager` hoặc `customer`), hệ thống lập tức trả về mã lỗi HTTP 403 Forbidden kèm thông báo: "Khu vực bảo mật cấp Admin. Bạn không có quyền truy cập."

2. Endpoint `GET /api/v1/users`:
   - Trả về danh sách tất cả các tài khoản trong hệ thống: `id`, `full_name`, `email`, `phone`, `role_id`, `role_code`, `role_name`, `is_active`, `created_at`.
   - Tuyệt đối không để lộ trường `hashed_password` trong response schema (Pydantic).

3. Endpoint `PATCH /api/v1/users/{id}/toggle-active`:
   - Đổi trạng thái kích hoạt tài khoản (`is_active` True <-> False) để khóa hoặc mở khóa tài khoản người dùng khi cần.
```

---

## 📌 2. Prompt Thiết Kế Giao Diện Quản Trị Phân Quyền (Users & Roles UI)

### 🎯 Mục tiêu:
Thiết kế giao diện bảng điều khiển dành riêng cho Admin, hiển thị rõ ràng 3 phân cấp vai trò và bảng giải trình quyền hạn.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML, CSS và JS cho màn hình Quản Trị Người Dùng (Users Tab):

1. Giao diện (HTML & CSS):
   - Tiêu đề có icon SVG Shield Users (`<svg class="svg-icon" ...>`).
   - Huy hiệu bảo mật màu đỏ nổi bật ở góc banner: "🛡️ Khu vực Bảo Mật Cấp Admin".
   - Bảng dữ liệu người dùng:
     + Cột ID: Hiển thị `#USR-{id}`.
     + Cột Họ và Tên: In đậm rõ nét.
     + Cột Email: Hiển thị màu xanh ngọc.
     + Cột Số Điện Thoại.
     + Cột Vai Trò (Role): Huy hiệu có màu sắc phân định:
       * 👑 Quản trị viên (Admin) - Badge màu đỏ.
       * 🏪 Quản lý cửa hàng (Store Manager) - Badge màu xanh dương (Info).
       * 🛒 Khách hàng (Customer) - Badge màu xanh lá (Success).
     + Cột Trạng Thái: Badge có chấm tròn (Đang hoạt động / Bị khóa).
     + Cột Phạm Vi Quyền Hạn: Mô tả ngắn gọn trách nhiệm nghiệp vụ của vai trò.

2. JavaScript Xử lý:
   - Tự động ẩn tab "Quản Trị Tài Khoản" trên thanh Sidebar nếu người dùng đăng nhập không phải là Admin.
   - Nếu cố tình truy cập vào tab này khi chưa có quyền, hiển thị Toast cảnh báo và tự động chuyển về trang Dashboard.
```
