from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    business_name = Column(String(100))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    owner = relationship("User", backref="vendor_profile")
    products = relationship("Product", back_populates="vendor_profile")



