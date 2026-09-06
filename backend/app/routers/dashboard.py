from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import LOW_STOCK_THRESHOLD
from app.database import get_db
from app.models import Customer, Inventory, Order, Product, User
from app.routers.products import _to_out
from app.schemas.report import DashboardOut, TopProductRow
from app.services.report_service import low_stock_products, top_products

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
inventory_router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    now = datetime.now()
    today_min = datetime.combine(now.date(), time.min)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    completed = db.query(Order).filter(Order.status == "completed")
    total_revenue = db.query(func.sum(Order.final_amount)).filter(Order.status == "completed").scalar() or 0
    total_orders = db.query(Order).filter(Order.status == "completed").count()
    today_revenue = (
        db.query(func.sum(Order.final_amount))
        .filter(Order.status == "completed", Order.created_at >= today_min)
        .scalar()
        or 0
    )
    month_revenue = (
        db.query(func.sum(Order.final_amount))
        .filter(Order.status == "completed", Order.created_at >= month_start)
        .scalar()
        or 0
    )
    month_orders = (
        db.query(Order).filter(Order.status == "completed", Order.created_at >= month_start).count()
    )
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.status == "active").count()
    total_customers = db.query(Customer).count()

    first_of_month = month_start
    tops = top_products(db, first_of_month.date(), now.date(), limit=5)
    lows = low_stock_products(db)

    return DashboardOut(
        total_revenue=round(total_revenue),
        total_orders=total_orders,
        today_revenue=round(today_revenue),
        month_revenue=round(month_revenue),
        month_orders=month_orders,
        total_products=total_products,
        active_products=active_products,
        total_customers=total_customers,
        low_stock_count=len(lows),
        top_products=[TopProductRow(**t) for t in tops],
        low_stock_products=[_to_out(p) for p in lows],
    )


@inventory_router.get("")
def inventory_list(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    keyword: str = "",
):
    q = db.query(Inventory).join(Product)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter((Product.code.ilike(kw)) | (Product.name.ilike(kw)))
    rows = []
    for inv in q.order_by(Inventory.quantity.asc()).all():
        p = inv.product
        rows.append(
            {
                "product_id": p.id,
                "code": p.code,
                "name": p.name,
                "category_name": p.category_name,
                "quantity": inv.quantity,
                "sell_price": p.sell_price,
                "import_price": p.import_price,
                "stock_value": round(p.import_price * inv.quantity),
                "low": inv.quantity <= LOW_STOCK_THRESHOLD,
                "updated_at": inv.updated_at.strftime("%Y-%m-%d %H:%M:%S") if inv.updated_at else None,
            }
        )
    return rows
