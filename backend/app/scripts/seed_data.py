"""Seed database with realistic initial retail data covering all 10 relational tables."""

from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
from app.database import engine, SessionLocal, Base
from app.models.role import Role
from app.models.user import User
from app.models.store import Store
from app.models.category import Category
from app.models.product import Product
from app.models.batch import ProductBatch
from app.models.ai_recommendation import AIDiscountRecommendation
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.core.security import get_password_hash


def utc_now():
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


def seed_database():
    """Drop and recreate all 10 tables, seeding comprehensive relational sample data."""
    print("Khởi tạo lại cấu trúc 10 bảng trong cơ sở dữ liệu SQLite...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Đang nạp dữ liệu mẫu cho 10 bảng...")
        today = date.today()

        # 1. ROLES
        role_admin = Role(
            code="admin",
            name="Quản trị viên tối cao",
            description="Toàn quyền quản trị hệ thống, quản lý tài khoản và chi nhánh.",
        )
        role_manager = Role(
            code="store_manager",
            name="Quản lý cửa hàng",
            description="Quản lý sản phẩm, lô hàng, phê duyệt đề xuất giảm giá AI.",
        )
        role_customer = Role(
            code="customer",
            name="Khách hàng",
            description="Người dùng mua sắm trực tuyến và theo dõi đơn hàng.",
        )
        db.add_all([role_admin, role_manager, role_customer])
        db.flush()

        # 2. USERS (hashed passwords using bcrypt)
        default_pwd = get_password_hash("Admin@123")
        user_admin = User(
            role_id=role_admin.id,
            email="admin@freshmart.vn",
            hashed_password=default_pwd,
            full_name="Nguyễn Văn Quản Trị",
            phone="0901112233",
            is_active=True,
        )
        user_manager = User(
            role_id=role_manager.id,
            email="manager@freshmart.vn",
            hashed_password=default_pwd,
            full_name="Trần Thị Quản Lý",
            phone="0902223344",
            is_active=True,
        )
        user_customer = User(
            role_id=role_customer.id,
            email="customer@freshmart.vn",
            hashed_password=default_pwd,
            full_name="Lê Hoàng Khách Hàng",
            phone="0903334455",
            is_active=True,
        )
        db.add_all([user_admin, user_manager, user_customer])
        db.flush()

        # 3. STORES (linked to owner_id)
        store1 = Store(
            owner_id=user_manager.id,
            name="Siêu thị FreshMart - Chi nhánh Cầu Giấy",
            phone="0901234567",
            address="Số 123 Đường Cầu Giấy, Quận Cầu Giấy, Hà Nội",
        )
        store2 = Store(
            owner_id=user_admin.id,
            name="FreshMart Express - Chi nhánh Ba Đình",
            phone="0918765432",
            address="Số 45 Phố Đội Cấn, Quận Ba Đình, Hà Nội",
        )
        db.add_all([store1, store2])
        db.flush()

        # 4. CATEGORIES
        cat_meat = Category(name="Đồ tươi sống & Thịt sạch", description="Thịt heo, bò, gia cầm tươi mới mỗi ngày")
        cat_dairy = Category(name="Sữa & Chế phẩm từ sữa", description="Sữa chua, sữa tươi tiệt trùng, phô mai")
        cat_bakery = Category(name="Bánh mì & Ngũ cốc", description="Bánh mì tươi, sandwich và ngũ cốc dinh dưỡng")
        cat_veggie = Category(name="Rau củ quả Đà Lạt", description="Rau thủy canh sạch đạt chuẩn VietGAP")
        db.add_all([cat_meat, cat_dairy, cat_bakery, cat_veggie])
        db.flush()

        # 5. PRODUCTS (linked to store_id and category_id)
        p1 = Product(
            store_id=store1.id,
            category_id=cat_dairy.id,
            name="Sữa tươi tiệt trùng Vinamilk 100% Không Đường 1L",
            sku="VM-MILK-1L",
            original_price=Decimal("38000.00"),
            image_url="https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400",
        )
        p2 = Product(
            store_id=store1.id,
            category_id=cat_bakery.id,
            name="Bánh mì Sandwich tươi Kinh Đô 250g",
            sku="KD-BREAD-250",
            original_price=Decimal("18000.00"),
            image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400",
        )
        p3 = Product(
            store_id=store1.id,
            category_id=cat_dairy.id,
            name="Sữa chua uống men sống Yakult (Lốc 5 chai)",
            sku="YK-YOG-5",
            original_price=Decimal("26500.00"),
            image_url="https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400",
        )
        p4 = Product(
            store_id=store1.id,
            category_id=cat_meat.id,
            name="Thịt ba chỉ heo sạch MeatDeli 400g",
            sku="MD-PORK-400",
            original_price=Decimal("72000.00"),
            image_url="https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400",
        )
        p5 = Product(
            store_id=store2.id,
            category_id=cat_meat.id,
            name="Trứng gà tươi Ba Huân (Hộp 10 quả)",
            sku="BH-EGG-10",
            original_price=Decimal("33000.00"),
            image_url="https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400",
        )
        p6 = Product(
            store_id=store2.id,
            category_id=cat_veggie.id,
            name="Rau xà lách mỡ thủy canh Đà Lạt 300g",
            sku="DL-VEG-300",
            original_price=Decimal("22000.00"),
            image_url="https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400",
        )
        db.add_all([p1, p2, p3, p4, p5, p6])
        db.flush()

        # 6. PRODUCT BATCHES
        b_p2_urgent = ProductBatch(
            product_id=p2.id,
            batch_code="BATCH-KD-0913",
            stock_quantity=18,
            expiry_date=today + timedelta(days=2),
            discount_rate=50,
            status="active",
        )
        b_p2_fresh = ProductBatch(
            product_id=p2.id,
            batch_code="BATCH-KD-0916",
            stock_quantity=45,
            expiry_date=today + timedelta(days=6),
            discount_rate=0,
            status="active",
        )
        b_p1_near = ProductBatch(
            product_id=p1.id,
            batch_code="BATCH-VM-0915",
            stock_quantity=24,
            expiry_date=today + timedelta(days=4),
            discount_rate=30,
            status="active",
        )
        b_p1_safe = ProductBatch(
            product_id=p1.id,
            batch_code="BATCH-VM-1010",
            stock_quantity=60,
            expiry_date=today + timedelta(days=28),
            discount_rate=0,
            status="active",
        )
        b_p4_critical = ProductBatch(
            product_id=p4.id,
            batch_code="BATCH-MD-0914",
            stock_quantity=12,
            expiry_date=today + timedelta(days=1),
            discount_rate=60,
            status="active",
        )
        b_p6_near = ProductBatch(
            product_id=p6.id,
            batch_code="BATCH-DL-0918",
            stock_quantity=15,
            expiry_date=today + timedelta(days=3),
            discount_rate=40,
            status="active",
        )
        db.add_all([b_p2_urgent, b_p2_fresh, b_p1_near, b_p1_safe, b_p4_critical, b_p6_near])
        db.flush()

        # 7. AI DISCOUNT RECOMMENDATIONS (Audit & Workflow)
        rec1 = AIDiscountRecommendation(
            batch_id=b_p2_urgent.id,
            recommended_discount=50,
            reason="Lô bánh mì chỉ còn 2 ngày đến hạn, đề xuất xả hàng 50% để thu hồi vốn.",
            status="approved",
            approved_by=user_manager.id,
            created_at=utc_now() - timedelta(hours=6),
        )
        rec2 = AIDiscountRecommendation(
            batch_id=b_p4_critical.id,
            recommended_discount=60,
            reason="Thịt heo sạch còn 1 ngày đến hạn. Mức độ khẩn cấp đỏ, giảm sâu 60%.",
            status="approved",
            approved_by=user_manager.id,
            created_at=utc_now() - timedelta(hours=4),
        )
        rec3 = AIDiscountRecommendation(
            batch_id=b_p1_near.id,
            recommended_discount=30,
            reason="Sữa tươi Vinamilk còn 4 ngày đến hạn sử dụng. Đề xuất giảm 30%.",
            status="pending",
            approved_by=None,
            created_at=utc_now() - timedelta(minutes=30),
        )
        db.add_all([rec1, rec2, rec3])
        db.flush()

        # 8. ORDERS (linked to user_id)
        order1 = Order(
            store_id=store1.id,
            user_id=user_customer.id,
            customer_name=user_customer.full_name,
            customer_phone=user_customer.phone,
            shipping_address="Toà nhà FPT Tower, 10 Phạm Văn Bạch, Cầu Giấy, HN",
            note="Giao giờ hành chính",
            total_amount=Decimal("45600.00"),
            status="completed",
            created_at=utc_now() - timedelta(hours=3),
        )
        order2 = Order(
            store_id=store1.id,
            user_id=None,  # Guest checkout
            customer_name="Nguyễn Khách Vãng Lai",
            customer_phone="0911223344",
            shipping_address="302 Cầu Giấy, Cầu Giấy, HN",
            note="Gọi trước khi đến",
            total_amount=Decimal("26600.00"),
            status="shipping",
            created_at=utc_now() - timedelta(hours=1),
        )
        db.add_all([order1, order2])
        db.flush()

        # 9. ORDER ITEMS
        item1 = OrderItem(
            order_id=order1.id,
            batch_id=b_p2_urgent.id,
            quantity=2,
            unit_price=Decimal("9000.00"),
        )
        item2 = OrderItem(
            order_id=order1.id,
            batch_id=b_p1_near.id,
            quantity=1,
            unit_price=Decimal("26600.00"),
        )
        item3 = OrderItem(
            order_id=order2.id,
            batch_id=b_p1_near.id,
            quantity=1,
            unit_price=Decimal("26600.00"),
        )
        db.add_all([item1, item2, item3])
        db.flush()

        # 10. PAYMENTS
        pay1 = Payment(
            order_id=order1.id,
            payment_method="momo",
            amount=Decimal("45600.00"),
            status="paid",
            paid_at=utc_now() - timedelta(hours=3),
        )
        pay2 = Payment(
            order_id=order2.id,
            payment_method="COD",
            amount=Decimal("26600.00"),
            status="pending",
            paid_at=None,
        )
        db.add_all([pay1, pay2])

        db.commit()
        print("Đã hoàn tất nạp dữ liệu cho 10 bảng cơ sở dữ liệu thành công!")
    except Exception as exc:
        db.rollback()
        print(f"Lỗi khi seed dữ liệu: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
