"""
Boston Data Dashboard - Database Operations
PostgreSQL connection and schema management with raw SQL (no ORM)
"""

import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, List
import logging

from .config import settings

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Returns connection with dict row factory for dict-like row access.
    """
    conn = None
    try:
        conn = psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Initialize database schema - creates tables and indexes if they don't exist"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create permits table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS permits (
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
                )
            """)

            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_permits_zip ON permits(zip)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_permits_issued_date ON permits(issued_date DESC)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_permits_work_type ON permits(work_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_permits_status ON permits(status)")

            # Create sync_log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sync_log (
                    id SERIAL PRIMARY KEY,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status VARCHAR(20),
                    records_fetched INTEGER,
                    records_inserted INTEGER,
                    records_updated INTEGER,
                    error_message TEXT
                )
            """)

            conn.commit()
            logger.info("Database schema initialized successfully")


def upsert_permit(conn, record: Dict) -> tuple[bool, str]:
    """
    Insert or update a permit record.
    Returns (was_inserted, permit_number)
    """
    with conn.cursor() as cur:
        # Parse declared_valuation - handle string format from API
        valuation = None
        if record.get('declared_valuation'):
            try:
                val_str = str(record['declared_valuation']).replace('$', '').replace(',', '')
                valuation = float(val_str) if val_str else None
            except (ValueError, AttributeError):
                valuation = None

        # Parse total_fees
        fees = None
        if record.get('total_fees'):
            try:
                fee_str = str(record['total_fees']).replace('$', '').replace(',', '')
                fees = float(fee_str) if fee_str else None
            except (ValueError, AttributeError):
                fees = None

        # Parse sq_feet
        sq_feet = None
        if record.get('sq_feet'):
            try:
                sq_feet = int(float(record['sq_feet']))
            except (ValueError, TypeError):
                sq_feet = None

        # Parse coordinates - use API field names (y_latitude, x_longitude)
        latitude = None
        longitude = None
        if record.get('y_latitude') and record.get('x_longitude'):
            try:
                lat = float(record['y_latitude'])
                lng = float(record['x_longitude'])
                # Validate Boston coordinates
                if 42.2 <= lat <= 42.4 and -71.2 <= lng <= -70.9:
                    latitude = lat
                    longitude = lng
            except (ValueError, TypeError):
                pass

        cur.execute("""
            INSERT INTO permits (
                permit_number, work_type, permit_type_descr, description, comments,
                applicant, declared_valuation, total_fees, issued_date, expiration_date,
                status, occupancy_type, sq_feet, address, zip,
                ward, property_id, parcel_id, latitude, longitude, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (permit_number) DO UPDATE SET
                work_type = EXCLUDED.work_type,
                permit_type_descr = EXCLUDED.permit_type_descr,
                description = EXCLUDED.description,
                comments = EXCLUDED.comments,
                applicant = EXCLUDED.applicant,
                declared_valuation = EXCLUDED.declared_valuation,
                total_fees = EXCLUDED.total_fees,
                issued_date = EXCLUDED.issued_date,
                expiration_date = EXCLUDED.expiration_date,
                status = EXCLUDED.status,
                occupancy_type = EXCLUDED.occupancy_type,
                sq_feet = EXCLUDED.sq_feet,
                address = EXCLUDED.address,
                zip = EXCLUDED.zip,
                ward = EXCLUDED.ward,
                property_id = EXCLUDED.property_id,
                parcel_id = EXCLUDED.parcel_id,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                updated_at = CURRENT_TIMESTAMP
            RETURNING (xmax = 0) AS inserted
        """, (
            record.get('permitnumber'),
            record.get('worktype'),
            record.get('permittypedescr'),
            record.get('description'),
            record.get('comments'),
            record.get('applicant'),
            valuation,
            fees,
            record.get('issued_date'),
            record.get('expiration_date'),
            record.get('status'),
            record.get('occupancytype'),
            sq_feet,
            record.get('address'),
            record.get('zip'),
            record.get('ward'),
            record.get('property_id'),
            record.get('parcel_id'),
            latitude,
            longitude,
            datetime.now()
        ))

        result = cur.fetchone()
        if result:
            was_inserted = result['inserted'] if isinstance(result, dict) else result[0]
        else:
            was_inserted = False
        return was_inserted, record.get('permitnumber')


def create_sync_log(conn) -> int:
    """Create a new sync log entry and return its ID"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO sync_log (started_at, status)
            VALUES (CURRENT_TIMESTAMP, 'running')
            RETURNING id
        """)
        result = cur.fetchone()
        sync_id = result['id'] if isinstance(result, dict) else result[0]
        conn.commit()
        return sync_id


def update_sync_log(
    conn,
    sync_id: int,
    records_fetched: int,
    records_inserted: int,
    records_updated: int,
    status: str,
    error_message: Optional[str] = None
):
    """Update sync log with completion details"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE sync_log
            SET completed_at = CURRENT_TIMESTAMP,
                status = %s,
                records_fetched = %s,
                records_inserted = %s,
                records_updated = %s,
                error_message = %s
            WHERE id = %s
        """, (status, records_fetched, records_inserted, records_updated, error_message, sync_id))
        conn.commit()


def get_last_sync(conn) -> Optional[Dict]:
    """Get the most recent sync log entry"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM sync_log
            ORDER BY started_at DESC
            LIMIT 1
        """)
        return cur.fetchone()


def get_permits(
    conn,
    zip_code: Optional[str] = None,
    work_type: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    offset: int = 0
) -> tuple[List[Dict], int]:
    """
    Get permits with filters and pagination.
    Returns (permits_list, total_count)
    """
    with conn.cursor() as cur:
        # Build WHERE clause
        conditions = ["issued_date >= CURRENT_DATE - INTERVAL '%s days'"]
        params = [days]

        if zip_code:
            conditions.append("zip = %s")
            params.append(zip_code)

        if work_type:
            conditions.append("work_type = %s")
            params.append(work_type)

        where_clause = " AND ".join(conditions)

        # Get total count
        cur.execute(f"SELECT COUNT(*) FROM permits WHERE {where_clause}", params)
        total = cur.fetchone()['count']

        # Get records
        query = f"""
            SELECT * FROM permits
            WHERE {where_clause}
            ORDER BY issued_date DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(query, params + [limit, offset])
        permits = cur.fetchall()

        return permits, total


if __name__ == "__main__":
    # Initialize database when run directly
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialized successfully")
