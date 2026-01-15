from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class InvoiceItem(BaseModel):
    name: str
    quantity: float
    unit_price: float
    amount: float

class InvoiceCreate(BaseModel):
    invoice_type: str
    invoice_number: Optional[str] = None
    seller_name: Optional[str] = None
    buyer_name: Optional[str] = None
    date: date
    subtotal: float = 0
    vat: float = 0
    total: float
    payment_method: Optional[str] = None
    items: Optional[List[InvoiceItem]] = None

class InvoiceResponse(InvoiceCreate):
    id: int
    
    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    invoice_id: Optional[int] = None
    category: str
    amount: float
    date: date
    description: Optional[str] = None
    is_deductible: bool = True

class ExpenseResponse(ExpenseCreate):
    id: int
    
    class Config:
        from_attributes = True

class TaxCalculationRequest(BaseModel):
    revenue: float
    expenses: float
    business_type: str = "food_service"

class TaxCalculationResponse(BaseModel):
    estimated_revenue: float
    estimated_expenses: float
    estimated_tax: dict
    notes: List[str]
    disclaimer: str
