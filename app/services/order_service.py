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

