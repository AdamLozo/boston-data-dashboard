# Sync Command

Run the sync job locally to test data pipeline.

## Prerequisites
- Local PostgreSQL running
- DATABASE_URL environment variable set
- Dependencies installed

## Steps

1. Ensure database schema exists:
```bash
python -m backend.database init
```

2. Run sync job:
```bash
SYNC_DAYS_BACK=30 python -m backend.sync_job
```

3. Verify data:
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM permits;"
```

## Troubleshooting

**"relation does not exist"**: Run database init first
**"connection refused"**: Start PostgreSQL
**"CKAN API error"**: Check network, verify resource ID
