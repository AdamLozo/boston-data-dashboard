# Data Pipeline Context

## What This Section Covers
CKAN API integration, sync job implementation, data validation and transformation.

## Quick Facts
- **Source**: Analyze Boston Open Data Portal
- **API**: CKAN datastore_search_sql endpoint
- **Resource ID**: 6ddcd912-32a0-43df-9908-63574f8c7e77
- **Update Frequency**: Daily at 6 AM EST
- **Initial Load**: 90 days of permits

---

## CKAN API Reference

### Endpoint
```
https://data.boston.gov/api/3/action/datastore_search_sql
```

### SQL Query Pattern
```python
resource_id = "6ddcd912-32a0-43df-9908-63574f8c7e77"
sql = f'''
SELECT * FROM "{resource_id}" 
WHERE issued_date >= '{start_date}'
ORDER BY issued_date DESC
LIMIT 10000
'''

response = requests.get(
    "https://data.boston.gov/api/3/action/datastore_search_sql",
    params={"sql": sql}
)
data = response.json()
records = data["result"]["records"]
```

### Important: API Quirks
1. **Date format**: YYYY-MM-DD in SQL queries
2. **Limit**: Max 32,000 records per query (paginate if needed)
3. **Rate limiting**: Be respectful, add delays between large fetches
4. **Field names**: Lowercase, some have underscores

### Available Fields
```
permitnumber, worktype, permittypedescr, description, comments,
applicant, declared_valuation, total_fees, issued_date, 
expiration_date, status, occupancytype, sq_feet, address, 
city, state, zip, ward, property_id, parcel_id, location,
lat, long, gpsy, gpsx
```

### Field Mapping (API → Database)
| API Field | DB Column | Transform |
|-----------|-----------|-----------|
| permitnumber | permit_number | None |
| worktype | work_type | None |
| permittypedescr | permit_type_descr | None |
| declared_valuation | declared_valuation | Parse to decimal |
| issued_date | issued_date | Parse YYYY-MM-DD |
| lat | latitude | Parse to decimal |
| long | longitude | Parse to decimal |
| occupancytype | occupancy_type | None |
| sq_feet | sq_feet | Parse to int |

---

## Sync Job Logic

### sync_job.py Pseudocode
```python
def sync():
    # 1. Log start
    sync_id = create_sync_log_entry()
    
    # 2. Calculate date range
    start_date = today - SYNC_DAYS_BACK
    
    # 3. Fetch from CKAN
    records = fetch_permits(start_date)
    
    # 4. Upsert to database
    for record in records:
        upsert_permit(transform(record))
    
    # 5. Log completion
    update_sync_log(sync_id, success=True, count=len(records))
```

### Upsert Strategy
```sql
INSERT INTO permits (permit_number, work_type, ...)
VALUES (%s, %s, ...)
ON CONFLICT (permit_number) DO UPDATE SET
    work_type = EXCLUDED.work_type,
    status = EXCLUDED.status,
    updated_at = CURRENT_TIMESTAMP
```

---

## Data Validation Rules

1. **permit_number**: Required, non-empty
2. **issued_date**: Must be valid date or NULL
3. **latitude/longitude**: Must be valid Boston coordinates or NULL
   - Lat: 42.2 to 42.4
   - Long: -71.2 to -70.9
4. **declared_valuation**: Must be positive number or NULL
5. **zip**: Must be Boston ZIP (02108-02215) or NULL

### Handling Bad Data
```python
def validate_coordinates(lat, lng):
    if lat is None or lng is None:
        return None, None
    if not (42.2 <= float(lat) <= 42.4):
        return None, None
    if not (-71.2 <= float(lng) <= -70.9):
        return None, None
    return float(lat), float(lng)
```

---

## Error Handling

### Transient Errors (Retry)
- Network timeout
- 5xx from CKAN API
- Database connection lost

### Permanent Errors (Log and Skip)
- Invalid record data
- Duplicate permit (handled by upsert)

### Fatal Errors (Stop and Alert)
- CKAN API returns error response
- Database schema mismatch
- Authentication failure

---

## Files in This Section
- `ckan-api.md` - Full API documentation with examples
- `sync-job.md` - Implementation details and edge cases
- `data-validation.md` - Validation rules and transformations

---

## Related Sections
- **01-infrastructure**: Database schema that receives the data
- **05-monitoring**: Health checks that verify sync is working
