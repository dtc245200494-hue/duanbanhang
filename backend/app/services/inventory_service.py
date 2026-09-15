"""Inventory and FEFO (First Expired, First Out) batch allocation service."""

from datetime import date
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.batch import ProductBatch
from app.models.product import Product


class InventoryService:
    """Service handling batch inventory deductions, status updates, and FEFO allocation."""

    @staticmethod
    def refresh_batch_statuses(db: Session) -> int:
        """Update statuses for batches that have expired or reached 0 stock."""
        today = date.today()
        # Mark expired batches
        expired_count = (
            db.query(ProductBatch)
            .filter(ProductBatch.expiry_date < today, ProductBatch.status != "expired")
            .update({"status": "expired"}, synchronize_session=False)
        )

        # Mark sold out batches
        sold_out_count = (
            db.query(ProductBatch)
            .filter(
                ProductBatch.stock_quantity == 0,
                ProductBatch.status == "active",
                ProductBatch.expiry_date >= today,
            )
            .update({"status": "sold_out"}, synchronize_session=False)
        )

        db.commit()
        return expired_count + sold_out_count

    @staticmethod
    def get_expiring_batches(
        db: Session, days_threshold: int = 15, store_id: Optional[int] = None
    ) -> List[ProductBatch]:
        """Fetch active batches with stock that expire within specified days."""
        today = date.today()
        query = (
            db.query(ProductBatch)
            .join(Product, ProductBatch.product_id == Product.id)
            .filter(
                ProductBatch.status == "active",
                ProductBatch.stock_quantity > 0,
                ProductBatch.expiry_date >= today,
            )
        )
        if store_id:
            query = query.filter(Product.store_id == store_id)

        # Sort by nearest expiry first (FEFO)
        batches = query.order_by(ProductBatch.expiry_date.asc()).all()
        return [b for b in batches if b.days_until_expiry <= days_threshold]

    @staticmethod
    def allocate_fefo_stock(
        db: Session, product_id: int, quantity_needed: int
    ) -> List[Tuple[ProductBatch, int]]:
        """Allocate required quantity across batches using FEFO (First Expired, First Out).

        Returns:
            List of (ProductBatch, allocated_quantity) pairs.

        Raises:
            ValueError: If available stock across active batches is insufficient.
        """
        today = date.today()
        active_batches = (
            db.query(ProductBatch)
            .filter(
                ProductBatch.product_id == product_id,
                ProductBatch.status == "active",
                ProductBatch.stock_quantity > 0,
                ProductBatch.expiry_date >= today,
            )
            .order_by(ProductBatch.expiry_date.asc())
            .all()
        )

        total_available = sum(b.stock_quantity for b in active_batches)
        if total_available < quantity_needed:
            raise ValueError(
                f"Sản phẩm (ID: {product_id}) không đủ tồn kho. Yêu cầu: {quantity_needed}, còn lại: {total_available}"
            )

        allocations: List[Tuple[ProductBatch, int]] = []
        remaining = quantity_needed

        for batch in active_batches:
            if remaining <= 0:
                break
            take_qty = min(batch.stock_quantity, remaining)
            batch.stock_quantity -= take_qty
            remaining -= take_qty

            if batch.stock_quantity == 0:
                batch.status = "sold_out"

            allocations.append((batch, take_qty))

        return allocations

    @staticmethod
    def deduct_from_specific_batch(
        db: Session, batch_id: int, quantity: int
    ) -> Tuple[ProductBatch, int]:
        """Directly deduct stock from a chosen batch."""
        today = date.today()
        batch = (
            db.query(ProductBatch)
            .filter(ProductBatch.id == batch_id)
            .first()
        )

        if not batch:
            raise ValueError(f"Không tìm thấy lô hàng với ID: {batch_id}")

        if batch.expiry_date < today:
            raise ValueError(f"Lô hàng {batch.batch_code or batch.id} đã hết hạn sử dụng!")

        if batch.stock_quantity < quantity:
            raise ValueError(
                f"Lô hàng {batch.batch_code or batch.id} chỉ còn {batch.stock_quantity} sản phẩm, không đủ {quantity}!"
            )

        batch.stock_quantity -= quantity
        if batch.stock_quantity == 0:
            batch.status = "sold_out"

        return batch, quantity
