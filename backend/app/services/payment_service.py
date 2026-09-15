"""Payment processing and transaction lifecycle service."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.order import Order


class PaymentService:
    """Service handling payment records and settlement status updates."""

    @staticmethod
    def create_payment(
        db: Session,
        order_id: int,
        payment_method: str = "COD",
        amount: Optional[Decimal] = None,
    ) -> Payment:
        """Create a payment transaction record for an order."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Không tìm thấy đơn hàng ID: {order_id}")

        pay_amount = amount if amount is not None else order.total_amount
        payment = Payment(
            order_id=order_id,
            payment_method=payment_method,
            amount=pay_amount,
            status="pending",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def update_payment_status(
        db: Session, payment_id: int, status: str
    ) -> Payment:
        """Update payment status (pending, paid, failed)."""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Không tìm thấy giao dịch thanh toán ID: {payment_id}")

        payment.status = status
        if status == "paid":
            payment.paid_at = datetime.now(timezone.utc)
            # If paid and order is pending, advance order to confirmed
            if payment.order and payment.order.status == "pending":
                payment.order.status = "confirmed"

        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def list_payments(
        db: Session,
        order_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Payment]:
        """Fetch list of payment records."""
        query = db.query(Payment)
        if order_id:
            query = query.filter(Payment.order_id == order_id)
        if status:
            query = query.filter(Payment.status == status)
        return query.order_by(Payment.id.desc()).offset(skip).limit(limit).all()
