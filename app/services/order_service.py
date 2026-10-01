from sqlalchemy.orm import Session
from app.repositories import order_repository


class InsufficientStockError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


def create_order(db: Session, buyer_user_id: int, items: list):
    try:
        total_amount = 0
        order_items_data = []

        for item in items:
            product = order_repository.get_product_for_update(db, item.product_id)
            if not product or not product.is_active:
                raise ProductNotFoundError(f"Product {item.product_id} not found")
            if product.stock_quantity < item.quantity:
                raise InsufficientStockError(f"Not enough stock for product {item.product_id}")

            product.stock_quantity -= item.quantity
            line_total = product.price * item.quantity
            total_amount += line_total
            order_items_data.append((product.id, item.quantity, product.price))

        new_order = order_repository.create_order(db, buyer_user_id, total_amount)

        for product_id, quantity, unit_price in order_items_data:
            order_repository.create_order_item(db, new_order.id, product_id, quantity, unit_price)

        db.commit()
        db.refresh(new_order)
        return new_order

    except Exception:
        db.rollback()
        raise

class OrderNotFoundError(Exception):
    pass


class OrderNotOwnedError(Exception):
    pass


class OrderNotCancellableError(Exception):
    pass


def cancel_order(db: Session, order_id: int, user_id: int):
    order = order_repository.get_order_by_id(db, order_id)
    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")
    if order.buyer_user_id != user_id:
        raise OrderNotOwnedError("This order does not belong to you")
    if order.status != "PENDING":
        raise OrderNotCancellableError(f"Order is '{order.status}', cannot be cancelled")

    try:
        items = order_repository.get_order_items(db, order_id)
        for item in items:
            order_repository.restore_product_stock(db, item.product_id, item.quantity)

        order_repository.update_order_status(db, order, "CANCELLED")

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise



def get_my_orders(db: Session, user_id: int):
    return order_repository.get_orders_by_user_id(db, user_id)


