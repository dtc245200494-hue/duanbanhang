# 📊 SƠ ĐỒ THIẾT KẾ HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP AI (AIA331)

> **Học phần:** Ứng dụng trí tuệ nhân tạo (K23.K1.CNTT K23C)  
> **Dự án:** Hệ thống Quản lý Bán hàng Tích hợp Trợ lý AI  
> **Nhóm thực hiện:** Nhóm 03 (Hoàng Trang Hiên & Nguyễn Viết Cường) | **GVHD:** ThS. Nguyễn Tuấn Anh  
> **Đặc tả:** Mô hình hệ thống tinh gọn gồm 2 Actor (Admin, Owner) và 7 bảng CSDL thực tế.

---

## 📑 MỤC LỤC CÁC SƠ ĐỒ CỐT LÕI

1. [Sơ đồ Use Case & Phân quyền (2 Actor: Admin, Owner)](#1-sơ-đồ-use-case--phân-quyền)
2. [Sơ đồ Quan hệ Thực thể CSDL (ERD - 7 Bảng Cốt lõi)](#2-sơ-đồ-quan-hệ-thực-thể-csdl-erd)
3. [Sơ đồ Kiến trúc Hệ thống 3 tầng (System Architecture)](#3-sơ-đồ-kiến-trúc-hệ-thống)
4. [Sơ đồ Luồng Hoạt động (Activity Diagrams)](#4-sơ-đồ-luồng-hoạt-động-activity-diagrams)
5. [Sơ đồ Tuần tự (Sequence Diagrams)](#5-sơ-đồ-tuần-tự-sequence-diagrams)
6. [Sơ đồ Luồng Dữ liệu (DFD Cấp 0 & Cấp 1)](#6-sơ-đồ-luồng-dữ-liệu-dfd)
7. [Sơ đồ Lớp Backend (Class Diagram)](#7-sơ-đồ-lớp-backend-class-diagram)
8. [Sơ đồ Chuyển trạng thái Đơn hàng (Order State Machine)](#8-sơ-đồ-chuyển-trạng-thái-đơn-hàng)

---

## 1. Sơ đồ Use Case & Phân quyền

Hệ thống được thiết kế tối giản, phân quyền rõ ràng cho 2 nhóm đối tượng:
- **👨‍💼 Quản trị viên (Admin):** Quản trị tài khoản, phân quyền, quản lý danh mục, sản phẩm, kho hàng, xem toàn bộ báo cáo và sử dụng AI.
- **👔 Chủ cửa hàng (Owner):** Trực tiếp quản lý bán hàng (POS), nhập hàng, theo dõi dashboard doanh thu và sử dụng trợ lý AI phân tích điều hành.

```mermaid
graph LR
    subgraph System["Hệ thống Quản lý Bán hàng Tích hợp AI"]
        UC1["1. Đăng nhập & Xác thực"]
        UC2["2. Quản lý Tài khoản (Admin only)"]
        UC3["3. Quản lý Danh mục & Sản phẩm"]
        UC4["4. Bán hàng tại quầy (POS)"]
        UC5["5. Hủy đơn hàng & Hoàn kho"]
        UC6["6. Nhập hàng & Quản lý Kho"]
        UC7["7. Xem Dashboard & Báo cáo"]
        UC8["8. Xuất báo cáo Excel / PDF"]
        UC9["9. Trợ lý AI Tư vấn Bán hàng"]
        UC10["10. Trợ lý AI Phân tích Kinh doanh"]
    end

    Admin(("👨‍💼 Quản trị viên<br/>(Admin)"))
    Owner(("👔 Chủ cửa hàng<br/>(Owner)"))

    %% Admin Connections
    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10

    %% Owner Connections
    Owner --> UC1
    Owner --> UC3
    Owner --> UC4
    Owner --> UC5
    Owner --> UC6
    Owner --> UC7
    Owner --> UC8
    Owner --> UC9
    Owner --> UC10
```

---

## 2. Sơ đồ Quan hệ Thực thể CSDL (ERD)

Mô hình CSDL thực tế gồm **7 bảng cốt lõi** phục vụ đầy đủ quy trình bán lẻ POS, quản lý xuất nhập tồn kho và trợ lý AI:

```mermaid
erDiagram
    USERS ||--o{ ORDERS : "lap"
    USERS ||--o{ PURCHASE_RECEIPTS : "nhap"
    CATEGORIES ||--o{ PRODUCTS : "chua"
    PRODUCTS ||--o{ ORDER_DETAILS : "co_trong"
    ORDERS ||--o{ ORDER_DETAILS : "gom"
    CUSTOMERS ||--o{ ORDERS : "mua"
    PRODUCTS ||--o| INVENTORIES : "theo_doi"

    USERS {
        int id PK
        string username UK
        string password_hash
        string full_name
        string role "admin | owner"
        datetime created_at
    }

    CATEGORIES {
        int id PK
        string name UK
        string description
    }

    PRODUCTS {
        int id PK
        string code UK
        string name
        int category_id FK
        float import_price
        float sell_price
        int stock
        string status "active | inactive"
        string description
    }

    CUSTOMERS {
        int id PK
        string name
        string phone UK
        string email
        string address
        string customer_group
    }

    ORDERS {
        int id PK
        string code UK
        int customer_id FK
        int user_id FK
        float total_amount
        float discount
        float final_amount
        string payment_method "cash | transfer | card"
        string status "completed | cancelled"
        datetime created_at
    }

    ORDER_DETAILS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float price
        float total
    }

    PURCHASE_RECEIPTS {
        int id PK
        string code UK
        string supplier
        int user_id FK
        float total_amount
        string status "completed | cancelled"
        datetime created_at
    }

    INVENTORIES {
        int id PK
        int product_id FK
        int quantity
        datetime last_updated
    }
```

---

## 3. Sơ đồ Kiến trúc Hệ thống

Kiến trúc 3 tầng chuẩn hiện đại, phân tách rõ ràng giữa Giao diện, Backend API và Tầng Trí tuệ Nhân tạo:

```mermaid
graph TB
    subgraph Presentation_Layer["1. TẦNG GIAO DIỆN (Presentation)"]
        UI_POS["Giao diện Bán hàng POS (React)"]
        UI_Dash["Dashboard Doanh thu & Báo cáo"]
        UI_AI["Khung Chat Trợ lý AI"]
    end

    subgraph Business_Layer["2. TẦNG NGHIỆP VỤ (Backend API - FastAPI)"]
        Router["API Routers (Auth, Orders, Products, AI)"]
        AuthMiddleware["JWT Authentication & RBAC Filter"]
        
        subgraph Services["Core Business Services"]
            OrderService["Order Service (POS Checkout & Auto Stock Deduct)"]
            InventoryService["Inventory Service (Stock Update)"]
            ReportService["Report Service (Stats & Excel Export)"]
            AIService["AI Service Wrapper (Prompt Engineering & Data Masking)"]
        end
    end

    subgraph Data_AI_Layer["3. TẦNG DỮ LIỆU & AI ENGINE"]
        DB[(CSDL SQLite: sales.db)]
        Prompts["Prompt Versioning Files (prompts/versions/)"]
        OpenAI["OpenAI GPT-4o-mini API Cloud"]
    end

    Presentation_Layer -->|HTTP / JSON REST API / JWT| Router
    Router --> AuthMiddleware
    AuthMiddleware --> Services
    OrderService --> DB
    InventoryService --> DB
    ReportService --> DB
    AIService --> DB
    AIService --> Prompts
    AIService -->|HTTPS Prompt Payload| OpenAI
```

---

## 4. Sơ đồ Luồng Hoạt động (Activity Diagrams)

### 4.1. Luồng Bán hàng POS & Trừ tồn kho tự động
```mermaid
flowchart TD
    Start([Bắt đầu bán hàng]) --> SelectProd[Chọn sản phẩm / Quét mã]
    SelectProd --> CheckStock{Kiểm tra tồn kho: stock >= qty?}
    CheckStock -- Không đủ --> AlertStock[Cảnh báo hết hàng] --> SelectProd
    CheckStock -- Đủ hàng --> AddCart[Thêm vào giỏ hàng & Tính tiền]
    AddCart --> Payment[Chọn hình thức thanh toán & Bấm Thanh toán]
    Payment --> DB_Order[Tạo bản ghi Orders & OrderDetails]
    DB_Order --> DB_Stock[Trừ tồn kho: stock = stock - qty]
    DB_Stock --> PrintBill[In hóa đơn POS cho khách]
    PrintBill --> End([Hoàn tất giao dịch])
```

### 4.2. Luồng Trợ lý AI Tư vấn & Bảo vệ dữ liệu (Data Masking)
```mermaid
flowchart TD
    Start([Khách/Chủ cửa hàng hỏi AI]) --> InputPrompt[Nhận câu hỏi người dùng]
    InputPrompt --> FetchDB[Truy vấn danh mục & Sản phẩm còn hàng stock > 0]
    FetchDB --> MaskData[Data Masking: Ẩn giá nhập, ẩn SĐT khách hàng]
    MaskData --> BuildPrompt[Gắn System Prompt + Dữ liệu đã làm sạch]
    BuildPrompt --> CallAI[Gửi request tới OpenAI API]
    CallAI --> CheckRes{Nhận phản hồi thành công?}
    CheckRes -- Thành công --> FormatOutput[Hiển thị tư vấn chuẩn xác]
    CheckRes -- Lỗi / Timeout --> Fallback[Fallback: Báo lỗi thân thiện hoặc dùng Rule mẫu]
    FormatOutput --> End([Kết thúc])
    Fallback --> End
```

---

## 5. Sơ đồ Tuần tự (Sequence Diagrams)

### 5.1. Tuần tự Đăng nhập & Xác thực JWT
```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng (Admin/Owner)
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant DB as SQLite DB

    User->>FE: Nhập username & password
    FE->>API: POST /api/auth/login
    API->>DB: Query User theo username
    DB-->>API: Trả về password_hash & role
    API->>API: Verify Password (Bcrypt)
    alt Mật khẩu đúng
        API->>API: Tạo Access Token (JWT)
        API-->>FE: HTTP 200 {access_token, role, user_info}
        FE->>FE: Lưu token vào localStorage & chuyển trang
    else Mật khẩu sai
        API-->>FE: HTTP 401 Unauthorized
        FE-->>User: Báo lỗi đăng nhập
    end
```

### 5.2. Tuần tự Bán hàng POS & Tạo Hóa đơn
```mermaid
sequenceDiagram
    autonumber
    actor User as Người bán (Owner/Admin)
    participant FE as Màn hình POS
    participant API as Backend (Orders Router)
    participant DB as SQLite Database

    User->>FE: Chọn danh sách sản phẩm + số lượng
    FE->>API: POST /api/orders/ (kèm Bearer Token)
    API->>DB: BEGIN TRANSACTION
    API->>DB: Kiểm tra stock từng sản phẩm
    alt Đủ hàng trong kho
        API->>DB: Insert vào ORDERS
        API->>DB: Insert vào ORDER_DETAILS
        API->>DB: Update PRODUCTS (stock = stock - qty)
        API->>DB: COMMIT TRANSACTION
        API-->>FE: HTTP 201 Created {order_id, code, total_amount}
        FE-->>User: Hiển thị hóa đơn thành công & In bill
    else Hết hàng hoặc không đủ tồn kho
        API->>DB: ROLLBACK TRANSACTION
        API-->>FE: HTTP 400 Bad Request (Tồn kho không đủ)
        FE-->>User: Cảnh báo không đủ số lượng
    end
```

---

## 6. Sơ đồ Luồng Dữ liệu (DFD)

### DFD Cấp 0 (Sơ đồ Ngữ cảnh)
```mermaid
graph TD
    User([Người dùng: Admin / Owner]) <-->|Đăng nhập / Bán hàng POS / Xem báo cáo| System[HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP AI]
    System <-->|Truy vấn & Lưu trữ dữ liệu| DB[(CSDL SQLite: sales.db)]
    System <-->|Gửi Prompt & Nhận phản hồi tư vấn| AIProvider[OpenAI GPT-4o-mini Engine]
```

### DFD Cấp 1 (Phân rã chức năng)
```mermaid
graph TB
    User([Người dùng]) -->|Thông tin đăng nhập| P1(1.0 Xác thực & Phân quyền)
    P1 --> D1[(USERS)]

    User -->|Thông tin sản phẩm & Nhập hàng| P2(2.0 Quản lý Hàng hóa & Kho)
    P2 <--> D2[(PRODUCTS & CATEGORIES)]
    P2 <--> D3[(PURCHASE_RECEIPTS)]

    User -->|Tạo đơn bán hàng POS| P3(3.0 Xử lý Bán hàng POS)
    P3 <--> D2
    P3 --> D4[(ORDERS & ORDER_DETAILS)]

    User -->|Yêu cầu thống kê| P4(4.0 Thống kê & Báo cáo)
    D4 --> P4
    P4 -->|Báo cáo doanh thu & Excel| User

    User -->|Câu hỏi tư vấn / Phân tích| P5(5.0 Trợ lý AI Assistant)
    D2 --> P5
    D4 --> P5
    P5 <--> AICloud[OpenAI Engine Cloud]
    P5 -->|Câu trả lời AI| User
```

---

## 7. Sơ đồ Lớp Backend (Class Diagram)

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string password_hash
        +string full_name
        +string role
        +datetime created_at
    }

    class Category {
        +int id
        +string name
        +string description
        +List~Product~ products
    }

    class Product {
        +int id
        +string code
        +string name
        +int category_id
        +float import_price
        +float sell_price
        +int stock
        +string status
        +string description
    }

    class Customer {
        +int id
        +string name
        +string phone
        +string email
        +string address
        +string customer_group
    }

    class Order {
        +int id
        +string code
        +int customer_id
        +int user_id
        +float total_amount
        +float discount
        +float final_amount
        +string payment_method
        +string status
        +datetime created_at
    }

    class OrderDetail {
        +int id
        +int order_id
        +int product_id
        +int quantity
        +float price
        +float total
    }

    class PurchaseReceipt {
        +int id
        +string code
        +string supplier
        +int user_id
        +float total_amount
        +string status
        +datetime created_at
    }

    Category "1" -- "*" Product : contains
    Product "1" -- "*" OrderDetail : included_in
    Order "1" -- "*" OrderDetail : items
    User "1" -- "*" Order : created_by
    User "1" -- "*" PurchaseReceipt : imported_by
    Customer "1" -- "*" Order : placed_by
```

---

## 8. Sơ đồ Chuyển trạng thái Đơn hàng

```mermaid
stateDiagram-v2
    [*] --> COMPLETED : Tạo đơn bán hàng tại quầy (POS)
    note right of COMPLETED
        - Ghi nhận doanh thu
        - Trừ tồn kho tự động (stock -= quantity)
    end note

    COMPLETED --> CANCELLED : Hủy đơn hàng (Khi có yêu cầu đổi trả)
    note right of CANCELLED
        - Hoàn lại số lượng tồn kho (stock += quantity)
        - Trừ doanh thu tương ứng trong báo cáo
    end note

    CANCELLED --> [*]
```
