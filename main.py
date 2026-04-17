"""
County Pre-Foreclosure System - Main Application
FastAPI backend with SQLite database - Full Implementation
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum, Boolean, DECIMAL, Float, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration - Works with both SQLite (local) and PostgreSQL (production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pre_foreclosure.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread=False for FastAPI
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    # PostgreSQL (production on Render.com)
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI(title="County Pre-Foreclosure System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class County(Base):
    __tablename__ = "counties"

    id = Column(Integer, primary_key=True, index=True)
    county_name = Column(String(255), nullable=False, unique=True)
    state = Column(String(50), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    contact_person = Column(String(255))
    status = Column(String(20), default='active')
    notes = Column(Text)
    last_request_sent = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payment_info = relationship("PaymentInfo", back_populates="county", uselist=False)
    addresses = relationship("Address", back_populates="county")
    email_logs = relationship("EmailLog", back_populates="county")
    received_files = relationship("ReceivedFile", back_populates="county")


class PaymentInfo(Base):
    __tablename__ = "payment_info"

    id = Column(Integer, primary_key=True, index=True)
    county_id = Column(Integer, ForeignKey("counties.id", ondelete="CASCADE"), nullable=False)
    payment_instructions = Column(Text)
    amount = Column(Float)
    payment_method = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="payment_info")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(Text, nullable=False)
    county_id = Column(Integer, ForeignKey("counties.id", ondelete="CASCADE"), nullable=False)
    source_file = Column(String(255))
    source_type = Column(String(20), default='manual')
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="addresses")


class EmailLog(Base):
    __tablename__ = "email_log"

    id = Column(Integer, primary_key=True, index=True)
    county_id = Column(Integer, ForeignKey("counties.id", ondelete="SET NULL"))
    email_type = Column(String(20), nullable=False)
    recipient = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    status = Column(String(20), default='pending')
    error_message = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    county = relationship("County", back_populates="email_logs")


class ReceivedFile(Base):
    __tablename__ = "received_files"

    id = Column(Integer, primary_key=True, index=True)
    county_id = Column(Integer, ForeignKey("counties.id", ondelete="CASCADE"))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_path = Column(String(500))
    file_size_kb = Column(Integer)
    processing_status = Column(String(20), default='pending')
    addresses_extracted = Column(Integer, default=0)
    error_message = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    county = relationship("County", back_populates="received_files")


# Create tables
Base.metadata.create_all(bind=engine)

# ==================== PYDANTIC SCHEMAS ====================

# --- Payment Info Schemas ---
class PaymentInfoCreate(BaseModel):
    payment_instructions: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class PaymentInfoResponse(BaseModel):
    id: int
    county_id: int
    payment_instructions: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# --- Address Schemas ---
class AddressCreate(BaseModel):
    address: str
    source_file: Optional[str] = None
    source_type: str = "manual"


class AddressResponse(BaseModel):
    id: int
    address: str
    county_id: int
    source_file: Optional[str] = None
    source_type: str
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Email Log Schemas ---
class EmailLogCreate(BaseModel):
    county_id: int
    email_type: str
    recipient: str
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str = "pending"


class EmailLogResponse(BaseModel):
    id: int
    county_id: Optional[int] = None
    email_type: str
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    sent_at: datetime

    class Config:
        from_attributes = True


# --- Received File Schemas ---
class ReceivedFileCreate(BaseModel):
    county_id: Optional[int] = None
    filename: str
    file_type: str
    file_path: Optional[str] = None
    file_size_kb: Optional[int] = None


class ReceivedFileResponse(BaseModel):
    id: int
    county_id: Optional[int] = None
    filename: str
    file_type: str
    file_path: Optional[str] = None
    file_size_kb: Optional[int] = None
    processing_status: str
    addresses_extracted: int
    error_message: Optional[str] = None
    received_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- County Schemas ---
class CountyCreate(BaseModel):
    county_name: str
    state: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None


class CountyUpdate(BaseModel):
    county_name: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class CountyResponse(BaseModel):
    id: int
    county_name: str
    state: str
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    status: str
    notes: Optional[str] = None
    last_request_sent: Optional[datetime] = None
    next_scheduled_email: Optional[datetime] = None
    created_at: datetime
    payment_info: Optional[PaymentInfoResponse] = None
    email_count: int = 0
    address_count: int = 0
    file_count: int = 0

    class Config:
        from_attributes = True


# ==================== DEPENDENCY ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== HELPER FUNCTIONS ====================

def calculate_next_email_schedule():
    """Calculate next scheduled email (Monday & Thursday at 9 AM)"""
    now = datetime.now()
    current_day = now.weekday()

    if current_day < 0:
        days_until = 0 - current_day
    elif current_day < 3:
        days_until = 3 - current_day
    else:
        days_until = (7 - current_day) + 0

    next_schedule = now + timedelta(days=days_until)
    next_schedule = next_schedule.replace(hour=9, minute=0, second=0, microsecond=0)

    return next_schedule


def county_to_response(county: County, db: Session):
    """Convert County model to response schema"""
    payment = db.query(PaymentInfo).filter(PaymentInfo.county_id == county.id).first()
    email_count = db.query(EmailLog).filter(EmailLog.county_id == county.id).count()
    address_count = db.query(Address).filter(Address.county_id == county.id).count()
    file_count = db.query(ReceivedFile).filter(ReceivedFile.county_id == county.id).count()

    return CountyResponse(
        id=county.id,
        county_name=county.county_name,
        state=county.state,
        phone=county.phone,
        email=county.email,
        contact_person=county.contact_person,
        status=county.status,
        notes=county.notes,
        last_request_sent=county.last_request_sent,
        next_scheduled_email=calculate_next_email_schedule(),
        created_at=county.created_at,
        payment_info=payment,
        email_count=email_count,
        address_count=address_count,
        file_count=file_count
    )

# ==================== ROUTES ====================

# Mount static files for production build
STATIC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")


@app.get("/api")
def api_info():
    return {
        "message": "County Pre-Foreclosure System API",
        "version": "1.0.0",
        "status": "running",
        "tables": ["counties", "payment_info", "addresses", "email_log", "received_files"]
    }


# ==================== COUNTY ROUTES ====================

@app.post("/api/counties", response_model=CountyResponse)
def create_county(county: CountyCreate, db: Session = Depends(get_db)):
    """Create a new county"""
    existing = db.query(County).filter(County.county_name == county.county_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="County already exists")

    db_county = County(**county.model_dump())
    db.add(db_county)
    db.commit()
    db.refresh(db_county)

    return county_to_response(db_county, db)


@app.get("/api/counties", response_model=List[CountyResponse])
def list_counties(
    status: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of all counties with optional filters"""
    query = db.query(County)

    if status:
        query = query.filter(County.status == status)
    if state:
        query = query.filter(County.state == state)

    counties = query.order_by(County.county_name).all()
    return [county_to_response(c, db) for c in counties]


@app.get("/api/counties/{county_id}", response_model=CountyResponse)
def get_county(county_id: int, db: Session = Depends(get_db)):
    """Get a specific county by ID"""
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")
    return county_to_response(county, db)


@app.put("/api/counties/{county_id}", response_model=CountyResponse)
def update_county(
    county_id: int,
    county_update: CountyUpdate,
    db: Session = Depends(get_db)
):
    """Update a county"""
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    update_data = county_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(county, field, value)

    county.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(county)

    return county_to_response(county, db)


@app.delete("/api/counties/{county_id}")
def delete_county(county_id: int, db: Session = Depends(get_db)):
    """Delete a county and all related records"""
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    db.delete(county)
    db.commit()

    return {"message": f"County '{county.county_name}' deleted successfully"}


# ==================== PAYMENT INFO ROUTES ====================

@app.post("/api/counties/{county_id}/payment", response_model=PaymentInfoResponse)
def create_payment_info(
    county_id: int,
    payment: PaymentInfoCreate,
    db: Session = Depends(get_db)
):
    """Create or update payment info for a county"""
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    existing = db.query(PaymentInfo).filter(PaymentInfo.county_id == county_id).first()
    if existing:
        for field, value in payment.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    db_payment = PaymentInfo(**payment.model_dump(), county_id=county_id)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


@app.get("/api/counties/{county_id}/payment", response_model=PaymentInfoResponse)
def get_payment_info(county_id: int, db: Session = Depends(get_db)):
    """Get payment info for a county"""
    payment = db.query(PaymentInfo).filter(PaymentInfo.county_id == county_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment info not found")
    return payment


# ==================== ADDRESS ROUTES ====================

@app.post("/api/counties/{county_id}/addresses", response_model=AddressResponse)
def create_address(
    county_id: int,
    address: AddressCreate,
    db: Session = Depends(get_db)
):
    """Add an address for a county"""
    county = db.query(County).filter(County.id == county_id).first()
    if not county:
        raise HTTPException(status_code=404, detail="County not found")

    db_address = Address(**address.model_dump(), county_id=county_id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


@app.get("/api/counties/{county_id}/addresses", response_model=List[AddressResponse])
def list_addresses(county_id: int, db: Session = Depends(get_db)):
    """Get all addresses for a county"""
    addresses = db.query(Address).filter(Address.county_id == county_id).all()
    return addresses


@app.delete("/api/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    """Delete an address"""
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()

    return {"message": "Address deleted successfully"}


# ==================== EMAIL LOG ROUTES ====================

@app.post("/api/email-logs", response_model=EmailLogResponse)
def create_email_log(
    email_log: EmailLogCreate,
    db: Session = Depends(get_db)
):
    """Create an email log entry"""
    db_log = EmailLog(**email_log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Update county's last_request_sent if it's a request email
    if email_log.email_type == 'request' and email_log.status == 'sent' and email_log.county_id:
        county = db.query(County).filter(County.id == email_log.county_id).first()
        if county:
            county.last_request_sent = datetime.utcnow()
            db.commit()

    return db_log


@app.get("/api/email-logs", response_model=List[EmailLogResponse])
def list_email_logs(
    county_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get email logs with optional filters"""
    query = db.query(EmailLog)

    if county_id:
        query = query.filter(EmailLog.county_id == county_id)
    if status:
        query = query.filter(EmailLog.status == status)

    logs = query.order_by(EmailLog.sent_at.desc()).all()
    return logs


@app.get("/api/counties/{county_id}/email-logs", response_model=List[EmailLogResponse])
def list_county_email_logs(county_id: int, db: Session = Depends(get_db)):
    """Get all email logs for a specific county"""
    logs = db.query(EmailLog).filter(EmailLog.county_id == county_id).order_by(EmailLog.sent_at.desc()).all()
    return logs


# ==================== RECEIVED FILE ROUTES ====================

@app.post("/api/received-files", response_model=ReceivedFileResponse)
def create_received_file(
    file_data: ReceivedFileCreate,
    db: Session = Depends(get_db)
):
    """Create a received file record"""
    db_file = ReceivedFile(**file_data.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return db_file


@app.get("/api/received-files", response_model=List[ReceivedFileResponse])
def list_received_files(
    county_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get received files with optional filters"""
    query = db.query(ReceivedFile)

    if county_id:
        query = query.filter(ReceivedFile.county_id == county_id)
    if status:
        query = query.filter(ReceivedFile.processing_status == status)

    files = query.order_by(ReceivedFile.received_at.desc()).all()
    return files


@app.put("/api/received-files/{file_id}", response_model=ReceivedFileResponse)
def update_received_file(
    file_id: int,
    processing_status: str,
    addresses_extracted: Optional[int] = None,
    error_message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update a received file's processing status"""
    file = db.query(ReceivedFile).filter(ReceivedFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file.processing_status = processing_status
    if addresses_extracted is not None:
        file.addresses_extracted = addresses_extracted
    if error_message:
        file.error_message = error_message
    if processing_status == 'completed':
        file.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(file)

    return file


# ==================== STATS ROUTE ====================

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_counties = db.query(County).count()
    active_counties = db.query(County).filter(County.status == 'active').count()
    inactive_counties = db.query(County).filter(County.status == 'inactive').count()

    total_addresses = db.query(Address).count()
    unsent_addresses = db.query(Address).filter(Address.is_sent == False).count()

    emails_sent = db.query(EmailLog).filter(EmailLog.status == 'sent').count()
    emails_failed = db.query(EmailLog).filter(EmailLog.status == 'failed').count()

    pending_files = db.query(ReceivedFile).filter(ReceivedFile.processing_status == 'pending').count()

    return {
        "total_counties": total_counties,
        "active_counties": active_counties,
        "inactive_counties": inactive_counties,
        "total_addresses": total_addresses,
        "unsent_addresses": unsent_addresses,
        "emails_sent": emails_sent,
        "emails_failed": emails_failed,
        "pending_files": pending_files,
        "next_email_schedule": calculate_next_email_schedule()
    }


# ==================== SCHEMA ENDPOINT ====================

@app.get("/api/schema")
def get_database_schema(db: Session = Depends(get_db)):
    """Get complete database schema information"""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    schema_info = {
        "tables": [],
        "relationships": []
    }

    tables = ["counties", "payment_info", "addresses", "email_log", "received_files"]

    for table_name in tables:
        try:
            # Get columns using SQLAlchemy inspector (works for all databases)
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_columns = pk_constraint.get('constrained_columns', [])

            columns_info = []
            for col in columns:
                columns_info.append({
                    "name": col['name'],
                    "type": str(col['type']),
                    "primary_key": col['name'] in pk_columns,
                    "nullable": col['nullable'],
                    "foreign_key": "county_id" in col['name'] and table_name != "counties"
                })

            # Get row count
            count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count_result.scalar()

            schema_info["tables"].append({
                "name": table_name,
                "columns": columns_info,
                "row_count": row_count
            })
        except Exception as e:
            # Table might not exist yet
            schema_info["tables"].append({
                "name": table_name,
                "columns": [],
                "row_count": 0,
                "error": str(e)
            })

    # Define relationships
    schema_info["relationships"] = [
        {"from": "payment_info", "to": "counties", "via": "county_id", "type": "1:1"},
        {"from": "addresses", "to": "counties", "via": "county_id", "type": "1:N"},
        {"from": "email_log", "to": "counties", "via": "county_id", "type": "1:N"},
        {"from": "received_files", "to": "counties", "via": "county_id", "type": "1:N"}
    ]

    return schema_info


# ==================== SERVE REACT APP ====================

@app.get("/")
def serve_app():
    """Serve the React app"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not built. Run: cd frontend && yarn build"}


# Catch-all route for React SPA (must be last)
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    """Serve React app for all non-API routes"""
    # Don't catch API routes
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # Serve index.html for React Router
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Page not found")


# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)