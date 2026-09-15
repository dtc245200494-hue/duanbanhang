"""Order fulfillment and lifecycle management service."""

from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.batch import ProductBatch
from app.models.payment import Payment
from app.schemas.order import OrderCreate
from app.services.inventory_service import InventoryService


class OrderService:
    """Service encapsulating order creation, pricing computation, and status management."""

    @staticmethod
    def create_order(db: Session, order_in: OrderCreate) -> Order:
        """Create a new customer order, deducting inventory via FEFO or chosen batch."""
        new_order = Order(
            store_id=order_in.store_id,
            user_id=order_in.user_id,
            customer_name=order_in.customer_name,
            customer_phone=order_in.customer_phone,
            shipping_address=order_in.shipping_address,
            note=order_in.note,
            total_amount=Decimal("0.00"),
            status="pending",
        )
        db.add(new_order)
        db.flush()  # Generates new_order.id

        total_amount = Decimal("0.00")

        for item_in in order_in.items:
            # Case 1: Specific batch chosen
            if item_in.batch_id:
                batch, qty = InventoryService.deduct_from_specific_batch(
                    db=db, batch_id=item_in.batch_id, quantity=item_in.quantity
                )
                unit_price = batch.effective_unit_price
                order_item = OrderItem(
                    order_id=new_order.id,
                    batch_id=batch.id,
                    quantity=qty,
                    unit_price=unit_price,
                )
                db.add(order_item)
                total_amount += unit_price * Decimal(str(qty))

            # Case 2: Product ID provided, automatically allocate via FEFO
            elif item_in.product_id:
                product = (
                    db.query(Product).filter(Product.id == item_in.product_id).first()
                )
                if not product:
                    raise ValueError(f"Không tìm thấy sản phẩm ID: {item_in.product_id}")

                allocations = InventoryService.allocate_fefo_stock(
                    db=db,
                    product_id=item_in.product_id,
                    quantity_needed=item_in.quantity,
                )

                for batch, qty in allocations:
                    unit_price = batch.effective_unit_price
                    order_item = OrderItem(
                        order_id=new_order.id,
                        batch_id=batch.id,
                        quantity=qty,
                        unit_price=unit_price,
                    )
                    db.add(order_item)
                    total_amount += unit_price * Decimal(str(qty))
            else:
                raise ValueError("Mỗi mặt hàng trong đơn phải chỉ định batch_id hoặc product_id!")

        final_total = round(total_amount, 2)
        new_order.total_amount = final_total

        # Automatically generate initial payment record
        pay_method = order_in.payment_method or "COD"
        payment = Payment(
            order_id=new_order.id,
            payment_method=pay_method,
            amount=final_total,
            status="pending",
        )
        db.add(payment)

        db.commit()
        db.refresh(new_order)
        return new_order

    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
        """Update order status and restore inventory if cancelled."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Không tìm thấy đơn hàng ID: {order_id}")

        old_status = order.status
        if old_status == new_status:
            return order

        # If transitioning to cancelled, restore allocated stock back to batches
        if new_status == "cancelled" and old_status in ["pending", "confirmed"]:
            for item in order.items:
                if item.batch:
                    item.batch.stock_quantity += item.quantity
                    if item.batch.status == "sold_out":
                        item.batch.status = "active"

        order.status = new_status
        db.commit()
        db.refresh(order)
        return order
