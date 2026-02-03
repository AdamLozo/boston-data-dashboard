"""
Boston Data Dashboard - Configuration
Environment variable management for database and sync settings
"""

import os
from pathlib import Path

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip loading .env
    pass


class Settings:
    """Application settings from environment variables"""

    # Database connection
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/boston_permits"
    )

    # Sync job configuration
    SYNC_DAYS_BACK: int = int(os.getenv("SYNC_DAYS_BACK", "90"))

    # CKAN API configuration
    CKAN_RESOURCE_ID: str = "6ddcd912-32a0-43df-9908-63574f8c7e77"
    CKAN_SQL_API_URL: str = "https://data.boston.gov/api/3/action/datastore_search_sql"

    # Server configuration
    PORT: int = int(os.getenv("PORT", "8000"))

    @property
    def is_production(self) -> bool:
        """Check if running in production (Render)"""
        return "render.com" in self.DATABASE_URL.lower()


settings = Settings()
