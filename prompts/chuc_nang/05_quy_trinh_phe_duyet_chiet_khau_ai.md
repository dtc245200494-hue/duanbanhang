# 🎯 BỘ PROMPT: QUY TRÌNH PHÊ DUYỆT ĐỀ XUẤT GIẢM GIÁ AI (AI APPROVAL WORKFLOW)

> **Chức năng:** Quản lý lịch sử các mức chiết khấu do AI sinh ra, cơ chế Human-in-the-loop: Quản lý cửa hàng (Store Manager) trực tiếp đánh giá và Duyệt (Approve) hoặc Từ chối (Reject) trước khi giá mới được áp dụng ra thị trường.  
> **Tác nhân:** Quản lý cửa hàng (Store Manager), Quản trị viên (Admin).  
> **Bảng CSDL liên quan:** `ai_discount_recommendations`, `product_batches`, `users`.

---

## 📌 1. Prompt Thiết Kế Bảng CSDL Lịch Sử & Phê Duyệt AI

### 🎯 Mục tiêu:
Thiết kế bảng `ai_discount_recommendations` lưu lại toàn bộ đề xuất, lý do, người duyệt và thời gian duyệt.

### 💬 Prompt gửi AI:
```text
Bạn là Kỹ sư Cơ sở dữ liệu và Kiến trúc sư Hệ thống. Hãy thiết kế bảng `ai_discount_recommendations` bằng SQLAlchemy 2.0:

1. Các trường dữ liệu:
   - `id`: Khóa chính Integer tự tăng.
   - `batch_id`: Khóa ngoại liên kết `product_batches.id` (ondelete="CASCADE").
   - `recommended_discount`: Tỷ lệ giảm giá do AI đề xuất (Integer, 0 - 100).
   - `reason`: Lý do chi tiết do AI phân tích và giải trình (Text).
   - `status`: Trạng thái duyệt (String 20, default "pending", các giá trị: "pending", "approved", "rejected").
   - `approved_by`: Khóa ngoại liên kết `users.id` (người thực hiện duyệt, nullable).
   - `created_at`: Thời gian đề xuất được tạo (DateTime default utcnow).
   - `updated_at`: Thời gian phê duyệt hoặc từ chối.

2. Các quan hệ:
   - `batch`: Relationship liên kết tới `ProductBatch`.
   - `approver`: Relationship liên kết tới `User`.

Đảm bảo mô hình hóa chuẩn 3NF và hỗ trợ truy vấn nhanh theo trạng thái (`status`).
```

---

## 📌 2. Prompt Viết Nghiệp Vụ Phê Duyệt (Approval Workflow Service)

### 🎯 Mục tiêu:
Viết logic khi Quản lý nhấn Duyệt -> cập nhật trạng thái đề xuất thành `approved`, gán `approved_by` = current_user.id, đồng thời tự động cập nhật trường `discount_rate` của lô hàng tương ứng. Nếu Từ chối -> cập nhật trạng thái thành `rejected` và giữ nguyên giá của lô hàng.

### 💬 Prompt gửi AI:
```text
Hãy viết lớp `RecommendationService` tại `backend/app/services/recommendation_service.py`:

1. Hàm `approve_recommendation(db: Session, rec_id: int, user_id: int) -> AIDiscountRecommendation`:
   - Tìm đề xuất theo `rec_id`. Nếu không thấy, ném lỗi 404 Not Found.
   - Kiểm tra: Nếu trạng thái không phải `pending`, ném lỗi 400 Bad Request ("Đề xuất này đã được xử lý trước đó").
   - Cập nhật đề xuất: `status = 'approved'`, `approved_by = user_id`, `updated_at = utcnow()`.
   - Cập nhật lô hàng tương ứng: `batch.discount_rate = rec.recommended_discount`.
   - Commit transaction an toàn và trả về bản ghi đề xuất.

2. Hàm `reject_recommendation(db: Session, rec_id: int, user_id: int) -> AIDiscountRecommendation`:
   - Tìm đề xuất theo `rec_id`.
   - Cập nhật đề xuất: `status = 'rejected'`, `approved_by = user_id`, `updated_at = utcnow()`.
   - Giữ nguyên `discount_rate` của lô hàng.
   - Commit transaction và trả về bản ghi.
```

---

## 📌 3. Prompt Xây Dựng RESTful API Router

### 🎯 Mục tiêu:
Cung cấp các endpoint: Lấy danh sách đề xuất (hỗ trợ lọc pending/approved/rejected), Duyệt đề xuất, Từ chối đề xuất.

### 💬 Prompt gửi AI:
```text
Hãy viết router FastAPI `api/v1/recommendations.py`:

1. `GET /api/v1/ai-recommendations`:
   - Query param: `status: Optional[str] = None`.
   - Trả về danh sách đề xuất kèm tên sản phẩm, mã lô hàng, tên người duyệt (nếu có).

2. `POST /api/v1/ai-recommendations/{id}/approve`:
   - Yêu cầu đăng nhập và phân quyền: `require_role(["admin", "store_manager"])`.
   - Gọi `RecommendationService.approve_recommendation()`.
   - Trả về thông báo thành công và đề xuất đã cập nhật.

3. `POST /api/v1/ai-recommendations/{id}/reject`:
   - Yêu cầu quyền `["admin", "store_manager"]`.
   - Gọi `RecommendationService.reject_recommendation()`.
```

---

## 📌 4. Prompt Thiết Kế Giao Diện Bảng Duyệt Đề Xuất (Approval UI)

### 🎯 Mục tiêu:
Giao diện quản lý đề xuất giảm giá AI với bộ lọc trạng thái và các nút bấm Duyệt / Từ chối 1-chạm.

### 💬 Prompt gửi AI:
```text
Hãy viết mã giao diện HTML/CSS/JS cho tab Duyệt Đề Xuất AI (Recommendations Tab):

1. Giao diện (HTML & CSS):
   - Thanh tiêu đề có dropdown lọc theo trạng thái: "Tất cả trạng thái", "⏳ Chờ duyệt (Pending)", "✓ Đã phê duyệt (Approved)", "✕ Đã từ chối (Rejected)".
   - Bảng dữ liệu:
     + Cột ID và Sản phẩm & Lô.
     + Cột Giảm Đề Xuất: Hiển thị chữ to đậm màu đỏ nổi bật (ví dụ: `-40%`).
     + Cột Lý Do: Hiển thị tóm tắt lập luận từ AI.
     + Cột Trạng Thái: Hiển thị badge có chấm phát sáng (vàng cho Chờ duyệt, xanh lá cho Đã duyệt, đỏ cho Từ chối).
     + Cột Hành Động:
       * Nếu `status == 'pending'`: Hiển thị 2 nút bấm: Nút màu xanh lá "✓ Duyệt" và nút màu đỏ "✕ Bỏ".
       * Nếu đã xử lý: Hiển thị text xám "Đã xử lý".

2. JavaScript Xử lý:
   - Hàm `handleApproveRec(id)`: Gọi API approve, hiển thị toast thông báo thành công và reload lại bảng.
   - Hàm `handleRejectRec(id)`: Gọi API reject, hiển thị toast và reload bảng.
```

---

## 📌 5. Prompt Viết Kiểm Thử Tự Động Pytest

### 🎯 Mục tiêu:
Kiểm thử luồng duyệt đề xuất làm thay đổi giá của lô hàng và luồng từ chối không làm đổi giá lô hàng.

### 💬 Prompt gửi AI:
```text
Hãy viết test cases Pytest tại `backend/tests/test_recommendation_workflow.py`:
1. `test_ai_recommendation_approval_workflow`: Tạo lô hàng với discount 0%. Tạo đề xuất AI giảm 35%. Thực hiện gọi API approve -> Xác nhận trạng thái đề xuất chuyển thành 'approved' và trường `discount_rate` của lô hàng được cập nhật chính xác thành 35.
2. `test_ai_recommendation_rejection`: Tạo đề xuất giảm 50%. Gọi API reject -> Xác nhận trạng thái đề xuất thành 'rejected' và `discount_rate` của lô hàng vẫn giữ nguyên giá trị cũ.
```
