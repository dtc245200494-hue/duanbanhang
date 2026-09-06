from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import OPENAI_MODEL
from app.database import get_db
from app.models import Category, Product, User
from app.routers.reports import _parse_dates
from app.services import ai_service, report_service
from app.services.ai_service import AIServiceError

router = APIRouter(prefix="/api/ai", tags=["ai"])


class ConsultIn(BaseModel):
    customer_request: str


class ReportIn(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class QAIn(BaseModel):
    question: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class AIOut(BaseModel):
    answer: str
    model: str
    prompt_file: str


def _handle_ai_error(exc: AIServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/consult", response_model=AIOut)
def consult(
    body: ConsultIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    products = (
        db.query(Product)
        .filter(Product.status == "active", Product.stock > 0)
        .order_by(Product.sell_price.asc())
        .all()
    )
    if products:
        lines = []
        for p in products:
            lines.append(
                f"- Mã {p.code} | {p.name} | Nhóm: {p.category_name or 'Khác'} | "
                f"Giá bán: {p.sell_price:,.0f} VND | Còn tồn: {p.stock} | {p.description or ''}"
            )
        product_table = "\n".join(lines)
    else:
        product_table = "(Hiện tại không còn sản phẩm nào trong kho)"

    prompt = ai_service.load_prompt(
        "product_consultant.txt",
        product_table=product_table,
        customer_request=ai_service.mask_sensitive(body.customer_request),
    )
    try:
        answer = ai_service.generate(prompt)
    except AIServiceError as exc:
        raise _handle_ai_error(exc)
    return AIOut(answer=answer, model=OPENAI_MODEL, prompt_file="product_consultant.txt")


@router.post("/report", response_model=AIOut)
def ai_report(
    body: ReportIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    f, t = _parse_dates(body.date_from, body.date_to)
    sales_data = report_service.summary_text(db, f, t)
    prompt = ai_service.load_prompt("sales_report.txt", sales_data=sales_data)
    try:
        answer = ai_service.generate(prompt)
    except AIServiceError as exc:
        raise _handle_ai_error(exc)
    return AIOut(answer=answer, model=OPENAI_MODEL, prompt_file="sales_report.txt")


@router.post("/qa", response_model=AIOut)
def ai_qa(
    body: QAIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    f, t = _parse_dates(body.date_from, body.date_to)
    sales_data = report_service.summary_text(db, f, t)
    prompt = ai_service.load_prompt(
        "sales_qa.txt",
        sales_data=sales_data,
        question=ai_service.mask_sensitive(body.question),
    )
    try:
        answer = ai_service.generate(prompt)
    except AIServiceError as exc:
        raise _handle_ai_error(exc)
    return AIOut(answer=answer, model=OPENAI_MODEL, prompt_file="sales_qa.txt")

