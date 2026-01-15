#!/usr/bin/env python
"""
Migration script to update old lowercase enum values to uppercase
"""
from db.database import SessionLocal, engine
from db.models import Invoice
from sqlalchemy import text

def migrate():
    """Update existing invoices with old lowercase enum values to uppercase"""
    db = SessionLocal()
    
    try:
        # Update invoices with lowercase 'purchase' to uppercase 'PURCHASE'
        db.execute(
            text("UPDATE invoices SET invoice_type = :new_val WHERE LOWER(invoice_type) = 'purchase'"),
            {"new_val": "PURCHASE"}
        )
        
        # Update invoices with lowercase 'sale' to uppercase 'SALE'
        db.execute(
            text("UPDATE invoices SET invoice_type = :new_val WHERE LOWER(invoice_type) = 'sale'"),
            {"new_val": "SALE"}
        )
        
        db.commit()
        print("✅ Migration successful! Updated all enum values to uppercase.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
