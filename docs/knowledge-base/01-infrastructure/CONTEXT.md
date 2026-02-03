# Infrastructure Context

## What This Section Covers
Database schema, Render deployment configuration, local development environment setup.

## Quick Facts
- **Database**: PostgreSQL (Render starter plan in prod, local install for dev)
- **Hosting**: Render (auto-deploy on push to main)
- **Web Service**: FastAPI served via uvicorn
- **Cron Job**: Daily sync at 6 AM EST (11:00 UTC)

---

## Database Schema

### permits table
```sql
CREATE TABLE permits (
    id SERIAL PRIMARY KEY,
    permit_number VARCHAR(50) UNIQUE NOT NULL,
    work_type VARCHAR(50),
    permit_type_descr VARCHAR(255),
    description TEXT,
    comments TEXT,
    applicant VARCHAR(255),
    declared_valuation DECIMAL(15,2),
    total_fees DECIMAL(10,2),
    issued_date DATE,
    expiration_date DATE,
    status VARCHAR(50),
    occupancy_type VARCHAR(100),
    sq_feet INTEGER,
    address VARCHAR(255),
    zip VARCHAR(10),
    ward VARCHAR(10),
    property_id VARCHAR(50),
    parcel_id VARCHAR(50),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_permits_zip ON permits(zip);
CREATE INDEX idx_permits_issued_date ON permits(issued_date DESC);
CREATE INDEX idx_permits_work_type ON permits(work_type);
CREATE INDEX idx_permits_status ON permits(status);
```

### sync_log table
```sql
CREATE TABLE sync_log (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20),
    records_fetched INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    error_message TEXT
);
```

---

## Render Configuration (render.yaml)

```yaml
databases:
  - name: boston-dashboard-db
    plan: starter
    databaseName: boston_permits
    user: dashboard

services:
  - type: web
    name: boston-data-dashboard
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: boston-dashboard-db
          property: connectionString
    autoDeploy: true

  - type: cron
    name: boston-dashboard-sync
    runtime: python
    buildCommand: pip install -r requirements.txt
    schedule: "0 11 * * *"  # 6 AM EST
    startCommand: python -m backend.sync_job
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: boston-dashboard-db
          property: connectionString
      - key: SYNC_DAYS_BACK
        value: "90"
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (local install)
- Git

### Database Setup
```bash
# Create local database
createdb boston_permits

# Set environment variable
export DATABASE_URL="postgresql://localhost/boston_permits"
```

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m backend.database init

# Run sync (one-time or testing)
python -m backend.sync_job

# Start API server
uvicorn backend.main:app --reload
```

---

## Files in This Section
- `database-schema.md` - Full schema with field descriptions
- `render-deployment.md` - Deployment checklist and troubleshooting
- `environment-setup.md` - Local dev environment guide

---

## Related Sections
- **02-data-pipeline**: Sync job that populates the database
- **03-backend**: API that reads from the database
- **05-monitoring**: Health checks for database and sync
