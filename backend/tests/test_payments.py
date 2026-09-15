"""Unit tests for payment transactions and order settlement."""

from decimal import Decimal
from app.models.product import Product
from app.models.payment import Payment
from app.schemas.order import OrderCreate, OrderItemCreate
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService


def test_order_creates_payment_record(db_session):
    """Test creating an order automatically creates an initial payment record."""
    prod = db_session.query(Product).first()

    order_in = OrderCreate(
        customer_name="Payment Tester",
        customer_phone="0988776655",
        shipping_address="Hanoi",
        payment_method="momo",
        items=[OrderItemCreate(product_id=prod.id, quantity=2)],
    )

    order = OrderService.create_order(db=db_session, order_in=order_in)

    assert len(order.payments) == 1
    payment = order.payments[0]
    assert payment.payment_method == "momo"
    assert payment.amount == order.total_amount
    assert payment.status == "pending"
    assert payment.paid_at is None

    # Mark as paid
    updated_pay = PaymentService.update_payment_status(
        db=db_session, payment_id=payment.id, status="paid"
    )
    assert updated_pay.status == "paid"
    assert updated_pay.paid_at is not None
