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


class ProductNotFoundError(Exception):
    pass


class ProductNotOwnedError(Exception):
    pass


def update_product(db: Session, user_id: int, product_id: int, name, description, price, stock_quantity):
    vendor_profile = vendor_repository.get_vendor_profile_by_user_id(db, user_id)
    if not vendor_profile:
        raise VendorProfileRequiredError("You must have a vendor profile to update products")

    product = product_repository.get_product_by_id(db, product_id)
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    if product.vendor_profile_id != vendor_profile.id:
        raise ProductNotOwnedError("This product does not belong to you")

    return product_repository.update_product(db, product, name, description, price, stock_quantity)



def deactivate_product(db: Session, user_id: int, product_id: int):
    vendor_profile = vendor_repository.get_vendor_profile_by_user_id(db, user_id)
    if not vendor_profile:
        raise VendorProfileRequiredError("You must have a vendor profile to delete products")

    product = product_repository.get_product_by_id(db, product_id)
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    if product.vendor_profile_id != vendor_profile.id:
        raise ProductNotOwnedError("This product does not belong to you")

    return product_repository.deactivate_product(db, product)


