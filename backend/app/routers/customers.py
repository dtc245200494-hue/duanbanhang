from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Customer, Order, User
from app.schemas.customer import CustomerIn, CustomerOut, CustomerUpdate
from app.schemas.order import OrderOut
from app.routers.orders import to_order_out

router = APIRouter(prefix="/api/customers", tags=["customers"])
manage_roles = [Depends(require_roles("admin", "owner"))]


@router.get("", response_model=List[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    keyword: str = "",
    customer_group: str = "",
):
    q = db.query(Customer)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(
            or_(
                Customer.name.ilike(kw),
                Customer.phone.ilike(kw),
                Customer.email.ilike(kw),
            )
        )
    if customer_group:
        q = q.filter(Customer.customer_group == customer_group)
    return q.order_by(Customer.id.desc()).all()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    return customer


@router.get("/{customer_id}/orders", response_model=List[OrderOut])
def customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    orders = (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .order_by(Order.id.desc())
        .all()
    )
    return [to_order_out(db, o) for o in orders]


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(body: CustomerIn, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if body.customer_group not in ("normal", "vip", "wholesale"):
        raise HTTPException(status_code=400, detail="Nhóm khách không hợp lệ")
    customer = Customer(**body.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", dependencies=manage_roles)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    count = db.query(Order).filter(Order.customer_id == customer_id).count()
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Khách hàng đã có {count} hóa đơn, không thể xóa",
        )
    db.delete(customer)
    db.commit()
    return {"detail": "Đã xóa khách hàng"}
