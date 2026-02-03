# Monitoring Context

## What This Section Covers
Health check implementation, logging strategy, alerting considerations.

## Quick Facts
- **Health Endpoint**: GET /api/health
- **Sync Threshold**: Warn if >36 hours since last sync
- **Logging**: Python logging module, structured for production

---

## Health Check Logic

### Healthy Conditions
1. Database is reachable
2. Last sync completed successfully
3. Last sync was within 36 hours

### Degraded Conditions
1. Last sync was >36 hours ago
2. Last sync failed (but previous data exists)

### Unhealthy Conditions
1. Database is unreachable
2. No sync records exist

### Implementation
```python
@app.get("/api/health")
async def health_check():
    try:
        # Check database connection
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        
        # Check last sync
        last_sync = get_last_successful_sync()
        
        if last_sync is None:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "database": "connected",
                    "last_sync": None,
                    "error": "No successful sync recorded"
                }
            )
        
        hours_since_sync = (datetime.utcnow() - last_sync.completed_at).total_seconds() / 3600
        
        if hours_since_sync > 36:
            return {
                "status": "degraded",
                "database": "connected",
                "last_sync": last_sync.completed_at.isoformat(),
                "hours_since_sync": round(hours_since_sync, 1),
                "warning": "Last sync was more than 36 hours ago"
            }
        
        return {
            "status": "healthy",
            "database": "connected",
            "last_sync": last_sync.completed_at.isoformat(),
            "hours_since_sync": round(hours_since_sync, 1)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        )
```

---

## Logging Strategy

### Log Levels
- **DEBUG**: Detailed sync progress, query details
- **INFO**: Sync started/completed, API requests
- **WARNING**: Slow queries, high memory, approaching limits
- **ERROR**: Sync failures, database errors, API errors

### Structured Logging Format
```python
import logging
import json

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def info(self, message, **kwargs):
        self.logger.info(json.dumps({
            "message": message,
            "level": "INFO",
            **kwargs
        }))

# Usage
logger = StructuredLogger("sync_job")
logger.info("Sync completed", records=150, duration_seconds=45)
```

### What to Log

**Sync Job**:
- Sync started (with date range)
- Records fetched from CKAN
- Records inserted/updated
- Sync completed (with duration)
- Any errors (with full context)

**API Requests**:
- Request path and method
- Response status code
- Duration (ms)
- Error details if 4xx/5xx

---

## Render Monitoring

Render provides built-in monitoring for:
- CPU and memory usage
- Request count and latency
- Cron job execution history

Access via Render Dashboard > Service > Metrics

---

## Future: Alerting

Consider adding later:
1. **Uptime monitoring**: External service like UptimeRobot
2. **Slack notifications**: On sync failure
3. **Email alerts**: Daily summary

---

## Files in This Section
- `health-checks.md` - Detailed health check specifications
- `logging.md` - Logging patterns and best practices

---

## Related Sections
- **01-infrastructure**: Database and deployment being monitored
- **02-data-pipeline**: Sync job that health check monitors
