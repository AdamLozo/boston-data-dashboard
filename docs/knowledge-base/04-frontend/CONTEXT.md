# Frontend Context

## What This Section Covers
Leaflet.js map implementation, responsive design, vanilla JS patterns for the dashboard.

## Quick Facts
- **Framework**: None (vanilla JS)
- **Map Library**: Leaflet.js with MarkerCluster
- **Styling**: CSS (mobile-first)
- **Build**: None needed (static files)

---

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ Boston Building Permits              [Last sync: 2h ago]│
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ ZIP Filter  │ │ Type Filter │ │ Date Range         │ │
│ │ [dropdown]  │ │ [dropdown]  │ │ [Last 30 days ▼]   │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                                                         │
│                    [ MAP ]                              │
│                                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Showing 150 permits │ Total value: $5.2M               │
└─────────────────────────────────────────────────────────┘
```

### Mobile Layout
- Filters stack vertically
- Map takes full width
- Stats bar scrolls with page

---

## Leaflet.js Setup

### CDN Links
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
```

### Map Initialization
```javascript
// Boston center coordinates
const BOSTON_CENTER = [42.3601, -71.0589];
const DEFAULT_ZOOM = 12;

const map = L.map('map').setView(BOSTON_CENTER, DEFAULT_ZOOM);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

const markers = L.markerClusterGroup();
map.addLayer(markers);
```

### Adding Permits to Map
```javascript
function addPermitsToMap(permits) {
    markers.clearLayers();
    
    permits.forEach(permit => {
        if (permit.latitude && permit.longitude) {
            const marker = L.marker([permit.latitude, permit.longitude]);
            marker.bindPopup(createPopupContent(permit));
            markers.addLayer(marker);
        }
    });
}

function createPopupContent(permit) {
    return `
        <div class="permit-popup">
            <strong>${permit.address}</strong><br>
            ${permit.work_type} - ${permit.permit_number}<br>
            Issued: ${formatDate(permit.issued_date)}<br>
            Value: ${formatCurrency(permit.declared_valuation)}
        </div>
    `;
}
```

---

## API Integration

### Fetching Permits
```javascript
async function fetchPermits() {
    const params = new URLSearchParams({
        zip: getSelectedZip(),
        work_type: getSelectedWorkType(),
        days: getSelectedDays(),
        limit: 1000
    });
    
    // Remove empty params
    for (const [key, value] of params.entries()) {
        if (!value) params.delete(key);
    }
    
    const response = await fetch(`/api/permits?${params}`);
    const data = await response.json();
    
    addPermitsToMap(data.data);
    updateStats(data);
}
```

### Error Handling
```javascript
async function fetchWithError(url) {
    try {
        showLoading();
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        showError(`Failed to load data: ${error.message}`);
        throw error;
    } finally {
        hideLoading();
    }
}
```

---

## Responsive Design

### Breakpoints
```css
/* Mobile first */
.filters {
    flex-direction: column;
    gap: 0.5rem;
}

/* Tablet and up */
@media (min-width: 768px) {
    .filters {
        flex-direction: row;
        gap: 1rem;
    }
}
```

### Map Container
```css
#map {
    width: 100%;
    height: 50vh;
    min-height: 300px;
}

@media (min-width: 768px) {
    #map {
        height: 60vh;
    }
}
```

---

## Work Type Labels
```javascript
const WORK_TYPE_LABELS = {
    'ELECTRICAL': 'Electrical Work',
    'PLUMBING': 'Plumbing',
    'GAS': 'Gas Work',
    'INTREN': 'Interior Renovation',
    'EXTREN': 'Exterior Renovation',
    'SOL': 'Solar Installation',
    'OCCPCY': 'Occupancy Permit',
    'ERECT': 'New Construction',
    'DEMO': 'Demolition',
    'ROOF': 'Roofing'
};
```

## ZIP to Neighborhood Mapping
```javascript
const ZIP_NEIGHBORHOODS = {
    '02108': 'Beacon Hill',
    '02109': 'Downtown/North End',
    '02110': 'Financial District',
    '02111': 'Chinatown',
    '02113': 'North End',
    '02114': 'West End',
    '02115': 'Fenway/Longwood',
    '02116': 'Back Bay',
    '02118': 'South End',
    '02119': 'Roxbury',
    '02120': 'Mission Hill',
    '02121': 'Dorchester',
    '02122': 'Dorchester',
    '02124': 'Dorchester',
    '02125': 'Dorchester',
    '02126': 'Mattapan',
    '02127': 'South Boston',
    '02128': 'East Boston',
    '02129': 'Charlestown',
    '02130': 'Jamaica Plain',
    '02131': 'Roslindale',
    '02132': 'West Roxbury',
    '02134': 'Allston',
    '02135': 'Brighton',
    '02136': 'Hyde Park',
    '02215': 'Fenway'
};
```

---

## Files in This Section
- `leaflet-maps.md` - Detailed Leaflet.js patterns
- `responsive-design.md` - CSS patterns and breakpoints
- `component-patterns.md` - Reusable JS patterns

---

## Related Sections
- **03-backend**: APIs that power the frontend
- **05-monitoring**: User-facing health indicators
