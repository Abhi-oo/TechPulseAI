from typing import Optional
import psycopg2
from supabase import create_client, Client
from config import settings

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Returns initialized Supabase Client if credentials are provided."""
    global _supabase_client
    if _supabase_client is None:
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client


def get_db_connection():
    """Returns a direct psycopg2 PostgreSQL connection using DATABASE_URL."""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured.")
    return psycopg2.connect(settings.DATABASE_URL)


def test_connection() -> dict:
    """Tests the PostgreSQL connection using DATABASE_URL."""
    if not settings.DATABASE_URL:
        return {"success": False, "error_category": "ConfigurationError", "message": "DATABASE_URL is not set"}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"success": True, "error_category": None}
    except psycopg2.OperationalError as e:
        return {"success": False, "error_category": "OperationalError (Connection/Auth/Network)"}
    except Exception as e:
        return {"success": False, "error_category": type(e).__name__}
