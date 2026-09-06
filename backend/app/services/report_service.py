from datetime import date, datetime, time, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import LOW_STOCK_THRESHOLD
from app.models import Category, Order, OrderDetail, Product


def completed_orders(db: Session, date_from=None, date_to=None):
    q = db.query(Order).filter(Order.status == "completed")
    if date_from:
        q = q.filter(Order.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        q = q.filter(
            Order.created_at < datetime.combine(date_to + timedelta(days=1), time.min)
        )
    return q


def revenue_series(db, date_from, date_to, group_by="day"):
    if group_by == "month":
        label = func.strftime("%Y-%m", Order.created_at)
    else:
        label = func.strftime("%Y-%m-%d", Order.created_at)
    rows = (
        completed_orders(db, date_from, date_to)
        .with_entities(
            label.label("label"),
            func.count(Order.id).label("orders"),
            func.sum(Order.final_amount).label("revenue"),
        )
        .group_by(label)
        .order_by(label)
        .all()
    )
    return [
        {
            "label": r.label,
            "orders": int(r.orders or 0),
            "revenue": round(float(r.revenue or 0)),
        }
        for r in rows
    ]


def revenue_by_category(db, date_from, date_to):
    rows = (
        completed_orders(db, date_from, date_to)
        .join(OrderDetail, OrderDetail.order_id == Order.id)
        .join(Product, Product.id == OrderDetail.product_id)
        .join(Category, Category.id == Product.category_id)
        .with_entities(
            Category.name.label("category"),
            func.sum(OrderDetail.quantity).label("quantity"),
            func.sum(OrderDetail.subtotal).label("revenue"),
        )
        .group_by(Category.name)
        .order_by(func.sum(OrderDetail.subtotal).desc())
        .all()
    )
    return [
        {
            "category": r.category,
            "quantity": int(r.quantity or 0),
            "revenue": round(float(r.revenue or 0)),
        }
        for r in rows
    ]


def top_products(db, date_from, date_to, limit=5):
    rows = (
        completed_orders(db, date_from, date_to)
        .join(OrderDetail, OrderDetail.order_id == Order.id)
        .join(Product, Product.id == OrderDetail.product_id)
        .with_entities(
            Product.id.label("product_id"),
            Product.code.label("code"),
            Product.name.label("name"),
            func.sum(OrderDetail.quantity).label("quantity"),
            func.sum(OrderDetail.subtotal).label("revenue"),
        )
        .group_by(Product.id, Product.code, Product.name)
        .order_by(func.sum(OrderDetail.quantity).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "product_id": r.product_id,
            "code": r.code,
            "name": r.name,
            "quantity": int(r.quantity or 0),
            "revenue": round(float(r.revenue or 0)),
        }
        for r in rows
    ]


def slow_products(db, date_from, date_to, limit=5):
    sold = dict(
        completed_orders(db, date_from, date_to)
        .join(OrderDetail, OrderDetail.order_id == Order.id)
        .with_entities(
            OrderDetail.product_id,
            func.sum(OrderDetail.quantity),
        )
        .group_by(OrderDetail.product_id)
        .all()
    )
    items = []
    for p in db.query(Product).filter(Product.status == "active").all():
        items.append(
            {
                "product_id": p.id,
                "code": p.code,
                "name": p.name,
                "quantity": int(sold.get(p.id, 0)),
                "revenue": 0.0,
            }
        )
    items.sort(key=lambda x: x["quantity"])
    return items[:limit]


def low_stock_products(db, threshold=None):
    threshold = threshold if threshold is not None else LOW_STOCK_THRESHOLD
    return (
        db.query(Product)
        .filter(Product.status == "active", Product.stock <= threshold)
        .order_by(Product.stock.asc())
        .all()
    )


def summary_text(db, date_from, date_to) -> str:
    series = revenue_series(db, date_from, date_to, group_by="month")
    total_rows = revenue_series(db, date_from, date_to, group_by="day")
    total_revenue = sum(r["revenue"] for r in total_rows)
    total_orders = sum(r["orders"] for r in total_rows)
    tops = top_products(db, date_from, date_to, limit=5)
    slows = slow_products(db, date_from, date_to, limit=5)
    lows = low_stock_products(db)

    lines = [f"Khoảng thời gian thống kê: {date_from} đến {date_to}"]
    lines.append(f"Tổng doanh thu: {total_revenue:,.0f} VND")
    lines.append(f"Số hóa đơn hoàn thành: {total_orders}")
    lines.append("Doanh thu theo tháng:")
    for row in series:
        lines.append(f"- {row['label']}: {row['revenue']:,.0f} VND ({row['orders']} hóa đơn)")
    lines.append("Sản phẩm bán chạy:")
    for t in tops:
        lines.append(f"- {t['name']} ({t['code']}): {t['quantity']} sản phẩm, {t['revenue']:,.0f} VND")
    if not tops:
        lines.append("- (Không có dữ liệu bán hàng trong kỳ)")
    lines.append("Sản phẩm bán chậm:")
    zero = [s for s in slows if s["quantity"] == 0]
    nonzero = [s for s in slows if s["quantity"] > 0]
    for s in nonzero:
        lines.append(f"- {s['name']} ({s['code']}): chỉ {s['quantity']} sản phẩm bán ra")
    for s in zero[:5]:
        lines.append(f"- {s['name']} ({s['code']}): không có đơn hàng trong kỳ")
    lines.append(f"Tình trạng tồn kho (các sản phẩm sắp hết, ngưỡng <= {LOW_STOCK_THRESHOLD}):")
    low_lines = [f"- {p.name} ({p.code}): còn {p.stock}" for p in lows]
    lines.extend(low_lines if low_lines else ["- Không có sản phẩm nào sắp hết hàng"])
    return "\n".join(lines)
