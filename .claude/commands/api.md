# API Command

Start the FastAPI development server.

## Steps

1. Set environment variable:
```bash
export DATABASE_URL="postgresql://localhost/boston_permits"
```

2. Start server with auto-reload:
```bash
uvicorn backend.main:app --reload --port 8000
```

3. Access:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health
- Frontend: http://localhost:8000/

## Testing Endpoints

```bash
# List permits
curl "http://localhost:8000/api/permits?limit=5"

# Filter by ZIP
curl "http://localhost:8000/api/permits?zip=02134&limit=5"

# Get stats
curl "http://localhost:8000/api/stats"

# Health check
curl "http://localhost:8000/api/health"
```

## Troubleshooting

**"Address already in use"**: Kill existing process or use different port
**"Database connection failed"**: Check DATABASE_URL and PostgreSQL status
