from sqlalchemy.orm import Session
from app.repositories import vendor_repository


class VendorProfileAlreadyExistsError(Exception):
    pass


def create_vendor_profile(db: Session, user_id: int, business_name: str | None):
    existing_profile = vendor_repository.get_vendor_profile_by_user_id(db, user_id)
    if existing_profile:
        raise VendorProfileAlreadyExistsError("You already have a vendor profile")

    new_profile = vendor_repository.create_vendor_profile(db, user_id, business_name)
    return new_profile

