# 📁 TỔNG HỢP TÀI LIỆU DỰ ÁN QUẢN LÝ BÁN HÀNG TÍCH HỢP AI (AIA331)

> **Học phần:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)  
> **Nhóm thực hiện:** Nhóm 03  
> **Thành viên:** Hoàng Trang Hiên (Trưởng nhóm) \| Nguyễn Viết Cường  
> **Học kỳ:** 2026_2027_1  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Tuấn Anh (0912662003)  
> **Cơ sở đào tạo:** Đại học Công nghệ Thông tin & Truyền thông (ICTU)  

---

## 📑 Danh mục tài liệu báo cáo học phần

| STT | Tài liệu | Mô tả nội dung | Liên kết |
| :---: | :--- | :--- | :--- |
| 1 | **Sơ đồ thiết kế hệ thống** | **Trọn bộ sơ đồ kỹ thuật chuẩn Mermaid:** Sơ đồ Use Case, CSDL ERD, Kiến trúc 3 tầng, 4 Luồng hoạt động (Activity), 3 Sơ đồ tuần tự (Sequence), Luồng dữ liệu (DFD Cấp 0 & 1), Sơ đồ triển khai. | [SO_DO_THIET_KE_HE_THONG.md](./SO_DO_THIET_KE_HE_THONG.md) |
| 2 | **Báo cáo TX1** | **Phân tích & Thiết kế hệ thống:** Yêu cầu chức năng/phi chức năng, Use Case, Sơ đồ ERD, Luồng xử lý AI, Thiết kế giao diện UI/UX. | [BAO_CAO_TX1_PHAN_TICH_THIET_KE.md](./BAO_CAO_TX1_PHAN_TICH_THIET_KE.md) |
| 3 | **Báo cáo TX2** | **Lập trình hệ thống quản lý:** Cấu trúc Backend FastAPI, SQLite + SQLAlchemy ORM, Frontend React 18, Nghiệp vụ POS, Quản lý kho, Xuất báo cáo. | [BAO_CAO_TX2_LAP_TRINH_HE_THONG.md](./BAO_CAO_TX2_LAP_TRINH_HE_THONG.md) |
| 4 | **Báo cáo TX3** | **Tích hợp & Tối ưu hóa AI:** Trợ lý tư vấn sản phẩm, Phân tích kinh doanh, Prompt Engineering & Quản lý phiên bản, Che giấu dữ liệu (Data Masking), Rate limit & Error handling. | [BAO_CAO_TX3_TICH_HOP_AI.md](./BAO_CAO_TX3_TICH_HOP_AI.md) |
| 5 | **Báo cáo KTHP** | **Tổng kết dự án & Kịch bản Demo:** Kiến trúc tổng thể, Đánh giá kết quả đạt được, Kịch bản thuyết trình và Demo chi tiết 7 bước khi chấm thi. | [BAO_CAO_KTHP_VA_KICH_BAN_DEMO.md](./BAO_CAO_KTHP_VA_KICH_BAN_DEMO.md) |
| 6 | **Tổng hợp Prompt AI (3 Giai đoạn)** | **Nhật ký minh chứng Prompting chuyên sâu:** Ứng dụng mô hình phân vai 5 Chuyên gia AI (BA, Architect, UI/UX, Dev, QA) sinh ERD, Wireframe, code CRUD, debug lệch kho và đối chiếu 3 phiên bản Prompt. | [TONG_HOP_PROMPT_AI_PHAT_TRIEN_DU_AN.md](./TONG_HOP_PROMPT_AI_PHAT_TRIEN_DU_AN.md) |

---

## 🚀 Tóm tắt hướng dẫn khởi chạy nhanh

### 1. Khởi động Backend (FastAPI - Cổng 8000)
```powershell
backend\.venv\Scripts\python.exe run.py
```
- Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Khởi động Frontend (React / Vite - Cổng 5173)
```powershell
cd frontend
npm.cmd run dev
```
- Giao diện người dùng: [http://localhost:5173](http://localhost:5173)

### 3. Tài khoản kiểm thử
- **Admin:** `admin` / `admin123` (Toàn quyền hệ thống, quản lý tài khoản, báo cáo, AI)
- **Chủ cửa hàng (Owner):** `owner` / `owner123` (Quản lý sản phẩm, bán hàng POS, xem dashboard, hỏi đáp AI)

### 4. Chạy kiểm thử tự động (Unit & Integration Tests)
```powershell
backend\.venv\Scripts\pytest.exe backend\tests -v
```
