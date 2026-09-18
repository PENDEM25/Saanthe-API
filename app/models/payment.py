from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status = Column(String(20), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    order = relationship("Order", back_populates="payments")
