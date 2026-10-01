from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.order import Order



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
