import random
from sqlalchemy.orm import Session
from app.repositories import payment_repository, order_repository
from app.repositories import vendor_repository



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

def get_my_payments(db: Session, user_id: int):
    return payment_repository.get_payments_by_user_id(db, user_id)

class VendorProfileRequiredError(Exception):
    pass


def get_vendor_payments(db: Session, user_id: int):
    vendor_profile = vendor_repository.get_vendor_profile_by_user_id(db, user_id)
    if not vendor_profile:
        raise VendorProfileRequiredError("You must have a vendor profile to view vendor payments")

    return payment_repository.get_payments_for_vendor(db, vendor_profile.id)



