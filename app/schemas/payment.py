from pydantic import BaseModel
from decimal import Decimal


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    status: str
    amount: Decimal

    class Config:
        from_attributes = True

