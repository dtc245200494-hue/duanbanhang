from app.models.inventory import Inventory


def set_stock(db, product, quantity: int) -> None:
    quantity = max(0, int(quantity))
    product.stock = quantity
    inv = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    if inv is None:
        db.add(Inventory(product_id=product.id, quantity=quantity))
    else:
        inv.quantity = quantity


def adjust_stock(db, product, delta: int) -> None:
    set_stock(db, product, (product.stock or 0) + delta)
