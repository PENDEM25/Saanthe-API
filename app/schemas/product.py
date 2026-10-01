from pydantic import BaseModel
from decimal import Decimal


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    is_active: bool

    class Config:
        from_attributes = True


class ProductCreateRequest(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock_quantity: int = 0
