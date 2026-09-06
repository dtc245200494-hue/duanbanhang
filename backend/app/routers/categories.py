from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Category, Product, User
from app.schemas.category import CategoryIn, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])
manage_roles = [Depends(require_roles("admin", "owner"))]


@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Category).order_by(Category.name).all()


@router.post("", response_model=CategoryOut, status_code=201, dependencies=manage_roles)
def create_category(body: CategoryIn, db: Session = Depends(get_db)):
    exists = db.query(Category).filter(Category.name == body.name.strip()).first()
    if exists:
        raise HTTPException(status_code=400, detail="Nhóm hàng đã tồn tại")
    cat = Category(name=body.name.strip(), description=body.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}", response_model=CategoryOut, dependencies=manage_roles)
def update_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhóm hàng")
    if body.name is not None:
        dup = (
            db.query(Category)
            .filter(Category.name == body.name.strip(), Category.id != category_id)
            .first()
        )
        if dup:
            raise HTTPException(status_code=400, detail="Nhóm hàng đã tồn tại")
        cat.name = body.name.strip()
    if body.description is not None:
        cat.description = body.description
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", dependencies=manage_roles)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhóm hàng")
    count = db.query(Product).filter(Product.category_id == category_id).count()
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể xóa: còn {count} sản phẩm thuộc nhóm hàng này",
        )
    db.delete(cat)
    db.commit()
    return {"detail": "Đã xóa nhóm hàng"}
