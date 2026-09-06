from datetime import date, datetime, time, timedelta
from typing import List, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Customer, Order, Product, User
from app.routers.products import to_order_out
from app.services import export_service, report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _parse_dates(date_from: Optional[date], date_to: Optional[date]):
    date_to = date_to or datetime.now().date()
    date_from = date_from or (date_to - timedelta(days=30))
    return date_from, date_to


@router.get("/revenue", response_model=List[dict])
def revenue(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    group_by: str = Query(default="day", pattern="^(day|month)$"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    f, t = _parse_dates(date_from, date_to)
    return report_service.revenue_series(db, f, t, group_by)


@router.get("/by-category", response_model=List[dict])
def by_category(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    f, t = _parse_dates(date_from, date_to)
    return report_service.revenue_by_category(db, f, t)


@router.get("/top-products", response_model=List[dict])
def top_products_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    limit: int = 5,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    f, t = _parse_dates(date_from, date_to)
    return report_service.top_products(db, f, t, limit=min(max(limit, 1), 50))


@router.get("/slow-products", response_model=List[dict])
def slow_products_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    limit: int = 5,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    f, t = _parse_dates(date_from, date_to)
    return report_service.slow_products(db, f, t, limit=min(max(limit, 1), 50))


def _build_rows(db: Session, rtype: str, f, t):
    if rtype == "sales":
        headers = ["Thời gian", "Số hóa đơn", "Doanh thu (VND)"]
        rows = [
            {"Thời gian": r["label"], "Số hóa đơn": r["orders"], "Doanh thu (VND)": r["revenue"]}
            for r in report_service.revenue_series(db, f, t, "day")
        ]
    elif rtype == "inventory":
        headers = ["Mã SP", "Tên sản phẩm", "Nhóm hàng", "Giá nhập", "Giá bán", "Tồn kho", "Trạng thái"]
        rows = [
            {
                "Mã SP": p.code,
                "Tên sản phẩm": p.name,
                "Nhóm hàng": p.category_name or "",
                "Giá nhập": round(p.import_price),
                "Giá bán": round(p.sell_price),
                "Tồn kho": p.stock,
                "Trạng thái": "Đang bán" if p.status == "active" else "Ngừng KD",
            }
            for p in db.query(Product).order_by(Product.code).all()
        ]
    else:
        headers = [
            "Mã HĐ", "Khách hàng", "Thời gian", "Tổng tiền", "Giảm giá",
            "Thành tiền", "Thanh toán", "Trạng thái",
        ]
        payment_label = {"cash": "Tiền mặt", "card": "Thẻ", "banking": "Chuyển khoản"}
        status_label = {"completed": "Hoàn thành", "cancelled": "Đã hủy"}
        q = db.query(Order).filter(
            Order.created_at >= datetime.combine(f, time.min),
            Order.created_at < datetime.combine(t + timedelta(days=1), time.min),
        )
        rows = []
        for o in q.order_by(Order.id.desc()).all():
            customer = db.get(Customer, o.customer_id) if o.customer_id else None
            rows.append(
                {
                    "Mã HĐ": o.code,
                    "Khách hàng": customer.name if customer else "Khách lẻ",
                    "Thời gian": o.created_at.strftime("%d/%m/%Y %H:%M"),
                    "Tổng tiền": round(o.total_amount),
                    "Giảm giá": round(o.discount),
                    "Thành tiền": round(o.final_amount),
                    "Thanh toán": payment_label.get(o.payment_method, o.payment_method),
                    "Trạng thái": status_label.get(o.status, o.status),
                }
            )
    return headers, rows


@router.get("/export")
def export_report(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    rtype: str = Query(default="sales", alias="type", pattern="^(sales|orders|inventory)$"),
    fmt: str = Query(default="csv", alias="format", pattern="^(csv|excel|pdf)$"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    f, t = _parse_dates(date_from, date_to)
    headers, rows = _build_rows(db, rtype, f, t)
    today = datetime.now().strftime("%Y%m%d")

    titles = {"sales": "BÁO CÁO DOANH THU THEO NGÀY", "orders": "DANH SÁCH HÓA ĐƠN", "inventory": "BÁO CÁO TỒN KHO"}
    title = f"{titles[rtype]} ({f:%d/%m/%Y} - {t:%d/%m/%Y})"

    if fmt == "csv":
        content = export_service.to_csv(rows, headers)
        media = "text/csv; charset=utf-8"
        ext = "csv"
    elif fmt == "excel":
        content = export_service.to_excel(rows, headers, sheet_name=titles[rtype])
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    else:
        content = export_service.to_pdf(title, rows, headers)
        media = "application/pdf"
        ext = "pdf"

    filename = f"report_{rtype}_{today}.{ext}"
    ascii_name = filename.encode("ascii", "ignore").decode() or "report"
    return Response(
        content=content,
        media_type=media,
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"
            )
        },
    )
