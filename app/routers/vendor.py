from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import vendor_service, product_service
from app.schemas.vendor import VendorProfileRequest, VendorProfileResponse
from app.schemas.product import ProductCreateRequest, ProductResponse
from app.services import order_service, payment_service
from app.schemas.vendor_order import VendorOrderItemResponse
from app.schemas.payment import PaymentResponse
from app.schemas.product import ProductUpdateRequest
from app.schemas.order import OrderStatusUpdateRequest, OrderResponse
from app.services import dashboard_service
from app.schemas.dashboard import VendorDashboardResponse




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


@router.get("/vendor/orders", response_model=list[VendorOrderItemResponse])
def get_vendor_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return order_service.get_vendor_order_items(db, current_user.id)
    except order_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/vendor/payments", response_model=list[PaymentResponse])
def get_vendor_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return payment_service.get_vendor_payments(db, current_user.id)
    except payment_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))



@router.put("/vendor/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        updated_product = product_service.update_product(
            db, current_user.id, product_id,
            request.name, request.description, request.price, request.stock_quantity
        )
        return updated_product
    except product_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except product_service.ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except product_service.ProductNotOwnedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/vendor/products/{product_id}", response_model=ProductResponse)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        deactivated_product = product_service.deactivate_product(db, current_user.id, product_id)
        return deactivated_product
    except product_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except product_service.ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except product_service.ProductNotOwnedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/vendor/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        updated_order = order_service.update_order_status_for_vendor(
            db, current_user.id, order_id, request.status
        )
        return updated_order
    except order_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except order_service.OrderItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except order_service.InvalidStatusTransitionError as e:
        raise HTTPException(status_code=409, detail=str(e))



@router.get("/vendor/dashboard", response_model=VendorDashboardResponse)
def get_vendor_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return dashboard_service.get_vendor_dashboard(db, current_user.id)
    except dashboard_service.VendorProfileRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))



