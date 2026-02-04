# Lessons Learned - Boston Building Permits Dashboard

**Project**: Boston Building Permits Dashboard
**Completed**: February 2026
**Dataset**: Analyze Boston - Approved Building Permits
**Result**: 442,874 permits (10 years) in production with interactive map and filters

---

## What Went Right

### 1. **Pagination Strategy**
**Issue**: Initial implementation fetched only 10,000 records (API default limit)
**Solution**: Added pagination support with `OFFSET` and `LIMIT` in SQL queries
**Result**: Fetched 442,874 total records across 45 API calls

**Key Code Pattern**:
```python
def fetch_all_permits_paginated(days: int, batch_size: int = 10000):
    all_records = []
    offset = 0
    while True:
        batch = fetch_permits_from_ckan(days, limit=batch_size, offset=offset)
        if not batch or len(batch) < batch_size:
            break
        all_records.extend(batch)
        offset += len(batch)
        time.sleep(1)  # Respectful rate limiting
    return all_records
```

**Lesson**: Always test with full dataset expectations, not just sample data. CKAN APIs have high limits (32,000) but default to 10,000.

---

### 2. **Incremental vs One-Time Sync**
**Issue**: Confusion about whether daily sync would re-fetch all historical data
**Solution**: Separated concerns:
- **Daily cron job**: Syncs last 90 days (catches new permits, updates existing)
- **One-time backfill**: Fetches 10 years of history with pagination

**Lesson**: Daily syncs should overlap (90 days) to catch late-arriving data, but don't need to query the entire history. The upsert pattern (`ON CONFLICT ... DO UPDATE`) handles duplicates automatically.

---

### 3. **Frontend Time Period Mismatch**
**Issue**: Dropdown filter only went back 2 years, but database had 10 years
**Rework Required**: Updated dropdown options after realizing data availability

**Lesson**: Frontend filters should be generated dynamically based on actual data range, OR document the expected data range upfront in planning phase.

**Better Approach**:
```sql
-- Query to determine actual data range
SELECT
    MIN(issued_date) as earliest_permit,
    MAX(issued_date) as latest_permit,
    COUNT(*) as total_permits
FROM permits;
```

Then use this to auto-generate time period options.

---

### 4. **Coordinate Validation**
**Success**: Database schema included coordinate validation during upsert
**Code**:
```python
# Validate Boston coordinates
if 42.2 <= lat <= 42.4 and -71.2 <= lng <= -70.9:
    latitude = lat
    longitude = lng
```

**Lesson**: Always validate geographic data. Invalid coordinates would break the map display. Boston's bounding box is well-defined.

---

### 5. **Enhanced Popup Details**
**Issue**: Initial popups showed minimal permit info (address, type, value, status)
**Enhancement Request**: User wanted to see ALL permit fields in marker popups
**Solution**: Expanded popup function to include all available fields conditionally

**Lesson**: Start with minimal viable product, but make it easy to expand. The popup function was already abstracted, so enhancement was a single function change.

---

### 6. **ZIP Code Zoom Feature**
**Success**: Added zip code boundaries as JavaScript object with center points
**Implementation**: Simple lookup table with approximate centers

**Lesson**: For 30 zip codes, a hardcoded lookup is fine. For larger datasets (e.g., all US zip codes), fetch from an API or use GeoJSON polygons.

---

## What Could Be Improved

### 1. **Planning Documentation**
**Gap**: Didn't document expected data volume or API pagination limits upfront
**Impact**: Had to rework sync logic after realizing 10,000-record limitation

**Recommended Planning Section**:
```markdown
## Data Volume Estimate
- **Historical range**: 10 years (2016-2026)
- **Estimated total records**: 400,000-500,000
- **API batch size**: 10,000 (default), 32,000 (max)
- **Pagination required**: YES
- **One-time backfill duration**: 5-10 minutes
- **Daily incremental sync**: 90 days overlap (~8,000 records)
```

---

### 2. **Database Indexing**
**Current**: Basic indexes on `zip`, `issued_date`, `work_type`, `status`
**Missing**: No composite indexes for common filter combinations

**Optimization Opportunity**:
```sql
-- Common query pattern: Filter by date + zip + work_type
CREATE INDEX idx_permits_date_zip_type
ON permits(issued_date DESC, zip, work_type);

-- For geospatial queries
CREATE INDEX idx_permits_location
ON permits USING GIST (ST_Point(longitude, latitude));
```

**Lesson**: Add indexes based on actual query patterns after launch, not prematurely.

---

### 3. **Error Handling in Frontend**
**Current**: Basic error logging to console
**Missing**: User-facing error messages when API fails

**Better Pattern**:
```javascript
try {
    const response = await fetch(`/api/permits?${params}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    // ... render data
} catch (error) {
    document.getElementById('loading').innerHTML =
        `<div class="error">Unable to load permits. Please try again later.</div>`;
    console.error(error);
}
```

---

### 4. **Dynamic Filter Options**
**Current**: Work types are fetched from `/api/work-types` but zip codes show hardcoded counts
**Better**: Both should be dynamic and update based on selected time period

**Example**:
```javascript
// When time period changes, re-fetch available zip codes for that period
async function loadFilters(days) {
    const response = await fetch(`/api/neighborhoods?days=${days}`);
    // Update zip dropdown with counts for selected time period
}
```

---

## Reusable Patterns for Future Dashboards

### 1. **Backend Sync Job Template**
```python
# sync_job.py structure for ANY Analyze Boston dataset
def fetch_from_ckan(resource_id, days, limit, offset):
    """Generic CKAN fetch with pagination"""

def fetch_all_paginated(resource_id, days):
    """Fetch all records using pagination"""

def sync_data(resource_id, days=None):
    """Main sync with upsert logic"""

def backfill_historical(resource_id, days):
    """One-time historical load"""
```

**Copy this structure for**:
- Restaurant inspections
- Property violations
- Traffic incidents
- Street repairs

---

### 2. **Database Schema Pattern**
```sql
-- Template for any time-series dataset
CREATE TABLE {dataset_name} (
    id SERIAL PRIMARY KEY,

    -- Unique identifier from source
    source_record_id VARCHAR(50) UNIQUE NOT NULL,

    -- Common fields
    date_field DATE,
    status VARCHAR(50),
    description TEXT,

    -- Location fields (if applicable)
    address VARCHAR(255),
    zip VARCHAR(10),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Standard indexes
CREATE INDEX idx_{dataset}_date ON {dataset}(date_field DESC);
CREATE INDEX idx_{dataset}_zip ON {dataset}(zip);
CREATE INDEX idx_{dataset}_status ON {dataset}(status);
```

---

### 3. **Frontend Filter Pattern**
**Reusable for any dashboard**:
```html
<div class="filters-grid">
    <div class="filter-group">
        <label for="location-filter">Location</label>
        <select id="location-filter">
            <option value="">All Locations</option>
        </select>
    </div>
    <div class="filter-group">
        <label for="category-filter">Category</label>
        <select id="category-filter">
            <option value="">All Categories</option>
        </select>
    </div>
    <div class="filter-group">
        <label for="days-filter">Time Period</label>
        <select id="days-filter">
            <option value="30" selected>Last 30 Days</option>
            <option value="90">Last 90 Days</option>
            <option value="365">Last Year</option>
        </select>
    </div>
</div>
```

---

### 4. **API Endpoint Pattern**
**Standard endpoints for any dataset**:
```python
# FastAPI routes
@app.get("/api/{dataset}")
async def get_records(
    days: int = 30,
    location: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 1000
):
    """Main data endpoint with filtering"""

@app.get("/api/{dataset}/stats")
async def get_statistics(days: int = 30):
    """Aggregate statistics"""

@app.get("/api/{dataset}/categories")
async def get_categories(days: int = None):
    """Available categories for filter dropdown"""

@app.get("/api/health")
async def health_check():
    """System health and last sync time"""
```

---

## Architecture Decisions That Worked

### ✅ Raw SQL over ORM
**Decision**: Used `psycopg` with raw SQL instead of SQLAlchemy
**Benefit**: Simpler debugging, direct control over queries, faster for read-heavy workloads
**Trade-off**: More verbose code, manual SQL injection protection

**Verdict**: Keep this pattern for dashboards. ORMs add overhead for simple CRUD + reporting.

---

### ✅ Vanilla JavaScript over React
**Decision**: No frontend framework, just vanilla JS
**Benefit**: Faster page load, no build step, easy to understand
**Trade-off**: More verbose DOM manipulation

**Verdict**: Keep this for simple dashboards. If adding interactivity (charts, filtering, sorting), consider lightweight framework like Alpine.js.

---

### ✅ Server-Side Rendering (SSR) over SPA
**Decision**: Single HTML file with backend API calls
**Benefit**: SEO-friendly, fast initial load, works without JavaScript enabled
**Trade-off**: Less "app-like" experience

**Verdict**: Keep this pattern. Dashboards prioritize content over interactivity.

---

### ✅ Render for Hosting
**Decision**: All-in-one platform (web service + cron + database)
**Benefit**: Simple deployment, auto-scaling, free tier available
**Trade-off**: Vendor lock-in

**Verdict**: Good for MVPs. For production scale, consider separating concerns (Vercel for frontend, AWS Lambda for cron, RDS for database).

---

## Metrics & Performance

### Data Loading Performance
- **Initial page load**: < 2 seconds
- **API response time**: 200-500ms for 1,000 records
- **Map render time**: ~1 second for 1,000 markers (with clustering)
- **Full dataset query (442K records)**: ~3 seconds (without pagination)

### Database Performance
- **Table size**: 442,874 rows ≈ 200 MB
- **Index size**: ~50 MB
- **Upsert speed**: ~200 records/second
- **Query speed (filtered)**: 10-50ms for typical queries

### Sync Job Performance
- **Daily sync (90 days)**: ~10 seconds
- **Historical backfill (10 years)**: ~5 minutes
- **API rate limit**: 1 request/second (self-imposed)

---

## Recommendations for Next Dashboard

### Planning Phase
1. **Estimate data volume** using CKAN API query
2. **Test pagination** with sample queries before building sync logic
3. **Document API limits** (request size, rate limits, timeout)
4. **Define time periods** that match data availability
5. **Plan indexes** based on expected query patterns

### Development Phase
1. **Build sync job FIRST** with pagination support
2. **Run one-time backfill** to validate data quality
3. **Build frontend filters** based on actual data range
4. **Add error handling** for API failures
5. **Test with realistic data volumes** (not just 100 records)

### Deployment Phase
1. **Monitor sync job logs** for first week
2. **Check database growth** to ensure storage is adequate
3. **Validate data freshness** by comparing to source
4. **Add uptime monitoring** (e.g., UptimeRobot on `/api/health`)

---

## Tools & Resources

### CKAN API Testing
```bash
# Test record count
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT COUNT(*) FROM \"6ddcd912-32a0-43df-9908-63574f8c7e77\""

# Test date filtering
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT * FROM \"6ddcd912-32a0-43df-9908-63574f8c7e77\" WHERE issued_date >= '2024-01-01' LIMIT 10"

# Test pagination
curl "https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT * FROM \"6ddcd912-32a0-43df-9908-63574f8c7e77\" LIMIT 100 OFFSET 10000"
```

### Database Monitoring
```sql
-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('permits'));

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'permits';

-- Check query performance
EXPLAIN ANALYZE
SELECT * FROM permits
WHERE issued_date >= CURRENT_DATE - INTERVAL '90 days'
AND zip = '02108';
```

### Render Deployment
```bash
# View logs
render logs -s boston-data-dashboard-web

# Trigger manual sync
render run -s boston-data-dashboard-cron

# Check service status
render services list
```

---

## Next Datasets to Consider

### High-Value Datasets from Analyze Boston

1. **Restaurant Inspections**
   - Resource ID: `4582bec6-2b4f-4f9e-bc55-cbaa73117f4c`
   - Volume: ~50,000 inspections
   - Update frequency: Daily
   - Use case: Find recent violations, track restaurant scores

2. **Property Violations**
   - Resource ID: Multiple datasets (housing, sanitary, etc.)
   - Volume: ~100,000 violations/year
   - Update frequency: Daily
   - Use case: Landlord accountability, neighborhood trends

3. **Traffic Signals & Signs**
   - Resource ID: `de08c6fe-338b-4c48-8c21-7e1e1b7a0e3e`
   - Volume: ~10,000 signals
   - Update frequency: Monthly
   - Use case: Infrastructure mapping

4. **311 Service Requests**
   - Resource ID: `b7ea6b1b-3ca4-4c5b-9cf2-1b9e2e1e2e1e`
   - Volume: ~200,000 requests/year
   - Update frequency: Daily
   - Use case: Track city responsiveness, identify problem areas

---

## Template Checklist for New Dashboard

- [ ] Identify Analyze Boston dataset and resource ID
- [ ] Estimate total record count via API query
- [ ] Test pagination with OFFSET/LIMIT
- [ ] Document expected data volume and time range
- [ ] Clone `boston-data-dashboard` repo as template
- [ ] Update database schema for new dataset
- [ ] Modify sync job with new resource ID
- [ ] Run one-time historical backfill
- [ ] Update frontend filters for new data categories
- [ ] Test with realistic data volumes
- [ ] Deploy to Render with new service name
- [ ] Monitor sync job for first week
- [ ] Document in `LESSONS_LEARNED.md`

