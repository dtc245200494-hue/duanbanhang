import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')

DRAWIO_DIR = f"{BASE_DIR}/tailieu/drawio"
IMG_TAILIEU = f"{BASE_DIR}/tailieu/images"
IMG_DOCS = f"{BASE_DIR}/docs/images"

os.makedirs(DRAWIO_DIR, exist_ok=True)
os.makedirs(IMG_TAILIEU, exist_ok=True)
os.makedirs(IMG_DOCS, exist_ok=True)

# Helper to get font
def get_fonts():
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 22)
        font_h = ImageFont.truetype("arialbd.ttf", 15)
        font_body = ImageFont.truetype("arial.ttf", 13)
        font_body_bold = ImageFont.truetype("arialbd.ttf", 13)
        font_sm = ImageFont.truetype("arial.ttf", 11)
        font_sm_bold = ImageFont.truetype("arialbd.ttf", 11)
    except Exception:
        font_title = ImageFont.load_default()
        font_h = font_title
        font_body = font_title
        font_body_bold = font_title
        font_sm = font_title
        font_sm_bold = font_title
    return font_title, font_h, font_body, font_body_bold, font_sm, font_sm_bold

def draw_rounded_box(draw, xy, fill, outline, radius=8, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start, end, fill="#1E3A8A", width=2, arrow_size=6):
    x0, y0 = start
    x1, y1 = end
    draw.line([start, end], fill=fill, width=width)
    if x0 == x1: # Vertical
        if y1 > y0:
            draw.polygon([(x1, y1), (x1 - arrow_size, y1 - arrow_size*1.5), (x1 + arrow_size, y1 - arrow_size*1.5)], fill=fill)
        else:
            draw.polygon([(x1, y1), (x1 - arrow_size, y1 + arrow_size*1.5), (x1 + arrow_size, y1 + arrow_size*1.5)], fill=fill)
    elif y0 == y1: # Horizontal
        if x1 > x0:
            draw.polygon([(x1, y1), (x1 - arrow_size*1.5, y1 - arrow_size), (x1 - arrow_size*1.5, y1 + arrow_size)], fill=fill)
        else:
            draw.polygon([(x1, y1), (x1 + arrow_size*1.5, y1 - arrow_size), (x1 + arrow_size*1.5, y1 + arrow_size)], fill=fill)

# ================= 1. USE CASE DIAGRAM =================
def generate_usecase():
    W, H = 1000, 620
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    # Title
    draw.text((W//2, 25), "SƠ ĐỒ USE CASE TỔNG QUÁT & PHÂN QUYỀN HỆ THỐNG", fill="#1E3A8A", font=f_title, anchor="mt")

    # Boundary Box
    draw_rounded_box(draw, (260, 65, 780, 580), fill="#F8FAFC", outline="#94A3B8", radius=12, width=2)
    draw.text((520, 80), "Hệ thống Quản lý Bán hàng Tích hợp AI (AI POS)", fill="#0F172A", font=f_h, anchor="mt")

    # Use Cases
    ucs = [
        "1. Đăng nhập & Xác thực JWT",
        "2. Quản lý Tài khoản (Admin)",
        "3. Quản lý Danh mục & Sản phẩm",
        "4. Bán hàng tại quầy (POS)",
        "5. Hủy đơn hàng & Hoàn tồn kho",
        "6. Nhập hàng & Quản lý Kho",
        "7. Xem Dashboard Doanh thu",
        "8. Xuất báo cáo Excel / PDF",
        "9. Trợ lý AI Tư vấn Sản phẩm",
        "10. Trợ lý AI Phân tích Kinh doanh"
    ]
    
    uc_boxes = []
    y_start = 115
    for i, uc in enumerate(ucs):
        col = 0 if i < 5 else 1
        row = i % 5
        x = 290 if col == 0 else 535
        y = y_start + row * 88
        w = 215
        h = 60
        bg = "#EFF6FF" if "AI" not in uc else "#F0FDF4"
        border = "#3B82F6" if "AI" not in uc else "#10B981"
        draw.ellipse([x, y, x + w, y + h], fill=bg, outline=border, width=2)
        draw.text((x + w//2, y + h//2), uc, fill="#1E293B", font=f_sm_bold, anchor="mm")
        uc_boxes.append((x, y + h//2, x + w, y + h//2))

    # Actors
    # Admin (Left)
    draw_rounded_box(draw, (30, 200, 180, 290), fill="#FEF3C7", outline="#F59E0B", radius=10, width=2)
    draw.text((105, 230), "👨‍💼 Quản trị viên", fill="#B45309", font=f_body_bold, anchor="mm")
    draw.text((105, 255), "(Admin)", fill="#78350F", font=f_sm, anchor="mm")

    # Owner (Right)
    draw_rounded_box(draw, (830, 200, 970, 290), fill="#E0E7FF", outline="#6366F1", radius=10, width=2)
    draw.text((900, 230), "👔 Chủ cửa hàng", fill="#4338CA", font=f_body_bold, anchor="mm")
    draw.text((900, 255), "(Owner / Bán hàng)", fill="#312E81", font=f_sm, anchor="mm")

    # Lines Admin -> Left UCs
    for i in range(5):
        draw_arrow(draw, (180, 245), (290, uc_boxes[i][1]), fill="#D97706", width=2, arrow_size=4)

    # Lines Owner -> Right UCs & Some Left
    for i in range(5, 10):
        draw_arrow(draw, (830, 245), (750, uc_boxes[i][1]), fill="#4F46E5", width=2, arrow_size=4)
    # Owner also connects to POS & Products
    draw.line([(830, 260), (790, 260), (790, 480), (505, uc_boxes[2][1])], fill="#4F46E5", width=2)
    draw.line([(830, 270), (800, 270), (800, 520), (505, uc_boxes[3][1])], fill="#4F46E5", width=2)

    return img

# ================= 2. ERD DIAGRAM =================
def generate_erd():
    W, H = 1000, 680
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    draw.text((W//2, 20), "SƠ ĐỒ QUAN HỆ THỰC THỂ CSDL (ERD - 7 BẢNG CỐT LÕI)", fill="#1E3A8A", font=f_title, anchor="mt")

    tables = {
        "USERS": (30, 70, 200, 160, ["PK id : int", "UK username : str", "password_hash : str", "full_name : str", "role : str", "created_at : datetime"]),
        "CATEGORIES": (270, 70, 200, 110, ["PK id : int", "UK name : str", "description : str"]),
        "PRODUCTS": (510, 70, 230, 200, ["PK id : int", "UK code : str", "name : str", "FK category_id : int", "import_price : float", "sell_price : float", "stock : int", "status : str", "description : str"]),
        "INVENTORIES": (780, 70, 190, 110, ["PK id : int", "FK product_id : int", "quantity : int", "last_updated : datetime"]),
        "CUSTOMERS": (30, 360, 200, 150, ["PK id : int", "name : str", "UK phone : str", "email : str", "address : str", "customer_group : str"]),
        "ORDERS": (270, 360, 220, 200, ["PK id : int", "UK code : str", "FK customer_id : int", "FK user_id : int", "total_amount : float", "discount : float", "final_amount : float", "payment_method : str", "status : str", "created_at : datetime"]),
        "ORDER_DETAILS": (530, 360, 200, 140, ["PK id : int", "FK order_id : int", "FK product_id : int", "quantity : int", "price : float", "total : float"]),
        "PURCHASE_RECEIPTS": (770, 360, 200, 160, ["PK id : int", "UK code : str", "supplier : str", "FK user_id : int", "total_amount : float", "status : str", "created_at : datetime"])
    }

    for name, (x, y, w, h, fields) in tables.items():
        # Header
        draw_rounded_box(draw, (x, y, x+w, y+h), fill="#FFFFFF", outline="#3B82F6", radius=6, width=2)
        draw.rectangle([x, y, x+w, y+28], fill="#1E3A8A")
        draw.text((x+w//2, y+14), name, fill="#FFFFFF", font=f_body_bold, anchor="mm")
        
        # Fields
        fy = y + 36
        for f in fields:
            is_pk = "PK" in f
            is_fk = "FK" in f
            col = "#B91C1C" if is_pk else ("#1D4ED8" if is_fk else "#334155")
            draw.text((x+8, fy), f, fill=col, font=f_sm)
            fy += 16

    # Connections
    # CATEGORIES -> PRODUCTS
    draw_arrow(draw, (470, 120), (510, 120), fill="#2563EB", width=2)
    draw.text((490, 108), "1..N", fill="#2563EB", font=f_sm, anchor="mb")

    # PRODUCTS -> INVENTORIES
    draw_arrow(draw, (740, 120), (780, 120), fill="#2563EB", width=2)
    draw.text((760, 108), "1..1", fill="#2563EB", font=f_sm, anchor="mb")

    # USERS -> ORDERS
    draw_arrow(draw, (130, 230), (270, 420), fill="#2563EB", width=2)
    draw.text((180, 310), "1..N", fill="#2563EB", font=f_sm, anchor="mm")

    # CUSTOMERS -> ORDERS
    draw_arrow(draw, (230, 420), (270, 420), fill="#2563EB", width=2)
    draw.text((250, 408), "1..N", fill="#2563EB", font=f_sm, anchor="mb")

    # ORDERS -> ORDER_DETAILS
    draw_arrow(draw, (490, 420), (530, 420), fill="#2563EB", width=2)
    draw.text((510, 408), "1..N", fill="#2563EB", font=f_sm, anchor="mb")

    # PRODUCTS -> ORDER_DETAILS
    draw.line([(620, 270), (620, 360)], fill="#2563EB", width=2)
    draw_arrow(draw, (620, 350), (620, 360), fill="#2563EB", width=2)
    draw.text((630, 315), "1..N", fill="#2563EB", font=f_sm, anchor="lm")

    # USERS -> PURCHASE_RECEIPTS
    draw.line([(130, 230), (130, 600), (870, 600), (870, 520)], fill="#2563EB", width=2)
    draw_arrow(draw, (870, 530), (870, 520), fill="#2563EB", width=2)

    return img

# ================= 3. ARCHITECTURE DIAGRAM =================
def generate_architecture():
    W, H = 1000, 600
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    draw.text((W//2, 20), "SƠ ĐỒ KIẾN TRÚC HỆ THỐNG 3 TẦNG (SYSTEM ARCHITECTURE)", fill="#1E3A8A", font=f_title, anchor="mt")

    # Layer 1: Client
    draw_rounded_box(draw, (40, 60, 960, 180), fill="#F8FAFC", outline="#3B82F6", radius=10, width=2)
    draw.text((55, 75), "1. TẦNG GIAO DIỆN CLIENT (React 18 SPA + Vite)", fill="#1E3A8A", font=f_h)
    draw_rounded_box(draw, (70, 105, 320, 160), fill="#EFF6FF", outline="#60A5FA", radius=6, width=1)
    draw.text((195, 132), "Màn hình Bán hàng POS", fill="#1E293B", font=f_body_bold, anchor="mm")
    draw_rounded_box(draw, (360, 105, 640, 160), fill="#EFF6FF", outline="#60A5FA", radius=6, width=1)
    draw.text((500, 132), "Dashboard & Báo cáo Doanh thu", fill="#1E293B", font=f_body_bold, anchor="mm")
    draw_rounded_box(draw, (680, 105, 930, 160), fill="#F0FDF4", outline="#34D399", radius=6, width=1)
    draw.text((805, 132), "Khung Chat Trợ lý AI (POS / Q&A)", fill="#065F46", font=f_body_bold, anchor="mm")

    # Down Arrow
    draw_arrow(draw, (500, 180), (500, 220), fill="#1E3A8A", width=3, arrow_size=6)
    draw.text((515, 200), "REST API / Bearer JWT", fill="#1E3A8A", font=f_sm_bold, anchor="lm")

    # Layer 2: API & Services
    draw_rounded_box(draw, (40, 220, 960, 400), fill="#F8FAFC", outline="#10B981", radius=10, width=2)
    draw.text((55, 235), "2. TẦNG DỊCH VỤ BACKEND (FastAPI - Python 3.12)", fill="#065F46", font=f_h)
    
    # Routers
    draw_rounded_box(draw, (70, 265, 480, 320), fill="#F0FDF4", outline="#6EE7B7", radius=6, width=1)
    draw.text((275, 292), "API Routers: Auth, Products, Orders, Reports", fill="#065F46", font=f_body_bold, anchor="mm")

    draw_rounded_box(draw, (520, 265, 930, 320), fill="#FEF3C7", outline="#FCD34D", radius=6, width=1)
    draw.text((725, 292), "AI Router: /api/ai/consult & /api/ai/report", fill="#92400E", font=f_body_bold, anchor="mm")

    # Services
    draw_rounded_box(draw, (70, 335, 480, 385), fill="#ECFDF5", outline="#A7F3D0", radius=6, width=1)
    draw.text((275, 360), "Services: Order, Inventory, Report Export", fill="#065F46", font=f_sm_bold, anchor="mm")

    draw_rounded_box(draw, (520, 335, 930, 385), fill="#FEF3C7", outline="#FDE68A", radius=6, width=1)
    draw.text((725, 360), "AI Service: Prompt Template & Data Masking", fill="#92400E", font=f_sm_bold, anchor="mm")

    # Down Arrow
    draw_arrow(draw, (275, 400), (275, 440), fill="#1E3A8A", width=3, arrow_size=6)
    draw_arrow(draw, (725, 400), (725, 440), fill="#D97706", width=3, arrow_size=6)

    # Layer 3: Data & External
    draw_rounded_box(draw, (40, 440, 960, 560), fill="#F8FAFC", outline="#6366F1", radius=10, width=2)
    draw.text((55, 455), "3. TẦNG DỮ LIỆU & ĐIỆN TOÁN NGOẠI VI (Data & Cloud AI)", fill="#3730A3", font=f_h)

    draw_rounded_box(draw, (70, 485, 480, 545), fill="#EEF2FF", outline="#A5B4FC", radius=6, width=1)
    draw.text((275, 515), "📁 SQLite Database: sales.db (7 Bảng)", fill="#312E81", font=f_body_bold, anchor="mm")

    draw_rounded_box(draw, (520, 485, 930, 545), fill="#FFFBEB", outline="#FDE68A", radius=6, width=1)
    draw.text((725, 515), "☁️ OpenAI API Cloud (GPT-4o-mini Engine)", fill="#B45309", font=f_body_bold, anchor="mm")

    return img

# ================= 4. ACTIVITY POS =================
def generate_activity_pos():
    W, H = 1000, 500
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    draw.text((W//2, 20), "SƠ ĐỒ HOẠT ĐỘNG: QUY TRÌNH BÁN HÀNG POS & TRỪ TỒN KHO", fill="#1E3A8A", font=f_title, anchor="mt")

    steps = [
        ("Bắt đầu bán hàng", (50, 220, 160, 280), "#EFF6FF", "#3B82F6"),
        ("Chọn SP / Quét mã", (200, 220, 330, 280), "#EFF6FF", "#3B82F6"),
        ("Kiểm tra tồn kho\n(stock >= qty?)", (370, 210, 510, 290), "#FEF3C7", "#F59E0B"),
        ("Tạo HĐ & Giảm giá\n(Orders & Details)", (560, 220, 710, 280), "#EFF6FF", "#3B82F6"),
        ("Trừ kho tự động\n(stock -= qty)", (750, 220, 870, 280), "#F0FDF4", "#10B981"),
        ("In hóa đơn &\nHoàn tất", (900, 220, 980, 280), "#DCFCE7", "#16A34A"),
    ]

    for label, (x0, y0, x1, y1), fill, outline in steps:
        draw_rounded_box(draw, (x0, y0, x1, y1), fill=fill, outline=outline, radius=8, width=2)
        draw.text(((x0+x1)//2, (y0+y1)//2), label, fill="#0F172A", font=f_sm_bold, anchor="mm")

    # Arrows
    draw_arrow(draw, (160, 250), (200, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (330, 250), (370, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (510, 250), (560, 250), fill="#1E3A8A", width=2)
    draw.text((535, 235), "Đủ", fill="#16A34A", font=f_sm_bold, anchor="mm")

    draw_arrow(draw, (710, 250), (750, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (870, 250), (900, 250), fill="#1E3A8A", width=2)

    # Reject arrow from check stock
    draw.line([(440, 210), (440, 140), (265, 140), (265, 220)], fill="#DC2626", width=2)
    draw_arrow(draw, (265, 210), (265, 220), fill="#DC2626", width=2)
    draw.text((350, 125), "Hết hàng / Thiếu tồn kho (Báo lỗi)", fill="#DC2626", font=f_sm_bold, anchor="mm")

    return img

# ================= 5. ACTIVITY AI =================
def generate_activity_ai():
    W, H = 1000, 520
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    draw.text((W//2, 20), "SƠ ĐỒ HOẠT ĐỘNG: TRỢ LÝ AI TƯ VẤN & BẢO VỆ DỮ LIỆU", fill="#1E3A8A", font=f_title, anchor="mt")

    boxes = [
        ("Nhận câu hỏi\nngười dùng", (50, 220, 160, 280), "#EFF6FF", "#3B82F6"),
        ("Kiểm tra tần suất\n(Rate Limit)", (190, 220, 320, 280), "#FEF3C7", "#F59E0B"),
        ("Data Masking\n(Ẩn giá nhập, SĐT)", (350, 220, 490, 280), "#FEE2E2", "#EF4444"),
        ("Lọc SP còn hàng\n(stock > 0)", (520, 220, 650, 280), "#EFF6FF", "#3B82F6"),
        ("Gọi OpenAI API\n(Timeout 30s)", (680, 220, 810, 280), "#FEF3C7", "#F59E0B"),
        ("Hiển thị tư vấn\ncho khách", (840, 220, 960, 280), "#DCFCE7", "#16A34A"),
    ]

    for label, (x0, y0, x1, y1), fill, outline in boxes:
        draw_rounded_box(draw, (x0, y0, x1, y1), fill=fill, outline=outline, radius=8, width=2)
        draw.text(((x0+x1)//2, (y0+y1)//2), label, fill="#0F172A", font=f_sm_bold, anchor="mm")

    # Connections
    draw_arrow(draw, (160, 250), (190, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (320, 250), (350, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (490, 250), (520, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (650, 250), (680, 250), fill="#1E3A8A", width=2)
    draw_arrow(draw, (810, 250), (840, 250), fill="#1E3A8A", width=2)

    # Fallback branch
    draw_rounded_box(draw, (680, 370, 810, 430), fill="#F1F5F9", outline="#64748B", radius=8, width=2)
    draw.text((745, 400), "Fallback Response\n(Dự phòng an toàn)", fill="#334155", font=f_sm_bold, anchor="mm")
    draw_arrow(draw, (745, 280), (745, 370), fill="#DC2626", width=2)
    draw.text((760, 325), "Lỗi / Timeout", fill="#DC2626", font=f_sm, anchor="lm")
    draw.line([(810, 400), (900, 400), (900, 280)], fill="#64748B", width=2)
    draw_arrow(draw, (900, 290), (900, 280), fill="#64748B", width=2)

    return img

# ================= 6. SEQUENCE POS =================
def generate_sequence_pos():
    W, H = 1000, 560
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    draw.text((W//2, 20), "SƠ ĐỒ TUẦN TỰ: GIAO DỊCH BÁN HÀNG POS & GHI NHẬN HÓA ĐƠN", fill="#1E3A8A", font=f_title, anchor="mt")

    actors = [
        ("Người bán (Owner)", 100),
        ("Màn hình POS (React)", 350),
        ("Backend (FastAPI)", 620),
        ("CSDL (SQLite)", 880),
    ]

    for name, x in actors:
        draw_rounded_box(draw, (x-80, 65, x+80, 105), fill="#1E3A8A", outline="#0F172A", radius=6)
        draw.text((x, 85), name, fill="#FFFFFF", font=f_sm_bold, anchor="mm")
        draw.line([(x, 105), (x, 510)], fill="#94A3B8", width=2)

    # Lifeline messages
    calls = [
        (1, "1. Chọn sản phẩm & Bấm thanh toán", 100, 350, 140, "#1E3A8A"),
        (2, "2. POST /api/orders (kèm token)", 350, 620, 190, "#1E3A8A"),
        (3, "3. BEGIN TRANSACTION", 620, 880, 240, "#1E3A8A"),
        (4, "4. Kiểm tra & Trừ tồn kho (stock = stock - qty)", 620, 880, 290, "#1E3A8A"),
        (5, "5. Insert ORDERS & ORDER_DETAILS", 620, 880, 340, "#1E3A8A"),
        (6, "6. COMMIT TRANSACTION", 620, 880, 390, "#16A34A"),
        (7, "7. HTTP 201 Created (Chi tiết hóa đơn)", 620, 350, 440, "#16A34A"),
        (8, "8. Hiển thị thông báo thành công & In bill", 350, 100, 480, "#16A34A"),
    ]

    for num, txt, x0, x1, y, col in calls:
        draw_arrow(draw, (x0, y), (x1, y), fill=col, width=2, arrow_size=5)
        draw.text(((x0+x1)//2, y-10), txt, fill=col, font=f_sm_bold, anchor="mb")

    return img

# ================= 7. CLASS DIAGRAM =================
def generate_class_diagram():
    W, H = 1000, 620
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    f_title, f_h, f_body, f_body_bold, f_sm, f_sm_bold = get_fonts()

    draw.text((W//2, 20), "SƠ ĐỒ LỚP BACKEND (CLASS DIAGRAM - FASTAPI & SQLALCHEMY)", fill="#1E3A8A", font=f_title, anchor="mt")

    classes = [
        ("User", (40, 70, 240, 210), ["+id: int", "+username: str", "+password_hash: str", "+full_name: str", "+role: str", "+created_at: datetime"]),
        ("Category", (290, 70, 470, 170), ["+id: int", "+name: str", "+description: str"]),
        ("Product", (520, 70, 720, 250), ["+id: int", "+code: str", "+name: str", "+category_id: int", "+import_price: float", "+sell_price: float", "+stock: int", "+status: str", "+description: str"]),
        ("PurchaseReceipt", (760, 70, 960, 210), ["+id: int", "+code: str", "+supplier: str", "+user_id: int", "+total_amount: float", "+status: str", "+created_at: datetime"]),
        ("Customer", (40, 340, 240, 480), ["+id: int", "+name: str", "+phone: str", "+email: str", "+address: str", "+customer_group: str"]),
        ("Order", (290, 340, 490, 520), ["+id: int", "+code: str", "+customer_id: int", "+user_id: int", "+total_amount: float", "+discount: float", "+final_amount: float", "+payment_method: str", "+status: str", "+created_at: datetime"]),
        ("OrderDetail", (540, 340, 720, 480), ["+id: int", "+order_id: int", "+product_id: int", "+quantity: int", "+price: float", "+total: float"]),
        ("AIService", (760, 340, 960, 500), ["+consult_products()", "+analyze_report()", "+business_qa()", "-_mask_sensitive()", "-_call_openai()"]),
    ]

    for name, (x0, y0, x1, y1), attrs in classes:
        draw_rounded_box(draw, (x0, y0, x1, y1), fill="#FFFFFF", outline="#1E3A8A", radius=6, width=2)
        draw.rectangle([x0, y0, x1, y0+26], fill="#1E3A8A")
        draw.text(((x0+x1)//2, y0+13), name, fill="#FFFFFF", font=f_body_bold, anchor="mm")
        
        ay = y0 + 34
        for a in attrs:
            draw.text((x0+8, ay), a, fill="#1E293B", font=f_sm)
            ay += 18

    # Relationships
    draw_arrow(draw, (470, 120), (520, 120), fill="#2563EB", width=2)
    draw.text((495, 108), "1..N", fill="#2563EB", font=f_sm, anchor="mb")

    draw_arrow(draw, (620, 250), (620, 340), fill="#2563EB", width=2)
    draw.text((630, 295), "1..N", fill="#2563EB", font=f_sm, anchor="lm")

    draw_arrow(draw, (490, 420), (540, 420), fill="#2563EB", width=2)
    draw.text((515, 408), "1..N", fill="#2563EB", font=f_sm, anchor="mb")

    draw_arrow(draw, (240, 420), (290, 420), fill="#2563EB", width=2)
    draw.text((265, 408), "1..N", fill="#2563EB", font=f_sm, anchor="mb")

    return img

print("Generating all 7 diagrams...")
img_uc = generate_usecase()
img_erd = generate_erd()
img_arch = generate_architecture()
img_act_pos = generate_activity_pos()
img_act_ai = generate_activity_ai()
img_seq = generate_sequence_pos()
img_class = generate_class_diagram()

# Save images
diagram_map = [
    (img_uc, "01_use_case.png", "image1.png"),
    (img_class, "02_class_diagram.png", "image2.png"),
    (img_erd, "03_erd.png", "image3.png"),
    (img_arch, "04_architecture.png", "image4.png"),
    (img_act_pos, "05_seq_pos.png", "image5.png"),
    (img_act_ai, "06_seq_ai.png", "image6.png"),
    (img_seq, "07_state_order.png", "image7.png"),
]

for img, name_named, name_idx in diagram_map:
    # Save to tailieu/images
    img.save(os.path.join(IMG_TAILIEU, name_named))
    img.save(os.path.join(IMG_TAILIEU, name_idx))
    # Save to docs/images
    img.save(os.path.join(IMG_DOCS, name_named))
    img.save(os.path.join(IMG_DOCS, name_idx))
    print(f"Saved {name_named} & {name_idx}")

print("All 7 diagrams generated successfully!")