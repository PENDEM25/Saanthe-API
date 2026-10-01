from pydantic import BaseModel, Field
from decimal import Decimal


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1)


class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: Decimal

    class Config:
        from_attributes = True


class OrderStatusUpdateRequest(BaseModel):
    status: str
