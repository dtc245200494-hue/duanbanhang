"""Product batches and expiry tracking API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.batch import ProductBatch
from app.models.product import Product
from app.schemas.batch import (
    BatchCreate,
    BatchUpdate,
    BatchDiscountUpdate,
    BatchOut,
    BatchExpiringOut,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=List[BatchOut])
def list_batches(
    product_id: Optional[int] = Query(None, description="Lọc theo sản phẩm"),
    status_filter: Optional[str] = Query(None, alias="status", description="active, sold_out, expired"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[BatchOut]:
    """Retrieve list of product batches."""
    query = db.query(ProductBatch)
    if product_id:
        query = query.filter(ProductBatch.product_id == product_id)
    if status_filter:
        query = query.filter(ProductBatch.status == status_filter)
    return query.order_by(ProductBatch.expiry_date.asc()).offset(skip).limit(limit).all()


@router.get("/expiring", response_model=List[BatchExpiringOut])
def list_expiring_batches(
    days: int = Query(15, ge=1, le=180, description="Số ngày cận hạn tối đa"),
    store_id: Optional[int] = Query(None, description="Lọc theo cửa hàng"),
    db: Session = Depends(get_db),
) -> List[BatchExpiringOut]:
    """Retrieve near-expiry batches prioritized for AI discount recommendations (FEFO)."""
    # Refresh statuses first
    InventoryService.refresh_batch_statuses(db)

    batches = InventoryService.get_expiring_batches(
        db=db, days_threshold=days, store_id=store_id
    )

    results: List[BatchExpiringOut] = []
    for b in batches:
        results.append(
            BatchExpiringOut(
                id=b.id,
                product_id=b.product_id,
                batch_code=b.batch_code,
                stock_quantity=b.stock_quantity,
                expiry_date=b.expiry_date,
                discount_rate=b.discount_rate,
                status=b.status,
                days_until_expiry=b.days_until_expiry,
                effective_unit_price=b.effective_unit_price,
                product_name=b.product.name,
                product_sku=b.product.sku,
                original_price=b.product.original_price,
                store_name=b.product.store.name if b.product.store else None,
            )
        )
    return results


@router.post("", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
def create_batch(batch_in: BatchCreate, db: Session = Depends(get_db)) -> BatchOut:
    """Create a new product batch with expiry date."""
    product = db.query(Product).filter(Product.id == batch_in.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product ID {batch_in.product_id} does not exist",
        )
    batch = ProductBatch(**batch_in.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/{batch_id}", response_model=BatchOut)
def get_batch(batch_id: int, db: Session = Depends(get_db)) -> BatchOut:
    """Get batch details by ID."""
    batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found",
        )
    return batch


@router.patch("/{batch_id}/discount", response_model=BatchOut)
def apply_discount_rate(
    batch_id: int,
    discount_in: BatchDiscountUpdate,
    db: Session = Depends(get_db),
) -> BatchOut:
    """Apply new discount rate (e.g. proposed by AI or manager) to a specific batch."""
    batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found",
        )
    batch.discount_rate = discount_in.discount_rate
    db.commit()
    db.refresh(batch)
    return batch


@router.put("/{batch_id}", response_model=BatchOut)
def update_batch(
    batch_id: int, batch_in: BatchUpdate, db: Session = Depends(get_db)
) -> BatchOut:
    """Update batch parameters."""
    batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found",
        )
    for key, value in batch_in.model_dump(exclude_unset=True).items():
        setattr(batch, key, value)
    db.commit()
    db.refresh(batch)
    return batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(batch_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a product batch."""
    batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with ID {batch_id} not found",
        )
    db.delete(batch)
    db.commit()


@router.post("/refresh-status", status_code=status.HTTP_200_OK)
def refresh_batches_status(db: Session = Depends(get_db)) -> dict:
    """Manually trigger background check to update expired and sold out batches."""
    updated = InventoryService.refresh_batch_statuses(db)
    return {"message": f"Updated statuses for {updated} batches"}
