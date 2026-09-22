# 📁 DANH MỤC PROMPT PHÁT TRIỂN DỰ ÁN THEO TỪNG CHỨC NĂNG (AIA331)

Thư mục này tổng hợp toàn bộ các bộ **Prompt chuẩn hóa** được phân chia độc lập theo từng chức năng nghiệp vụ của hệ thống **SmartRetail AI - Quản lý Bán lẻ & Xả hàng Động FEFO**.

Mỗi chức năng được đóng gói trong một file Markdown riêng biệt, bao gồm đầy đủ 5 giai đoạn: Thiết kế CSDL & Model -> Logic Nghiệp vụ & Thuật toán -> RESTful API Router -> Giao diện Web SPA (UI/UX Pro Max) -> Bộ kiểm thử tự động (Pytest).

---

## 🗂️ Danh Sách Chi Tiết Từng Chức Năng (10 Tệp Markdown)

| STT | Tên Tệp Markdown | Chức Năng Nghiệp Vụ Chính | Tác Nhân & Phân Quyền |
| :---: | :--- | :--- | :--- |
| **01** | [`01_xac_thuc_va_phan_quyen_rbac.md`](./01_xac_thuc_va_phan_quyen_rbac.md) | Đăng nhập, Đăng ký, Mã hóa `bcrypt`, JWT Token & Phân quyền RBAC 3 cấp. | Admin, Store Manager, Customer |
| **02** | [`02_quan_ly_danh_muc_va_san_pham.md`](./02_quan_ly_danh_muc_va_san_pham.md) | Quản lý danh mục hàng hóa (Categories) & Thông tin sản phẩm (Products), SKU, giá niêm yết. | Store Manager, Admin, Customer |
| **03** | [`03_quan_ly_lo_hang_va_xuat_kho_fefo.md`](./03_quan_ly_lo_hang_va_xuat_kho_fefo.md) | Quản lý lô hàng cận date, Hạn dùng (`expiry_date`) & Thuật toán xuất kho **FEFO** tự động. | Store Manager, Customer |
| **04** | [`04_tro_ly_ai_dinh_gia_xa_hang_dong.md`](./04_tro_ly_ai_dinh_gia_xa_hang_dong.md) | Trợ lý AI định giá xả hàng động (**GPT-4o-mini & Rule-Based Fallback Engine 100% Uptime**). | Store Manager, Admin |
| **05** | [`05_quy_trinh_phe_duyet_chiet_khau_ai.md`](./05_quy_trinh_phe_duyet_chiet_khau_ai.md) | Quy trình phê duyệt đề xuất chiết khấu AI (**Approval Workflow - Duyệt / Từ chối**). | Store Manager, Admin |
| **06** | [`06_ban_hang_pos_va_dat_hang_truc_tuyen.md`](./06_ban_hang_pos_va_dat_hang_truc_tuyen.md) | Bán hàng trực tiếp (POS), Đặt hàng online, trừ kho theo lô và Live Receipt Preview. | Store Manager, Customer |
| **07** | [`07_quan_ly_giao_dich_thanh_toan.md`](./07_quan_ly_giao_dich_thanh_toan.md) | Quản lý giao dịch thanh toán đa phương thức (COD, MoMo, VNPAY, Chuyển khoản ngân hàng). | Store Manager, Admin, Customer |
| **08** | [`08_quan_tri_nguoi_dung_he_thong.md`](./08_quan_tri_nguoi_dung_he_thong.md) | Giám sát tài khoản, vai trò và phạm vi phân quyền toàn hệ thống (Dành riêng cho Admin). | Admin Only |
| **09** | [`09_kiem_thu_tu_dong_pytest.md`](./09_kiem_thu_tu_dong_pytest.md) | Bộ kiểm thử tự động toàn diện với **17 Test Cases Pytest** (Auth, FEFO, AI, Orders). | QA, Developer |
| **10** | [`10_thiet_ke_giao_dien_ui_ux_pro_max.md`](./10_thiet_ke_giao_dien_ui_ux_pro_max.md) | Thiết kế giao diện Web SPA: Bento Box Grid, Dark/Light Mode, Lucide SVG, Mobile Drawer. | Toàn hệ thống |

---

## 💡 Phương Pháp Sử Dụng Prompt Đạt Hiệu Quả Cao Nhất (Prompt Engineering Framework)

Khi sử dụng các prompt này với bất kỳ mô hình LLM nào (ChatGPT, Claude, Gemini, Cursor, Copilot), bạn nên tuân thủ công thức **C-R-T-C-O**:

1. **C - Context (Bối cảnh):** Cung cấp cấu trúc công nghệ của dự án (FastAPI, SQLAlchemy 2.0, SQLite, Vanilla CSS/JS SPA).
2. **R - Role (Vai trò):** Giao vai trò chuyên gia cụ thể (Lead Backend Engineer, UI/UX Designer, QA Automation).
3. **T - Task (Nhiệm vụ cụ thể):** Mô tả rõ ràng chức năng cần sinh mã hoặc giải quyết.
4. **C - Constraints (Ràng buộc):** Ràng buộc về thư viện, thuật toán (FEFO không được âm kho, không dùng emoji làm icon, băm mật khẩu bcrypt).
5. **O - Output Format (Định dạng đầu ra):** Yêu cầu trả về mã nguồn đầy đủ, type hints, docstring hoặc JSON schema hợp lệ.

---
*Thư mục được xây dựng phục vụ học phần Ứng dụng Trí tuệ Nhân tạo (AIA331) - ĐH Công nghệ Thông tin & Truyền thông (ICTU).*
