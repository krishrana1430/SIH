# Local Development (No Docker)

Since you're on WSL2 without Docker Desktop configured, you can run the application locally for testing.

## Prerequisites

- Node.js 18+ installed
- Python 3.9+ with pip installed
- .env file configured in the root directory

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend/web
npm install
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
uvicorn backend.api.main:app --reload --reload-include frontend/web
```

This will start the backend on `http://localhost:8000`.

### Start Frontend (Terminal 2)

```bash
cd frontend/web
npm run dev
```

This will start the frontend on `http://localhost:3000`.

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### Port already in use

If port 8000 or 3000 is already in use:

```bash
# For backend, change the port
uvicorn backend.api.main:app --reload --port 8001
```

### Backend can't reach frontend

The backend needs to access the frontend. Make sure:
1. The backend is running before the frontend
2. The frontend is accessible at http://localhost:3000
3. Check your `.env` file for correct URLs

## Stopping the Application

Press `Ctrl+C` in each terminal to stop the services.

## Alternative: Using Docker (When Available)

If you install Docker Desktop in the future:

```bash
# Build and run everything
docker-compose up --build

# Or use the simplified compose file
docker-compose -f docker-compose.local.yml up --build
```
