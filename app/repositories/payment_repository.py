from sqlalchemy.orm import Session
from app.models.payment import Payment


def get_successful_payment_by_order_id(db: Session, order_id: int):
    return db.query(Payment).filter(
        Payment.order_id == order_id, Payment.status == "SUCCESS"
    ).first()


def create_payment(db: Session, order_id: int, status: str, amount):
    new_payment = Payment(order_id=order_id, status=status, amount=amount)
    db.add(new_payment)
    db.flush()
    return new_payment

