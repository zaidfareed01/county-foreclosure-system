# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

County Pre-Foreclosure Data Collection System - A web application for managing county contacts and automating pre-foreclosure data collection. Built with FastAPI backend and vanilla HTML/CSS/JS frontend.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy ORM + Pydantic
- **Database**: MySQL 8.0+
- **Frontend**: Pure HTML/CSS/JavaScript (no framework)
- **Python**: 3.8+

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env with your MySQL credentials

# Setup database (MySQL must be running)
mysql -u root -p
CREATE DATABASE pre_foreclosure_db;
exit

# Import schema
mysql -u root -p pre_foreclosure_db < database_schema.sql
```

### Running
```bash
# Start backend (runs on http://localhost:8000)
python main.py

# Alternative: use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Serve frontend (optional, can also just open index.html in browser)
python -m http.server 8080
```

### API Documentation
Access interactive docs at: `http://localhost:8000/docs` or `http://localhost:8000/redoc`

## Architecture

### Backend (main.py)
Single-file FastAPI application with three layers:
1. **Models**: SQLAlchemy ORM models (`County`, `EmailLog`) defined inline
2. **Schemas**: Pydantic models for request/response validation
3. **Routes**: RESTful endpoints under `/api/counties`

Key design decisions:
- Database connection via `DATABASE_URL` env variable
- CORS middleware allows all origins in development (restrict in production)
- Tables auto-created on startup via `Base.metadata.create_all()`
- Email schedule calculated: Mondays & Thursdays at 9 AM

### Frontend (index.html)
Single-file SPA with:
- Embedded CSS (lines 7-292)
- HTML structure (lines 294-390)
- JavaScript for API calls (lines 392-610)

Communicates with backend via `API_URL` constant (default: `http://localhost:8000/api`).

### Database Schema (database_schema.sql)
Tables (in dependency order):
1. `counties` - Main entity, tracks contact info and last email sent
2. `payment_info` - Payment instructions per county (FK: counties)
3. `addresses` - Extracted addresses from files (FK: counties)
4. `email_log` - Track sent/received emails (FK: counties, nullable)
5. `received_files` - Track incoming files and processing status (FK: counties)

Note: SQLAlchemy models in main.py only define `counties` and `email_log`. Additional tables exist in schema but not yet in ORM.

## Environment Variables

Required in `.env`:
- `DATABASE_URL`: MySQL connection string (format: `mysql+pymysql://user:password@host:port/db_name`)

Future use (not yet implemented):
- `SMTP_SERVER`, `SMTP_PORT`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`

## Key Endpoints

```
GET    /api/counties           - List counties (optional ?status=&state= filters)
POST   /api/counties           - Create county
GET    /api/counties/{id}      - Get single county
PUT    /api/counties/{id}      - Update county
DELETE /api/counties/{id}      - Delete county
GET    /api/stats              - Dashboard statistics
```

## Development Notes

- Backend uses `echo=True` for SQL query logging (disable in production)
- County names must be unique
- Response model includes computed `next_scheduled_email` field
- Frontend handles loading states and empty states inline