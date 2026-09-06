# HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP TRỢ LÝ AI (AIA331)

> **Môn học:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)  
> **Nhóm thực hiện:** Nhóm 03  
> **Học kỳ:** 2026_2027_1  
> **Giảng viên hướng dẫn:** Nguyễn Tuấn Anh (SĐT: 0912662003)  
> **Trường:** Đại học Công nghệ Thông tin & Truyền thông (ICTU)

---

## 📌 1. Giới thiệu dự án
Hệ thống quản lý bán hàng đa kênh cho cửa hàng thiết bị công nghệ và phụ kiện, tích hợp trợ lý AI thông minh (OpenAI GPT-4o-mini). Hệ thống đáp ứng đầy đủ quy trình bán hàng (POS), quản lý kho, nhập hàng, phân tích báo cáo doanh thu và ứng dụng AI hỗ trợ tư vấn bán hàng, hỏi đáp số liệu kinh doanh.

### 🌟 Tính năng nổi bật:
- **Xác thực & Phân quyền đa vai trò:** Admin (Quản trị viên), Chủ cửa hàng (Owner kiêm Quản lý & Bán hàng POS) với JWT token & mã hóa mật khẩu bảo mật.
- **Nghiệp vụ Bán hàng & Quản lý:** Quản lý danh mục, sản phẩm, khách hàng, đơn hàng, phiếu nhập kho, điều chỉnh tồn kho tự động.
- **Báo cáo & Phân tích:** Thống kê doanh thu theo ngày/tháng, Top sản phẩm bán chạy, sản phẩm tồn kho chậm luân chuyển; xuất báo cáo Excel, CSV, PDF.
- **Trợ lý AI tích hợp (AI-Powered Assistant):**
  - **Tư vấn sản phẩm thông minh:** Khai thác dữ liệu thời gian thực của kho hàng, chỉ gợi ý sản phẩm còn hàng (`stock > 0`), che giấu thông tin nhạy cảm khách hàng (Data Masking).
  - **Phân tích báo cáo kinh doanh:** Tóm tắt tình hình doanh số, nhận định xu hướng và khuyến nghị chiến lược.
  - **Hỏi đáp quản lý (Business Q&A):** Giải đáp thắc mắc của chủ cửa hàng dựa trên số liệu kinh doanh thực tế.

---

## 🏗️ 2. Kiến trúc & Công nghệ
- **Backend:** Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, Uvicorn, Jose JWT, Pytest.
- **Database:** SQLite (Relational DB với `sales.db`), hỗ trợ migration và seed data tự động.
- **Frontend:** React 18, Vite, React Router DOM, Axios, Vanilla Modern CSS Responsive.
- **AI Integration:** OpenAI API / LLM Wrapper với hệ thống quản lý Prompt phiên bản hóa (`prompts/versions/`), cơ chế Rate Limiting, Timeout và Error Handling.

---

## 🚀 3. Hướng dẫn cài đặt & Khởi chạy

### Yêu cầu hệ thống:
- Python 3.10+ (Đã có sẵn môi trường `.venv` trong thư mục `backend`)
- Node.js 18+ và npm

### Bước 1: Cấu hình biến môi trường
Kiểm tra file `.env` tại thư mục gốc của dự án:
```ini
DATABASE_URL=sqlite:///./database/sales.db
OPENAI_API_KEY=your_api_key_here
SECRET_KEY=aia331-sales-secret-2026
OPENAI_MODEL=gpt-4o-mini
```

### Bước 2: Nạp dữ liệu mẫu (Seed Data)
```powershell
cd backend
.venv\Scripts\python.exe -m app.seed
cd ..
```

### Bước 3: Khởi động Backend API (Port 8000)
Mở cửa sổ Terminal 1:
```powershell
backend\.venv\Scripts\python.exe run.py
```
- **API Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Kiểm tra Health:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Bước 4: Khởi động Frontend (Port 5173)
Mở cửa sổ Terminal 2:
```powershell
cd frontend
npm.cmd run dev
```
- **Giao diện Web:** [http://localhost:5173](http://localhost:5173)

---

## 🔑 4. Tài khoản Demo kiểm thử

| Tên đăng nhập | Mật khẩu | Vai trò | Quyền hạn chính |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Quản trị viên (Admin)** | Toàn quyền hệ thống, quản lý tài khoản, sản phẩm, xem báo cáo, dùng AI |
| `owner` | `owner123` | **Chủ cửa hàng (Owner)** | Quản lý sản phẩm, bán hàng POS, xem dashboard doanh thu, dùng AI phân tích |

---

## 🧪 5. Chạy Kiểm thử tự động (Unit / Integration Tests)
Chạy bộ test 45/45 test cases bao gồm xác thực, nghiệp vụ kho, đơn hàng, báo cáo và AI:
```powershell
backend\.venv\Scripts\pytest.exe backend\tests -v
```

---

## 📚 6. Hệ thống Tài liệu đánh giá
Bộ tài liệu chi tiết phục vụ các bài đánh giá học phần đặt tại thư mục [tailieu/](file:///d:/duanbanhang/tailieu/):
- [Tổng hợp & Mục lục tài liệu](file:///d:/duanbanhang/tailieu/README.md)
- [Báo cáo TX1 - Phân tích & Thiết kế hệ thống](file:///d:/duanbanhang/tailieu/BAO_CAO_TX1_PHAN_TICH_THIET_KE.md)
- [Báo cáo TX2 - Lập trình hệ thống quản lý](file:///d:/duanbanhang/tailieu/BAO_CAO_TX2_LAP_TRINH_HE_THONG.md)
- [Báo cáo TX3 - Tích hợp & Tối ưu hóa AI](file:///d:/duanbanhang/tailieu/BAO_CAO_TX3_TICH_HOP_AI.md)
- [Báo cáo KTHP & Kịch bản thuyết trình Demo](file:///d:/duanbanhang/tailieu/BAO_CAO_KTHP_VA_KICH_BAN_DEMO.md)
