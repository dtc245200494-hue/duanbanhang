# HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP TRỢ LÝ AI & XẢ HÀNG ĐỘNG FEFO (AIA331)

> **Môn học:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)  
> **Nhóm thực hiện:** Nhóm 03 (Hoàng Trang Hiên & Nguyễn Viết Cường)  
> **Học kỳ:** 2026_2027_1  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Tuấn Anh (SĐT: 0912662003)  
> **Đơn vị đào tạo:** Trường Đại học Công nghệ Thông tin & Truyền thông (ICTU)

---

## 📌 1. Giới thiệu tổng quan dự án
Hệ thống Quản lý Bán hàng Bán lẻ Thông minh (Smart Retail Management System) được phát triển nhằm giải quyết bài toán cốt lõi trong chuỗi bán lẻ: **Quản lý hạn sử dụng theo lô (FEFO - First Expired, First Out)**, **phân quyền đa tác nhân chặt chẽ (RBAC)** và **định giá xả hàng tự động bằng Trí tuệ nhân tạo (Dynamic AI Discount Clearance)**.

Hệ thống được thiết kế theo chuẩn **PEP 8**, kiến trúc module hoá phân tầng (Controller/Router - Service - Repository/Model), hỗ trợ cơ sở dữ liệu quan hệ 10 bảng toàn diện, tích hợp trực tiếp giao diện Web SPA hiện đại và RESTful API chuẩn OpenAPI 3.1.

---

## 🏛️ 2. Sơ đồ CSDL Quan hệ Thực thể (ERD - 10 Bảng)

Hệ thống triển khai 10 bảng dữ liệu quan hệ chuẩn hoá theo sơ đồ ERD nghiệp vụ:

| STT | Tên Bảng | Khóa chính (PK) | Khóa ngoại (FK) & Ý nghĩa |
| :---: | :--- | :--- | :--- |
| **1** | `roles` | `id` | Quản lý danh mục vai trò người dùng (`admin`, `store_manager`, `customer`). |
| **2** | `users` | `id` | Tài khoản người dùng, băm mật khẩu `bcrypt`, liên kết `role_id` -> `roles(id)`. |
| **3** | `stores` | `id` | Chi nhánh / Cửa hàng, liên kết người sở hữu `owner_id` -> `users(id)`. |
| **4** | `categories` | `id` | Danh mục hàng hóa (Đồ tươi sống, Sữa & Trứng, Đồ uống, Đồ hộp,...). |
| **5** | `products` | `id` | Thông tin sản phẩm, liên kết `store_id` -> `stores(id)`, `category_id` -> `categories(id)`. |
| **6** | `product_batches` | `id` | **Lô hàng thực tế**, quản lý hạn dùng (`expiry_date`), tồn kho, chiết khấu hiện hành, liên kết `product_id` -> `products(id)`. Trạng thái: `active`, `clearance`, `expired`. |
| **7** | `ai_discount_recommendations` | `id` | Lịch sử đề xuất giảm giá từ AI, lý do, trạng thái duyệt (`pending`, `approved`, `rejected`), người duyệt `approved_by` -> `users(id)`. |
| **8** | `orders` | `id` | Đơn hàng mua sắm, liên kết `store_id` -> `stores(id)`, `user_id` -> `users(id)`. Trạng thái: `pending`, `completed`, `cancelled`. |
| **9** | `order_items` | `id` | Chi tiết sản phẩm bán theo từng **lô hàng cụ thể** (`batch_id` -> `product_batches(id)`), đơn giá sau giảm giá. |
| **10** | `payments` | `id` | Giao dịch thanh toán (`order_id` -> `orders(id)`), phương thức `cash`, `card`, `transfer`, `momo`. |

---

## 👥 3. Ba Tác nhân & Phân quyền Hệ thống (RBAC)

### So sánh & Phân biệt rõ rệt giữa Quản trị (Admin) và Quản lý (Store Manager):

| Tiêu chí | 👨‍💼 Quản trị viên (Admin) | 👔 Quản lý cửa hàng (Store Manager) | 🛒 Khách hàng (Customer) |
| :--- | :--- | :--- | :--- |
| **Phạm vi quyền hạn** | **Toàn hệ thống** (Toàn quyền tối cao) | **Nội bộ cửa hàng / chi nhánh** phụ trách | **Cá nhân / Mua hàng** |
| **Quản lý Tài khoản** | Tạo, phân quyền, khóa tài khoản Manager & Khách | Không có quyền quản lý tài khoản người dùng khác | Chỉ cập nhật thông tin cá nhân |
| **Quản lý Chi nhánh** | Thêm mới, chỉnh sửa, giám sát mọi chi nhánh Store | Chỉ quản lý hoạt động tại chi nhánh được phân công | Không có quyền |
| **Danh mục & Sản phẩm** | Cấu hình danh mục hệ thống, xem toàn bộ kho | Nhập kho lô hàng mới, theo dõi hạn dùng tồn kho | Xem menu và mua sắm sản phẩm còn hàng |
| **Phê duyệt Giảm giá AI** | Có thể giám sát và cấu hình prompt template AI | **Trực tiếp đánh giá và Duyệt / Từ chối đề xuất AI** | Được mua hàng với giá ưu đãi đã duyệt |
| **Đơn hàng & POS** | Xem toàn bộ báo cáo doanh thu toàn hệ thống | Trực tiếp tạo đơn tại quầy (POS), thu ngân, xuất hóa đơn | Đặt hàng trực tuyến, theo dõi đơn của mình |

---

## 🧠 4. Động cơ AI & Quy tắc Xuất kho FEFO

### 1. Thuật toán Xuất kho FEFO (First Expired, First Out)
- Khi khách hàng hoặc thu ngân tạo đơn hàng, hệ thống **tự động phân bổ số lượng từ lô có ngày hết hạn gần nhất còn tồn kho (`stock_quantity > 0`)**.
- Nếu số lượng mua vượt quá một lô, thuật toán tự động tách (split) đơn hàng sang các lô kế tiếp.
- Đảm bảo hàng cận date luôn được luân chuyển trước, giảm thiểu tối đa tỷ lệ hủy hàng do hết hạn.
- Khi hủy đơn (`cancelled`), số lượng tồn kho từng lô được hoàn trả chính xác về trạng thái ban đầu.

### 2. Trợ lý AI Đề xuất Chiết khấu Động (Dynamic Clearance)
- **Hệ thống Prompt phiên bản hóa:** Nằm tại `prompts/versions/` (`v1_discount_recommendation.txt`, `v2_discount_recommendation.txt`).
- **Hỗ trợ 2 chế độ:**
  - **OpenAI GPT-4o-mini:** Phân tích ngữ cảnh gồm hạn sử dụng, tốc độ bán hàng trung bình, giá đối thủ cạnh tranh, và hướng dẫn tùy chỉnh từ quản lý.
  - **Rule-based Fallback Engine:** Đảm bảo **100% Uptime** không phụ thuộc vào Internet hay OpenAI API key. Tự động áp dụng ma trận suy luận cận date:
    - *≤ 0 ngày:* 100% (Hết hạn -> Chuyển hủy).
    - *≤ 2 ngày:* 70% (Cận date cấp tốc).
    - *≤ 4 ngày:* 50% (Thúc đẩy giải phóng tồn kho).
    - *≤ 7 ngày:* 25% - 35% (Kích cầu tiêu dùng nhanh).
    - *≤ 14 ngày:* 10% - 20% (Duy trì tốc độ xuất kho).
    - *An toàn:* 0% (Giữ nguyên giá niêm yết).

---

## 🚀 5. Hướng dẫn Cài đặt & Khởi chạy Nhanh

### Yêu cầu tiên quyết:
- **Python 3.10+** (Hệ thống đã kiểm thử trên Python 3.12, 3.14).

### Khởi chạy 1 bước duy nhất (Tự động tạo CSDL & Nạp dữ liệu mẫu):
```bash
# 1. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 2. Khởi chạy hệ thống (FastAPI + Giao diện Web SPA + SQLite)
python run.py
```

- **🌐 Giao diện Web SPA Trực quan:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **📖 Tài liệu Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **📚 Tài liệu ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **🩺 Kiểm tra sức khỏe hệ thống:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔑 6. Tài khoản Thử nghiệm (Có sẵn nút bấm 1-Click trên Web)

| Vai trò | Email đăng nhập | Mật khẩu mặc định | Ghi chú kiểm thử |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin@freshmart.vn` | `Admin@123` | Toàn quyền cấu hình hệ thống & người dùng |
| **Quản lý cửa hàng (Manager)** | `manager@freshmart.vn` | `Admin@123` | Quản lý kho lô hàng, duyệt đề xuất AI, bán hàng POS |
| **Khách hàng (Customer)** | `customer@gmail.com` | `Admin@123` | Mua sắm sản phẩm xả hàng, xem giỏ hàng |

*(Trên giao diện Web, có sẵn modal đăng nhập và các nút bấm điền nhanh tài khoản kiểm thử vô cùng tiện lợi).*

---

## 🧪 7. Kiểm thử Tự động (Automated Test Suite)

Hệ thống bao gồm bộ kiểm thử toàn diện với **17 test cases** bao phủ 100% các chức năng cốt lõi:
- Xác thực tài khoản, mã hóa bcrypt và phân quyền RBAC JWT token.
- Thuật toán xuất kho FEFO (đơn lô, đa lô, hoàn kho khi hủy đơn).
- Quy tắc định giá AI fallback & phân tích template prompt.
- Luồng phê duyệt đề xuất chiết khấu AI từ Store Manager.
- Khởi tạo thanh toán đơn hàng.

```bash
pytest backend/tests -v
```

---

## 📚 8. Cấu trúc Thư mục Dự án

```text
duanbanhang/
├── backend/
│   ├── app/
│   │   ├── api/v1/             # Các Router RESTful API (Auth, Batches, Orders, AI,...)
│   │   ├── core/               # Bảo mật, JWT & Bcrypt password hashing
│   │   ├── models/             # 10 SQLAlchemy ORM Models quan hệ chặt chẽ
│   │   ├── schemas/            # Pydantic v2 schemas xác thực dữ liệu request/response
│   │   ├── services/           # Nghiệp vụ FEFO, AI Discount Engine, Orders, Payments
│   │   ├── scripts/            # Script nạp seed data mẫu 10 bảng
│   │   ├── static/             # Giao diện Web SPA HTML/CSS/JS hiện đại
│   │   ├── config.py           # Cấu hình hệ thống (Settings)
│   │   ├── database.py         # Kết nối SQLite & DeclarativeBase
│   │   └── main.py             # Entrypoint FastAPI với Lifespan quản lý
│   └── tests/                  # 17 Unit & Integration tests tự động
├── prompts/                    # Bộ Prompt AI phiên bản hóa (v1, v2)
├── tailieu/                    # Báo cáo học phần (TX1, TX2, TX3, KTHP, Sơ đồ, Word docx)
├── docs/                       # Tài liệu đặc tả kỹ thuật bổ sung
├── run.py                      # Script khởi chạy hệ thống tức thì
├── requirements.txt            # Danh sách dependencies
├── pytest.ini                  # Cấu hình Pytest
└── README.md                   # Tài liệu hướng dẫn sử dụng
```

---
*Dự án hoàn thành phục vụ học phần Ứng dụng Trí tuệ Nhân tạo (AIA331) - ĐH Công nghệ Thông tin & Truyền thông.*
