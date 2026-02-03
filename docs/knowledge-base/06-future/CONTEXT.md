# Future Expansions Context

## What This Section Covers
Planned features and additional datasets for future phases.

---

## Dataset: Restaurant Inspections

### Source
Analyze Boston - Food Establishment Inspections

### Resource ID
TBD - Research needed

### Why This Dataset
- Highly relevant to neighbors
- Updates frequently
- Natural fit with existing architecture
- Location-based like permits

### Schema Additions
```sql
CREATE TABLE inspections (
    id SERIAL PRIMARY KEY,
    inspection_id VARCHAR(50) UNIQUE NOT NULL,
    business_name VARCHAR(255),
    dba_name VARCHAR(255),
    license_no VARCHAR(50),
    facility_id VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(10),
    zip VARCHAR(10),
    property_id VARCHAR(50),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    inspection_date DATE,
    result VARCHAR(50),
    result_comments TEXT,
    violation_level VARCHAR(20),
    violation_desc TEXT,
    violation_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Additions
```
GET /api/inspections
GET /api/inspections/{inspection_id}
GET /api/restaurants/{license_no}/history
```

---

## Feature: Time Series Charts

### Library Options
1. **Chart.js** - Simple, lightweight
2. **Plotly.js** - Interactive, more features
3. **D3.js** - Maximum flexibility (overkill for this)

Recommendation: **Chart.js** for simplicity

### Planned Charts
1. Permits per day (line chart)
2. Permits by type (pie/donut chart)
3. Valuation over time (bar chart)

---

## Feature: Neighborhood Deep Dive

### Concept
Click a neighborhood to see:
- Recent permits
- Most common work types
- Average valuation
- Trend vs city average

### Implementation
- New endpoint: GET /api/neighborhoods/{zip}/details
- Dedicated page or modal

---

## Feature: Email Notifications

### Concept
Subscribe to updates for:
- Specific ZIP code
- Specific address
- High-value permits (>$X)

### Complexity
- Requires email service integration
- User authentication or simple email verification
- Background job for sending

Recommendation: Phase 2+ feature

---

## Feature: Historical Analysis

### Concept
- Show permits over longer time ranges
- Year-over-year comparisons
- Identify trends

### Data Needs
- Extend initial load beyond 90 days
- Add database indexes for historical queries

---

## Other Analyze Boston Datasets

Potential future additions:
1. **Code Violations** - Housing code enforcement
2. **311 Requests** - Service requests by neighborhood
3. **Property Assessment** - Tax valuations
4. **Crime Reports** - Safety data (sensitive)

---

## Files in This Section
- `restaurant-inspections.md` - Dataset research and implementation plan
- `expansion-datasets.md` - Other datasets to consider
