"""Payments management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.payment import Payment
from app.schemas.payment import PaymentUpdateStatus, PaymentOut
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=List[PaymentOut])
def list_payments(
    order_id: Optional[int] = Query(None, description="Lọc theo đơn hàng"),
    status_filter: Optional[str] = Query(None, alias="status", description="pending, paid, failed"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[Payment]:
    """List payment transactions."""
    return PaymentService.list_payments(
        db=db, order_id=order_id, status=status_filter, skip=skip, limit=limit
    )


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    """Get single payment record details."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found",
        )
    return payment


@router.patch("/{payment_id}/status", response_model=PaymentOut)
def update_payment_status(
    payment_id: int,
    status_in: PaymentUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "store_manager"])),
) -> Payment:
    """Update payment status (mark as paid or failed)."""
    try:
        return PaymentService.update_payment_status(
            db=db, payment_id=payment_id, status=status_in.status
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
