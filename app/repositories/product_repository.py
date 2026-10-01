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

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product: Product, name: str | None, description: str | None,
                    price, stock_quantity: int | None):
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if stock_quantity is not None:
        product.stock_quantity = stock_quantity

    db.commit()
    db.refresh(product)
    return product




