import pytest
from app.database.connection import SessionLocal
from app.models.user import User
from app.models.vendor_profile import VendorProfile
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment


@pytest.fixture(autouse=True)
def cleanup_test_users():
    yield
    db = SessionLocal()

    test_user_ids = [u.id for u in db.query(User).filter(User.email.like("%@test.com")).all()]

    if test_user_ids:
        vendor_profile_ids = [
            vp.id for vp in db.query(VendorProfile).filter(VendorProfile.user_id.in_(test_user_ids)).all()
        ]
        product_ids = [
            p.id for p in db.query(Product).filter(Product.vendor_profile_id.in_(vendor_profile_ids)).all()
        ] if vendor_profile_ids else []
        order_ids = [
            o.id for o in db.query(Order).filter(Order.buyer_user_id.in_(test_user_ids)).all()
        ]

        if order_ids:
            db.query(Payment).filter(Payment.order_id.in_(order_ids)).delete(synchronize_session=False)
            db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).delete(synchronize_session=False)
            db.query(Order).filter(Order.id.in_(order_ids)).delete(synchronize_session=False)

        if product_ids:
            db.query(Product).filter(Product.id.in_(product_ids)).delete(synchronize_session=False)

        if vendor_profile_ids:
            db.query(VendorProfile).filter(VendorProfile.id.in_(vendor_profile_ids)).delete(synchronize_session=False)

        db.query(User).filter(User.id.in_(test_user_ids)).delete(synchronize_session=False)

    db.commit()
    db.close()
