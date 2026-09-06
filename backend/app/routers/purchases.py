from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Product, PurchaseReceipt, User
from app.schemas.purchase import PurchaseReceiptIn, PurchaseReceiptOut
from app.services.inventory_service import adjust_stock

router = APIRouter(prefix="/api/purchases", tags=["purchases"])


def _to_out(r: PurchaseReceipt) -> PurchaseReceiptOut:
    return PurchaseReceiptOut(
        id=r.id,
        code=r.code,
        product_id=r.product_id,
        product_name=r.product.name if r.product else "",
        quantity=r.quantity,
        import_price=r.import_price,
        total_amount=r.import_price * r.quantity,
        supplier=r.supplier or "",
        note=r.note or "",
        received_at=r.received_at.strftime("%Y-%m-%d %H:%M:%S"),
    )


def _next_code(db: Session) -> str:
    seq = db.query(PurchaseReceipt).count() + 1
    return f"PR-{datetime.now():%Y%m%d}-{seq:04d}"


@router.get("")
def list_receipts(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    keyword: str = "",
    product_id: int = 0,
):
    q = db.query(PurchaseReceipt)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.join(Product).filter(
            (PurchaseReceipt.supplier.ilike(kw))
            | (PurchaseReceipt.code.ilike(kw))
            | (Product.name.ilike(kw))
        )
    if product_id:
        q = q.filter(PurchaseReceipt.product_id == product_id)
    return [_to_out(r) for r in q.order_by(PurchaseReceipt.id.desc()).limit(200).all()]


@router.post("", response_model=PurchaseReceiptOut, status_code=201)
def create_receipt(
    body: PurchaseReceiptIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.get(Product, body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    receipt = PurchaseReceipt(
        code=_next_code(db),
        product_id=product.id,
        quantity=body.quantity,
        import_price=body.import_price,
        supplier=body.supplier,
        note=body.note,
        user_id=user.id,
        received_at=datetime.now(),
    )
    db.add(receipt)
    adjust_stock(db, product, body.quantity)
    if body.import_price > 0:
        product.import_price = body.import_price
    db.commit()
    db.refresh(receipt)
    return _to_out(receipt)


@router.delete("/{receipt_id}", dependencies=[Depends(require_roles("admin", "owner"))])
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.get(PurchaseReceipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu nhập")
    product = db.get(Product, receipt.product_id)
    if product and product.stock >= receipt.quantity:
        adjust_stock(db, product, -receipt.quantity)
    else:
        raise HTTPException(
            status_code=400,
            detail="Không thể hủy phiếu nhập vì tồn kho hiện tại đã nhỏ hơn số lượng nhập",
        )
    db.delete(receipt)
    db.commit()
    return {"detail": "Đã xóa phiếu nhập và trừ lại tồn kho"}
