from datetime import datetime, time, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Customer, Order, OrderDetail, Product, User
from app.schemas.order import OrderCreate, OrderOut
from app.routers.products import PAYMENT_METHODS, _next_order_code, to_order_out
from app.services.inventory_service import adjust_stock

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=List[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    keyword: str = "",
    status: str = "",
    payment_method: str = "",
    customer_id: int = 0,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    q = db.query(Order)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.join(Customer, Order.customer_id == Customer.id, isouter=True).filter(
            or_(Order.code.ilike(kw), Customer.name.ilike(kw))
        )
    if status:
        q = q.filter(Order.status == status)
    if payment_method:
        q = q.filter(Order.payment_method == payment_method)
    if customer_id:
        q = q.filter(Order.customer_id == customer_id)
    if date_from:
        d = datetime.strptime(date_from, "%Y-%m-%d")
        q = q.filter(Order.created_at >= datetime.combine(d.date(), time.min))
    if date_to:
        d = datetime.strptime(date_to, "%Y-%m-%d")
        q = q.filter(
            Order.created_at < datetime.combine(d.date() + timedelta(days=1), time.min)
        )
    return [to_order_out(db, o) for o in q.order_by(Order.id.desc()).limit(300).all()]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
    return to_order_out(db, order)


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.payment_method not in PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="Phương thức thanh toán không hợp lệ")

    product_ids = [i.product_id for i in body.items]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    total_amount = 0.0
    lines = []
    for item in body.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm id={item.product_id}")
        if product.status != "active":
            raise HTTPException(status_code=400, detail=f"Sản phẩm '{product.name}' đã ngừng kinh doanh")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product.name}' không đủ tồn kho (còn {product.stock}, cần {item.quantity})",
            )
        subtotal = product.sell_price * item.quantity
        total_amount += subtotal
        lines.append((product, item.quantity, product.sell_price, subtotal))

    discount = min(max(body.discount, 0.0), total_amount)
    final_amount = total_amount - discount

    order = Order(
        code=_next_order_code(db),
        customer_id=body.customer_id,
        user_id=user.id,
        total_amount=total_amount,
        discount=discount,
        final_amount=final_amount,
        payment_method=body.payment_method,
        status="completed",
        note=body.note,
        created_at=datetime.now(),
    )
    if body.customer_id and not db.get(Customer, body.customer_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")

    for product, quantity, unit_price, subtotal in lines:
        detail = OrderDetail(
            order_id=None,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )
        order.details.append(detail)
        adjust_stock(db, product, -quantity)

    db.add(order)
    db.commit()
    db.refresh(order)
    return to_order_out(db, order)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Hóa đơn đã bị hủy trước đó")
    for d in order.details:
        product = db.get(Product, d.product_id)
        if product:
            adjust_stock(db, product, d.quantity)
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return to_order_out(db, order)
