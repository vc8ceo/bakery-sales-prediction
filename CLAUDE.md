# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a bakery sales prediction system with user authentication, built as a full-stack web application with machine learning capabilities.

### Core Architecture

**Frontend-Backend Integration**: The application uses a monolithic deployment where the React frontend is built into static files and served by the FastAPI backend. In development, they run separately (React on :3000, FastAPI on :8000), but in production, everything is served from the FastAPI server.

**User-Centric Data Isolation**: Every piece of data is isolated by user ID. Each user has their own:
- CSV data stored in `user_data` table with `user_id` foreign key
- Machine learning models saved in `models/users/{user_id}/` directory
- Prediction history in `prediction_history` table
- Personal settings (store name, postal code) in the `users` table

**Authentication Flow**: Uses JWT tokens with Bearer authentication. The frontend `AuthContext` manages authentication state globally, and the backend validates JWT tokens on all protected endpoints (all `/api/*` except `/api/auth/*`).

**Database Strategy**: Dynamically chooses database based on environment:
- Railway deployment: Auto-detects PostgreSQL via `PGHOST`, `PGPORT`, etc.
- Local development: Uses SQLite when `ENVIRONMENT=development`
- Manual PostgreSQL: Falls back to `DATABASE_URL` environment variable

### API Structure

All API endpoints are prefixed with `/api/` to separate from static file serving:
- `/api/auth/*` - Authentication (register, login, user management)
- `/api/user/*` - User-specific data (dashboard, predictions, data management)  
- `/api/*` - Core functionality (upload-data, train-model, predict, model-status, data-stats)

The backend serves React static files for all non-API routes to support client-side routing.

### Machine Learning Pipeline

**Data Processing**: `UserDataProcessor` class handles user-specific data processing:
- CSV upload → Database storage (replaces existing user data)
- Feature engineering with time-series features (weekday, season, moving averages)
- Weather integration via Livedoor Weather API

**Model Training**: Each user gets their own RandomForest models:
- Separate models for sales and customer predictions
- Models saved as pickle files in `models/users/{user_id}/`
- Model metadata stored in `user_models` database table

**Prediction**: Combines user's historical data with weather forecast to predict sales/customers for a specific date, with confidence intervals.

## Development Commands

### Local Development Setup

```bash
# Database (PostgreSQL via Docker)
docker run --name bakery-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# Environment variables
export DATABASE_URL="postgresql://postgres:password@localhost/bakery_db"
export SECRET_KEY="your-secret-key-here"  
export ENVIRONMENT="development"

# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm start
```

### Testing

```bash
# Backend API tests
cd backend && python -m pytest tests/

# Frontend tests  
cd frontend && npm test

# Manual API testing
curl http://localhost:8000/api/health
```

### Building

```bash
# Frontend production build
cd frontend && npm run build

# Production build with Docker
docker build -t bakery-app .
```

### Railway Deployment

```bash
# Deploy to Railway (after pushing to GitHub)
# Railway auto-deploys from main branch

# Check deployment
curl https://your-app.up.railway.app/api/health

# Environment variables needed in Railway:
# SECRET_KEY=<strong-random-string>
# ENVIRONMENT=production  
# FRONTEND_URL=https://your-app.up.railway.app
```

## Key Implementation Details

**CSV Data Processing**: Uses Shift_JIS encoding for Japanese CSV files. Column names are mapped from Japanese to English during processing (`data_processor.py`).

**Weather Integration**: Supports Japanese postal codes with extensive mapping to weather station codes. Falls back to default weather data if API fails.

**Frontend State Management**: Uses React Context for global authentication state and local state for component-specific data. Material-UI provides the component library.

**Error Handling**: Backend returns structured error responses. Frontend automatically logs out users on 401 responses and shows user-friendly error messages.

**File Structure Critical**: The `models/users/` and `models/trained/` directories must exist for model storage (maintained with `.gitkeep` files).

## Environment Configuration

The system automatically adapts to different environments:

- **Development**: Uses SQLite, serves API and frontend separately
- **Railway Production**: Auto-detects PostgreSQL, serves frontend from backend  
- **Manual Production**: Uses provided `DATABASE_URL`

Environment detection happens in `backend/app/database.py` and affects database connections, CORS settings, and static file serving.