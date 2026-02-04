# Analyze Boston Dashboard Template

**Purpose**: Step-by-step guide for creating new dashboards from Analyze Boston datasets
**Based on**: Boston Building Permits Dashboard (Feb 2026)
**Estimated time**: 4-6 hours for complete implementation

---

## Phase 1: Dataset Research (30 minutes)

### 1.1 Find Your Dataset
Browse **Analyze Boston**: https://data.boston.gov/dataset

Look for datasets with:
- ✅ Regular updates (daily/weekly)
- ✅ Geographic data (address, coordinates, or zip code)
- ✅ Time series data (date field for filtering)
- ✅ Public interest (permits, violations, inspections)

### 1.2 Extract Key Information

Create a planning document with:

```markdown
## Dataset Information

**Name**: [Dataset Name]
**URL**: https://data.boston.gov/dataset/[dataset-slug]
**Resource ID**: [Copy from API endpoint or page source]
**Update Frequency**: [Daily/Weekly/Monthly]
**License**: [Usually Open Data Commons PDDL]

## Data Volume Estimate

Run this query to check record count:
```bash
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT COUNT(*) FROM \"[RESOURCE_ID]\""
```

**Total Records**: [Number]
**Date Range**: [Earliest to Latest]
**Expected Daily Growth**: [Records per day]

## Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| [unique_id] | text | Primary key |
| [date_field] | timestamp | For time filtering |
| [category_field] | text | For category filtering |
| [location_field] | text | For location filtering |
| [value_field] | numeric | For statistics |
| latitude | numeric | For mapping |
| longitude | numeric | For mapping |

## Work Type/Category Codes

[Document all category values and their meanings]
```

### 1.3 Test API Queries

Validate the API works as expected:

```bash
# Test basic query
curl "https://data.boston.gov/api/3/action/datastore_search?resource_id=[RESOURCE_ID]&limit=5"

# Test date filtering
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT * FROM \"[RESOURCE_ID]\" WHERE [date_field] >= '2024-01-01' LIMIT 10"

# Test pagination
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT * FROM \"[RESOURCE_ID]\" LIMIT 100 OFFSET 10000"

# Test coordinate availability
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT COUNT(*) FROM \"[RESOURCE_ID]\" WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
```

**Decision Point**: If < 50% of records have coordinates, consider alternative visualization (list view, table, charts instead of map).

---

## Phase 2: Repository Setup (30 minutes)

### 2.1 Clone Template Repository

```bash
# Clone the building permits repo as a template
git clone https://github.com/AdamLozo/boston-data-dashboard.git boston-[dataset-name]-dashboard
cd boston-[dataset-name]-dashboard

# Update remote
git remote set-url origin https://github.com/AdamLozo/boston-[dataset-name]-dashboard.git

# Clean up
rm -rf .git
git init
git add .
git commit -m "Initial commit from template"
```

### 2.2 Update Configuration Files

**File: `backend/config.py`**
```python
# Update resource ID
CKAN_RESOURCE_ID = "[YOUR_RESOURCE_ID]"

# Update sync settings if needed
SYNC_DAYS_BACK = 90  # Adjust based on data volatility
```

**File: `render.yaml`**
```yaml
services:
  - type: web
    name: boston-[dataset-name]-web
    # ... update all service names

  - type: cron
    name: boston-[dataset-name]-cron
    # ... update all service names

databases:
  - name: boston-[dataset-name]-db
    # ... update database name
```

**File: `README.md`**
- Update title and description
- Update screenshot (placeholder initially)
- Update dataset URL and resource ID
- Update feature list based on new dataset

---

## Phase 3: Database Schema (45 minutes)

### 3.1 Design Schema

**File: `backend/database.py`**

Map your dataset fields to database columns:

```python
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS [dataset_table] (
                    id SERIAL PRIMARY KEY,

                    -- Unique identifier from API
                    source_record_id VARCHAR(100) UNIQUE NOT NULL,

                    -- Core fields (customize based on your dataset)
                    date_field DATE,
                    category_field VARCHAR(100),
                    status_field VARCHAR(50),
                    description TEXT,
                    value_field DECIMAL(15,2),

                    -- Location fields
                    address VARCHAR(255),
                    zip VARCHAR(10),
                    ward VARCHAR(10),
                    latitude DECIMAL(10,7),
                    longitude DECIMAL(10,7),

                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_[table]_date ON [dataset_table](date_field DESC)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_[table]_zip ON [dataset_table](zip)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_[table]_category ON [dataset_table](category_field)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_[table]_status ON [dataset_table](status_field)")

            conn.commit()
```

### 3.2 Update Upsert Logic

Map API field names to database columns:

```python
def upsert_record(conn, record: Dict) -> tuple[bool, str]:
    """
    Insert or update a record.
    Returns (was_inserted, record_id)
    """
    with conn.cursor() as cur:
        # Parse/validate fields
        date_value = record.get('date_field')  # API field name
        category_value = record.get('category')
        # ... parse other fields

        # Validate coordinates if present
        latitude = None
        longitude = None
        if record.get('latitude') and record.get('longitude'):
            try:
                lat = float(record['latitude'])
                lng = float(record['longitude'])
                # Boston bounding box
                if 42.2 <= lat <= 42.4 and -71.2 <= lng <= -70.9:
                    latitude = lat
                    longitude = lng
            except (ValueError, TypeError):
                pass

        cur.execute("""
            INSERT INTO [dataset_table] (
                source_record_id, date_field, category_field,
                status_field, description, address, zip,
                latitude, longitude, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (source_record_id) DO UPDATE SET
                date_field = EXCLUDED.date_field,
                category_field = EXCLUDED.category_field,
                status_field = EXCLUDED.status_field,
                description = EXCLUDED.description,
                address = EXCLUDED.address,
                zip = EXCLUDED.zip,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                updated_at = CURRENT_TIMESTAMP
            RETURNING (xmax = 0) AS inserted
        """, (
            record.get('unique_id'),
            date_value,
            category_value,
            # ... other values
        ))

        result = cur.fetchone()
        was_inserted = result['inserted'] if isinstance(result, dict) else result[0]
        return was_inserted, record.get('unique_id')
```

---

## Phase 4: Sync Job (45 minutes)

### 4.1 Update Sync Configuration

**File: `backend/sync_job.py`**

The sync job structure is already in place. You just need to update:

1. **Function names** (optional, for clarity):
   - `fetch_permits_from_ckan` → `fetch_[dataset]_from_ckan`
   - `sync_permits` → `sync_[dataset]`

2. **Date field name** in SQL query:
   ```python
   sql = f'''
       SELECT * FROM "{settings.CKAN_RESOURCE_ID}"
       WHERE "[your_date_field]" >= '{cutoff_date}'
       ORDER BY "[your_date_field]" DESC
       LIMIT {limit} OFFSET {offset}
   '''
   ```

3. **Upsert function call**:
   ```python
   was_inserted, record_id = upsert_record(conn, record)
   ```

### 4.2 Test Sync Locally

```bash
# Initialize database
python -m backend.database

# Run sync for last 30 days
python -m backend.sync_job 30

# Check results
psql $DATABASE_URL -c "SELECT COUNT(*) FROM [dataset_table];"
```

### 4.3 Create Backfill Script

Copy `backfill_historical.py` and update:

```python
# Change default days if needed
days = 3650  # 10 years

# Update function call
records = fetch_all_[dataset]_paginated(days=days, batch_size=10000)

# Update upsert call
was_inserted, record_id = upsert_record(conn, record)
```

Run backfill:
```bash
python backfill_historical.py
```

---

## Phase 5: Backend API (30 minutes)

### 5.1 Update API Endpoints

**File: `backend/main.py`**

The FastAPI endpoints are generic enough to work with any dataset. Just update:

1. **Table name** in SQL queries:
   ```python
   @app.get("/api/records")  # Rename from /api/permits
   async def get_records(...):
       # Update table name in query
       query = f"SELECT * FROM [dataset_table] WHERE ..."
   ```

2. **Filter parameters** based on your dataset:
   ```python
   async def get_records(
       days: int = 30,
       zip_code: Optional[str] = None,
       category: Optional[str] = None,  # Update field name
       limit: int = 1000,
       offset: int = 0
   ):
   ```

3. **Stats endpoint**:
   ```python
   @app.get("/api/stats")
   async def get_statistics(days: int = 30):
       # Update aggregation field
       cur.execute("""
           SELECT SUM(value_field) as total_value
           FROM [dataset_table]
           WHERE date_field >= CURRENT_DATE - INTERVAL '%s days'
       """, (days,))
   ```

4. **Filter endpoints**:
   ```python
   @app.get("/api/categories")  # Rename from /api/work-types
   async def get_categories(days: Optional[int] = None):
       # Update field names
       cur.execute("""
           SELECT
               category_field as code,
               category_label as label,
               COUNT(*) as count
           FROM [dataset_table]
           GROUP BY category_field, category_label
           ORDER BY count DESC
       """)
   ```

### 5.2 Test API Endpoints

```bash
# Start server
uvicorn backend.main:app --reload

# Test endpoints
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/records?days=30&limit=10"
curl http://localhost:8000/api/stats?days=30
curl http://localhost:8000/api/categories
curl http://localhost:8000/api/neighborhoods
```

---

## Phase 6: Frontend (90 minutes)

### 6.1 Update HTML Structure

**File: `frontend/index.html`**

1. **Page title and header**:
   ```html
   <title>Boston [Dataset Name] Dashboard</title>
   <h1>Boston [Dataset Name] Dashboard</h1>
   <div class="subtitle">[One-line description of the dashboard]</div>
   ```

2. **Filter dropdowns**:
   ```html
   <div class="filter-group">
       <label for="category-filter">[Category Label]</label>
       <select id="category-filter">
           <option value="">All [Categories]</option>
       </select>
   </div>
   ```

3. **Statistics bar**:
   ```html
   <div class="stat">
       <div class="stat-value" id="total-records">-</div>
       <div class="stat-label">Total [Records]</div>
   </div>
   <div class="stat">
       <div class="stat-value" id="total-value">-</div>
       <div class="stat-label">Total [Metric]</div>
   </div>
   ```

### 6.2 Update JavaScript

1. **API endpoint URLs**:
   ```javascript
   // Update all fetch() calls
   fetch(`/api/records?${params}`)  // Changed from /api/permits
   fetch(`/api/stats?days=${days}`)
   fetch(`/api/categories`)  // Changed from /api/work-types
   ```

2. **Popup content**:
   ```javascript
   function popup(record) {
       let html = `<div class="record-popup">`;
       html += `<strong>${record.address || 'No address'}</strong><br>`;
       html += `<strong>Category:</strong> ${record.category_label}<br>`;
       html += `<strong>Date:</strong> ${fmtDate(record.date_field)}<br>`;
       html += `<strong>Status:</strong> ${record.status_field}<br>`;
       // Add other relevant fields
       html += `</div>`;
       return html;
   }
   ```

3. **Data field names**:
   ```javascript
   // Update to match your database schema
   document.getElementById('total-records').textContent = data.total.toLocaleString();
   ```

### 6.3 Update Map Markers (if applicable)

If your dataset has different visualization needs:

```javascript
// Example: Color-code markers by category
function getMarkerColor(category) {
    const colors = {
        'CATEGORY_A': 'red',
        'CATEGORY_B': 'blue',
        'CATEGORY_C': 'green'
    };
    return colors[category] || 'gray';
}

// Use custom icons
const marker = L.marker([lat, lng], {
    icon: L.icon({
        iconUrl: `markers/${getMarkerColor(record.category)}.png`,
        iconSize: [25, 41]
    })
});
```

---

## Phase 7: Deployment (30 minutes)

### 7.1 Create Render Services

1. **Database**:
   - Name: `boston-[dataset]-db`
   - Plan: Free (or Starter if > 1GB)

2. **Web Service**:
   - Name: `boston-[dataset]-web`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `DATABASE_URL`: Link to database
     - `SYNC_DAYS_BACK`: `90`

3. **Cron Job**:
   - Name: `boston-[dataset]-cron`
   - Schedule: `0 11 * * *` (6 AM EST)
   - Command: `python -m backend.sync_job`
   - Environment Variables:
     - `DATABASE_URL`: Link to database
     - `SYNC_DAYS_BACK`: `90`

### 7.2 Initial Deployment

```bash
# Commit changes
git add .
git commit -m "Initial deployment for [dataset name]"
git push

# Render auto-deploys on push to main
# Monitor deployment at https://dashboard.render.com
```

### 7.3 Run Historical Backfill

Once web service is live:

```bash
# Option 1: Via Render Shell
# Go to Render dashboard → Web Service → Shell
python backfill_historical.py

# Option 2: Locally (if DATABASE_URL is set)
python backfill_historical.py
```

---

## Phase 8: Testing & Monitoring (30 minutes)

### 8.1 Functional Testing

- [ ] Homepage loads without errors
- [ ] Map displays markers correctly
- [ ] Filters work (zip, category, time period)
- [ ] Statistics update when filters change
- [ ] Marker popups show correct data
- [ ] Mobile view is responsive
- [ ] No console errors in browser

### 8.2 Data Quality Testing

Run SQL queries to validate:

```sql
-- Check for missing coordinates
SELECT COUNT(*) as missing_coords
FROM [dataset_table]
WHERE latitude IS NULL OR longitude IS NULL;

-- Check date range
SELECT
    MIN(date_field) as earliest,
    MAX(date_field) as latest,
    COUNT(*) as total_records
FROM [dataset_table];

-- Check for duplicates
SELECT source_record_id, COUNT(*)
FROM [dataset_table]
GROUP BY source_record_id
HAVING COUNT(*) > 1;

-- Check category distribution
SELECT category_field, COUNT(*) as count
FROM [dataset_table]
GROUP BY category_field
ORDER BY count DESC;
```

### 8.3 Performance Testing

- [ ] API response time < 500ms for 1,000 records
- [ ] Map renders in < 2 seconds
- [ ] Filter changes respond instantly
- [ ] No memory leaks (check DevTools Performance tab)

### 8.4 Set Up Monitoring

1. **Uptime Monitoring** (UptimeRobot):
   - Monitor: `https://boston-[dataset]-web.onrender.com/api/health`
   - Interval: 5 minutes
   - Alert: Email if down > 5 minutes

2. **Sync Job Monitoring**:
   - Check Render logs daily for first week
   - Verify `hours_since_sync` in `/api/health` endpoint
   - Set up alert if sync hasn't run in > 36 hours

---

## Checklist: Dashboard Complete

### Planning
- [ ] Dataset identified and resource ID extracted
- [ ] Data volume estimated via API query
- [ ] Key fields documented
- [ ] Category codes mapped
- [ ] API pagination tested

### Backend
- [ ] Database schema created
- [ ] Upsert logic implemented
- [ ] Sync job configured
- [ ] Historical backfill completed
- [ ] API endpoints tested locally

### Frontend
- [ ] HTML updated with new labels
- [ ] JavaScript updated for new fields
- [ ] Map markers display correctly
- [ ] Filters populate dynamically
- [ ] Mobile responsive

### Deployment
- [ ] Render services created
- [ ] Database connected
- [ ] Web service deployed
- [ ] Cron job scheduled
- [ ] Historical backfill run

### Testing
- [ ] Functional tests pass
- [ ] Data quality validated
- [ ] Performance acceptable
- [ ] Monitoring configured

### Documentation
- [ ] README updated
- [ ] LESSONS_LEARNED updated with new insights
- [ ] API endpoints documented
- [ ] Dataset information documented

---

## Common Issues & Solutions

### Issue: Map markers not appearing
**Causes**:
- Latitude/longitude are NULL in database
- Coordinate validation rejected valid coordinates
- API field names don't match database schema

**Debug**:
```sql
-- Check coordinate distribution
SELECT
    COUNT(*) FILTER (WHERE latitude IS NOT NULL) as with_coords,
    COUNT(*) as total
FROM [dataset_table];

-- Sample records with coordinates
SELECT * FROM [dataset_table]
WHERE latitude IS NOT NULL
LIMIT 10;
```

---

### Issue: Sync job runs but no new records
**Causes**:
- API date field name is wrong
- Upsert treats all records as duplicates
- API returns no new data

**Debug**:
```python
# Add logging to sync job
logger.info(f"Record sample: {records[0]}")  # Check field names
logger.info(f"Inserted: {inserted_count}, Updated: {updated_count}")
```

---

### Issue: Frontend shows "Loading..." forever
**Causes**:
- API endpoint returns 500 error
- CORS issue
- JavaScript error

**Debug**:
- Open browser DevTools → Console
- Check Network tab for failed requests
- Check Render logs for backend errors

---

## Next Steps

After launching your dashboard:

1. **Share with community** (Reddit r/boston, Hacker News, Twitter)
2. **Gather feedback** and prioritize features
3. **Add analytics** (if desired) to track usage
4. **Document in LESSONS_LEARNED.md** for next dashboard
5. **Plan next dataset** using this template

---

## Example Dashboards to Build Next

### Restaurant Inspections
- **Complexity**: Medium
- **Value**: High (public health)
- **Unique features**: Score trends, violation categories
- **Estimated time**: 5 hours

### 311 Service Requests
- **Complexity**: High (large volume)
- **Value**: Very high (city responsiveness)
- **Unique features**: Heat maps, response time tracking
- **Estimated time**: 8 hours

### Property Violations
- **Complexity**: Medium
- **Value**: High (landlord accountability)
- **Unique features**: Repeat offenders, violation types
- **Estimated time**: 6 hours

### Traffic Signals
- **Complexity**: Low (static data)
- **Value**: Medium (infrastructure mapping)
- **Unique features**: Signal type clustering
- **Estimated time**: 3 hours

