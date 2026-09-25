from sqlalchemy.orm import Session
from app.repositories import product_repository


def get_all_active_products(db: Session):
    return product_repository.get_active_products(db)
