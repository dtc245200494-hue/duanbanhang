import random
from datetime import datetime, timedelta

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import (
    Category,
    Customer,
    Order,
    OrderDetail,
    Product,
    PurchaseReceipt,
    User,
)
from app.services.inventory_service import set_stock

CATEGORIES = [
    ("Phụ kiện", "Chuột, bàn phím, tai nghe, sạc, cáp..."),
    ("Điện thoại", "Điện thoại di động chính hãng"),
    ("Laptop", "Máy tính xách tay văn phòng và gaming"),
    ("Âm thanh", "Loa, tai nghe các loại"),
]

PRODUCTS = [
    ("ACC-001", "Tai nghe Bluetooth A1", "Phụ kiện", 220000, 350000, 60,
     "Pin 20 giờ, chống ồn chủ động, kết nối Bluetooth 5.3"),
    ("ACC-002", "Sạc nhanh 65W Anker", "Phụ kiện", 420000, 590000, 40,
     "Sạc nhanh đa thiết bị, kèm cáp Type-C"),
    ("ACC-003", "Ốp lưng chống sốc iPhone 15", "Phụ kiện", 85000, 150000, 80,
     "Chống sốc chuẩn quân đội, trong suốt"),
    ("AUD-001", "Tai nghe Sony WH-CH520", "Âm thanh", 980000, 1290000, 30,
     "Pin 50 giờ, âm bass mạnh"),
    ("AUD-002", "Loa Bluetooth JBL Go 3", "Âm thanh", 750000, 990000, 25,
     "Nhỏ gọn, chống nước IP67"),
    ("PHN-001", "iPhone 15 128GB", "Điện thoại", 18500000, 21500000, 12,
     "Chip A16, camera 48MP, chính hãng"),
    ("PHN-002", "Samsung Galaxy S24 256GB", "Điện thoại", 17000000, 19900000, 10,
     "Galaxy AI, màn hình 120Hz"),
    ("PHN-003", "Xiaomi Redmi Note 13 8/256GB", "Điện thoại", 4800000, 5700000, 35,
     "Pin 5000mAh, sạc nhanh 33W"),
    ("LAP-001", "Laptop Acer Nitro 5 GTX1650", "Laptop", 14200000, 16900000, 8,
     "Core i5-12450H, RAM 16GB, SSD 512GB"),
    ("LAP-002", "MacBook Air M2 8/256GB", "Laptop", 24500000, 27900000, 6,
     "Chip M2, màn hình Retina 13.6 inch"),
    ("WCH-001", "Đồng hồ thông minh Watch Fit 3", "Phụ kiện", 1450000, 1890000, 22,
     "Theo dõi sức khỏe, GPS, pin 10 ngày"),
    ("OLD-001", "Cáp sạc Micro USB (ngừng KD)", "Phụ kiện", 20000, 35000, 5,
     "Sản phẩm cũ, ngừng kinh doanh"),
]

CUSTOMERS = [
    ("Nguyễn Thị Lan", "0912345678", "lan.nguyen@example.com", "12 Hai Bà Trưng, Hà Nội", "vip"),
    ("Trần Văn Bình", "0987654321", "binh.tran@example.com", "45 Nguyễn Trãi, Hà Nội", "normal"),
    ("Lê Hoàng Nam", "0901122334", "nam.le@example.com", "78 Giải Phóng, Hà Nội", "wholesale"),
    ("Phạm Thu Hà", "0977558899", "ha.pham@example.com", "159 Cầu Giấy, Hà Nội", "vip"),
    ("Vũ Đức Anh", "0933445566", "", "234 Láng Hạ, Hà Nội", "normal"),
]


def seed_base(db):
    users = [
        User(username="admin", password_hash=hash_password("admin123"),
             full_name="Nguyễn Quản Trị", role="admin"),
        User(username="owner", password_hash=hash_password("owner123"),
             full_name="Trần Văn Chủ", role="owner"),
    ]
    db.add_all(users)

    cats = {name: Category(name=name, description=desc) for name, desc in CATEGORIES}
    db.add_all(cats.values())

    initial_stock = {}
    for code, name, cat_name, imp, sell, stock, desc in PRODUCTS:
        p = Product(
            code=code, name=name, category=cats[cat_name],
            import_price=imp, sell_price=sell, stock=stock,
            status="inactive" if code.startswith("OLD") else "active",
            description=desc,
        )
        db.add(p)
        db.flush()
        set_stock(db, p, stock)
        initial_stock[code] = stock

    for name, phone, email, address, group in CUSTOMERS:
        db.add(Customer(name=name, phone=phone, email=email,
                        address=address, customer_group=group))

    db.commit()
    return initial_stock


def seed_transactions(db, initial_stock):
    random.seed(42)
    products_by_code = {p.code: p for p in db.query(Product).all()}
    customers = db.query(Customer).all()
    owner = db.query(User).filter(User.username == "owner").first()

    hot_codes = ["ACC-001", "AUD-001", "ACC-002"]
    normal_codes = ["ACC-003", "AUD-002", "PHN-003", "LAP-001", "WCH-001", "PHN-001"]

    today = datetime.now()
    start_day = (today - timedelta(days=55)).replace(hour=0, minute=0, second=0)
    seq = 0
    sold = {}
    received = {}

    receipt_plan = [("ACC-001", 20), ("AUD-001", 15), ("ACC-003", 30)]
    for offset, (code, qty) in enumerate(receipt_plan):
        product = products_by_code[code]
        db.add(PurchaseReceipt(
            code=f"PR-{start_day:%Y%m%d}-{offset + 1:04d}",
            product_id=product.id,
            quantity=qty,
            import_price=product.import_price,
            supplier="Công ty TNHH Phân phối Việt",
            note="Nhập hàng định kỳ",
            user_id=owner.id if owner else None,
            received_at=start_day + timedelta(days=offset + 1),
        ))
        received[code] = received.get(code, 0) + qty

    day = start_day
    while day <= today - timedelta(days=1):
        n_orders = random.choice([0, 1, 2, 2, 3])
        for _ in range(n_orders):
            cancelled = random.random() < 0.08
            n_items = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            picked = []
            seen = set()
            for _ in range(n_items):
                code = random.choice(hot_codes) if random.random() < 0.55 else random.choice(normal_codes)
                if code not in seen:
                    seen.add(code)
                    qty = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
                    picked.append((code, qty))

            total = 0.0
            details = []
            for code, qty in picked:
                p = products_by_code[code]
                subtotal = p.sell_price * qty
                total += subtotal
                details.append((p, qty, p.sell_price, subtotal))
                if not cancelled:
                    sold[code] = sold.get(code, 0) + qty

            discount = random.choice([0, 0, 0, 20000, 50000]) if total >= 500000 else 0
            discount = min(discount, total)
            seq += 1
            order_time = day.replace(
                hour=random.randint(8, 21),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )
            order = Order(
                code=f"ORD-{order_time:%Y%m%d}-{seq:04d}",
                customer_id=random.choice(customers).id if random.random() < 0.8 else None,
                user_id=random.choice([u.id for u in db.query(User).filter(User.role.in_(["owner", "admin"]))]),
                total_amount=total,
                discount=float(discount),
                final_amount=total - discount,
                payment_method=random.choices(["cash", "card", "banking"], weights=[60, 15, 25])[0],
                status="cancelled" if cancelled else "completed",
                created_at=order_time,
            )
            for p, qty, price, sub in details:
                order.details.append(OrderDetail(
                    product_id=p.id, quantity=qty, unit_price=price, subtotal=sub,
                ))
            db.add(order)
        day += timedelta(days=1)

    db.commit()

    for code, initial in initial_stock.items():
        final = max(0, initial - sold.get(code, 0))
        set_stock(db, products_by_code[code], final)
    db.commit()


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database đã có dữ liệu, bỏ qua seed.")
            return
        initial_stock = seed_base(db)
        seed_transactions(db, initial_stock)
        print("Seed dữ liệu mẫu thành công!")
        print("Tài khoản: admin/admin123 | owner/owner123")
        print(f"Database: {engine.url}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
