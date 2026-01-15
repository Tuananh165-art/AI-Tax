from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    disclaimer: str

class TaxAdviceRequest(BaseModel):
    revenue: float
    expenses: float
    business_type: str = "food_service"

class TaxAdviceResponse(BaseModel):
    advice: List[str]
    recommendation: str
