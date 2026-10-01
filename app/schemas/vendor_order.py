from pydantic import BaseModel
from decimal import Decimal


class VendorOrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price_at_purchase: Decimal

    class Config:
        from_attributes = True

