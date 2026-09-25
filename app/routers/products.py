from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import product_service
from app.schemas.product import ProductResponse

router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return product_service.get_all_active_products(db)

