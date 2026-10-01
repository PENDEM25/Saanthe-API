from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem


def get_product_for_update(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).with_for_update().first()


def create_order(db: Session, buyer_user_id: int, total_amount):
    new_order = Order(buyer_user_id=buyer_user_id, total_amount=total_amount)
    db.add(new_order)
    db.flush()
    return new_order


def create_order_item(db: Session, order_id: int, product_id: int, quantity: int, unit_price):
    new_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        unit_price_at_purchase=unit_price,
    )
    db.add(new_item)



def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def update_order_status(db: Session, order: Order, new_status: str):
    order.status = new_status

def get_order_items(db: Session, order_id: int):
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()


def restore_product_stock(db: Session, product_id: int, quantity: int):
    product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
    product.stock_quantity += quantity

def get_orders_by_user_id(db: Session, user_id: int):
    return db.query(Order).filter(Order.buyer_user_id == user_id).all()



