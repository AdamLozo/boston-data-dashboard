# Boston Data Dashboard - Claude Code Context

## Project Overview
Hyperlocal dashboard tracking Boston building permits with automated daily data collection from Analyze Boston's open data portal.

## Quick Reference
- **Repo**: boston-data-dashboard
- **Stack**: Python/FastAPI + PostgreSQL + Vanilla JS/Leaflet.js
- **Hosting**: Render (web service + cron job + PostgreSQL)
- **Data Source**: Analyze Boston CKAN API

## Directory Structure
```
boston-data-dashboard/
├── .claude/                    # YOU ARE HERE - Claude Code context
├── docs/
│   ├── PLAN.md                 # Detailed implementation plan
│   ├── MASTER_PLAN.md          # Roadmap and milestones
│   └── knowledge-base/         # Domain-specific context files
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── database.py             # DB operations (raw SQL, no ORM)
│   ├── sync_job.py             # Cron script for daily sync
│   └── config.py               # Environment config
├── frontend/
│   ├── index.html              # Single-page dashboard
│   └── css/styles.css          # Responsive styles
├── requirements.txt
├── render.yaml                 # Render deployment config
└── README.md
```

## Critical Context Files (Read These First)
1. `docs/PLAN.md` - Complete technical specification
2. `docs/knowledge-base/*/CONTEXT.md` - Domain entry points

## Code Conventions
- **Python**: Black formatting, type hints, docstrings
- **SQL**: Raw SQL via psycopg2 (no ORM) - parameterized queries only
- **Frontend**: Vanilla JS (no frameworks), mobile-first CSS
- **Error Handling**: Always return meaningful JSON errors
- **Logging**: Use Python logging module, structured logs for production

## Environment Variables
```
DATABASE_URL=postgresql://user:pass@host:port/db
SYNC_DAYS_BACK=90
```

## Key Patterns

### Database Connection
```python
# Use context manager pattern
with get_db_connection() as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
```

### API Response Format
```python
# Success
{"data": [...], "count": n, "page": 1}

# Error
{"error": "message", "detail": "..."}
```

### CKAN API Query
```python
# Always use SQL endpoint for complex queries
url = "https://data.boston.gov/api/3/action/datastore_search_sql"
sql = f"SELECT * FROM \"{resource_id}\" WHERE issued_date >= '{date}'"
```

## When You're Stuck
1. Check `docs/knowledge-base/` for domain-specific guidance
2. Reference `docs/PLAN.md` for specifications
3. Ask Adam for clarification before guessing
