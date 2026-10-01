from sqlalchemy.orm import Session
from app.repositories import vendor_repository, order_repository, payment_repository


class VendorProfileRequiredError(Exception):
    pass


def get_vendor_dashboard(db: Session, user_id: int):
    vendor_profile = vendor_repository.get_vendor_profile_by_user_id(db, user_id)
    if not vendor_profile:
        raise VendorProfileRequiredError("You must have a vendor profile to view the dashboard")

    total_orders = order_repository.count_orders_for_vendor(db, vendor_profile.id)
    successful_payments = payment_repository.count_payments_by_status_for_vendor(
        db, vendor_profile.id, "SUCCESS"
    )
    failed_payments = payment_repository.count_payments_by_status_for_vendor(
        db, vendor_profile.id, "FAILED"
    )
    total_revenue = payment_repository.get_total_revenue_for_vendor(db, vendor_profile.id)

    return {
        "total_orders": total_orders,
        "successful_payments": successful_payments,
        "failed_payments": failed_payments,
        "total_revenue": total_revenue,
    }

