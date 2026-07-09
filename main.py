"""
County Pre-Foreclosure System - Main Application
FastAPI backend with SQLite database - Full Implementation
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
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
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import json
import imaplib
import email as email_lib
import io
import re
import pandas as pd
import pdfplumber

# Load environment variables
load_dotenv()

# Email Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)

# Database configuration - Works with both SQLite (local) and PostgreSQL (production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pre_foreclosure.db")

# Debug: Print which database is being used
print("=" * 60)
print(f"DATABASE_URL: {DATABASE_URL[:30]}..." if len(DATABASE_URL) > 30 else f"DATABASE_URL: {DATABASE_URL}")
print("=" * 60)

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    print("WARNING: Using SQLite (development mode)")
    # SQLite requires check_same_thread=False for FastAPI
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    print("OK: Using PostgreSQL (production mode)")
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
    outreach_status = Column(String(30), default='no_reply')
    status_notes = Column(Text)
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
    is_sent = Column(Boolean, default=False)
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
print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("OK: Tables created successfully!")

    # Test database connection
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

    # Lightweight migration: add columns that create_all() won't add to existing tables
    existing_county_columns = {c['name'] for c in inspector.get_columns('counties')} if 'counties' in tables else set()
    with engine.begin() as conn:
        if 'outreach_status' not in existing_county_columns:
            conn.execute(text("ALTER TABLE counties ADD COLUMN outreach_status VARCHAR(30) DEFAULT 'no_reply'"))
            print("OK: Added outreach_status column to counties")
        if 'status_notes' not in existing_county_columns:
            conn.execute(text("ALTER TABLE counties ADD COLUMN status_notes TEXT"))
            print("OK: Added status_notes column to counties")
except Exception as e:
    print(f"ERROR creating tables: {e}")

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


class AddressResponse(BaseModel):
    id: int
    address: str
    county_id: int
    is_sent: bool
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
    outreach_status: Optional[str] = None
    status_notes: Optional[str] = None
    notes: Optional[str] = None


class CountyResponse(BaseModel):
    id: int
    county_name: str
    state: str
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    status: str
    outreach_status: str = 'no_reply'
    status_notes: Optional[str] = None
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
        outreach_status=county.outreach_status or 'no_reply',
        status_notes=county.status_notes,
        notes=county.notes,
        last_request_sent=county.last_request_sent,
        next_scheduled_email=calculate_next_email_schedule(),
        created_at=county.created_at,
        payment_info=payment,
        email_count=email_count,
        address_count=address_count,
        file_count=file_count
    )


# ==================== EMAIL FUNCTIONS ====================

STATE_FOIA_LAWS = {
    "FL": "Florida Public Records Law (Chapter 119, Florida Statutes)",
    "NJ": "New Jersey Open Public Records Act (N.J.S.A. 47:1A-1)",
    "NY": "New York Freedom of Information Law (Public Officers Law § 84-90)",
    "OH": "Ohio Public Records Act (Ohio Revised Code Section 149.43)",
    "IN": "Indiana Access to Public Records Act (IC 5-14-3)",
    "IL": "Illinois Freedom of Information Act (5 ILCS 140)",
    "TX": "Texas Public Information Act (Chapter 552, Texas Government Code)",
    "GA": "Georgia Open Records Act (O.C.G.A. § 50-18-70)",
    "PA": "Pennsylvania Right-to-Know Law (65 P.S. § 67.101)",
    "NC": "North Carolina Public Records Law (G.S. Chapter 132)",
    "MI": "Michigan Freedom of Information Act (MCL 15.231)",
}


def get_email_template(county_name: str, state: str, contact_person: Optional[str] = None) -> tuple[str, str]:
    """
    Generate public records request email for active Lis Pendens filings.
    Returns: (subject, html_body)
    """
    greeting = f"Dear {contact_person}," if contact_person else "Dear County Clerk,"
    foia_law = STATE_FOIA_LAWS.get(state, "applicable state public records law")
    cutoff_date = (datetime.utcnow() - timedelta(days=60)).strftime("%B %d, %Y")

    subject = f"Public Records Request – Active Lis Pendens Filings – {county_name} County, {state}"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <p>{greeting}</p>

            <p>I am submitting this request pursuant to the <strong>{foia_law}</strong> for access to
            public records maintained by {county_name} County.</p>

            <p><strong>Records Requested:</strong></p>
            <p>All active <strong>Lis Pendens</strong> filings recorded within the past 60 days
            (from <strong>{cutoff_date}</strong> to present), including:</p>
            <ul>
                <li>Property address(es) associated with each filing</li>
                <li>Filing/recording date</li>
            </ul>

            <p><strong>Preferred Format:</strong> Please provide the data as an
            <strong>Excel (.xlsx)</strong> or <strong>CSV</strong> file sent directly
            to this email address.</p>

            <p>If there are any fees associated with fulfilling this request, please notify me
            in advance. I am happy to provide any additional information needed to process
            this request.</p>

            <p>Thank you for your time and assistance.</p>

            <p style="margin-top: 30px;">Sincerely,<br>
            <strong>Travis Morrison</strong><br>
            readysetgrowautomations@gmail.com</p>

            <hr style="margin-top: 40px; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #777;">
                This is a public records request. Please reply to this email with the
                requested data or any questions.
            </p>
        </div>
    </body>
    </html>
    """

    return subject, html_body


async def send_email_async(
    recipient: str,
    subject: str,
    html_body: str,
    county_id: Optional[int] = None,
    db: Optional[Session] = None
) -> tuple[bool, Optional[str]]:
    """
    Send email using SMTP and log to database
    Returns: (success: bool, error_message: Optional[str])
    """
    log_id = None

    try:
        # Validate SMTP configuration
        if not SMTP_USER or not SMTP_PASSWORD:
            error_msg = "SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD in .env file"
            print(f"ERROR: {error_msg}")

            # Log failed attempt to database
            if db and county_id:
                email_log = EmailLog(
                    county_id=county_id,
                    email_type='request',
                    recipient=recipient,
                    subject=subject,
                    body=html_body[:5000],  # Truncate body for storage
                    status='failed',
                    error_message=error_msg
                )
                db.add(email_log)
                db.commit()

            return False, error_msg

        # Create email message
        message = MIMEMultipart('alternative')
        message['From'] = SENDER_EMAIL
        message['To'] = recipient
        message['Subject'] = subject

        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)

        print(f"Sending email to {recipient}...")
        print(f"   Subject: {subject}")

        # Send email via SMTP
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True
        )

        print(f"OK: Email sent successfully to {recipient}")

        # Log successful email to database
        if db and county_id:
            email_log = EmailLog(
                county_id=county_id,
                email_type='request',
                recipient=recipient,
                subject=subject,
                body=html_body[:5000],
                status='sent',
                sent_at=datetime.utcnow()
            )
            db.add(email_log)

            # Update county's last_request_sent
            county = db.query(County).filter(County.id == county_id).first()
            if county:
                county.last_request_sent = datetime.utcnow()

            db.commit()
            db.refresh(email_log)
            log_id = email_log.id

        return True, None

    except aiosmtplib.SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        print(f"ERROR: Failed to send email to {recipient}: {error_msg}")

        # Log failed email to database
        if db and county_id:
            email_log = EmailLog(
                county_id=county_id,
                email_type='request',
                recipient=recipient,
                subject=subject,
                body=html_body[:5000],
                status='failed',
                error_message=error_msg
            )
            db.add(email_log)
            db.commit()

        return False, error_msg

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"ERROR: Failed to send email to {recipient}: {error_msg}")

        # Log failed email to database
        if db and county_id:
            email_log = EmailLog(
                county_id=county_id,
                email_type='request',
                recipient=recipient,
                subject=subject,
                body=html_body[:5000],
                status='failed',
                error_message=error_msg
            )
            db.add(email_log)
            db.commit()

        return False, error_msg


async def send_to_all_active_counties_async(db: Session) -> dict:
    """
    Send pre-foreclosure request emails to all active counties
    Returns summary of results
    """
    print("\n" + "=" * 60)
    print("SENDING EMAILS TO ALL ACTIVE COUNTIES")
    print("=" * 60)

    # Get all active counties with email addresses
    counties = db.query(County).filter(
        County.status == 'active',
        County.email.isnot(None),
        County.email != ''
    ).all()

    print(f"Found {len(counties)} active counties with email addresses")

    results = {
        'total': len(counties),
        'sent': 0,
        'failed': 0,
        'details': []
    }

    for county in counties:
        print(f"\nProcessing: {county.county_name}, {county.state}")

        # Generate email template
        subject, html_body = get_email_template(
            county.county_name,
            county.state,
            county.contact_person
        )

        # Send email
        success, error_msg = await send_email_async(
            recipient=county.email,
            subject=subject,
            html_body=html_body,
            county_id=county.id,
            db=db
        )

        if success:
            results['sent'] += 1
            results['details'].append({
                'county': county.county_name,
                'email': county.email,
                'status': 'sent'
            })
        else:
            results['failed'] += 1
            results['details'].append({
                'county': county.county_name,
                'email': county.email,
                'status': 'failed',
                'error': error_msg
            })

    print("\n" + "=" * 60)
    print(f"OK: Email batch complete: {results['sent']} sent, {results['failed']} failed")
    print("=" * 60 + "\n")

    return results


def send_to_all_active_counties(db: Session) -> dict:
    """
    Synchronous wrapper for async email sending function
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(send_to_all_active_counties_async(db))
    finally:
        loop.close()


def scheduled_email_job():
    """
    Job function for APScheduler to send emails on schedule
    """
    print(f"\nScheduled email job triggered at {datetime.now()}")
    db = SessionLocal()
    try:
        send_to_all_active_counties(db)
    except Exception as e:
        print(f"ERROR in scheduled email job: {e}")
    finally:
        db.close()


# ==================== INBOX POLLER ====================

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

# Common column names counties might use for addresses
ADDRESS_COLUMN_HINTS = [
    "address", "property address", "prop address", "street", "location",
    "situs", "parcel address", "property", "site address"
]


def find_address_column(df: pd.DataFrame) -> str | None:
    """Find the address column in a dataframe using common name hints."""
    for col in df.columns:
        if any(hint in col.lower() for hint in ADDRESS_COLUMN_HINTS):
            return col
    return None


def parse_pdf_for_addresses(data: bytes, filename: str) -> list[str]:
    """Extract property addresses from a PDF using pdfplumber."""
    addresses = []
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                # Try structured table extraction first
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    # Detect header row to find address column index
                    header = [str(c).lower().strip() if c else "" for c in table[0]]
                    addr_idx = None
                    for i, h in enumerate(header):
                        if any(hint in h for hint in ADDRESS_COLUMN_HINTS):
                            addr_idx = i
                            break
                    if addr_idx is not None:
                        for row in table[1:]:
                            if row and addr_idx < len(row) and row[addr_idx]:
                                val = str(row[addr_idx]).strip()
                                if len(val) > 5:
                                    addresses.append(val)
                    else:
                        # No address column header — scan all cells for address-like values
                        for row in table:
                            if not row:
                                continue
                            for cell in row:
                                if not cell:
                                    continue
                                val = str(cell).strip()
                                # Heuristic: starts with a number, has a street word, reasonable length
                                if re.match(r'^\d+\s+\w', val) and 8 < len(val) < 200:
                                    addresses.append(val)

                # Fallback: plain text extraction if no table addresses found
                if not addresses:
                    text = page.extract_text() or ""
                    for line in text.splitlines():
                        line = line.strip()
                        if re.match(r'^\d+\s+\w', line) and 8 < len(line) < 200:
                            addresses.append(line)

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for a in addresses:
            if a not in seen:
                seen.add(a)
                unique.append(a)
        addresses = unique
        print(f"  Parsed {len(addresses)} addresses from PDF: {filename}")
    except Exception as e:
        print(f"  ERROR parsing PDF {filename}: {e}")
    return addresses


def parse_attachment_for_addresses(data: bytes, filename: str) -> list[str]:
    """Parse CSV, Excel, or PDF attachment and extract property addresses."""
    addresses = []
    try:
        ext = filename.lower().rsplit(".", 1)[-1]
        if ext == "pdf":
            return parse_pdf_for_addresses(data, filename)
        elif ext == "csv":
            df = pd.read_csv(io.BytesIO(data), dtype=str, on_bad_lines="skip")
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(data), dtype=str)
        else:
            return []

        df.columns = [str(c).strip() for c in df.columns]
        addr_col = find_address_column(df)

        if addr_col:
            addresses = df[addr_col].dropna().astype(str).str.strip().tolist()
            addresses = [a for a in addresses if len(a) > 5]
        else:
            # Fallback: grab all non-empty text from every column and filter address-like rows
            for col in df.columns:
                vals = df[col].dropna().astype(str).str.strip().tolist()
                for v in vals:
                    if any(ch.isdigit() for ch in v) and 8 < len(v) < 200:
                        addresses.append(v)

        print(f"  Parsed {len(addresses)} addresses from {filename}")
    except Exception as e:
        print(f"  ERROR parsing {filename}: {e}")
    return addresses


def match_county_by_sender(sender: str, db: Session) -> County | None:
    """Try to match an email sender to a county in the database."""
    sender_lower = sender.lower()
    counties = db.query(County).filter(County.email.isnot(None)).all()
    for county in counties:
        if county.email and county.email.lower() in sender_lower:
            return county
    return None


def poll_inbox_for_replies():
    """
    Connect to Gmail via IMAP, find unread replies from county clerks,
    parse any CSV/Excel attachments, and save addresses to the database.
    Runs every 15 minutes via APScheduler.
    """
    print(f"\n[INBOX POLL] Checking Gmail at {datetime.now().strftime('%H:%M:%S')}")

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[INBOX POLL] SMTP credentials not configured, skipping.")
        return

    db = SessionLocal()
    new_addresses_total = 0

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASSWORD)
        mail.select("INBOX")

        # Search for emails with our subject keyword received in the last 24 hours
        since_date = (datetime.utcnow() - timedelta(days=1)).strftime("%d-%b-%Y")
        _, msg_ids = mail.search(None, f'SUBJECT "Lis Pendens" SINCE "{since_date}"')
        ids = msg_ids[0].split()

        # Filter out already-processed message IDs stored in DB
        processed_subjects = set(
            r[0] for r in db.execute(
                text("SELECT subject FROM email_log WHERE email_type='received'")
            ).fetchall()
        )
        print(f"[INBOX POLL] Found {len(ids)} Lis Pendens emails in last 24h")

        for mid in ids:
            _, msg_data = mail.fetch(mid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email_lib.message_from_bytes(raw)

            sender = msg.get("From", "")
            subject = msg.get("Subject", "")
            print(f"  From: {sender} | Subject: {subject[:60]}")

            # Skip already processed emails
            if subject[:500] in processed_subjects:
                print(f"  Skipping (already processed)")
                continue

            # Match sender to a county
            county = match_county_by_sender(sender, db)
            county_id = county.id if county else None
            county_name = county.county_name if county else "Unknown"

            # Look for CSV/Excel attachments
            attachments_found = 0
            for part in msg.walk():
                content_disp = part.get("Content-Disposition", "")
                filename = part.get_filename()
                if not filename:
                    continue

                ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
                if ext not in ("csv", "xlsx", "xls", "pdf"):
                    continue

                print(f"  Attachment: {filename} (county: {county_name})")
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                addresses = parse_attachment_for_addresses(payload, filename)

                # Save file record
                file_record = ReceivedFile(
                    county_id=county_id,
                    filename=filename,
                    file_type=ext,
                    file_size_kb=len(payload) // 1024,
                    processing_status="processed" if addresses else "empty",
                    addresses_extracted=len(addresses),
                    received_at=datetime.utcnow(),
                    processed_at=datetime.utcnow()
                )
                db.add(file_record)
                db.flush()

                # Save addresses
                for addr in addresses:
                    db.add(Address(address=addr, county_id=county_id or 0))

                new_addresses_total += len(addresses)
                attachments_found += 1

            # Log the received email regardless of attachments
            db.add(EmailLog(
                county_id=county_id,
                email_type="received",
                recipient=SMTP_USER,
                subject=subject[:500],
                body=f"From: {sender}\nAttachments: {attachments_found}",
                status="received",
                sent_at=datetime.utcnow()
            ))

            # Mark as read
            mail.store(mid, "+FLAGS", "\\Seen")

        db.commit()
        mail.logout()
        print(f"[INBOX POLL] Done. {new_addresses_total} new addresses saved.")

    except imaplib.IMAP4.error as e:
        print(f"[INBOX POLL] IMAP error: {e}")
    except Exception as e:
        print(f"[INBOX POLL] Unexpected error: {e}")
    finally:
        db.close()


# ==================== EMAIL SCHEDULER ====================

# Initialize APScheduler
scheduler = BackgroundScheduler()

# Schedule emails for Monday and Thursday at 9 AM
scheduler.add_job(
    scheduled_email_job,
    trigger=CronTrigger(day_of_week='mon,thu', hour=9, minute=0),
    id='email_scheduler',
    name='Send emails to active counties (Monday & Thursday at 9 AM)',
    replace_existing=True
)

# Poll inbox for replies every 15 minutes
scheduler.add_job(
    poll_inbox_for_replies,
    trigger=CronTrigger(minute='*/15'),
    id='inbox_poller',
    name='Check Gmail inbox for county replies every 15 minutes',
    replace_existing=True
)

print("Email scheduler configured: Monday & Thursday at 9:00 AM")
print("Inbox poller configured: every 15 minutes")

# Start scheduler
@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the app starts"""
    if not scheduler.running:
        scheduler.start()
        print("OK: Email scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the scheduler when the app stops"""
    if scheduler.running:
        scheduler.shutdown()
        print("STOP: Email scheduler stopped")

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
    print(f"\nCreating county: {county.county_name}, {county.state}")

    existing = db.query(County).filter(County.county_name == county.county_name).first()
    if existing:
        print(f"WARNING: County '{county.county_name}' already exists!")  
        raise HTTPException(status_code=400, detail="County already exists")

    try:
        db_county = County(**county.model_dump())
        db.add(db_county)
        print(f"Committing to database...")
        db.commit()
        db.refresh(db_county)
        print(f"OK: County created successfully! ID: {db_county.id}")

        # Verify it was saved
        verify = db.query(County).filter(County.id == db_county.id).first()
        if verify:
            print(f"Verified: County {verify.id} exists in database")
        else:
            print(f"ERROR: County not found after commit!")

        return county_to_response(db_county, db)
    except Exception as e:
        print(f"ERROR creating county: {e}")
        raise


@app.get("/api/counties", response_model=List[CountyResponse])
def list_counties(
    status: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of all counties with optional filters"""
    print(f"\nListing counties (status={status}, state={state})")
    query = db.query(County)

    if status:
        query = query.filter(County.status == status)
    if state:
        query = query.filter(County.state == state)

    counties = query.order_by(County.county_name).all()
    print(f"Found {len(counties)} counties")
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


# ==================== INBOX POLL ROUTES ====================

@app.post("/api/poll-inbox")
def manual_poll_inbox(background_tasks: BackgroundTasks):
    """Manually trigger inbox poll — checks Gmail right now for county replies."""
    background_tasks.add_task(poll_inbox_for_replies)
    return {"message": "Inbox poll started", "status": "processing"}


@app.get("/api/received-files")
def list_received_files(db: Session = Depends(get_db)):
    """Get all received files with county info."""
    files = db.query(ReceivedFile).order_by(ReceivedFile.received_at.desc()).all()
    result = []
    for f in files:
        county = db.query(County).filter(County.id == f.county_id).first() if f.county_id else None
        result.append({
            "id": f.id,
            "county_name": county.county_name if county else "Unknown",
            "state": county.state if county else "-",
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size_kb": f.file_size_kb,
            "processing_status": f.processing_status,
            "addresses_extracted": f.addresses_extracted,
            "received_at": f.received_at,
            "processed_at": f.processed_at,
            "error_message": f.error_message,
        })
    return result


@app.get("/api/received-emails")
def list_received_emails(db: Session = Depends(get_db)):
    """Get all emails received from counties (type=received)."""
    logs = db.query(EmailLog).filter(EmailLog.email_type == 'received').order_by(EmailLog.sent_at.desc()).all()
    result = []
    for l in logs:
        county = db.query(County).filter(County.id == l.county_id).first() if l.county_id else None
        result.append({
            "id": l.id,
            "county_name": county.county_name if county else "Unknown",
            "state": county.state if county else "-",
            "subject": l.subject,
            "body": l.body,
            "received_at": l.sent_at,
        })
    return result


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


# ==================== EMAIL ROUTES ====================

@app.post("/api/send-emails")
async def trigger_email_send(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Manual trigger to send emails to all active counties
    This runs in the background so the API returns immediately
    """
    print("Manual email send triggered via API")

    # Run email sending in background
    background_tasks.add_task(send_to_all_active_counties, db)

    # Get count of counties that will receive emails
    active_count = db.query(County).filter(
        County.status == 'active',
        County.email.isnot(None),
        County.email != ''
    ).count()

    return {
        "message": "Email sending started",
        "recipients": active_count,
        "status": "processing",
        "note": "Emails are being sent in the background. Check the email_log table for results."
    }


@app.post("/api/send-test-email")
async def send_test_email(db: Session = Depends(get_db)):
    """
    Send a single test email to Miami-Dade County to verify SMTP configuration.
    Creates a temporary county record if one doesn't exist yet.
    """
    TEST_EMAIL = "cocpubreq@miamidadeclerk.gov"
    TEST_COUNTY = "Miami-Dade"
    TEST_STATE = "FL"

    county = db.query(County).filter(County.county_name == TEST_COUNTY).first()
    if not county:
        county = County(county_name=TEST_COUNTY, state=TEST_STATE, email=TEST_EMAIL, status='active')
        db.add(county)
        db.commit()
        db.refresh(county)

    subject, html_body = get_email_template(TEST_COUNTY, TEST_STATE)
    success, error_msg = await send_email_async(
        recipient=TEST_EMAIL,
        subject=subject,
        html_body=html_body,
        county_id=county.id,
        db=db
    )

    if success:
        return {"success": True, "message": f"Test email sent successfully to {TEST_EMAIL}"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {error_msg}")


@app.post("/api/seed-counties")
def seed_counties(db: Session = Depends(get_db)):
    """
    Seed the database with the 9 target counties. Skips any that already exist.
    """
    counties_data = [
        {"county_name": "Miami-Dade",  "state": "FL", "email": "cocpubreq@miamidadeclerk.gov"},
        {"county_name": "Broward",     "state": "FL", "email": "Eclerk@browardclerk.org"},
        {"county_name": "Bergen",      "state": "NJ", "email": "countyclerk@bergencountynj.gov"},
        {"county_name": "Middlesex",   "state": "NJ", "email": "mxclerk@co.middlesex.nj.us"},
        {"county_name": "Kings",       "state": "NY", "email": "kings.civil@nycourts.gov"},
        {"county_name": "Queens",      "state": "NY", "email": "queens.civil@nycourts.gov"},
        {"county_name": "Cuyahoga",    "state": "OH", "email": "coccfr@cuyahogacounty.us"},
        {"county_name": "Marion",      "state": "IN", "email": "CivilDepartment@marioncountyclerk.org"},
        {"county_name": "Lake",        "state": "IL", "email": "countyclerk@lakecountyil.gov"},
    ]

    added = []
    skipped = []
    for data in counties_data:
        existing = db.query(County).filter(County.county_name == data["county_name"]).first()
        if existing:
            skipped.append(data["county_name"])
        else:
            county = County(**data, status='active')
            db.add(county)
            added.append(data["county_name"])

    db.commit()
    return {"added": added, "skipped": skipped}


@app.get("/api/email-status")
def get_email_status(db: Session = Depends(get_db)):
    """Get recent email sending statistics"""
    from sqlalchemy import func

    # Get emails from last 24 hours
    yesterday = datetime.utcnow() - timedelta(hours=24)

    recent_sent = db.query(EmailLog).filter(
        EmailLog.sent_at >= yesterday,
        EmailLog.status == 'sent'
    ).count()

    recent_failed = db.query(EmailLog).filter(
        EmailLog.sent_at >= yesterday,
        EmailLog.status == 'failed'
    ).count()

    # Get last email batch time
    last_batch = db.query(func.max(EmailLog.sent_at)).filter(
        EmailLog.email_type == 'request'
    ).scalar()

    # Get next scheduled time
    next_schedule = calculate_next_email_schedule()

    return {
        "last_24h_sent": recent_sent,
        "last_24h_failed": recent_failed,
        "last_batch_time": last_batch,
        "next_scheduled": next_schedule,
        "scheduler_running": scheduler.running
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


# ==================== SERVE HTML PAGES ====================

# Directory for standalone HTML pages (database.html, schema.html, etc.)
HTML_DIR = os.path.join(os.path.dirname(__file__))


@app.get("/database")
def serve_database_page():
    """Serve the database browser page"""
    db_html = os.path.join(HTML_DIR, "database.html")
    if os.path.exists(db_html):
        return FileResponse(db_html)
    raise HTTPException(status_code=404, detail="Database page not found")


@app.get("/schema")
def serve_schema_page():
    """Serve the database schema viewer page"""
    schema_html = os.path.join(HTML_DIR, "schema.html")
    if os.path.exists(schema_html):
        return FileResponse(schema_html)
    raise HTTPException(status_code=404, detail="Schema page not found")


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
    import logging

    # Suppress uvicorn's default info logs
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    print("\n" + "=" * 60)
    print("  COUNTY PRE-FORECLOSURE SYSTEM")
    print("=" * 60)
    print("\n  Server starting...\n")
    print("  Open these URLs in your browser:")
    print("  --------------------------------")
    print("  Main App:      http://localhost:8000/")
    print("  Database:      http://localhost:8000/database")
    print("  Schema:        http://localhost:8000/schema")
    print("  API:           http://localhost:8000/api")
    print("\n" + "=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)