# Boston Development Tracker - Project Plan

## Overview

A hyperlocal dashboard tracking building permits and development activity across Boston neighborhoods. Data sourced from Analyze Boston's open data portal, with automated daily updates.

**Primary Goal**: Build something useful for neighbors while learning Claude Code workflows
**Scope**: City of Boston only (suburbs like Newton have separate systems)
**Future**: Expandable to other Analyze Boston datasets (restaurant inspections, violations, etc.)

---

## Decisions Log

| Decision | Choice | Notes |
|----------|--------|-------|
| Initial data load | ~~90 days~~ **10 years** | Updated after implementing pagination |
| Sync schedule | 6 AM EST (11:00 UTC) | Adjustable via render.yaml if city posts data later |
| Repository | `boston-data-dashboard` | Named for expansion to other Analyze Boston datasets |
| Database | PostgreSQL on Render | Shared between web + cron services |
| Local dev database | PostgreSQL | Matches production for consistency |
| Sync failure alerts | /api/health endpoint | Adam will monitor externally |
| Mobile priority | Equal with desktop | Responsive design required |
| Deployment | Auto-deploy on push to main | No staging branch for v1 |
| API pagination | **Implemented** | Required to fetch > 10,000 records |
| Historical backfill | **442,874 records** | One-time load of 10 years (2016-2026) |
| Daily sync overlap | 90 days | Catches late-arriving permits, handles updates |
| Map clustering | Enabled (50px radius) | Performance optimization for large datasets |
| Default time period | 90 days | Balances data freshness with volume |

---

## Data Source

**Analyze Boston - Approved Building Permits**
- URL: https://data.boston.gov/dataset/approved-building-permits
- Resource ID: `6ddcd912-32a0-43df-9908-63574f8c7e77`
- API: CKAN Datastore API (supports SQL queries)
- Update Frequency: Daily by the city
- License: Open Data Commons Public Domain (PDDL)
- Records: 713,000+ permits from 2009 to present

### API Endpoints

1. **Simple Query**: `https://data.boston.gov/api/3/action/datastore_search`
   - Params: `resource_id`, `limit`, `offset`, `filters`
   
2. **SQL Query**: `https://data.boston.gov/api/3/action/datastore_search_sql`
   - Allows date filtering, aggregation, sorting
   - Example: `SELECT * FROM "{resource_id}" WHERE "issued_date" >= '2025-01-01'`

### Data Fields (25 columns)

| Field | Type | Description |
|-------|------|-------------|
| permitnumber | text | Unique permit identifier |
| worktype | text | Work type code (ELECTRICAL, PLUMBING, INTREN, etc.) |
| permittypedescr | text | Human-readable permit type |
| description | text | Brief description |
| comments | text | Detailed notes |
| applicant | text | Applicant name |
| declared_valuation | text | Dollar value (formatted as "$X,XXX.XX") |
| total_fees | text | Permit fees |
| issued_date | timestamp | When permit was issued |
| expiration_date | timestamp | When permit expires |
| status | text | Open, Closed, Stop Work |
| occupancytype | text | Building use type |
| sq_feet | numeric | Square footage |
| address | text | Street address |
| city | text | Always "Boston" |
| state | text | Always "MA" |
| zip | text | ZIP code (maps to neighborhood) |
| ward | numeric | City ward number |
| property_id | numeric | Property identifier |
| parcel_id | numeric | Parcel identifier |
| y_latitude | numeric | Latitude coordinate |
| x_longitude | numeric | Longitude coordinate |

### Work Type Codes

| Code | Meaning |
|------|---------|
| ELECTRICAL | Electrical work |
| PLUMBING | Plumbing work |
| GAS | Gas line work |
| INTREN | Interior renovation |
| EXTREN | Exterior renovation |
| INTEXT | Interior + exterior |
| INTDEM | Interior demolition |
| EXTDEM | Exterior demolition |
| LVOLT | Low voltage (data, security) |
| FA | Fire alarm |
| INSUL | Insulation |
| ROOF | Roofing |
| SIDE | Siding |
| SOL | Solar installation |
| FSTTRK | Fast track permit |
| ERT | Erect/new construction |
| COO | Certificate of occupancy |
| ADDITION | Building addition |

### ZIP Code to Neighborhood Mapping

| ZIP | Neighborhood |
|-----|--------------|
| 02108 | Beacon Hill |
| 02109 | Downtown/Waterfront |
| 02110 | Financial District |
| 02111 | Chinatown |
| 02113 | North End |
| 02114 | West End |
| 02115 | Back Bay/Fenway |
| 02116 | Back Bay |
| 02118 | South End |
| 02119 | Roxbury |
| 02120 | Mission Hill |
| 02121-02125 | Dorchester |
| 02126 | Mattapan |
| 02127 | South Boston |
| 02128 | East Boston |
| 02129 | Charlestown |
| 02130 | Jamaica Plain |
| 02131 | Roslindale |
| 02132 | West Roxbury |
| 02134 | Allston |
| 02135 | Brighton |
| 02136 | Hyde Park |
| 02210 | Seaport |
| 02215 | Fenway |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RENDER (Paid Tier)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌─────────────────────────────┐  │
│  │   Cron Job       │         │   PostgreSQL Database       │  │
│  │   (Daily 6am)    │────────▶│   - permits table           │  │
│  │   sync_job.py    │         │   - sync_log table          │  │
│  └──────────────────┘         └──────────────┬──────────────┘  │
│                                              │                  │
│                                              │                  │
│  ┌───────────────────────────────────────────┴──────────────┐  │
│  │                    Web Service                            │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  FastAPI Backend                                     │ │  │
│  │  │  - /api/permits (list, filter, paginate)            │ │  │
│  │  │  - /api/permits/{id} (single permit)                │ │  │
│  │  │  - /api/stats (aggregations)                        │ │  │
│  │  │  - /api/neighborhoods (ZIP summaries)               │ │  │
│  │  │  - /api/sync-status (last sync info)                │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  Static Frontend (served by FastAPI)                 │ │  │
│  │  │  - index.html (dashboard)                           │ │  │
│  │  │  - Leaflet.js for maps                              │ │  │
│  │  │  - Chart.js for visualizations (optional)           │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Analyze Boston    │
                    │   CKAN API          │
                    │   (data source)     │
                    └─────────────────────┘
```

---

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend | Python + FastAPI | Lightweight, async, automatic OpenAPI docs |
| Database | PostgreSQL (Render) | Shared between web + cron, reliable |
| ORM | Raw SQL via psycopg2 | Simple project, no need for SQLAlchemy overhead |
| Frontend | Vanilla JS + HTML | No build step, easy to iterate |
| Maps | Leaflet.js + MarkerCluster | Free, lightweight, handles thousands of points |
| Hosting | Render (paid tier) | Already familiar, supports cron jobs natively |

---

## Project Structure

```
boston-development-tracker/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, routes
│   ├── database.py          # DB connection, schema, queries
│   ├── sync_job.py          # Cron job script
│   └── config.py            # Environment config
├── frontend/
│   ├── index.html           # Main dashboard
│   └── css/
│       └── styles.css       # Custom styles (inline in HTML is fine too)
├── docs/
│   ├── PLAN.md              # This file
│   └── API.md               # API documentation
├── .env.example             # Environment variables template
├── .gitignore
├── requirements.txt
├── render.yaml              # Render deployment config
└── README.md
```

---

## Implementation Phases

### Phase 1: Core Infrastructure
**Goal**: Working local prototype

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| 1.1 | Set up project structure and files | 10 min |
| 1.2 | Create database schema (PostgreSQL-compatible) | 15 min |
| 1.3 | Build sync job to fetch from CKAN API | 30 min |
| 1.4 | Build FastAPI backend with endpoints | 30 min |
| 1.5 | Create frontend with map view | 45 min |
| 1.6 | Test end-to-end locally | 15 min |

**Deliverable**: Run locally, see permits on a map

### Phase 2: Deployment
**Goal**: Live on Render with daily updates

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| 2.1 | Create GitHub repository | 5 min |
| 2.2 | Create Render PostgreSQL database | 5 min |
| 2.3 | Deploy web service | 10 min |
| 2.4 | Configure and deploy cron job | 10 min |
| 2.5 | Run initial data sync | 5 min |
| 2.6 | Verify everything works | 10 min |

**Deliverable**: Public URL with auto-updating data

### Phase 3: Enhancements (Future)
- Neighborhood-level statistics cards
- Time-series charts
- Mobile-optimized layout
- "What's new this week" email digest

### Phase 4: Restaurant Inspections (Future)
- Integrate Food Establishment Inspections dataset
- Restaurant search feature

---

## Database Schema

### permits table

```sql
CREATE TABLE IF NOT EXISTS permits (
    id SERIAL PRIMARY KEY,
    permit_number VARCHAR(20) UNIQUE NOT NULL,
    work_type VARCHAR(20),
    permit_type_descr VARCHAR(100),
    description TEXT,
    comments TEXT,
    applicant VARCHAR(200),
    declared_valuation DECIMAL(12,2),
    total_fees DECIMAL(10,2),
    issued_date TIMESTAMP,
    expiration_date TIMESTAMP,
    status VARCHAR(20),
    occupancy_type VARCHAR(50),
    sq_feet INTEGER,
    address VARCHAR(200),
    zip VARCHAR(10),
    ward INTEGER,
    property_id BIGINT,
    parcel_id BIGINT,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_permits_zip ON permits(zip);
CREATE INDEX IF NOT EXISTS idx_permits_issued ON permits(issued_date DESC);
CREATE INDEX IF NOT EXISTS idx_permits_work_type ON permits(work_type);
CREATE INDEX IF NOT EXISTS idx_permits_status ON permits(status);
```

### sync_log table

```sql
CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT
);
```

---

## API Endpoints

### GET /api/permits

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| zip | string | null | Filter by ZIP code |
| work_type | string | null | Filter by work type code |
| days | int | 30 | Look back N days |
| limit | int | 100 | Results per page (max 500) |
| offset | int | 0 | Pagination offset |

**Response:**
```json
{
  "total": 1234,
  "permits": [
    {
      "permit_number": "B1234567",
      "address": "123 Main St",
      "zip": "02127",
      "work_type": "ELECTRICAL",
      "work_type_label": "Electrical",
      "declared_valuation": 15000,
      "issued_date": "2025-01-15T10:30:00",
      "latitude": 42.338,
      "longitude": -71.045
    }
  ]
}
```

### GET /api/stats

**Query Parameters:**
| Param | Type | Default |
|-------|------|---------|
| days | int | 30 |

**Response:**
```json
{
  "period_days": 30,
  "total_permits": 1500,
  "total_valuation": 45000000,
  "by_type": [...],
  "by_zip": [...],
  "by_day": [...]
}
```

### GET /api/neighborhoods
List all ZIP codes with permit counts.

### GET /api/work-types
List all work type codes with labels.

### GET /api/health
Health check endpoint for monitoring sync status and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "last_sync": {
    "timestamp": "2025-02-03T11:00:00Z",
    "status": "success",
    "records_synced": 150
  },
  "hours_since_sync": 5.2,
  "warning": null
}
```

Returns `"status": "degraded"` with `"warning"` message if:
- Last sync was >36 hours ago
- Last sync failed
- Database connection issues

### GET /api/sync-status
Get last sync timestamp and status.

---

## Render Configuration

### render.yaml

```yaml
databases:
  - name: boston-dashboard-db
    plan: starter
    databaseName: boston_data
    user: dashboard_user

services:
  - type: web
    name: boston-data-dashboard
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    autoDeploy: true
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: boston-dashboard-db
          property: connectionString
      - key: PYTHON_VERSION
        value: "3.11"

  - type: cron
    name: boston-dashboard-sync
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m backend.sync_job
    schedule: "0 11 * * *"  # 6 AM EST (adjustable in Render dashboard)
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: boston-dashboard-db
          property: connectionString
      - key: SYNC_DAYS_BACK
        value: "90"
```

---

## Environment Variables

```bash
# Render provides this automatically for linked databases
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Sync configuration (adjustable without code changes)
SYNC_DAYS_BACK=90      # Initial load: 90 days, can increase later
SYNC_FULL_RELOAD=false # Set true to reload all historical data
```

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Sync job fetches permits and stores in database
- [ ] API endpoints return filtered data correctly
- [ ] Map displays permit markers with clustering
- [ ] Filter dropdowns work (ZIP, work type, days)

### Phase 2 Complete When:
- [ ] Public URL accessible
- [ ] Cron job runs daily without intervention
- [ ] Data stays fresh for 1 week unattended

---

## Implementation Summary (February 2026)

### ✅ Phase 1: Complete
- [x] Sync job fetches permits and stores in database
- [x] API endpoints return filtered data correctly
- [x] Map displays permit markers with clustering
- [x] Filter dropdowns work (ZIP, work type, days)

### ✅ Phase 2: Complete
- [x] Public URL accessible at Render
- [x] Cron job runs daily without intervention
- [x] Data stays fresh with automated syncs

### Enhancements Added Post-Launch

1. **Pagination Support** (Critical)
   - Initial implementation limited to 10,000 records
   - Added `fetch_all_permits_paginated()` with OFFSET/LIMIT support
   - Fetched complete 10-year dataset (442,874 records)

2. **Enhanced Popups**
   - Expanded from 5 fields to all available permit data
   - Added scrollable container for long content
   - Improved readability with structured layout

3. **ZIP Code Zoom**
   - Map automatically zooms to selected ZIP code area
   - Added 30 ZIP code center points and zoom levels
   - Resets to city view when filter is cleared

4. **Extended Time Periods**
   - Added 3, 5, and 10-year options to match data availability
   - Default changed from 30 days to 90 days
   - Users can now explore full decade of historical data

### Final Dataset Metrics

- **Total Records**: 442,874 permits
- **Date Range**: February 6, 2016 to February 3, 2026 (10 years)
- **Database Size**: ~200 MB (data) + ~50 MB (indexes)
- **Backfill Duration**: ~5 minutes for full historical load
- **Daily Sync**: ~10 seconds for 90-day overlap

### Production URLs

- **Dashboard**: https://boston-data-dashboard-web.onrender.com
- **API Health**: https://boston-data-dashboard-web.onrender.com/api/health
- **GitHub Repo**: https://github.com/AdamLozo/boston-data-dashboard

---

## Documentation for Future Dashboards

This project serves as a template for building additional Analyze Boston dashboards. See:

- **LESSONS_LEARNED.md** - Issues encountered and solutions implemented
- **DASHBOARD_TEMPLATE.md** - Step-by-step guide for new datasets (4-6 hours)
- **QUICK_START.md** - Reference card for experienced developers (~4 hours)

### Recommended Next Datasets

1. **Restaurant Inspections** - High public interest, daily updates
2. **311 Service Requests** - Large volume, tracks city responsiveness
3. **Property Violations** - Landlord accountability, neighborhood trends
4. **Traffic Signals** - Static infrastructure mapping

Each new dashboard reuses 80% of code and gets faster to build with experience.
