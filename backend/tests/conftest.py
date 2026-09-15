"""Test configuration and fixtures module (10 relational models with RBAC)."""

from datetime import date, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
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


@pytest.fixture(scope="function")
def test_engine():
    """Create a persistent shared in-memory SQLite engine using StaticPool."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for the test with 10 tables seeded."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()

    # 1. Roles
    r_admin = Role(code="admin", name="Admin", description="Administrator")
    r_mgr = Role(code="store_manager", name="Store Manager", description="Manager")
    r_cust = Role(code="customer", name="Customer", description="Buyer")
    session.add_all([r_admin, r_mgr, r_cust])
    session.flush()

    # 2. Users
    pwd_hash = get_password_hash("Admin@123")
    user_admin = User(
        role_id=r_admin.id,
        email="admin@freshmart.vn",
        hashed_password=pwd_hash,
        full_name="Admin Test",
        phone="0901111111",
        is_active=True,
    )
    user_cust = User(
        role_id=r_cust.id,
        email="customer@freshmart.vn",
        hashed_password=pwd_hash,
        full_name="Customer Test",
        phone="0902222222",
        is_active=True,
    )
    session.add_all([user_admin, user_cust])
    session.flush()

    # 3. Store
    store = Store(
        owner_id=user_admin.id,
        name="Test Store",
        phone="0123456789",
        address="Hanoi, Vietnam",
    )
    session.add(store)
    session.flush()

    # 4. Category
    cat = Category(name="Test Dairy", description="Milk and cheese")
    session.add(cat)
    session.flush()

    # 5. Product
    prod = Product(
        store_id=store.id,
        category_id=cat.id,
        name="Test Milk 1L",
        sku="TEST-MILK",
        original_price=Decimal("30000.00"),
    )
    session.add(prod)
    session.flush()

    today = date.today()
    # 6. Batches
    b1 = ProductBatch(
        product_id=prod.id,
        batch_code="B1",
        stock_quantity=10,
        expiry_date=today + timedelta(days=2),
        discount_rate=50,
        status="active",
    )
    b2 = ProductBatch(
        product_id=prod.id,
        batch_code="B2",
        stock_quantity=20,
        expiry_date=today + timedelta(days=10),
        discount_rate=0,
        status="active",
    )
    session.add_all([b1, b2])
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_engine, db_session):
    """FastAPI TestClient fixture overriding get_db dependency to point to shared engine."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
