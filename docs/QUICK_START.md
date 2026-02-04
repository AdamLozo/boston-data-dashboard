# Quick Start: New Analyze Boston Dashboard

**Time estimate**: 4-6 hours | **Based on**: Building Permits Dashboard template

---

## Pre-Flight Checklist (5 minutes)

```bash
# 1. Find dataset at https://data.boston.gov/dataset
# 2. Get resource ID from API endpoint
# 3. Test record count:

curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT COUNT(*) FROM \"[RESOURCE_ID]\""

# If > 100,000 records, plan for pagination
# If < 10,000 records, simple sync is fine
```

---

## Step 1: Clone & Configure (15 min)

```bash
# Clone template
git clone https://github.com/AdamLozo/boston-data-dashboard.git boston-[NAME]-dashboard
cd boston-[NAME]-dashboard

# Update config
# Edit: backend/config.py → CKAN_RESOURCE_ID
# Edit: render.yaml → service names
# Edit: README.md → title, description, dataset URL
```

---

## Step 2: Database Schema (30 min)

**File**: `backend/database.py`

1. Map API fields to database columns
2. Update `CREATE TABLE` statement
3. Update `upsert_record()` function with field mappings
4. Test locally:

```bash
python -m backend.database  # Initialize schema
```

---

## Step 3: Sync Job (30 min)

**File**: `backend/sync_job.py`

1. Update date field name in SQL query
2. Update upsert function call
3. Test locally:

```bash
python -m backend.sync_job 7  # Sync last 7 days
psql $DATABASE_URL -c "SELECT COUNT(*) FROM [table];"
```

---

## Step 4: Historical Backfill (5-10 min)

```bash
# Run once to load historical data
python backfill_historical.py

# This fetches all available records with pagination
# Monitor progress in console logs
```

---

## Step 5: API Endpoints (20 min)

**File**: `backend/main.py`

1. Rename `/api/permits` → `/api/[dataset]`
2. Update table name in SQL queries
3. Update filter parameters (zip, category, etc.)
4. Test locally:

```bash
uvicorn backend.main:app --reload

# Open http://localhost:8000/docs for API explorer
```

---

## Step 6: Frontend (60 min)

**File**: `frontend/index.html`

1. **Update HTML** (10 min):
   - Page title
   - Header text
   - Filter labels
   - Stat labels

2. **Update JavaScript** (30 min):
   - API endpoint URLs
   - Field names in popup()
   - Filter loading logic
   - Stat calculations

3. **Test locally** (20 min):
   - Open in browser
   - Test all filters
   - Check map markers
   - Verify mobile view

---

## Step 7: Deploy to Render (30 min)

### Create Services

1. **Database**: `boston-[name]-db` (Free tier)
2. **Web Service**: `boston-[name]-web`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Env: `DATABASE_URL` (link to database)
3. **Cron Job**: `boston-[name]-cron`
   - Schedule: `0 11 * * *` (6 AM EST)
   - Command: `python -m backend.sync_job`
   - Env: `DATABASE_URL` (link to database)

### Deploy

```bash
git add .
git commit -m "Initial deployment"
git push

# Render auto-deploys on push to main branch
```

### Run Backfill on Production

```bash
# Via Render Shell (Web Service → Shell tab)
python backfill_historical.py
```

---

## Step 8: Verify & Monitor (15 min)

### Functional Tests
- [ ] Homepage loads
- [ ] Map shows markers
- [ ] Filters work
- [ ] Stats update
- [ ] Mobile responsive

### Data Quality
```sql
-- Check record count
SELECT COUNT(*) FROM [table];

-- Check date range
SELECT MIN(date_field), MAX(date_field) FROM [table];

-- Check coordinates
SELECT COUNT(*) FILTER (WHERE latitude IS NOT NULL) FROM [table];
```

### Set Up Monitoring
- Add UptimeRobot monitor for `/api/health`
- Check Render logs daily for first week
- Verify cron job runs successfully

---

## Common Gotchas

### ❌ Map markers not showing
**Fix**: Check coordinate validation range (42.2-42.4, -71.2 to -70.9 for Boston)

### ❌ Sync runs but no new records
**Fix**: Verify date field name in SQL query matches API response

### ❌ "Loading..." never finishes
**Fix**: Check browser console for API errors, verify backend is running

### ❌ Stats show "$NaN" or "0"
**Fix**: Update stat calculation field names to match database schema

### ❌ Filters populate but don't filter data
**Fix**: Verify filter parameter names match backend API expectations

---

## Files to Modify (Summary)

| File | What to Change |
|------|----------------|
| `backend/config.py` | Resource ID, sync settings |
| `backend/database.py` | Table schema, field mappings, upsert logic |
| `backend/sync_job.py` | Date field name, function names (optional) |
| `backend/main.py` | API endpoint paths, table names, filter fields |
| `frontend/index.html` | Title, labels, field names, API URLs |
| `render.yaml` | Service names, database name |
| `README.md` | Title, description, dataset URL |

---

## Time Breakdown

- **Planning & Research**: 30 min
- **Clone & Configure**: 15 min
- **Database Schema**: 30 min
- **Sync Job**: 30 min
- **Historical Backfill**: 10 min
- **API Endpoints**: 20 min
- **Frontend**: 60 min
- **Deployment**: 30 min
- **Testing & Monitoring**: 15 min

**Total**: ~4 hours for experienced developer, 6 hours for first time

---

## Need Help?

- **Full guide**: See `docs/DASHBOARD_TEMPLATE.md`
- **Lessons learned**: See `docs/LESSONS_LEARNED.md`
- **Original plan**: See `docs/PLAN.md`

---

## Next Dashboard Ideas

1. **Restaurant Inspections** (~5 hours)
2. **311 Service Requests** (~8 hours, large volume)
3. **Property Violations** (~6 hours)
4. **Traffic Signals** (~3 hours, static data)

Each new dashboard gets faster as you learn the pattern!
