from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import order_service
from app.schemas.order import OrderCreateRequest, OrderResponse
from app.services import payment_service
from app.schemas.payment import PaymentResponse


router = APIRouter()


@router.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(
    request: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_order = order_service.create_order(db, current_user.id, request.items)
        return new_order
    except order_service.ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except order_service.InsufficientStockError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/orders/{order_id}/pay", response_model=PaymentResponse)
def pay_for_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        payment = payment_service.process_payment(db, order_id, current_user.id)
        return payment
    except payment_service.OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except payment_service.OrderNotOwnedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except payment_service.OrderNotPayableError as e:
        raise HTTPException(status_code=409, detail=str(e))



@router.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        order = order_service.cancel_order(db, order_id, current_user.id)
        return order
    except order_service.OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except order_service.OrderNotOwnedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except order_service.OrderNotCancellableError as e:
        raise HTTPException(status_code=409, detail=str(e))



