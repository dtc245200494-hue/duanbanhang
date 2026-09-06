# BÁO CÁO BÀI KIỂM TRA THƯỜNG XUYÊN 2 (TX2)
## LẬP TRÌNH VÀ TRIỂN KHAI HỆ THỐNG QUẢN LÝ BÁN HÀNG CƠ BẢN

- **Học phần:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)
- **Nhóm sinh viên:** Nhóm 03
- **Thành viên thực hiện:**
  - **Hoàng Trang Hiên** (Trưởng nhóm — Phân tích yêu cầu SRS, Thiết kế Kiến trúc & UML, Kỹ nghệ Prompt AI, Guardrails PII, Kịch bản Demo & Tổng hợp báo cáo)
  - **Nguyễn Viết Cường** (Lập trình viên chính — Phát triển Backend FastAPI, Frontend React 18, Tích hợp OpenAI/Gemini API, Xử lý giao dịch kho & Bộ kiểm thử Pytest)
- **Học kỳ:** 2026_2027_1
- **Giảng viên hướng dẫn:** ThS. Nguyễn Tuấn Anh (0912662003)
- **Cơ sở đào tạo:** Đại học Công nghệ Thông tin & Truyền thông (ICTU)
---

## 1. Cấu trúc dự án (Project Architecture)
Dự án được phân chia module rõ ràng theo chuẩn kiến trúc Client-Server hiện đại:
```
duanbanhang/
├── backend/
│   ├── app/
│   │   ├── models/          # Định nghĩa các bảng dữ liệu SQLAlchemy ORM
│   │   ├── routers/         # Các API Endpoints (auth, products, orders, reports, ai,...)
│   │   ├── schemas/         # Pydantic Schemas validate dữ liệu vào/ra
│   │   ├── services/        # Business logic: AI, Báo cáo, Tồn kho, Xuất file
│   │   ├── auth.py          # Cơ chế JWT & Middleware kiểm tra vai trò người dùng
│   │   ├── config.py        # Quản lý cấu hình & biến môi trường
│   │   ├── database.py      # Kết nối SQLAlchemy SessionLocal & Engine
│   │   ├── main.py          # Khởi tạo ứng dụng FastAPI & CORS
│   │   └── seed.py          # Script nạp dữ liệu mẫu phong phú
│   ├── tests/               # Bộ kiểm thử tự động 45 Test cases (Pytest)
│   └── requirements.txt     # Danh sách thư viện Python
├── frontend/
│   ├── src/
│   │   ├── components/      # Layout, ProtectedRoute, AuthContext
│   │   ├── pages/           # Dashboard, Products, Orders, Customers, Reports, AIChat
│   │   ├── services/        # Axios API Client & Interceptors
│   │   ├── App.jsx          # Cấu hình Routing
│   │   └── index.css        # Hệ thống giao diện Vanilla CSS responsive hiện đại
│   └── package.json         # Danh sách thư viện React & Vite
├── database/                # Lưu trữ CSDL SQLite (sales.db)
├── prompts/                 # Lưu trữ các mẫu Prompt AI và phiên bản thử nghiệm
├── docs/                    # Tài liệu báo cáo TX1, TX2, TX3, KTHP
├── .env.example             # Mẫu cấu hình môi trường
├── run.py                   # Điểm khởi chạy Backend tiện lợi
└── README.md                # Hướng dẫn cài đặt & vận hành tổng quan
```

---

## 2. Xây dựng chức năng Đăng nhập & Phân quyền (Authentication & Authorization)
- **Xác thực JWT:** Khi đăng nhập thành công (`/api/auth/login`), server cấp phát JWT Bearer Token chứa `sub` (User ID), `role` và `exp` (thời hạn 8 tiếng).
- **Mã hóa mật khẩu:** Sử dụng `passlib[bcrypt]` để băm mật khẩu một chiều, bảo vệ tuyệt đối thông tin người dùng.
- **Phân quyền đa cấp (Role-Based Access Control - RBAC):**
  - Sử dụng Dependency Injection trong FastAPI: `require_roles("admin")` và `require_roles("admin", "owner")` để chặn các hành vi trái quyền ở cấp độ API.
  - Trên Frontend: `ProtectedRoute` tự động kiểm tra token và chuyển hướng về trang Login nếu chưa đăng nhập; chỉ hiển thị menu quản lý tài khoản với vai trò Admin.

---

## 3. Hoàn thiện CRUD nghiệp vụ chính
Hệ thống đã xây dựng và kiểm thử hoàn chỉnh các chức năng CRUD:
1. **Sản phẩm & Danh mục:** Thêm mới, xem danh sách, cập nhật thông tin/giá bán, kích hoạt/ngừng kinh doanh sản phẩm.
2. **Khách hàng:** Quản lý hồ sơ khách hàng, phân loại nhóm khách hàng (`normal`, `vip`, `wholesale`), liên kết lịch sử mua hàng.
3. **Lập hóa đơn bán hàng (POS):**
   - Hỗ trợ chọn nhiều mặt hàng, tự động tính thành tiền, áp dụng chiết khấu/giảm giá.
   - Tự động trừ tồn kho theo thời gian thực.
   - Kiểm tra số lượng tồn kho trước khi tạo đơn: Báo lỗi `400 Bad Request` nếu tồn kho không đủ.
4. **Hủy đơn hàng & Hoàn tồn kho:**
   - Khi hủy đơn, hệ thống tự động hoàn lại số lượng sản phẩm vào kho hàng tương ứng.
   - Chặn không cho phép hủy đơn hàng 2 lần.
5. **Nhập hàng (Purchases):** Lập phiếu nhập kho, tự động cộng dồn số lượng tồn kho của sản phẩm.

---

## 4. Xây dựng chức năng Tìm kiếm và Lọc dữ liệu
- **Tìm kiếm đa năng:** Cho phép tìm kiếm sản phẩm theo Mã SP (`code`) hoặc Tên SP (`name`).
- **Lọc theo nhiều tiêu chí:**
  - Lọc theo Danh mục sản phẩm (`category_id`).
  - Lọc sản phẩm sắp hết hàng (`low_stock=true`, mặc định ngưỡng <= 5 sản phẩm).
  - Lọc đơn hàng theo Trạng thái (`completed`, `cancelled`), theo Phương thức thanh toán (`cash`, `card`, `banking`), và theo khoảng ngày (`date_from`, `date_to`).

---

## 5. Xây dựng Thống kê & Báo cáo cơ bản
1. **Dashboard tổng quan:**
   - Thống kê Tổng doanh thu, Tổng đơn hàng, Số khách hàng và Cảnh báo sản phẩm sắp hết hàng.
   - Danh sách 5 đơn hàng mới nhất và Top 5 sản phẩm bán chạy nhất.
2. **Báo cáo chuyên sâu:**
   - Biểu đồ và bảng doanh thu theo Ngày hoặc theo Tháng.
   - Doanh thu theo Danh mục hàng hóa.
   - Báo cáo sản phẩm bán chậm / tồn kho chưa phát sinh đơn hàng.
   - Chức năng xuất báo cáo ra các định dạng: **Excel (`.xlsx`)**, **PDF (`.pdf`)**, và **CSV (`.csv`)**.

---

## 6. Thiết kế giao diện (UI/UX)
- **Công nghệ:** React 18, Vite, Responsive CSS hiện đại, phong cách tinh gọn, trực quan.
- **Tính năng giao diện:**
  - Sidebar điều hướng tiện lợi, tự động nhận diện vai trò người dùng.
  - Các bảng dữ liệu hiển thị rõ ràng, có trạng thái màu sắc trực quan (Badge: Còn hàng, Sắp hết, Hoàn thành, Đã hủy).
  - Modal tạo đơn hàng trực tiếp, chọn sản phẩm nhanh chóng và tính tiền tức thì.
  - Toast thông báo kết quả thành công / thông báo lỗi khi thao tác thất bại.

---

## 7. Kết nối & Thao tác CSDL ổn định
- **Công nghệ CSDL:** SQLite thông qua SQLAlchemy ORM 2.0.
- **Tính ổn định & Transaction:**
  - Quản lý phiên làm việc (`SessionLocal`) thông qua cơ chế Generator `get_db()`, đảm bảo đóng kết nối an toàn sau mỗi request.
  - Mọi thao tác ghi đơn hàng và trừ kho đều được bọc trong SQLAlchemy Transaction.
- **Dữ liệu mẫu (Seed Data):**
  - Script `seed.py` tự động khởi tạo dữ liệu phong phú: 2 tài khoản mẫu (Admin & Owner), 4 danh mục, 12 sản phẩm công nghệ, 5 khách hàng và 83 đơn hàng thực tế trải dài trong 60 ngày để demo báo cáo.

---

## 8. Xử lý lỗi và kiểm soát ngoại lệ
- **Validation bằng Pydantic:** Tự động bắt lỗi định dạng dữ liệu đầu vào (ví dụ: số lượng sản phẩm <= 0, giá tiền âm, thiếu trường bắt buộc).
- **HTTP Exception chuẩn RESTful:**
  - `401 Unauthorized`: Token không hợp lệ hoặc hết hạn.
  - `403 Forbidden`: Người dùng không đủ quyền thực hiện thao tác (ví dụ: Owner cố tình tạo/xóa tài khoản người dùng).
  - `404 Not Found`: Không tìm thấy sản phẩm / đơn hàng / khách hàng.
  - `400 Bad Request`: Số lượng tồn kho không đủ, mã sản phẩm bị trùng lặp, hoặc đơn hàng đã bị hủy trước đó.
- Ứng dụng không bị crash server khi gặp ngoại lệ.

---

## 9. Minh chứng sử dụng AI khi lập trình (AI Coding Log)
- **Prompt sử dụng với AI:** *"Hãy viết hàm xử lý tạo đơn hàng trong FastAPI, yêu cầu kiểm tra số lượng tồn kho của từng sản phẩm, nếu không đủ thì báo lỗi 400 và không lưu đơn, nếu đủ thì trừ kho và lưu đơn trong cùng 1 transaction."*
- **Kết quả sinh ra từ AI:** Sinh mã nguồn hàm `create_order` với vòng lặp kiểm tra và trừ kho.
- **Phần sinh viên kiểm tra & cải tiến:** Sinh viên nhận thấy cần bổ sung trường `customer_id` tùy chọn, hỗ trợ tính giảm giá và trả về `OrderOut` schema chuẩn kèm chi tiết sản phẩm.

---

## 10. Quản lý mã nguồn & Tài liệu chạy thử
- Đã cấu hình `.gitignore` chuẩn cho Python và Node.js.
- Có sẵn file `.env.example` và hướng dẫn cài đặt chi tiết trong `README.md`.
- Cung cấp sẵn file khởi động nhanh `run.py` và script nạp dữ liệu mẫu `app.seed`.
