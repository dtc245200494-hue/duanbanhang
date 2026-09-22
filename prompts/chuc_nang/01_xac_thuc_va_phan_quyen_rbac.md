# 🔐 BỘ PROMPT: XÁC THỰC TÀI KHOẢN, MÃ HÓA MẬT KHẨU & PHÂN QUYỀN RBAC

> **Chức năng:** Đăng nhập, Đăng ký, Quản lý Token JWT và Phân quyền đa tác nhân (Role-Based Access Control).  
> **Tác nhân:** Khách hàng (Customer), Quản lý cửa hàng (Store Manager), Quản trị viên (Admin).  
> **Bảng CSDL liên quan:** `roles`, `users`.

---

## 📌 1. Prompt Thiết Kế CSDL & Mã Hóa Mật Khẩu (Database & Security)

### 🎯 Mục tiêu:
Tạo 2 bảng `roles` và `users`, mã hóa mật khẩu một chiều bằng `bcrypt`, bảo vệ an toàn thông tin đăng nhập.

### 💬 Prompt gửi AI:
```text
Bạn là một Kỹ sư An toàn Thông tin & Backend Developer cao cấp sử dụng FastAPI và SQLAlchemy 2.0.
Hãy thiết kế module xác thực và phân quyền (Authentication & Authorization) đáp ứng các yêu cầu sau:

1. Cơ sở dữ liệu (SQLAlchemy Models):
   - Bảng `roles`: `id` (PK, int), `code` (string, unique: "admin", "store_manager", "customer"), `name` (string), `description` (text).
   - Bảng `users`: `id` (PK, int), `email` (string, unique, index), `hashed_password` (string), `full_name` (string), `phone` (string), `role_id` (FK liên kết roles.id), `is_active` (boolean, default True), `created_at` (datetime).

2. Bảo mật mật khẩu:
   - Sử dụng thư viện `bcrypt` nguyên bản (native) để băm mật khẩu với salt ngẫu nhiên.
   - Giới hạn độ dài password byte ở 72 ký tự để tránh lỗi tràn bộ đệm của thuật toán bcrypt.
   - Hàm `verify_password(plain_password, hashed_password) -> bool` kiểm tra mật khẩu.
   - Hàm `get_password_hash(password) -> str` tạo chuỗi hash an toàn.

3. Chuẩn hóa mã nguồn:
   - Tuân thủ PEP 8, có type hints và docstrings chi tiết bằng tiếng Việt hoặc tiếng Anh.
```

---

## 📌 2. Prompt Tạo Token JWT & Dependency Phân Quyền (JWT & RBAC Middleware)

### 🎯 Mục tiêu:
Cấp phát Access Token chuẩn JWT (HS256) khi đăng nhập thành công và chặn các yêu cầu trái phép theo vai trò.

### 💬 Prompt gửi AI:
```text
Tiếp tục dự án FastAPI trên, hãy xây dựng module quản lý JWT token và các Dependencies kiểm tra quyền hạn (RBAC):

1. Module `core/security.py`:
   - Hàm `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`: Tạo mã JWT chứa `sub` là user_id, mã hóa bằng thuật toán HS256, thời hạn sống cấu hình qua `SECRET_KEY` và `ACCESS_TOKEN_EXPIRE_MINUTES`.
   - Hàm `decode_access_token(token: str) -> Optional[dict]`: Giải mã token, xử lý ngoại lệ JWTError và hết hạn an toàn.

2. Module `api/deps.py`:
   - Dependency `get_db()`: Cung cấp session cơ sở dữ liệu và tự động đóng sau khi request kết thúc.
   - Dependency `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User`: Lấy thông tin người dùng hiện tại từ token. Nếu token sai hoặc người dùng bị khóa (`is_active == False`), bắn lỗi HTTP 401 Unauthorized.
   - Dependency factory `require_role(allowed_roles: list[str])`: Kiểm tra vai trò của người dùng. Nếu vai trò không nằm trong `allowed_roles`, bắn lỗi HTTP 403 Forbidden ("Bạn không có quyền thực hiện thao tác này").

Hãy viết code ngắn gọn, xử lý đầy đủ các trường hợp ngoại lệ.
```

---

## 📌 3. Prompt Xây Dựng RESTful API Router (Auth API Endpoints)

### 🎯 Mục tiêu:
Xây dựng các endpoint `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`.

### 💬 Prompt gửi AI:
```text
Hãy viết API Router FastAPI cho chức năng Xác thực tại đường dẫn `backend/app/api/v1/auth.py`:

1. Endpoint `POST /api/v1/auth/register`:
   - Input: Pydantic schema `UserRegisterRequest` gồm: email, password (min 6 ký tự), full_name, phone, role_code ("customer" hoặc "store_manager").
   - Logic: Kiểm tra email đã tồn tại hay chưa (nếu trùng trả về HTTP 400), tìm role_id theo role_code, băm password, lưu user vào DB.
   - Output: Thông tin user vừa tạo (ẩn hashed_password).

2. Endpoint `POST /api/v1/auth/login`:
   - Input: Pydantic schema `UserLoginRequest` gồm: email, password.
   - Logic: Tìm user theo email, dùng verify_password kiểm tra mật khẩu. Nếu sai trả về HTTP 401. Tạo access token JWT.
   - Output: `{"access_token": token, "token_type": "bearer", "user": {id, email, full_name, role_code, role_name}}`.

3. Endpoint `GET /api/v1/auth/me`:
   - Yêu cầu xác thực Bearer token qua `get_current_user`.
   - Trả về toàn bộ profile người dùng hiện tại kèm vai trò.
```

---

## 📌 4. Prompt Thiết Kế Giao Diện Frontend Modal & Nút 1-Click Login

### 🎯 Mục tiêu:
Tạo modal đăng nhập/đăng ký hiện đại, hỗ trợ chuyển tab, lưu token vào `localStorage` và cung cấp các nút đăng nhập nhanh 1-chạm (1-click test accounts).

### 💬 Prompt gửi AI:
```text
Hãy viết mã HTML, CSS và JavaScript cho Hộp thoại Đăng nhập & Đăng ký (Auth Modal) theo chuẩn thiết kế UI/UX hiện đại:

1. Giao diện (HTML & CSS):
   - Hộp thoại Modal backdrop làm mờ hậu cảnh (glassmorphism: backdrop-filter blur).
   - Thanh Tab chuyển đổi giữa "Đăng Nhập" và "Đăng Ký Tài Khoản".
   - Form đăng nhập với input email, password có hiệu ứng viền phát sáng khi focus.
   - Khu vực "Đăng nhập nhanh 1 chạm" với 3 thẻ vai trò có màu sắc phân biệt:
     + 👑 Quản trị viên (Admin): admin@freshmart.vn / Admin@123
     + 🏪 Quản lý cửa hàng (Manager): manager@freshmart.vn / Admin@123
     + 🛒 Khách hàng (Customer): customer@freshmart.vn / Admin@123
   - Sử dụng icon SVG Lucide (không dùng emoji làm icon điều khiển).

2. JavaScript Xử lý:
   - Hàm `handleLoginSubmit(e)`: Gửi POST `/api/v1/auth/login`, lưu token vào `localStorage`, hiển thị Toast thông báo thành công và cập nhật thanh người dùng (User Bar).
   - Hàm `quickLoginAs(email)`: Tự động đăng nhập với mật khẩu mặc định `Admin@123`.
   - Hàm `applyRolePermissions()`: Ẩn/hiện các tab điều hướng trên Sidebar tùy theo quyền:
     + Khách hàng: chỉ xem POS Mua sắm, Danh mục và Đơn của tôi.
     + Quản lý: xem toàn bộ kho, duyệt giá AI, quản lý đơn hàng.
     + Admin: toàn quyền kèm thêm tab Quản trị người dùng & Phân quyền.
```

---

## 📌 5. Prompt Viết Kiểm Thử Tự Động Pytest (Testing Suite)

### 🎯 Mục tiêu:
Viết Unit Test kiểm thử đăng ký, đăng nhập sai/đúng và giải mã token JWT.

### 💬 Prompt gửi AI:
```text
Hãy viết bộ unit test Pytest cho module xác thực tại `backend/tests/test_auth_rbac.py`:
- `test_user_registration_and_password_hashing`: Kiểm tra tạo tài khoản mới, đảm bảo mật khẩu trong DB không phải dạng plain text mà được băm bcrypt.
- `test_user_authentication_success_and_jwt`: Đăng nhập với thông tin đúng, nhận token JWT hợp lệ, giải mã payload kiểm tra đúng user_id.
- `test_user_authentication_wrong_password`: Đăng nhập với mật khẩu sai, xác nhận hệ thống trả về mã lỗi HTTP 401 Unauthorized.
```
