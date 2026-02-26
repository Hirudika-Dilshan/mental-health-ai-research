# Mental Health AI Research

A research-focused mental health screening app that runs a conversational GAD-7 workflow using a React frontend and a FastAPI backend.

## Tech Stack
- Frontend: React (`frontend/`)
- Backend API: FastAPI (`api/main.py`)
- Auth + Database: Supabase
- LLM Provider: Groq (`llama-3.3-70b-versatile`)
- Deployment: Vercel (`vercel.json`)

## Features
- User registration and login with Supabase Auth
- Chat session history (create, list, rename, delete)
- Conversational GAD-7 screening flow
- Crisis keyword detection with emergency guidance
- Session/message persistence in Supabase tables

## Project Structure
- `frontend/` React app
- `api/` FastAPI app used by Vercel serverless routes
- `backend/` legacy/local backend copy (not used by current Vercel config)
- `vercel.json` frontend + API routing/build config

## Prerequisites
- Node.js 18+
- Python 3.10+
- Supabase project (Auth + database tables)
- Groq API key

## Environment Variables

### Backend (`api/`)
Create a `.env` file or set environment variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_or_anon_key
GROQ_API_KEY=your_groq_api_key
FRONTEND_URL=http://localhost:3000
```

### Frontend (`frontend/`)
Create `frontend/.env`:

```env
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_KEY=your_supabase_anon_key
REACT_APP_API_URL=http://localhost:8000/api
```

## Local Development

### 1. Run Backend

```bash
cd api
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API base URL: `http://localhost:8000`

### 2. Run Frontend

```bash
cd frontend
npm install
npm start
```

Frontend URL: `http://localhost:3000`

## Main API Endpoints
- `POST /api/register`
- `POST /api/login`
- `POST /api/sessions`
- `GET /api/sessions/{user_id}`
- `GET /api/sessions/{session_id}/messages`
- `PUT /api/sessions/{session_id}/title`
- `DELETE /api/sessions/{session_id}`
- `POST /api/chat`

## Deployment (Vercel)
- Backend entrypoint: `api/main.py`
- Frontend build: `frontend/` (`npm run build`)
- Routes are configured in `vercel.json`

Set Vercel environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GROQ_API_KEY`
- `FRONTEND_URL`
- `PYTHONUNBUFFERED=1`
- Frontend `REACT_APP_*` variables

## Notes
- This project is a screening/research tool, not a clinical diagnosis system.
- Crisis contacts in current code are hard-coded and should be updated for your target region before wider use.
