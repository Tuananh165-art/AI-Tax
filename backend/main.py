from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from datetime import datetime
from typing import Optional

from db.database import get_db, init_db
from db.models import Invoice, Expense, InvoiceType
from db.user_model import User
from api.schemas import InvoiceResponse, ExpenseResponse, TaxCalculationRequest, TaxCalculationResponse
from services.ocr.ocr_service import OCRService
from services.expense.classifier import ExpenseClassifier
from services.tax_engine.tax_calculator import TaxEngine
from services.auth.auth_service import create_access_token, verify_token

# Chatbot import - optional, will be loaded on demand
try:
    from api.chatbot_schemas import ChatRequest, ChatResponse, TaxAdviceRequest, TaxAdviceResponse
    from services.chatbot.chatbot_service import TaxChatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False

app = FastAPI(title="AI Tax Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ocr_service = OCRService()
expense_classifier = ExpenseClassifier()
tax_engine = TaxEngine()
tax_chatbot = None

if CHATBOT_AVAILABLE:
    tax_chatbot = TaxChatbot()

@app.on_event("startup")
def startup_event():
    init_db()
    from db.database import engine
    User.metadata.create_all(bind=engine)
    if CHATBOT_AVAILABLE and tax_chatbot:
        tax_chatbot.setup_qa_chain()

@app.get("/")
def root():
    return {"message": "AI Tax Assistant API", "version": "1.0.0"}

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/api/auth/google")
async def google_auth(request: dict, db: Session = Depends(get_db)):
    import os
    from google.auth.transport.requests import Request
    from google.oauth2 import id_token
    
    token = request.get('token')
    if not token:
        raise HTTPException(status_code=400, detail="No token provided")
    
    try:
        # Get Google Client ID from environment
        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "442353970313-3ihpmj8i0pbe0jd02fpghbjhej9f1obo.apps.googleusercontent.com")
        
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(token, Request(), google_client_id)
        user_info = idinfo
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")
    
    user = db.query(User).filter(User.email == user_info['email']).first()
    
    if not user:
        user = User(
            email=user_info['email'],
            name=user_info.get('name', ''),
            picture=user_info.get('picture'),
            google_id=user_info.get('sub')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email, "name": user.name})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    }

@app.post("/api/invoices/upload", response_model=InvoiceResponse)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    invoice_data = ocr_service.parse_invoice(str(file_path))
    
    invoice = Invoice(
        invoice_type=InvoiceType.PURCHASE,
        invoice_number=invoice_data.get("invoice_number"),
        seller_name=invoice_data.get("seller_name"),
        date=datetime.strptime(invoice_data.get("date"), "%Y-%m-%d").date(),
        subtotal=invoice_data.get("subtotal", 0),
        vat=invoice_data.get("vat", 0),
        total=invoice_data.get("total", 0),
        items=invoice_data.get("items", []),
        image_path=str(file_path)
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return invoice

@app.get("/api/invoices", response_model=list[InvoiceResponse])
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()

@app.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.post("/api/expenses", response_model=ExpenseResponse)
def create_expense(description: str, amount: float, date: str, db: Session = Depends(get_db)):
    classification = expense_classifier.classify(description)
    
    expense = Expense(
        category=classification["category"],
        amount=amount,
        date=datetime.strptime(date, "%Y-%m-%d").date(),
        description=description,
        is_deductible=classification["is_deductible"]
    )
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense

@app.get("/api/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).all()

@app.post("/api/tax/calculate", response_model=TaxCalculationResponse)
def calculate_tax(request: TaxCalculationRequest):
    result = tax_engine.calculate_tax(
        revenue=request.revenue,
        expenses=request.expenses,
        business_type=request.business_type
    )
    return result

@app.get("/api/reports/summary")
def get_summary(db: Session = Depends(get_db)):
    total_revenue = db.query(Invoice).filter(Invoice.invoice_type == "sale").count()
    total_expenses = db.query(Expense).count()
    
    revenue_sum = sum([inv.total for inv in db.query(Invoice).filter(Invoice.invoice_type == "sale").all()])
    expense_sum = sum([exp.amount for exp in db.query(Expense).all()])
    
    return {
        "total_invoices": total_revenue,
        "total_expenses": total_expenses,
        "revenue": revenue_sum,
        "expenses": expense_sum,
        "profit": revenue_sum - expense_sum
    }

@app.post("/api/chatbot/ask", response_model=ChatResponse)
def ask_chatbot(request: ChatRequest):
    if not CHATBOT_AVAILABLE or not tax_chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not available. Install: pip install -r requirements-chatbot.txt")
    response = tax_chatbot.ask(request.question)
    return response

@app.post("/api/chatbot/advice", response_model=TaxAdviceResponse)
def get_tax_advice(request: TaxAdviceRequest):
    if not CHATBOT_AVAILABLE or not tax_chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not available. Install: pip install -r requirements-chatbot.txt")
    advice = tax_chatbot.get_tax_advice(
        revenue=request.revenue,
        expenses=request.expenses,
        business_type=request.business_type
    )
    return advice
