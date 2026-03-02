from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    available_stock = Column(Integer)
    unit_price = Column(Float)
    tax_percentage = Column(Float)


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    customer_email = Column(String, index=True)
    total_without_tax = Column(Float)
    total_tax = Column(Float)
    net_price = Column(Float)
    rounded_price = Column(Float)
    paid_amount = Column(Float)
    balance_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("PurchaseItem", back_populates="purchase")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))

    product_id = Column(String)
    product_name = Column(String)   

    quantity = Column(Integer)
    unit_price = Column(Float)
    tax_percentage = Column(Float)
    total_price = Column(Float)

    purchase = relationship("Purchase", back_populates="items")
