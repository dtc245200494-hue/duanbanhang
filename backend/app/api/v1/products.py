"""Products API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.product import Product
from app.models.store import Store
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.schemas.batch import BatchOut

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductOut])
def list_products(
    store_id: Optional[int] = Query(None, description="Lọc theo cửa hàng"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[ProductOut]:
    """Retrieve list of products with total active inventory."""
    query = db.query(Product)
    if store_id:
        query = query.filter(Product.store_id == store_id)
    products = query.offset(skip).limit(limit).all()

    results: List[ProductOut] = []
    for prod in products:
        stock = sum(
            b.stock_quantity for b in prod.batches if b.status == "active"
        )
        out = ProductOut(
            id=prod.id,
            store_id=prod.store_id,
            name=prod.name,
            sku=prod.sku,
            original_price=prod.original_price,
            image_url=prod.image_url,
            created_at=prod.created_at,
            total_stock=stock,
        )
        results.append(out)
    return results


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    prod_in: ProductCreate, db: Session = Depends(get_db)
) -> ProductOut:
    """Create a new product record."""
    store = db.query(Store).filter(Store.id == prod_in.store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Store ID {prod_in.store_id} does not exist",
        )
    prod = Product(**prod_in.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return ProductOut(
        id=prod.id,
        store_id=prod.store_id,
        name=prod.name,
        sku=prod.sku,
        original_price=prod.original_price,
        image_url=prod.image_url,
        created_at=prod.created_at,
        total_stock=0,
    )


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductOut:
    """Get single product details."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    stock = sum(b.stock_quantity for b in prod.batches if b.status == "active")
    return ProductOut(
        id=prod.id,
        store_id=prod.store_id,
        name=prod.name,
        sku=prod.sku,
        original_price=prod.original_price,
        image_url=prod.image_url,
        created_at=prod.created_at,
        total_stock=stock,
    )


@router.get("/{product_id}/batches", response_model=List[BatchOut])
def get_product_batches(
    product_id: int, db: Session = Depends(get_db)
) -> List[BatchOut]:
    """List all batches belonging to a product, ordered by expiry date (FEFO)."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    batches = sorted(prod.batches, key=lambda b: b.expiry_date)
    return batches


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int, prod_in: ProductUpdate, db: Session = Depends(get_db)
) -> ProductOut:
    """Update product information."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    for key, value in prod_in.model_dump(exclude_unset=True).items():
        setattr(prod, key, value)
    db.commit()
    db.refresh(prod)
    stock = sum(b.stock_quantity for b in prod.batches if b.status == "active")
    return ProductOut(
        id=prod.id,
        store_id=prod.store_id,
        name=prod.name,
        sku=prod.sku,
        original_price=prod.original_price,
        image_url=prod.image_url,
        created_at=prod.created_at,
        total_stock=stock,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a product and all of its batches."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    db.delete(prod)
    db.commit()
