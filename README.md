# County Pre-Foreclosure Data Collection System

A web application for managing county contacts and automating pre-foreclosure data collection.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (auto-created)
- **Frontend**: React + Vite

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ (only needed for development)

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python main.py
```

3. **Open in browser:**
```
http://localhost:8000
```

That's it! The application will:
- Create the SQLite database automatically
- Serve the React frontend
- Start the API server

## Features

### Current Implementation

- Add, edit, delete counties
- View county list with contact information
- Dashboard with statistics
- Email schedule tracking (Monday & Thursday at 9 AM)
- Clean database structure with 5 tables

### Database Tables

| Table | Description |
|-------|-------------|
| counties | Main county contact information |
| payment_info | Payment instructions per county |
| addresses | Extracted property addresses |
| email_log | Track sent/received emails |
| received_files | Track incoming data files |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/counties | List all counties |
| POST | /api/counties | Create a county |
| GET | /api/counties/{id} | Get a county |
| PUT | /api/counties/{id} | Update a county |
| DELETE | /api/counties/{id} | Delete a county |
| GET | /api/stats | Get statistics |
| GET | /api/schema | Get database schema |

Full API documentation: `http://localhost:8000/docs`

## Development

### Running in Development Mode

1. **Start backend:**
```bash
python main.py
```

2. **Start React dev server (in another terminal):**
```bash
cd frontend
yarn install
yarn dev
```

### Building Frontend for Production

```bash
cd frontend
yarn build
```

## Project Structure

```
County Pre-Foreclosure Data Collection System/
├── main.py              # FastAPI backend (single file)
├── pre_foreclosure.db   # SQLite database (auto-created)
├── requirements.txt     # Python dependencies
├── database_schema.sql  # SQL schema reference
└── frontend/            # React frontend
    ├── src/
    │   ├── App.jsx      # Main React component
    │   ├── main.jsx     # Entry point
    │   └── index.css    # Styles
    ├── dist/            # Production build
    └── package.json
```

## Requirements Reference

Based on project requirements:

- [x] Database structure
- [x] GUI to add counties
- [x] Display list of counties
- [x] Last email sent activity visible
- [x] Next schedule of email visible
- [ ] Email automation (not implemented)
- [ ] File upload/parsing (not implemented)
- [ ] Data export (not implemented)

## Support

For issues or questions, contact the development team.