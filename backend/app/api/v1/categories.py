"""Product categories API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryOut])
def list_categories(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[CategoryOut]:
    """Retrieve list of product categories with item count."""
    cats = db.query(Category).offset(skip).limit(limit).all()
    return [
        CategoryOut(
            id=c.id,
            name=c.name,
            description=c.description,
            product_count=len(c.products),
        )
        for c in cats
    ]


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "store_manager"])),
) -> CategoryOut:
    """Create a new category (Admin/Manager only)."""
    existing = db.query(Category).filter(Category.name == cat_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Danh mục '{cat_in.name}' đã tồn tại!",
        )
    cat = Category(**cat_in.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryOut(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        product_count=0,
    )


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryOut:
    """Get single category details."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return CategoryOut(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        product_count=len(cat.products),
    )


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    cat_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "store_manager"])),
) -> CategoryOut:
    """Update a category."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    for key, value in cat_in.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return CategoryOut(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        product_count=len(cat.products),
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
) -> None:
    """Delete a category (Admin only)."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    db.delete(cat)
    db.commit()
