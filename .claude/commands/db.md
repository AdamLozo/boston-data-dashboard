# Database Command

Common database operations for development.

## Prerequisites
- PostgreSQL installed and running
- DATABASE_URL environment variable set

## Operations

### Initialize Schema
Create tables and indexes:
```bash
python -m backend.database init
```

### Reset Database
Drop and recreate tables (WARNING: destroys data):
```bash
python -m backend.database reset
```

### Check Status
```bash
psql $DATABASE_URL -c "
SELECT 
    (SELECT COUNT(*) FROM permits) as permit_count,
    (SELECT MAX(issued_date) FROM permits) as latest_permit,
    (SELECT COUNT(*) FROM sync_log WHERE status = 'success') as successful_syncs;
"
```

### View Recent Syncs
```bash
psql $DATABASE_URL -c "
SELECT id, started_at, completed_at, status, records_fetched, records_inserted
FROM sync_log 
ORDER BY started_at DESC 
LIMIT 5;
"
```

### Sample Data Query
```bash
psql $DATABASE_URL -c "
SELECT permit_number, work_type, address, zip, issued_date
FROM permits 
ORDER BY issued_date DESC 
LIMIT 10;
"
```

### Create Local Database
```bash
createdb boston_permits
export DATABASE_URL="postgresql://localhost/boston_permits"
```

### Drop Local Database
```bash
dropdb boston_permits
```

## Connect to Render Database
```bash
# Get connection string from Render dashboard
# Or use render CLI:
render postgres connect boston-dashboard-db
```

## Troubleshooting

**"database does not exist"**: Run createdb first
**"permission denied"**: Check PostgreSQL user permissions
**"relation does not exist"**: Run database init
