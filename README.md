  County Pre-Foreclosure Data Collection System

  A web application for managing county contacts and automating pre-foreclosure data collection.

  Tech Stack

  - Backend: FastAPI (Python)
  - Database: PostgreSQL (production) / SQLite (local development)
  - Frontend: React + Vite 
  - Deployment: Railway.app

  Live Application

  Production URL: https://county-foreclosure-system-production.up.railway.app/

  Available Pages

  - Main App: / - Add and manage county contacts
  - Database Browser: /database - View all records across tables
  - Schema Viewer: /schema - Interactive database schema
  - API Docs: /docs - Interactive API documentation

  Local Development

  Prerequisites

  - Python 3.12+
  - Node.js 18+ (only for frontend development)

  Quick Start

  1. Install Python dependencies:
  pip install -r requirements.txt

  2. Run the application:
  python main.py

  3. Open in browser:
  http://localhost:8000

  The application will:
  - Create SQLite database automatically (local)
  - Serve the pre-built React frontend
  - Start the API server on port 8000

  Features

  Current Implementation

  - Add, edit, delete counties with full CRUD operations
  - View county list with contact information
  - Real-time dashboard with statistics
  - Email schedule tracking (Monday & Thursday at 9 AM)
  - Interactive database browser (/database)
  - Visual schema viewer (/schema)
  - Full API documentation (/docs)
  - PostgreSQL support for production
  - Persistent data storage

  Database Tables

  | Table          | Description                     |
  |----------------|---------------------------------|
  | counties       | Main county contact information |
  | payment_info   | Payment instructions per county |
  | addresses      | Extracted property addresses    |
  | email_log      | Track sent/received emails      |
  | received_files | Track incoming data files       |

  API Endpoints

  | Method | Endpoint           | Description         |
  |--------|--------------------|---------------------|
  | GET    | /api               | API info            |
  | GET    | /api/counties      | List all counties   |
  | POST   | /api/counties      | Create a county     |
  | GET    | /api/counties/{id} | Get a county        |
  | PUT    | /api/counties/{id} | Update a county     |
  | DELETE | /api/counties/{id} | Delete a county     |
  | GET    | /api/stats         | Get statistics      |
  | GET    | /api/schema        | Get database schema |

  Full interactive documentation: /docs or /redoc

  Environment Configuration

  Local Development

  No configuration needed - uses SQLite by default.

  Production (Railway)

  Set DATABASE_URL environment variable:
  postgresql://user:password@host:port/database

  The application automatically detects the database type from the URL.

  Frontend Development

  Building Frontend

  cd frontend
  npm install
  npm run build

  Built files are served automatically by FastAPI from frontend/dist/.

  Frontend Development Mode

  cd frontend
  npm run dev

  Note: For production builds, do NOT set VITE_API_URL in .env - it should use relative paths.

  Project Structure

  County Pre-Foreclosure Data Collection System/
  ├── main.py                  # FastAPI backend with all routes
  ├── database.html            # Database browser page
  ├── schema.html              # Schema viewer page
  ├── requirements.txt         # Python dependencies
  ├── runtime.txt              # Python version (3.12.0)
  ├── nixpacks.toml           # Railway build configuration
  ├── pre_foreclosure.db      # SQLite database (local only)
  └── frontend/
      ├── src/
      │   ├── App.jsx         # Main React component
      │   ├── main.jsx        # Entry point
      │   └── index.css       # Styles
      ├── dist/               # Production build (committed)
      ├── .env.production     # Production config
      └── package.json

  Deployment

  The application is configured for automatic deployment on Railway:

  1. Push to master branch
  2. Railway automatically builds and deploys
  3. PostgreSQL database is linked via DATABASE_URL
  4. Frontend is pre-built and committed to frontend/dist/

  Implementation Status

  Based on project requirements:

  - ✅ Database structure with 5 tables
  - ✅ GUI to add/edit/delete counties
  - ✅ Display list of counties
  - ✅ Last email sent activity visible
  - ✅ Next schedule of email visible
  - ✅ Database browser interface
  - ✅ Schema visualization
  - ✅ PostgreSQL production database
  - ⏳ Email automation (planned)
  - ⏳ File upload/parsing (planned)
  - ⏳ Data export (planned)
