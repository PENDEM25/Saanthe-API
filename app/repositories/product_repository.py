from sqlalchemy.orm import Session
from app.models.product import Product


def get_active_products(db: Session):
    return db.query(Product).filter(Product.is_active == True).all()

def create_product(db: Session, vendor_profile_id: int, name: str, description: str | None,
                    price, stock_quantity: int):
    new_product = Product(
        vendor_profile_id=vendor_profile_id,
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


