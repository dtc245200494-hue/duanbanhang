# 🎨 BỘ PROMPT: THIẾT KẾ GIAO DIỆN WEB SPA THEO CHUẨN UI/UX PRO MAX

> **Chức năng:** Xây dựng hệ thống giao diện Web Single Page Application (SPA) hiện đại, đẳng cấp cao theo tiêu chuẩn **UI/UX Pro Max**: Bento Box Grid, Dark/Light Mode, Lucide SVG Icons, Glassmorphism, Micro-interactions và chuẩn tiếp cận WCAG 4.5:1.  
> **Tác nhân:** Toàn bộ người dùng hệ thống.  
> **Thư mục liên quan:** `backend/app/static/css/`, `backend/app/static/js/`, `backend/app/static/index.html`.

---

## 📌 1. Prompt Xây Dựng Hệ Thống Design System & Bảng Màu (CSS Tokens)

### 🎯 Mục tiêu:
Thiết kế bộ biến CSS Variables hỗ trợ chuyển đổi linh hoạt giữa Chế độ Sáng (mặc định) và Chế độ Tối, sử dụng bảng màu tươi sáng chuẩn ngành bán lẻ thực phẩm.

### 💬 Prompt gửi AI:
```text
Bạn là Giám đốc Thiết kế Giao diện (Lead UI/UX Designer & Design System Architect) áp dụng tiêu chuẩn UI/UX Pro Max.
Hãy viết file `backend/app/static/css/styles.css` định nghĩa toàn bộ Design System cho ứng dụng SmartRetail:

1. Nguyên tắc màu sắc (Color Tokens):
   - Mặc định là Chế độ Sáng (`:root, [data-theme="light"]`):
     + Nền chính: Trắng sáng tinh khôi xen kẽ xám slate nhẹ (`--bg-base: #f8fafc`, `--bg-surface: #ffffff`).
     + Màu thương hiệu bán lẻ tươi sống: Xanh ngọc lục bảo Emerald (`--primary: #059669`, hover: `#047857`).
     + Màu nhấn Trí tuệ Nhân tạo: Xanh tím Indigo (`--ai-accent: #4f46e5`).
     + Màu trạng thái: Thành công xanh ngọc (`#059669`), Cảnh báo hổ phách (`#d97706`), Báo động đỏ (`#dc2626`).
     + Đảm bảo độ tương phản chữ trên nền tối thiểu 4.5:1 (WCAG AA).
   - Chế độ Tối (`[data-theme="dark"]`):
     + Nền đêm sâu thẳm (`--bg-base: #080c15`, `--bg-surface: #0f172a`).
     + Màu thương hiệu: `#10b981`, Màu AI: `#6366f1`.

2. Bố cục & Hiệu ứng (Layout & Effects):
   - Bento Box Grid cho các khối thống kê: Thẻ có bo góc tròn mềm mại `border-radius: 16px`, đường viền bán trong suốt `border: 1px solid var(--border-card)`.
   - Hiệu ứng đổ bóng nhiều lớp (multi-layered shadow) và hiệu ứng kính mờ Glassmorphism (`backdrop-filter: blur(16px)`).
   - Dải viền phát sáng (glowing line) trên đỉnh mỗi thẻ KPI phản ánh trạng thái ngữ cảnh.

3. Tương tác vi mô (Micro-interactions):
   - Nút bấm và thẻ card có hiệu ứng hover nâng nhẹ: `transform: translateY(-2px); transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1)`.
   - Hiệu ứng nhấp nháy cho đèn báo động đỏ khẩn cấp: `@keyframes pulse-dot`.
```

---

## 📌 2. Prompt Chuyển Đổi Hoàn Toàn Emoji Sang Inline SVG (No-Emoji Rule)

### 🎯 Mục tiêu:
Loại bỏ anti-pattern sử dụng emoji làm icon chức năng. Thay thế toàn bộ bằng các biểu tượng vector SVG Lucide chuẩn, có độ dày nét `stroke-width: 2` đồng nhất và kích thước tỉ lệ `1.15em`.

### 💬 Prompt gửi AI:
```text
Trong file `backend/app/static/index.html`, hãy rà soát và thay thế toàn bộ emoji (📊, ⚡, 🎯, 🏷️, 📦, 🛍️, 📋, 💳, 👥, 🚪, 🔑, ⏳, 🚨, 💰, 🤖) bằng bộ icon vector SVG inline chuẩn Lucide:

1. Icon Điều hướng (Navigation):
   - Tổng quan: SVG Layout Dashboard (4 ô lưới).
   - Lô cận date: SVG Zap (Tia sét).
   - Duyệt đề xuất AI: SVG Sparkles (Ngôi sao lấp lánh).
   - Danh mục: SVG Tag.
   - Sản phẩm: SVG Package (Hộp hàng).
   - POS: SVG Shopping Cart.
   - Đơn hàng: SVG Clipboard Check.
   - Thanh toán: SVG Credit Card.
   - Quản trị: SVG Shield User.

2. Icon Thao tác & Trạng thái:
   - Đổi theme: SVG Sun & Moon.
   - Xác nhận: SVG Check Circle.
   - Hủy bỏ: SVG X Circle.
   - Báo động: SVG Alert Triangle.

Yêu cầu: Tất cả SVG đều có `class="svg-icon"`, `stroke="currentColor"`, `fill="none"`, căn chỉnh thẳng hàng với chữ (`vertical-align: -0.18em`).
```

---

## 📌 3. Prompt Xây Dựng Trải Nghiệm POS Chia Cột & Hóa Đơn Xem Trước

### 🎯 Mục tiêu:
Thiết kế giao diện Bán hàng POS chuẩn thương mại điện tử với phiếu hóa đơn xem trước (Live Receipt Card) tự động cập nhật.

### 💬 Prompt gửi AI:
```text
Hãy thiết kế bố cục màn hình POS Checkout kết hợp phong cách Bento Box và Live Receipt:
- Cột bên trái: Thẻ chứa Form đặt hàng với các trường nhập liệu chuẩn (Chi nhánh xuất, Tên người nhận, SĐT, Địa chỉ, Phương thức thanh toán, Dropdown chọn sản phẩm kèm thông tin tồn kho và giá niêm yết, Số lượng đặt).
- Cột bên phải: Thẻ Hóa Đơn Xuất Kho FEFO có viền nét đứt (dashed border).
  + Khi người dùng đổi sản phẩm, số lượng hoặc phương thức thanh toán: JavaScript tự động tính toán và cập nhật ngay tên món, số lượng, phương thức thanh toán và tổng tiền dự kiến lên hóa đơn bên phải.
  + Gắn huy hiệu xanh "Tự động FEFO" nhấn mạnh việc hệ thống tự động chọn lô hàng có giá ưu đãi tốt nhất cho khách.
```

---

## 📌 4. Prompt Thiết Kế Đáp Ứng Di Động (Responsive Mobile & Drawer)

### 🎯 Mục tiêu:
Đảm bảo giao diện hiển thị mượt mà trên tất cả kích thước màn hình từ điện thoại 375px, máy tính bảng 768px đến màn hình máy tính 1440px.

### 💬 Prompt gửi AI:
```text
Hãy bổ sung mã CSS Media Queries và JavaScript để xử lý hiển thị trên thiết bị di động:
1. Header Di Động:
   - Ẩn trên màn hình máy tính (`display: none`), tự động hiển thị trên màn hình nhỏ (<= 768px).
   - Chứa logo rút gọn, tên ứng dụng và nút bấm Menu Hamburger 3 gạch.
2. Ngăn kéo Sidebar (Drawer):
   - Trên mobile: Mặc định ẩn ra ngoài mép màn hình (`transform: translateX(-100%)`).
   - Khi bấm Hamburger: Thêm class `mobile-open` để trượt ra mượt mà (`transform: translateX(0)`).
   - Lớp phủ mờ (Backdrop overlay): Nhấp vào nền mờ tự động đóng sidebar.
   - Khi người dùng bấm chuyển tab trên Sidebar: Tự động đóng sidebar để người dùng xem ngay nội dung.
```
