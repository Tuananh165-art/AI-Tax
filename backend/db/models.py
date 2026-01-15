from sqlalchemy import Column, Integer, String, Float, Date, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
import enum

Base = declarative_base()

class InvoiceType(enum.Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_type = Column(SQLEnum(InvoiceType), nullable=False)
    invoice_number = Column(String, nullable=True)
    seller_name = Column(String, nullable=True)
    buyer_name = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    subtotal = Column(Float, default=0)
    vat = Column(Float, default=0)
    total = Column(Float, nullable=False)
    payment_method = Column(String, nullable=True)
    items = Column(JSON, nullable=True)
    image_path = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, nullable=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    is_deductible = Column(Integer, default=1)
    user_id = Column(Integer, nullable=True)
