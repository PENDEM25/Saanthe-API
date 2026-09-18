from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    vendor_profile_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    vendor_profile = relationship("VendorProfile", back_populates="products")

