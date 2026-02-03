"""
Boston Data Dashboard - FastAPI Backend
API endpoints for building permits data
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
from pathlib import Path
import logging

from .config import settings
from .database import get_db_connection, init_db, get_last_sync
from decimal import Decimal
from datetime import date, datetime as dt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serialize_row(row: dict) -> dict:
    """Convert database row to JSON-serializable dict"""
    result = {}
    for key, value in row.items():
        if isinstance(value, (date, dt)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result


app = FastAPI(
    title="Boston Data Dashboard",
    description="Track building permits and development activity in Boston",
    version="1.0.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    logger.info("Starting Boston Data Dashboard API")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# Work type code mappings for human-readable labels
WORK_TYPE_LABELS = {
    "ELECTRICAL": "Electrical",
    "PLUMBING": "Plumbing",
    "GAS": "Gas",
    "INTREN": "Interior Renovation",
    "EXTREN": "Exterior Renovation",
    "INTEXT": "Interior/Exterior",
    "INTDEM": "Interior Demolition",
    "EXTDEM": "Exterior Demolition",
    "LVOLT": "Low Voltage",
    "FA": "Fire Alarm",
    "INSUL": "Insulation",
    "ROOF": "Roofing",
    "SIDE": "Siding",
    "SOL": "Solar",
    "FSTTRK": "Fast Track",
    "ERT": "Erect/New Construction",
    "COO": "Certificate of Occupancy",
    "ADDITION": "Addition",
    "OTHER": "Other"
}


@app.get("/api/permits")
async def get_permits(
    zip: Optional[str] = Query(None, alias="zip", description="Filter by ZIP code"),
    work_type: Optional[str] = Query(None, description="Filter by work type"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get permits with optional filters and pagination"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Build WHERE clause
                conditions = [f"issued_date >= CURRENT_DATE - INTERVAL '{days} days'"]
                params = []

                if zip:
                    conditions.append("zip = %s")
                    params.append(zip)

                if work_type:
                    conditions.append("work_type = %s")
                    params.append(work_type)

                where_clause = " AND ".join(conditions)

                # Get total count
                cur.execute(f"SELECT COUNT(*) as count FROM permits WHERE {where_clause}", params)
                total = cur.fetchone()['count']

                # Get records
                query = f"""
                    SELECT * FROM permits
                    WHERE {where_clause}
                    ORDER BY issued_date DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, params + [limit, offset])
                permits = cur.fetchall()

                # Serialize and add work type labels
                serialized_permits = []
                for permit in permits:
                    p = serialize_row(permit)
                    p['work_type_label'] = WORK_TYPE_LABELS.get(
                        permit.get('work_type'),
                        permit.get('work_type')
                    )
                    serialized_permits.append(p)

                return {
                    "data": serialized_permits,
                    "count": len(serialized_permits),
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }

    except Exception as e:
        logger.error(f"Error fetching permits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/permits/{permit_number}")
async def get_permit(permit_number: str):
    """Get a single permit by permit number"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM permits WHERE permit_number = %s", (permit_number,))
                permit = cur.fetchone()

                if not permit:
                    raise HTTPException(status_code=404, detail="Permit not found")

                p = serialize_row(permit)
                p['work_type_label'] = WORK_TYPE_LABELS.get(
                    permit.get('work_type'),
                    permit.get('work_type')
                )
                return p

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching permit {permit_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats(days: int = Query(30, ge=1, le=365, description="Number of days to analyze")):
    """Get permit statistics"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Total permits
                cur.execute(f"""
                    SELECT COUNT(*) as count
                    FROM permits
                    WHERE issued_date >= CURRENT_DATE - INTERVAL '{days} days'
                """)
                total = cur.fetchone()['count']

                # By work type
                cur.execute(f"""
                    SELECT work_type, COUNT(*) as count
                    FROM permits
                    WHERE issued_date >= CURRENT_DATE - INTERVAL '{days} days'
                    GROUP BY work_type
                    ORDER BY count DESC
                """)
                by_type = [
                    {
                        "type": row['work_type'],
                        "label": WORK_TYPE_LABELS.get(row['work_type'], row['work_type']),
                        "count": row['count']
                    }
                    for row in cur.fetchall()
                ]

                # By ZIP code
                cur.execute(f"""
                    SELECT zip, COUNT(*) as count
                    FROM permits
                    WHERE issued_date >= CURRENT_DATE - INTERVAL '{days} days'
                      AND zip IS NOT NULL
                    GROUP BY zip
                    ORDER BY count DESC
                    LIMIT 15
                """)
                by_zip = [{"zip": row['zip'], "count": row['count']} for row in cur.fetchall()]

                # By day (for charts)
                cur.execute(f"""
                    SELECT issued_date::date as day, COUNT(*) as count
                    FROM permits
                    WHERE issued_date >= CURRENT_DATE - INTERVAL '{days} days'
                    GROUP BY issued_date::date
                    ORDER BY day
                """)
                by_day = [
                    {"date": row['day'].isoformat(), "count": row['count']}
                    for row in cur.fetchall()
                ]

                # Total declared valuation
                cur.execute(f"""
                    SELECT COALESCE(SUM(declared_valuation), 0) as total
                    FROM permits
                    WHERE issued_date >= CURRENT_DATE - INTERVAL '{days} days'
                """)
                total_valuation = float(cur.fetchone()['total'])

                return {
                    "period_days": days,
                    "total_permits": total,
                    "total_valuation": total_valuation,
                    "by_type": by_type,
                    "by_zip": by_zip,
                    "by_day": by_day
                }

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/neighborhoods")
async def get_neighborhoods():
    """Get list of all ZIP codes with permit counts"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT zip, COUNT(*) as count
                    FROM permits
                    WHERE zip IS NOT NULL
                    GROUP BY zip
                    ORDER BY zip
                """)
                zip_codes = cur.fetchall()

                return {"data": [serialize_row(row) for row in zip_codes]}

    except Exception as e:
        logger.error(f"Error fetching neighborhoods: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/work-types")
async def get_work_types():
    """Get list of all work types with labels"""
    return {
        "data": [
            {"code": code, "label": label}
            for code, label in WORK_TYPE_LABELS.items()
        ]
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns healthy/degraded/unhealthy based on database and sync status.
    """
    try:
        # Check database connection
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

            # Get last sync
            last_sync = get_last_sync(conn)

            if last_sync is None:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "database": "connected",
                        "last_sync": None,
                        "error": "No sync records found"
                    }
                )

            # Calculate hours since last sync
            if last_sync['completed_at']:
                hours_since_sync = (
                    datetime.now() - last_sync['completed_at']
                ).total_seconds() / 3600
            else:
                hours_since_sync = None

            # Determine health status
            if hours_since_sync and hours_since_sync > 36:
                return {
                    "status": "degraded",
                    "database": "connected",
                    "last_sync": last_sync['completed_at'].isoformat() if last_sync['completed_at'] else None,
                    "hours_since_sync": round(hours_since_sync, 1),
                    "warning": "Last sync was more than 36 hours ago"
                }

            if last_sync['status'] == 'error':
                return {
                    "status": "degraded",
                    "database": "connected",
                    "last_sync": last_sync['completed_at'].isoformat() if last_sync['completed_at'] else None,
                    "hours_since_sync": round(hours_since_sync, 1) if hours_since_sync else None,
                    "warning": f"Last sync failed: {last_sync.get('error_message', 'Unknown error')}"
                }

            return {
                "status": "healthy",
                "database": "connected",
                "last_sync": last_sync['completed_at'].isoformat() if last_sync['completed_at'] else None,
                "hours_since_sync": round(hours_since_sync, 1) if hours_since_sync else None,
                "records_synced": last_sync.get('records_inserted', 0) + last_sync.get('records_updated', 0)
            }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        )


@app.get("/api/sync-status")
async def get_sync_status():
    """Get recent sync log entries"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM sync_log
                    ORDER BY started_at DESC
                    LIMIT 5
                """)
                logs = cur.fetchall()

                return {"data": [serialize_row(row) for row in logs]}

    except Exception as e:
        logger.error(f"Error fetching sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files (frontend) - mount after API routes
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
