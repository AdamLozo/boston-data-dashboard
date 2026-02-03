# Boston Data Dashboard

A hyperlocal dashboard tracking Boston building permits with automated daily data collection from Analyze Boston's open data portal.

## Features

- Interactive Map with marker clustering
- Real-time filtering by ZIP code, work type, and date range
- Statistics dashboard
- Automated daily sync from CKAN API
- Responsive mobile-first design

## Tech Stack

- Backend: Python/FastAPI + psycopg3
- Database: PostgreSQL
- Frontend: Vanilla JS + Leaflet.js
- Data Source: Analyze Boston CKAN API

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Create database: `createdb boston_permits`
3. Create `.env` file (see `.env.example`)
4. Initialize schema: `python -m backend.database`
5. Sync data: `python -m backend.sync_job 30`
6. Start server: `uvicorn backend.main:app --reload`
7. Open: http://localhost:8000

## API Endpoints

- `GET /api/permits` - List permits with filters
- `GET /api/stats` - Aggregate statistics
- `GET /api/health` - Health check
- `GET /api/neighborhoods` - ZIP codes
- `GET /api/work-types` - Work types

## Status

Milestone 1: Local Prototype - COMPLETE
- PostgreSQL migration complete
- 2,500+ permits synced
- All endpoints working
- Frontend with Leaflet.js map operational

Next: Deploy to Render
