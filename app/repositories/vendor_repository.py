from sqlalchemy.orm import Session
from app.models.vendor_profile import VendorProfile


def get_vendor_profile_by_user_id(db: Session, user_id: int):
    return db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()


def create_vendor_profile(db: Session, user_id: int, business_name: str | None):
    new_profile = VendorProfile(user_id=user_id, business_name=business_name)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

