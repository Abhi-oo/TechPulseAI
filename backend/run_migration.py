import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load .env from backend/ or root
backend_dir = Path(__file__).resolve().parent
root_dir = backend_dir.parent

load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=root_dir / ".env")

REQUIRED_TABLES = [
    "sources",
    "stories",
    "submissions",
    "story_sources",
    "story_updates",
    "claims",
    "agent_runs",
]


def execute_migration():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("[ERROR] DATABASE_URL is not set in environment or .env file.")
        print("Please configure DATABASE_URL in your .env file:")
        print("Example: DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres")
        sys.exit(1)

    migration_file = backend_dir / "migrations" / "001_initial_schema.sql"
    if not migration_file.exists():
        print(f"[ERROR] Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"[1/3] Reading migration SQL from {migration_file.name}...")
    with open(migration_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("[2/3] Connecting to Supabase PostgreSQL database...")
    try:
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        print("Executing migration statements...")
        cur.execute(sql_content)
        print("[OK] Migration SQL executed successfully.")

        print("[3/3] Verifying created tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE';
        """)
        existing_tables = {row[0] for row in cur.fetchall()}

        missing_tables = []
        verified_tables = []
        for t in REQUIRED_TABLES:
            if t in existing_tables:
                cur.execute(f"""
                    SELECT count(*) 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = '{t}';
                """)
                col_count = cur.fetchone()[0]
                verified_tables.append((t, col_count))
            else:
                missing_tables.append(t)

        print("-" * 50)
        print("MIGRATION VERIFICATION REPORT")
        print("-" * 50)
        for tbl, cols in verified_tables:
            print(f"  [VERIFIED] Table: {tbl:<20} Columns: {cols}")

        if missing_tables:
            print(f"\n[FAILED] Missing tables: {missing_tables}")
            sys.exit(1)
        else:
            print(f"\n[SUCCESS] All {len(REQUIRED_TABLES)} required tables are present and verified in Supabase!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"[DATABASE ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    execute_migration()
