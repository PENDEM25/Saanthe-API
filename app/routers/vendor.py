from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import vendor_service, product_service
from app.schemas.vendor import VendorProfileRequest, VendorProfileResponse
from app.schemas.product import ProductCreateRequest, ProductResponse

router = APIRouter()


@router.post("/vendor/profile", response_model=VendorProfileResponse, status_code=201)
def create_vendor_profile(
    request: VendorProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_profile = vendor_service.create_vendor_profile(
            db, current_user.id, request.business_name
        )
        return new_profile
    except vendor_service.VendorProfileAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/vendor/products", response_model=ProductResponse, status_code=201)
def create_product(
    request: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_product = product_service.create_product(
            db, current_user.id, request.name, request.description,
            request.price, request.stock_quantity
        )
        return new_product
    except product_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))
