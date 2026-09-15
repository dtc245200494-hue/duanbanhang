"""Orders and checkout API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_optional
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdateStatus, OrderOut, OrderItemOut
from app.schemas.payment import PaymentOut
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderOut])
def list_orders(
    store_id: Optional[int] = Query(None, description="Lọc theo cửa hàng"),
    user_id: Optional[int] = Query(None, description="Lọc theo khách hàng"),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[OrderOut]:
    """Retrieve list of orders with items and payment transactions."""
    query = db.query(Order)
    if store_id:
        query = query.filter(Order.store_id == store_id)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    results: List[OrderOut] = []
    for ord_obj in orders:
        items_out = [
            OrderItemOut(
                id=item.id,
                order_id=item.order_id,
                batch_id=item.batch_id,
                batch_code=item.batch.batch_code if item.batch else None,
                product_name=item.batch.product.name if (item.batch and item.batch.product) else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in ord_obj.items
        ]
        payments_out = [
            PaymentOut(
                id=p.id,
                order_id=p.order_id,
                payment_method=p.payment_method,
                amount=p.amount,
                status=p.status,
                paid_at=p.paid_at,
            )
            for p in ord_obj.payments
        ]
        results.append(
            OrderOut(
                id=ord_obj.id,
                store_id=ord_obj.store_id,
                user_id=ord_obj.user_id,
                customer_name=ord_obj.customer_name,
                customer_phone=ord_obj.customer_phone,
                shipping_address=ord_obj.shipping_address,
                note=ord_obj.note,
                total_amount=ord_obj.total_amount,
                status=ord_obj.status,
                created_at=ord_obj.created_at,
                items=items_out,
                payments=payments_out,
            )
        )
    return results


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> OrderOut:
    """Create a customer order with automatic FEFO batch allocation and payment initialization."""
    try:
        # If user is logged in and user_id is not specified, associate with current user
        if current_user and not order_in.user_id:
            order_in.user_id = current_user.id

        order = OrderService.create_order(db=db, order_in=order_in)

        items_out = [
            OrderItemOut(
                id=item.id,
                order_id=item.order_id,
                batch_id=item.batch_id,
                batch_code=item.batch.batch_code if item.batch else None,
                product_name=item.batch.product.name if (item.batch and item.batch.product) else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ]
        payments_out = [
            PaymentOut(
                id=p.id,
                order_id=p.order_id,
                payment_method=p.payment_method,
                amount=p.amount,
                status=p.status,
                paid_at=p.paid_at,
            )
            for p in order.payments
        ]
        return OrderOut(
            id=order.id,
            store_id=order.store_id,
            user_id=order.user_id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            shipping_address=order.shipping_address,
            note=order.note,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            items=items_out,
            payments=payments_out,
        )
    except ValueError as val_err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý đơn hàng: {str(exc)}",
        )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderOut:
    """Get single order details, items, and payment status."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )
    items_out = [
        OrderItemOut(
            id=item.id,
            order_id=item.order_id,
            batch_id=item.batch_id,
            batch_code=item.batch.batch_code if item.batch else None,
            product_name=item.batch.product.name if (item.batch and item.batch.product) else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in order.items
    ]
    payments_out = [
        PaymentOut(
            id=p.id,
            order_id=p.order_id,
            payment_method=p.payment_method,
            amount=p.amount,
            status=p.status,
            paid_at=p.paid_at,
        )
        for p in order.payments
    ]
    return OrderOut(
        id=order.id,
        store_id=order.store_id,
        user_id=order.user_id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        note=order.note,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        items=items_out,
        payments=payments_out,
    )


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int, status_in: OrderUpdateStatus, db: Session = Depends(get_db)
) -> OrderOut:
    """Update order status (pending, confirmed, shipping, completed, cancelled)."""
    try:
        order = OrderService.update_order_status(
            db=db, order_id=order_id, new_status=status_in.status
        )
        items_out = [
            OrderItemOut(
                id=item.id,
                order_id=item.order_id,
                batch_id=item.batch_id,
                batch_code=item.batch.batch_code if item.batch else None,
                product_name=item.batch.product.name if (item.batch and item.batch.product) else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ]
        payments_out = [
            PaymentOut(
                id=p.id,
                order_id=p.order_id,
                payment_method=p.payment_method,
                amount=p.amount,
                status=p.status,
                paid_at=p.paid_at,
            )
            for p in order.payments
        ]
        return OrderOut(
            id=order.id,
            store_id=order.store_id,
            user_id=order.user_id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            shipping_address=order.shipping_address,
            note=order.note,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            items=items_out,
            payments=payments_out,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
