from sqlalchemy.orm import Session
from app.models.product import Product


def get_active_products(db: Session):
    return db.query(Product).filter(Product.is_active == True).all()

