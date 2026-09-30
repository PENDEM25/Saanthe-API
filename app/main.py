from fastapi import FastAPI
from app.models import user, vendor_profile, product, order, order_item, payment
from app.routers import products, auth, health, vendor

app = FastAPI(title="Saanthe API")

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(vendor.router)


