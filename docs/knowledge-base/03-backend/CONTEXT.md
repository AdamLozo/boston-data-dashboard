# Backend Context

## What This Section Covers
FastAPI application structure, API endpoint specifications, error handling patterns.

## Quick Facts
- **Framework**: FastAPI
- **Database Access**: psycopg2 with RealDictCursor (raw SQL, no ORM)
- **Server**: uvicorn
- **Port**: $PORT (Render sets this)

---

## API Endpoints

### GET /api/permits
List permits with optional filters.

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| zip | string | - | Filter by ZIP code |
| work_type | string | - | Filter by work type (ELECTRICAL, PLUMBING, etc.) |
| days | int | 30 | Include permits from last N days |
| limit | int | 100 | Max records to return |
| offset | int | 0 | Pagination offset |

**Response**:
```json
{
  "data": [
    {
      "permit_number": "B2024-00001",
      "work_type": "ELECTRICAL",
      "address": "123 Main St",
      "zip": "02134",
      "issued_date": "2024-01-15",
      "declared_valuation": 50000.00,
      "latitude": 42.3601,
      "longitude": -71.0589
    }
  ],
  "count": 1,
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

### GET /api/permits/{permit_number}
Get single permit details.

### GET /api/stats
Aggregated statistics.

**Response**:
```json
{
  "by_type": {"ELECTRICAL": 45, "PLUMBING": 32, ...},
  "by_zip": {"02134": 28, "02135": 19, ...},
  "by_day": [{"date": "2024-01-15", "count": 12}, ...],
  "total_valuation": 5000000.00,
  "total_count": 150
}
```

### GET /api/neighborhoods
ZIP code summaries with counts.

### GET /api/work-types
Work type codes with human-readable labels.

**Response**:
```json
{
  "data": [
    {"code": "ELECTRICAL", "label": "Electrical Work", "count": 45},
    {"code": "PLUMBING", "label": "Plumbing", "count": 32},
    {"code": "INTREN", "label": "Interior Renovation", "count": 28}
  ]
}
```

### GET /api/health
Monitoring endpoint.

**Response** (healthy):
```json
{
  "status": "healthy",
  "database": "connected",
  "last_sync": "2024-01-15T11:00:00Z",
  "hours_since_sync": 5
}
```

**Response** (degraded):
```json
{
  "status": "degraded",
  "database": "connected",
  "last_sync": "2024-01-13T11:00:00Z",
  "hours_since_sync": 53,
  "warning": "Last sync was more than 36 hours ago"
}
```

### GET /api/sync-status
Last sync details.

---

## File Structure

```
backend/
├── main.py          # FastAPI app, route definitions
├── database.py      # Connection pool, queries, schema
├── sync_job.py      # Cron script (standalone)
└── config.py        # Environment variables
```

### main.py Pattern
```python
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from .database import get_db_connection
from .config import settings

app = FastAPI(title="Boston Data Dashboard")

@app.get("/api/permits")
async def list_permits(
    zip: str = Query(None),
    work_type: str = Query(None),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    # Implementation...
    pass

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

### database.py Pattern
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from .config import settings

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(settings.DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_permits(filters: dict) -> list:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build parameterized query
            cur.execute(query, params)
            return cur.fetchall()
```

---

## Error Handling

### HTTP Status Codes
- 200: Success
- 400: Bad request (invalid parameters)
- 404: Not found (permit doesn't exist)
- 500: Server error (database down, etc.)

### Error Response Format
```json
{
  "error": "Not Found",
  "detail": "Permit B2024-99999 not found"
}
```

### Exception Handler
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )
```

---

## Files in This Section
- `fastapi-patterns.md` - Detailed FastAPI patterns and best practices
- `api-endpoints.md` - Full endpoint specifications with examples
- `error-handling.md` - Error handling and logging patterns

---

## Related Sections
- **01-infrastructure**: Database schema being queried
- **02-data-pipeline**: Sync job that populates data
- **04-frontend**: UI that consumes these APIs
