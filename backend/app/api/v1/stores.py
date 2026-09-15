"""Stores API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreOut

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("", response_model=List[StoreOut])
def list_stores(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Store]:
    """Retrieve list of stores."""
    return db.query(Store).offset(skip).limit(limit).all()


@router.post("", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
def create_store(store_in: StoreCreate, db: Session = Depends(get_db)) -> Store:
    """Create a new store."""
    store = Store(**store_in.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("/{store_id}", response_model=StoreOut)
def get_store(store_id: int, db: Session = Depends(get_db)) -> Store:
    """Get store details by ID."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID {store_id} not found",
        )
    return store


@router.put("/{store_id}", response_model=StoreOut)
def update_store(
    store_id: int, store_in: StoreUpdate, db: Session = Depends(get_db)
) -> Store:
    """Update store details."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID {store_id} not found",
        )
    for key, value in store_in.model_dump(exclude_unset=True).items():
        setattr(store, key, value)
    db.commit()
    db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(store_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a store and all associated products."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID {store_id} not found",
        )
    db.delete(store)
    db.commit()
