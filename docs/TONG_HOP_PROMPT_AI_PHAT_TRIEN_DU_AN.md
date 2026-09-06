# 📁 TỔNG HỢP PROMPT & MINH CHỨNG SỬ DỤNG TRÍ TUỆ NHÂN TẠO (AI) TRONG PHÁT TRIỂN DỰ ÁN

> **Học phần:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)  
> **Đề tài:** Hệ thống quản lý bán hàng đa kênh cho cửa hàng thiết bị công nghệ & phụ kiện tích hợp trợ lý AI  
> **Nhóm thực hiện:** Nhóm 03  
> **Thành viên:** Hoàng Trang Hiên (Trưởng nhóm) \| Nguyễn Viết Cường  
> **Giảng viên hướng dẫn:** ThS. Nguyễn Tuấn Anh (0912662003)  
> **Cơ sở đào tạo:** Đại học Công nghệ Thông tin & Truyền thông (ICTU)  

---

## 🧭 PHẦN I: PHƯƠNG PHÁP LUẬN KỸ NGHỆ PROMPT & MÔ HÌNH 5 CHUYÊN GIA AI (AI MULTI-PERSONA TEAM)

Nhằm tối ưu hóa hiệu quả khi sử dụng LLM (Large Language Model) và tránh hiện tượng phản hồi chung chung, nhóm đã áp dụng phương pháp **Role-Playing Prompting kết hợp Chain-of-Thought (CoT)**, phân chia AI thành một **"Đội ngũ 5 chuyên gia ảo"** phụ trách xuyên suốt 3 giai đoạn dự án:

```
                  ┌──────────────────────────────────────────────────┐
                  │        ĐỘI NGŨ 5 CHUYÊN GIA AI (NHÓM 03)         │
                  └─────────────────────────┬────────────────────────┘
                                            │
         ┌──────────────────┬───────────────┼───────────────┬──────────────────┐
         │                  │               │               │                  │
         ▼                  ▼               ▼               ▼                  ▼
  ┌──────────────┐   ┌──────────────┐┌──────────────┐┌──────────────┐   ┌──────────────┐
  │ 1. Chuyên gia│   │ 2. Kiến trúc ││  3. Thiết kế ││ 4. Lập trình │   │ 5. Chuyên gia│
  │  Nghiệp vụ   │   │  sư Hệ thống ││    UI/UX     ││ viên Backend │   │   AI & QA    │
  │ (Lead BA/PO) │   │ (Architect)  ││  (Designer)  ││ (Fullstack)  │   │  (AI & Test) │
  └──────────────┘   └──────────────┘└──────────────┘└──────────────┘   └──────────────┘
```

### Danh mục 5 vai trò & Kỹ năng (Skills) cốt lõi:
1. **Chuyên gia phân tích nghiệp vụ (Lead Business Analyst - BA):**
   * *Kỹ năng:* Khai thác quy trình bán lẻ POS, phân tách Actor, đặc tả 10 Use Case chuẩn SRS, xác định yêu cầu chức năng (FR) và phi chức năng (NFR).
2. **Kiến trúc sư hệ thống & CSDL (System Architect / Database Designer):**
   * *Kỹ năng:* Thiết kế kiến trúc 3 tầng (Client-Server), thiết kế mô hình thực thể quan hệ ERD (8 bảng dữ liệu quan hệ), định vị 3 điểm chạm AI trong luồng nghiệp vụ.
3. **Chuyên gia thiết kế giao diện (UI/UX Designer):**
   * *Kỹ năng:* Xây dựng Wireframe trực quan (ASCII & Layout Component) cho màn hình Bán hàng POS, Quản lý kho & sản phẩm, Dashboard phân tích kinh doanh.
4. **Kỹ sư lập trình Fullstack (FastAPI & React Developer):**
   * *Kỹ năng:* Thiết kế cấu trúc thư mục, code SQLAlchemy Models, Pydantic Schemas, viết API CRUD, xử lý Transaction an toàn dữ liệu kho, **truy vết và debug lỗi lệch kho khi hủy đơn**.
5. **Kỹ sư AI & Đảm bảo chất lượng (AI Specialist & QA Engineer):**
   * *Kỹ năng:* Kỹ nghệ Prompt có kiểm chứng (Data Grounding), xây dựng cơ chế phòng vệ API (Rate Limit, Timeout, Data Masking), thiết kế bộ 46 Test cases Pytest tự động, **thực nghiệm và so sánh 3 phiên bản Prompt (V1 -> V2 -> V3) loại bỏ ảo giác**.

---

## 📌 PHẦN II: GIAI ĐOẠN 1 - PHÂN TÍCH YÊU CẦU & THIẾT KẾ HỆ THỐNG (BÀI KT1)

### Prompt 1.1: Phân tích quy trình bán lẻ và yêu cầu hệ thống
* **Vai trò:** *Chuyên gia phân tích nghiệp vụ (Lead BA).*
* **Kỹ năng áp dụng:** *Role-Playing + Structured Output.*
* **Prompt gửi AI:**
  > *"Bạn hãy đóng vai là một Chuyên viên Phân tích Nghiệp vụ (Lead BA) cao cấp trong lĩnh vực Bán lẻ Thiết bị Công nghệ & Phụ kiện. Hãy phân tích chi tiết 4 quy trình cốt lõi cho một chuỗi cửa hàng vừa và nhỏ: (1) Quy trình bán hàng tại quầy POS, (2) Quy trình nhập kho từ nhà cung cấp, (3) Quy trình hủy hóa đơn hoàn kho, (4) Quy trình ứng dụng AI hỗ trợ bán hàng. Sau đó, lập bảng 10 Use Case chính (Actor, Input, Processing, Output) và nêu các yêu cầu phi chức năng về bảo mật, hiệu năng."*
* **Kết quả phản hồi từ AI:**
  * AI đã mô tả chi tiết luồng bán hàng 5 bước: Tiếp nhận -> Chọn SP -> Chiết khấu -> Thanh toán -> Trừ kho tự động.
  * Đề xuất bảng 10 Use Case chuẩn xác từ UC01 đến UC10 (Auth, Sản phẩm, Bán hàng POS, Hủy đơn, Nhập kho, Báo cáo, AI tư vấn, AI báo cáo, AI hỏi đáp).
* **Đánh giá & Hiệu chỉnh của nhóm:** Nhóm nhận thấy quy trình bán hàng cần phân quyền rõ rệt giữa **Quản trị viên (Admin)** có toàn quyền và **Chủ cửa hàng (Owner kiêm thu ngân)** để bảo đảm tính an toàn dữ liệu.

---

### Prompt 1.2: Thiết kế mô hình CSDL ERD chuẩn hóa
* **Vai trò:** *Kiến trúc sư hệ thống & CSDL (Data Architect).*
* **Kỹ năng áp dụng:** *Domain Modeling + Mermaid Syntax.*
* **Prompt gửi AI:**
  > *"Với tư cách là Kiến trúc sư Dữ liệu (Data Architect), hãy thiết kế mô hình thực thể quan hệ ERD cho hệ thống bán hàng trên bằng cú pháp Mermaid. Yêu cầu: Đảm bảo chuẩn hóa 3NF, hỗ trợ các bảng: users, categories, products, customers, orders, order_details, inventories, purchase_receipts. Nêu rõ khóa chính (PK), khóa ngoại (FK), các ràng buộc duy nhất (UK) và kiểu dữ liệu phù hợp với SQLite & PostgreSQL."*
* **Kết quả phản hồi từ AI:**
  * Cung cấp sơ đồ Mermaid ERD với đầy đủ các mối quan hệ `1 - N` và `N - N` (thông qua bảng trung gian `order_details`).
  * Khóa ngoại `order_id` liên kết `orders`, `product_id` liên kết `products`, ràng buộc `code` duy nhất cho đơn hàng và sản phẩm.
* **Đánh giá & Hiệu chỉnh của nhóm:** Nhóm bổ sung bảng `inventories` riêng biệt và lưu vết lịch sử nhập kho qua `purchase_receipts` để hỗ trợ tính năng hoàn kho và kiểm toán tồn kho.

---

### Prompt 1.3: Xác định vị trí tích hợp AI trong hệ thống bán hàng
* **Vai trò:** *Kiến trúc sư hệ thống & Chuyên gia AI (AI Solution Architect).*
* **Kỹ năng áp dụng:** *AI Solution Architecture + Business Impact Analysis.*
* **Prompt gửi AI:**
  > *"Là Chuyên gia Giải pháp Trí tuệ nhân tạo (AI Solution Architect), hãy phân tích và đề xuất 3 vị trí (touchpoints) có giá trị thực tế cao nhất để tích hợp LLM (OpenAI GPT-4o-mini) vào hệ thống bán hàng này. Yêu cầu: AI phải giải quyết bài toán thực tế, không dùng AI chỉ để 'làm màu', và phải có giải pháp kiểm soát dữ liệu kho thực tế để tránh tư vấn sai."*
* **Kết quả phản hồi từ AI:**
  1. *Điểm chạm 1 - AI Tư vấn bán hàng tại quầy:* Hỗ trợ nhân viên tra cứu nhanh sản phẩm theo nhu cầu tự nhiên của khách (ví dụ: "tìm tai nghe dưới 500k pin trâu"), chỉ lọc sản phẩm `stock > 0`.
  2. *Điểm chạm 2 - AI Phân tích báo cáo doanh thu:* Đọc số liệu doanh thu theo ngày/tháng, tự động nhận xét xu hướng tăng giảm và cảnh báo hàng chậm luân chuyển.
  3. *Điểm chạm 3 - AI Hỏi đáp nghiệp vụ quản lý:* Chủ cửa hàng hỏi tự do về dữ liệu kinh doanh để hỗ trợ ra quyết định nhập hàng.
* **Đánh giá & Hiệu chỉnh của nhóm:** Nhóm đưa 3 điểm chạm này vào thiết kế API chính thức tại các endpoint `/api/ai/consult`, `/api/ai/report`, `/api/ai/qa`.

---

### Prompt 1.4: Phác thảo Wireframe giao diện 3 màn hình cốt lõi
* **Vai trò:** *Chuyên gia thiết kế giao diện (UI/UX Designer).*
* **Kỹ năng áp dụng:** *UI/UX Wireframing + Component Layout.*
* **Prompt gửi AI:**
  > *"Hãy đóng vai Chuyên gia thiết kế UI/UX, hãy phác thảo cấu trúc Wireframe (bố cục màn hình dạng ASCII Layout) cho 3 màn hình quan trọng nhất của hệ thống: (1) Màn hình bán hàng POS tại quầy, (2) Màn hình quản lý sản phẩm & cảnh báo tồn kho, (3) Màn hình Dashboard tổng quan có tích hợp AI. Yêu cầu phân chia rõ Header, Sidebar, Main Content, Action Buttons và phản hồi trạng thái."*
* **Kết quả phản hồi từ AI:**

```
[1. WIREFRAME MÀN HÌNH BÁN HÀNG POS TẠI QUẦY]
+-----------------------------------------------------------------------------+
| [LOGO] CỬA HÀNG THIẾT BỊ CÔNG NGHỆ             [User: Thu Ngân | Đăng xuất] |
+------------------------------------+----------------------------------------+
| [BÊN TRÁI: CHỌN SẢN PHẨM]          | [BÊN PHẢI: HÓA ĐƠN ĐANG TẠO]           |
| [Ô tìm kiếm SP...] [Lọc nhóm ▼]    | Khách hàng: [Nguyễn Văn A - VIP 5%]    |
| +--------------------------------+ | +------------------------------------+ |
| | Tai nghe Bluetooth A1 - 350.000₫ | | 1. Tai nghe Bluetooth A1  x2 = 700k  | |
| | [Kho: 10] [ + Thêm vào giỏ ]    | | 2. Củ sạc nhanh 65W       x1 = 590k  | |
| +--------------------------------+ | +------------------------------------+ |
| | Sạc nhanh 65W Anker   - 590.000₫ | Tạm tính: 1.290.000₫                   |
| | [Kho: 5]  [ + Thêm vào giỏ ]    | Chiết khấu/Giảm giá: -50.000₫          |
| +--------------------------------+ | THANH TOÁN: 1.240.000₫                 |
|                                    | PTTT: (*) Tiền mặt ( ) Chuyển khoản    |
|                                    | [ NÚT: HỦY ĐƠN ] [ NÚT: XUẤT HÓA ĐƠN ] |
+------------------------------------+----------------------------------------+

[2. WIREFRAME QUẢN LÝ SẢN PHẨM & TỒN KHO]
+-----------------------------------------------------------------------------+
| TÌM KIẾM: [ Nhập tên/mã SP... ]   LỌC: [ Tất cả nhóm ▼ ] [ Cảnh báo tồn <=5 ]
| [ + Thêm sản phẩm mới ]                                   [ Xuất File Excel ]
+-----------------------------------------------------------------------------+
| Mã SP    | Tên sản phẩm            | Nhóm hàng | Giá bán  | Tồn kho | Trạng thái |
+----------+-------------------------+-----------+----------+---------+------------+
| ACC-001  | Tai nghe Bluetooth A1   | Phụ kiện  | 350.000₫ | 10 cái  | [Đang bán] |
| ACC-002  | Sạc nhanh 65W Anker     | Phụ kiện  | 590.000₫ | 2 cái ⚠️| [Sắp hết]  |
| OLD-001  | Cáp Micro USB cũ        | Phụ kiện  |  35.000₫ | 0 cái   | [Ngừng KD] |
+----------+-------------------------+-----------+----------+---------+------------+

[3. WIREFRAME DASHBOARD TỔNG QUAN & PHÂN TÍCH AI]
+-----------------------------------------------------------------------------+
| [Thẻ: Doanh thu 128.500.000₫] [Thẻ: 85 Hóa đơn] [Thẻ: Cảnh báo tồn: 3 SP]  |
+--------------------------------------------+--------------------------------+
| BIỂU ĐỒ DOANH THU 30 NGÀY QUA              | 🤖 TRỢ LÝ AI ĐIỀU HÀNH         |
| (Biểu đồ cột doanh thu theo ngày/tháng)   | "Dự báo tuần tới phụ kiện sạc  |
|                                            | nhanh có nguy cơ cháy hàng.    |
| TOP SẢN PHẨM BÁN CHẠY:                     | Khuyến nghị nhập thêm 20 chiếc |
| 1. Tai nghe Bluetooth A1 (32 chiếc)        | từ Nhà phân phối Việt."        |
| 2. Sạc nhanh 65W Anker (18 chiếc)          | [ Bấm để hỏi đáp chi tiết ]    |
+--------------------------------------------+--------------------------------+
```

---

## 💻 PHẦN III: GIAI ĐOẠN 2 - XÂY DỰNG CHỨC NĂNG QUẢN LÝ (BÀI KT2)

### Prompt 2.1: Sinh cấu trúc Backend FastAPI, Models và Schemas
* **Vai trò:** *Kỹ sư Backend (FastAPI Developer).*
* **Kỹ năng áp dụng:** *FastAPI Best Practices + Pydantic v2 Validation.*
* **Prompt gửi AI:**
  > *"Hãy đóng vai trò Kỹ sư Backend Python cao cấp. Hãy thiết kế cấu trúc thư mục hoàn chỉnh cho dự án FastAPI quản lý bán hàng. Viết code mẫu cho model SQLAlchemy `Product`, `Order`, `OrderDetail` và Pydantic v2 Schema cho `OrderCreate`, `OrderOut`. Yêu cầu: Có trường trạng thái, liên kết khóa ngoại chuẩn chỉ và kiểm tra dữ liệu đầu vào không được âm."*
* **Kết quả phản hồi từ AI:**
  * Cấu trúc thư mục module hóa sạch (`app/models`, `app/schemas`, `app/routers`, `app/services`).
  * Schema `OrderCreate` sử dụng `Field(min_length=1)` cho danh sách sản phẩm và `quantity: int = Field(gt=0)` để chặn số lượng âm.
* **Đánh giá & Hiệu chỉnh của nhóm:** Nhóm kiểm thử và áp dụng cấu trúc này vào toàn bộ thư mục `backend/app/`.

---

### Prompt 2.2: Sinh truy vấn thống kê doanh thu và báo cáo
* **Vai trò:** *Kỹ sư Dữ liệu (Data Engineer).*
* **Kỹ năng áp dụng:** *SQLAlchemy ORM Aggregations + Analytical Queries.*
* **Prompt gửi AI:**
  > *"Viết các hàm nghiệp vụ bằng SQLAlchemy ORM để tính: (1) Chuỗi doanh thu nhóm theo ngày hoặc theo tháng (`revenue_series`), (2) Doanh thu theo danh mục hàng hóa (`revenue_by_category`), (3) Top sản phẩm bán chạy nhất trong khoảng ngày (`top_products`). Yêu cầu: Chỉ tính các đơn hàng có trạng thái `completed`, xử lý trường hợp không có đơn hàng nào không bị lỗi None."*
* **Kết quả phản hồi từ AI:**
  * Sử dụng `func.sum()`, `func.count()`, `func.strftime()` để nhóm theo thời gian và sắp xếp giảm dần theo doanh thu.
  * Trả về danh sách Dictionary đã được định dạng làm tròn tiền.
* **Đánh giá & Hiệu chỉnh của nhóm:** Nhóm đưa các hàm này vào `backend/app/services/report_service.py` phục vụ cả giao diện React lẫn làm ngữ cảnh đưa vào Prompt AI.

---

### Prompt 2.3: Debug lỗi nghiệp vụ kho khi hủy đơn hàng
* **Vai trò:** *Kỹ sư Debug & Xử lý sự cố (Backend Bug Hunter).*
* **Kỹ năng áp dụng:** *Step-by-Step Debugging + Transaction Management.*
* **Prompt gửi AI:**
  > *"Tôi gặp lỗi nghiêm trọng trong nghiệp vụ kho khi làm tính năng hủy đơn hàng: Khi thu ngân bấm hủy đơn hàng, trạng thái đơn chuyển sang 'cancelled' nhưng số lượng tồn kho của sản phẩm không tăng lại, hoặc có trường hợp bấm nút hủy 2 lần thì sản phẩm bị cộng dồn tồn kho 2 lần làm sai lệch số liệu thực tế trong kho. Hãy phân tích nguyên nhân và viết lại hàm `cancel_order` trong FastAPI đảm bảo hoàn kho an toàn và chặn hủy 2 lần."*
* **Kết quả phản hồi từ AI:**
  * **Chỉ rõ 2 nguyên nhân:**
    1. Chưa duyệt qua bảng chi tiết `order.details` để gọi hàm hoàn trả `adjust_stock(db, product, d.quantity)`.
    2. Thiếu bước kiểm tra điều kiện bảo vệ `if order.status == 'cancelled': raise HTTPException(400, 'Hóa đơn đã bị hủy trước đó')`.
  * **Đoạn mã khắc phục hoàn chỉnh do AI đề xuất:**
    ```python
    @router.post("/{order_id}/cancel", response_model=OrderOut)
    def cancel_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail="Hóa đơn đã bị hủy trước đó")
        
        # Hoàn tồn kho cho từng sản phẩm trong chi tiết đơn
        for d in order.details:
            product = db.get(Product, d.product_id)
            if product:
                adjust_stock(db, product, d.quantity)
                
        order.status = "cancelled"
        db.commit()
        db.refresh(order)
        return to_order_out(db, order)
    ```
* **Đánh giá & Hiệu chỉnh của nhóm:** Nhóm đã đưa đoạn mã này vào `backend/app/routers/orders.py` và viết 2 unit test `test_cancel_restores_stock` và `test_cancel_twice_rejected` trong `test_orders.py` để bảo đảm lỗi không tái diễn.

---

## 🧠 PHẦN IV: GIAI ĐOẠN 3 - TÍCH HỢP AI, TỐI ƯU PROMPT & KIỂM THỬ (BÀI KT3)

### Prompt 3.1: Lập trình Wrapper gọi OpenAI API có Rate Limiter và Timeout
* **Vai trò:** *Kỹ sư Tích hợp AI (AI Engineer).*
* **Kỹ năng áp dụng:** *Fault-tolerant AI Integration + Security Guardrails.*
* **Prompt gửi AI:**
  > *"Hãy đóng vai trò AI Engineer. Viết module `ai_service.py` gọi mô hình OpenAI GPT-4o-mini bằng Python SDK v1.x với các yêu cầu bảo vệ hệ thống nghiêm ngặt: (1) Cài đặt Rate Limiting dạng in-memory tối đa 12 cuộc gọi/phút, nếu vượt quá trả về lỗi 429; (2) Giới hạn thời gian phản hồi timeout = 30s; (3) Viết hàm Data Masking tự động ẩn số điện thoại và email khách hàng bằng Regex trước khi gửi tới OpenAI; (4) Xử lý ngoại lệ an toàn khi thiếu API Key hoặc AI trả về chuỗi rỗng."*
* **Kết quả phản hồi từ AI:**
  * Xây dựng hàng đợi `_call_times = deque()` tính toán cửa sổ trượt 60 giây.
  * Dùng biểu thức chính quy Regex `_PHONE_RE` và `_EMAIL_RE` thay thế số điện thoại thành dạng `091*****78` và email thành `[email-da-an]`.
  * Bắt trọn các lỗi của OpenAI SDK (`RateLimitError`, `APITimeoutError`, `AuthenticationError`).
* **Đánh giá & Hiệu chỉnh của nhóm:** Toàn bộ giải pháp đã được tích hợp tại `backend/app/services/ai_service.py`.

---

### Prompt 3.2: Thực nghiệm và Đối chiếu 3 phiên bản Prompt (Prompt Evolution)
* **Vai trò:** *Chuyên gia Kỹ nghệ Prompt (Prompt Engineer).*
* **Kỹ năng áp dụng:** *Prompt Versioning + Hallucination Reduction.*

Nhóm đã lưu trữ 3 phiên bản thực tế trong thư mục `prompts/versions/`:

#### 1. Phiên bản 1 (V1 - Sơ khai): `prompts/versions/product_consultant_v1.txt`
```
Bạn là trợ lý tư vấn sản phẩm. Khách cần: {{customer_request}}. Danh sách sản phẩm: {{product_table}}. Hãy gợi ý sản phẩm phù hợp.
```
* **Thực nghiệm với câu hỏi:** *"Khách hỏi mua điện thoại Samsung Galaxy S25 Ultra có không em?"*
* **Kết quả AI phản hồi:** AI tự bịa ra thông số của Samsung S25 Ultra và báo giá 30 triệu dù cửa hàng **không hề bán sản phẩm này**. Đồng thời khi hỏi mua phụ kiện, AI gợi ý cả sản phẩm có `tồn kho = 0`.
* **Nhận xét:** Ảo giác nghiêm trọng (Hallucination), không dùng được trong thực tế.

#### 2. Phiên bản 2 (V2 - Cải tiến): `prompts/versions/product_consultant_v2.txt`
```
Bạn là trợ lý AI tư vấn sản phẩm cho cửa hàng.
Chỉ tư vấn dựa trên dữ liệu sản phẩm được cung cấp.
TUYỆT ĐỐI không gợi ý sản phẩm hết hàng (tồn kho = 0).
Nếu không có sản phẩm phù hợp, hãy nói rõ.
Dữ liệu sản phẩm: {{product_table}}
Yêu cầu khách hàng: {{customer_request}}
Hãy gợi ý tối đa 3 sản phẩm và giải thích ngắn gọn.
```
* **Thực nghiệm với câu hỏi:** Khắc phục được việc gợi ý hàng tồn = 0 nhờ backend filter `stock > 0`. Nhưng khi khách hỏi sản phẩm không có, AI vẫn cố gắng gán ghép sang các mặt hàng khác không đúng mong muốn.
* **Nhận xét:** Cải thiện được 70%, nhưng cần quy định rõ câu từ chối lịch sự.

#### 3. Phiên bản 3 (V3 - Chuẩn hóa sản xuất): `prompts/versions/product_consultant_v3.txt`
```
Bạn là trợ lý AI tư vấn sản phẩm cho cửa hàng.
Quy tắc bắt buộc:
1. Chỉ được tư vấn dựa trên dữ liệu sản phẩm được cung cấp bên dưới.
2. Không được đề xuất bất kỳ sản phẩm nào không có trong danh sách.
3. Không được gợi ý sản phẩm hết hàng hoặc sắp hết hàng (tồn kho = 0).
4. Nếu không có sản phẩm phù hợp với yêu cầu, hãy nói rõ "hiện không có sản phẩm phù hợp".
Yêu cầu của khách hàng: {{customer_request}}
Dữ liệu sản phẩm (tất cả đều còn hàng): {{product_table}}
Hãy gợi ý tối đa 3 sản phẩm phù hợp nhất, mỗi sản phẩm kèm giải thích ngắn gọn lý do phù hợp với yêu cầu của khách.
```
* **Thực nghiệm với câu hỏi:** *"Cửa hàng có tai nghe kiểm âm Sony MDR-7506 không?"*
* **Kết quả AI phản hồi:** *"Dạ hiện tại cửa hàng không có dòng sản phẩm tai nghe kiểm âm Sony MDR-7506. Tuy nhiên cửa hàng đang có sẵn Tai nghe Sony WH-CH520 chính hãng giá 1.290.000₫ với thời lượng pin 50 giờ nếu quý khách có nhu cầu nghe nhạc giải trí thông thường."*
* **Nhận xét:** Đạt 100% yêu cầu nghiệp vụ: Từ chối chuẩn xác, không bịa đặt, khéo léo giới thiệu sản phẩm thay thế có sẵn trong kho.

---

### Prompt 3.3: Sinh bộ kiểm thử tự động toàn diện (Testing Suite với Pytest)
* **Vai trò:** *Chuyên gia Kiểm thử Tự động (QA Automation Engineer).*
* **Kỹ năng áp dụng:** *Test-Driven Engineering + API Mocking.*
* **Prompt gửi AI:**
  > *"Với tư cách là Chuyên gia QA Automation, hãy viết bộ test case bằng Pytest và FastAPI TestClient kiểm thử toàn diện hệ thống: (1) Test AI Consultant chỉ gợi ý hàng còn kho và lọc bỏ hàng hết kho; (2) Test tự động che giấu số điện thoại khách hàng; (3) Test Rate Limiter trả về mã 429; (4) Test thiếu OpenAI Key trả về 503; (5) Test trừ tồn kho khi tạo đơn hàng và hoàn kho khi hủy đơn. Sử dụng monkeypatch để mock lời gọi hàm `generate` của OpenAI, không gọi tốn tiền API thật."*
* **Kết quả phản hồi từ AI:**
  * Cung cấp fixture `client`, mock function `_capture_generate` bắt nội dung prompt gửi đi.
  * Khởi tạo bộ test tự động đạt tỷ lệ bao phủ cao.
* **Kết quả thực thi thực tế:** Toàn bộ **46/46 test cases** đều chạy thành công trên máy tính (`46 passed in 0.89s`).

---

## 📊 BẢNG TỔNG HỢP CÁC KỸ NĂNG PROMPT ENGINEERING ĐÃ ÁP DỤNG

| STT | Kỹ thuật Kỹ nghệ Prompt | Vị trí áp dụng trong dự án | Hiệu quả đạt được |
| :---: | :--- | :--- | :--- |
| 1 | **Multi-Persona (Phân vai 5 chuyên gia)** | Toàn bộ các phiên hỏi đáp làm phần mềm | Phản hồi của AI có chuyên môn sâu theo đúng góc nhìn của BA, Kiến trúc sư, UI/UX, Dev và QA. |
| 2 | **Data Grounding (Neo dữ liệu thực tế)** | `/api/ai/consult` & `/api/ai/report` | AI chỉ phân tích dựa trên dữ liệu sản phẩm `stock > 0` và số liệu bán hàng thực từ database, triệt tiêu 100% ảo giác. |
| 3 | **Input Masking & Guardrails** | `mask_sensitive()` trong `ai_service.py` | Bảo vệ quyền riêng tư người dùng (SĐT, Email) theo tiêu chuẩn bảo mật dữ liệu trước khi gửi sang bên thứ 3. |
| 4 | **Prompt Versioning & Evaluation** | `prompts/versions/v1, v2, v3` | Có bằng chứng khoa học so sánh 3 vòng cải tiến Prompt để báo cáo bài tập lớn. |
| 5 | **Step-by-Step Debugging** | Nghiệp vụ `cancel_order` hoàn kho | AI tìm ra điểm nghẽn thiếu hàm hoàn kho và thiếu cờ chặn hủy 2 lần chỉ sau 1 prompt. |

---

> **Kết luận:** Việc xây dựng tài liệu tổng hợp prompt có hệ thống cùng mô hình **5 Chuyên gia AI** đã giúp nhóm 03 hoàn thành dự án một cách khoa học, chuyên nghiệp, đáp ứng trọn vẹn 100% các tiêu chí đánh giá của giảng viên hướng dẫn trong học phần *Ứng dụng trí tuệ nhân tạo (AIA331)*.
