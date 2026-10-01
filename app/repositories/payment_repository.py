
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.payment import Payment
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


def get_successful_payment_by_order_id(db: Session, order_id: int):
    return db.query(Payment).filter(
        Payment.order_id == order_id, Payment.status == "SUCCESS"
    ).first()


def create_payment(db: Session, order_id: int, status: str, amount):
    new_payment = Payment(order_id=order_id, status=status, amount=amount)
    db.add(new_payment)
    db.flush()
    return new_payment

def get_payments_by_user_id(db: Session, user_id: int):
    return db.query(Payment).join(Order).filter(Order.buyer_user_id == user_id).all()
def get_payments_for_vendor(db: Session, vendor_profile_id: int):
    return (
        db.query(Payment)
        .join(Order, Payment.order_id == Order.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(Product.vendor_profile_id == vendor_profile_id)
        .distinct()
        .all()
    )



def count_payments_by_status_for_vendor(db: Session, vendor_profile_id: int, status: str):
    return (
        db.query(func.count(func.distinct(Payment.id)))
        .join(Order, Payment.order_id == Order.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(Product.vendor_profile_id == vendor_profile_id, Payment.status == status)
        .scalar()
    )


def get_total_revenue_for_vendor(db: Session, vendor_profile_id: int):
    total = (
        db.query(func.sum(Payment.amount))
        .join(Order, Payment.order_id == Order.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(Product.vendor_profile_id == vendor_profile_id, Payment.status == "SUCCESS")
        .scalar()
    )
    return total or 0



