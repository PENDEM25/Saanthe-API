from sqlalchemy.orm import Session
from app.repositories import product_repository
from app.repositories import vendor_repository


def get_all_active_products(db: Session):
    return product_repository.get_active_products(db)


class VendorProfileRequiredError(Exception):
    pass


def create_product(db: Session, user_id: int, name: str, description: str | None,
                    price, stock_quantity: int):
    vendor_profile = vendor_repository.get_vendor_profile_by_user_id(db, user_id)
    if not vendor_profile:
        raise VendorProfileRequiredError("You must create a vendor profile before listing products")

    new_product = product_repository.create_product(
        db, vendor_profile.id, name, description, price, stock_quantity
    )
    return new_product


