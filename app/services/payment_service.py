import random
from sqlalchemy.orm import Session
from app.repositories import payment_repository, order_repository


class OrderNotFoundError(Exception):
    pass


class OrderNotOwnedError(Exception):
    pass


class OrderNotPayableError(Exception):
    pass


def process_payment(db: Session, order_id: int, user_id: int):
    order = order_repository.get_order_by_id(db, order_id)
    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")
    if order.buyer_user_id != user_id:
        raise OrderNotOwnedError("This order does not belong to you")

    existing_success = payment_repository.get_successful_payment_by_order_id(db, order_id)
    if existing_success:
        return existing_success

    if order.status != "PENDING":
        raise OrderNotPayableError(f"Order is '{order.status}', cannot be paid")

    try:
        payment_succeeds = random.choice([True, True, True, False])  # simulated 75% success rate

        if payment_succeeds:
            payment = payment_repository.create_payment(db, order_id, "SUCCESS", order.total_amount)
            order_repository.update_order_status(db, order, "PAID")
        else:
            payment = payment_repository.create_payment(db, order_id, "FAILED", order.total_amount)

        db.commit()
        db.refresh(payment)
        return payment

    except Exception:
        db.rollback()
        raise

