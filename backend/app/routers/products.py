from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import (
    Category,
    Inventory,
    Order,
    OrderDetail,
    Product,
    PurchaseReceipt,
    User,
)
from app.schemas.order import OrderItemOut, OrderOut
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.inventory_service import set_stock

router = APIRouter(prefix="/api/products", tags=["products"])
manage_roles = [Depends(require_roles("admin", "owner"))]

PAYMENT_METHODS = ("cash", "card", "banking")


def _to_out(p: Product) -> ProductOut:
    out = ProductOut.model_validate(p)
    out.category_name = p.category_name
    return out


def _next_order_code(db: Session) -> str:
    seq = db.query(Order).count() + 1
    return f"ORD-{datetime.now():%Y%m%d}-{seq:04d}"


def to_order_out(db: Session, order: Order) -> OrderOut:
    items = []
    for d in order.details:
        items.append(
            OrderItemOut(
                id=d.id,
                product_id=d.product_id,
                product_name=d.product.name if d.product else "",
                quantity=d.quantity,
                unit_price=d.unit_price,
                subtotal=d.subtotal,
            )
        )
    return OrderOut(
        id=order.id,
        code=order.code,
        customer_id=order.customer_id,
        customer_name=order.customer.name if order.customer else None,
        created_by=order.user.full_name or (order.user.username if order.user else ""),
        created_at=order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        total_amount=order.total_amount,
        discount=order.discount,
        final_amount=order.final_amount,
        payment_method=order.payment_method,
        status=order.status,
        note=order.note or "",
        items=items,
    )


@router.get("", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    keyword: str = "",
    category_id: int = 0,
    status: str = "",
    low_stock: bool = False,
    skip: int = 0,
    limit: int = 200,
):
    q = db.query(Product)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(or_(Product.code.ilike(kw), Product.name.ilike(kw)))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if status:
        q = q.filter(Product.status == status)
    if low_stock:
        from app.config import LOW_STOCK_THRESHOLD

        q = q.filter(Product.stock <= LOW_STOCK_THRESHOLD)
    return [_to_out(p) for p in q.order_by(Product.id).offset(skip).limit(limit).all()]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return _to_out(product)


@router.post("", response_model=ProductOut, status_code=201, dependencies=manage_roles)
def create_product(body: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.code == body.code.strip()).first():
        raise HTTPException(status_code=400, detail="Mã sản phẩm đã tồn tại")
    if body.category_id and not db.get(Category, body.category_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy nhóm hàng")
    product = Product(**body.model_dump())
    db.add(product)
    db.flush()
    set_stock(db, product, body.stock)
    db.commit()
    db.refresh(product)
    return _to_out(product)


@router.put("/{product_id}", response_model=ProductOut, dependencies=manage_roles)
def update_product(product_id: int, body: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    data = body.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"]:
        if not db.get(Category, data["category_id"]):
            raise HTTPException(status_code=404, detail="Không tìm thấy nhóm hàng")
    if "stock" in data and data["stock"] is not None:
        new_stock = data.pop("stock")
        set_stock(db, product, new_stock)
    for field, value in data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return _to_out(product)


@router.delete("/{product_id}", dependencies=manage_roles)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    used_orders = db.query(OrderDetail).filter(OrderDetail.product_id == product_id).count()
    used_receipts = (
        db.query(PurchaseReceipt).filter(PurchaseReceipt.product_id == product_id).count()
    )
    if used_orders or used_receipts:
        raise HTTPException(
            status_code=400,
            detail="Sản phẩm đã có lịch sử bán/nhập hàng, chỉ có thể chuyển trạng thái Ngừng kinh doanh",
        )
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if inv:
        db.delete(inv)
    db.delete(product)
    db.commit()
    return {"detail": "Đã xóa sản phẩm"}
