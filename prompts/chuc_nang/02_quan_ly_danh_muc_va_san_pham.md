# 📦 BỘ PROMPT: QUẢN LÝ DANH MỤC HÀNG HÓA & SẢN PHẨM (CATEGORIES & PRODUCTS)

> **Chức năng:** Quản lý nhóm phân loại hàng hóa, thông tin sản phẩm, mã SKU, giá niêm yết gốc và số lượng tồn kho tổng hợp.  
> **Tác nhân:** Quản lý cửa hàng (Store Manager), Quản trị viên (Admin), Khách hàng (Customer xem).  
> **Bảng CSDL liên quan:** `categories`, `products`, `stores`.

---

## 📌 1. Prompt Thiết Kế Model CSDL & Quan Hệ (SQLAlchemy ORM)

### 🎯 Mục tiêu:
Thiết kế bảng `categories` và `products` có quan hệ khóa ngoại chặt chẽ, hỗ trợ thuộc tính tính toán tổng tồn kho thực tế từ các lô hàng.

### 💬 Prompt gửi AI:
```text
Bạn là chuyên gia thiết kế CSDL & Backend Python. Hãy viết SQLAlchemy 2.0 ORM Models cho 2 bảng `categories` và `products`:

1. Bảng `categories`:
   - `id`: Khóa chính Integer tự tăng.
   - `name`: Tên danh mục (String 100, không trùng lặp, không null).
   - `description`: Mô tả nhóm hàng hóa (Text, có thể null).
   - Quan hệ: `products = relationship("Product", back_populates="category", cascade="all, delete-orphan")`.

2. Bảng `products`:
   - `id`: Khóa chính Integer tự tăng.
   - `store_id`: Khóa ngoại liên kết `stores.id` (ondelete="CASCADE").
   - `category_id`: Khóa ngoại liên kết `categories.id` (ondelete="CASCADE").
   - `name`: Tên sản phẩm hàng hóa (String 255).
   - `sku`: Mã quản lý kho hàng (String 50, unique index).
   - `original_price`: Giá niêm yết ban đầu (Numeric(12, 2)).
   - `image_url`: Đường link hình ảnh sản phẩm (String 500).
   - `created_at`: Thời gian tạo sản phẩm (DateTime default utcnow).
   - Quan hệ: `batches = relationship("ProductBatch", back_populates="product")`.
   - Property `total_stock`: Thuộc tính động tính tổng tồn kho từ các lô hàng có trạng thái 'active' và tồn kho > 0.

Tuân thủ quy chuẩn PEP 8 và dùng cú pháp DeclarativeBase hiện đại của SQLAlchemy 2.0.
```

---

## 📌 2. Prompt Xây Dựng Schemas Pydantic v2 (Data Validation)

### 🎯 Mục tiêu:
Xác thực dữ liệu request và serialize response chuẩn OpenAPI 3.1.

### 💬 Prompt gửi AI:
```text
Hãy viết các Pydantic v2 schemas cho Danh mục và Sản phẩm tại `backend/app/schemas/`:

1. Schemas cho Category:
   - `CategoryCreate`: Validate tên danh mục không rỗng (1 - 100 ký tự), mô tả tùy chọn.
   - `CategoryResponse`: id, name, description, product_count (tổng số sản phẩm thuộc nhóm). Cấu hình `from_attributes = True`.

2. Schemas cho Product:
   - `ProductCreate`: store_id (int), category_id (int), name (str), sku (optional str), original_price (float > 0), image_url (optional str).
   - `ProductResponse`: Đầy đủ thông tin sản phẩm kèm `total_stock`, `category_name`, `store_name`.
```

---

## 📌 3. Prompt Xây Dựng API Endpoints (FastAPI Routers)

### 🎯 Mục tiêu:
Viết router cho phép liệt kê danh mục, tạo danh mục, tìm kiếm và thêm mới sản phẩm.

### 💬 Prompt gửi AI:
```text
Hãy tạo 2 router FastAPI: `api/v1/categories.py` và `api/v1/products.py`:

1. Router Categories:
   - `GET /api/v1/categories/`: Trả về danh sách tất cả danh mục kèm số lượng sản phẩm. Cho phép mọi người truy cập (kể cả khách vãng lai).
   - `POST /api/v1/categories/`: Tạo danh mục mới. Chỉ cho phép vai trò `["admin", "store_manager"]`.

2. Router Products:
   - `GET /api/v1/products/`: Trả về danh sách sản phẩm, hỗ trợ lọc theo `category_id`, `store_id` hoặc tìm kiếm theo từ khóa `query`.
   - `POST /api/v1/products/`: Thêm sản phẩm mới vào cửa hàng. Tự động sinh mã SKU nếu người dùng để trống. Yêu cầu quyền `["admin", "store_manager"]`.
   - `GET /api/v1/products/{id}`: Xem thông tin chi tiết một sản phẩm kèm danh sách các lô hàng hiện hành của sản phẩm đó.
```

---

## 📌 4. Prompt Thiết Kế Giao Diện Frontend (Categories & Products UI)

### 🎯 Mục tiêu:
Giao diện quản lý danh mục dạng 2 cột (Form thêm mới + Bảng danh sách) và giao diện bảng sản phẩm có nút bấm "Nhập lô mới" tiện lợi.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML/CSS/JS cho 2 màn hình Danh mục và Sản phẩm:

1. Màn hình Danh Mục (Categories Tab):
   - Layout chia 2 cột (Bên trái: Thẻ form "+ Thêm danh mục mới", Bên phải: Bảng danh sách danh mục).
   - Khi đăng nhập bằng tài khoản Customer: Form thêm mới tự động ẩn đi và bảng danh mục mở rộng toàn màn hình (Responsive 1 cột).

2. Màn hình Sản Phẩm (Products Tab):
   - Nút "+ Thêm Sản Phẩm Mới" ở góc trên bên phải kích hoạt Modal form nhập liệu.
   - Bảng dữ liệu sản phẩm hiển thị: ID, Tên & SKU, Giá niêm yết gốc (định dạng tiền tệ VNĐ), Tổng tồn kho còn lại, và cột Hành động chứa nút "+ Nhập Lô Mới" (kích hoạt Modal mở thêm lô cho đúng sản phẩm đó).
   - Sử dụng icon SVG Lucide (Tag, Package, Plus).
```

---

## 📌 5. Prompt Viết Kiểm Thử Tự Động Pytest

### 🎯 Mục tiêu:
Kiểm thử tính toàn vẹn quan hệ giữa danh mục và sản phẩm, kiểm thử xóa cascade.

### 💬 Prompt gửi AI:
```text
Hãy viết test case Pytest tại `backend/tests/test_categories.py`:
- Tạo 1 danh mục mới qua API hoặc DB Session.
- Thêm 2 sản phẩm thuộc về danh mục đó.
- Kiểm tra `product_count` của danh mục có đúng bằng 2 không.
- Kiểm tra thuộc tính `total_stock` khi sản phẩm chưa có lô hàng thì trả về 0.
```
