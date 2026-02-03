"""
Boston Building Permits Data Fetcher
Pulls data from Analyze Boston CKAN API
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# CKAN API configuration
BASE_URL = "https://data.boston.gov/api/3/action/datastore_search"
RESOURCE_ID = "6ddcd912-32a0-43df-9908-63574f8c7e77"  # Approved Building Permits

def fetch_permits(limit=100, offset=0):
    """Fetch permits from CKAN API"""
    params = {
        "resource_id": RESOURCE_ID,
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

def fetch_recent_permits(days=30):
    """Fetch permits from the last N days"""
    # CKAN datastore_search_sql allows date filtering
    sql_url = "https://data.boston.gov/api/3/action/datastore_search_sql"
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # SQL query to get recent permits
    sql = f'''
        SELECT * FROM "{RESOURCE_ID}" 
        WHERE "issued_date" >= '{cutoff_date}'
        ORDER BY "issued_date" DESC
        LIMIT 1000
    '''
    
    response = requests.get(sql_url, params={"sql": sql})
    response.raise_for_status()
    return response.json()

def explore_data_structure():
    """Fetch a small sample to understand the data structure"""
    print("Fetching sample data to explore structure...\n")
    
    result = fetch_permits(limit=5)
    
    if result.get("success"):
        records = result["result"]["records"]
        fields = result["result"]["fields"]
        total = result["result"].get("total", "unknown")
        
        print(f"Total records in dataset: {total}")
        print(f"\n{'='*60}")
        print("AVAILABLE FIELDS:")
        print('='*60)
        
        for field in fields:
            print(f"  {field['id']:30} ({field['type']})")
        
        print(f"\n{'='*60}")
        print("SAMPLE RECORD:")
        print('='*60)
        
        if records:
            for key, value in records[0].items():
                print(f"  {key:30}: {value}")
        
        return fields, records
    else:
        print(f"API Error: {result}")
        return None, None

def test_recent_permits():
    """Test fetching recent permits"""
    print("\n" + "="*60)
    print("TESTING RECENT PERMITS (last 30 days):")
    print("="*60)
    
    try:
        result = fetch_recent_permits(days=30)
        
        if result.get("success"):
            records = result["result"]["records"]
            print(f"Found {len(records)} permits in the last 30 days")
            
            if records:
                # Show permit type breakdown
                permit_types = {}
                neighborhoods = {}
                
                for record in records:
                    ptype = record.get("worktype", "Unknown")
                    permit_types[ptype] = permit_types.get(ptype, 0) + 1
                    
                    neighborhood = record.get("city", "Unknown")
                    neighborhoods[neighborhood] = neighborhoods.get(neighborhood, 0) + 1
                
                print("\nPermit types:")
                for ptype, count in sorted(permit_types.items(), key=lambda x: -x[1])[:10]:
                    print(f"  {ptype:40}: {count}")
                
                print("\nNeighborhoods/Areas:")
                for neighborhood, count in sorted(neighborhoods.items(), key=lambda x: -x[1])[:10]:
                    print(f"  {neighborhood:40}: {count}")
                    
            return records
        else:
            print(f"API Error: {result}")
            return None
            
    except Exception as e:
        print(f"Error fetching recent permits: {e}")
        return None

if __name__ == "__main__":
    # First, explore the data structure
    fields, sample = explore_data_structure()
    
    # Then test recent permits
    recent = test_recent_permits()
    
    print("\n" + "="*60)
    print("API VALIDATION COMPLETE")
    print("="*60)
