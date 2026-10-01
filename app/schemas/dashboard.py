from pydantic import BaseModel
from decimal import Decimal


class VendorDashboardResponse(BaseModel):
    total_orders: int
    successful_payments: int
    failed_payments: int
    total_revenue: Decimal

