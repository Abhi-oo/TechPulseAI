import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from config import settings
from database import test_connection

def verify_all():
    root_dir = backend_dir.parent
    root_env = root_dir / ".env"
    
    env_exists = root_env.exists()
    
    # Check key presence in root .env without exposing values
    has_db_url_env = False
    has_sub_url_env = False
    has_sub_key_env = False
    
    if env_exists:
        with open(root_env, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if "=" in line:
                    k = line.split("=", 1)[0].strip()
                    if k == "DATABASE_URL":
                        has_db_url_env = True
                    elif k == "SUPABASE_URL":
                        has_sub_url_env = True
                    elif k == "SUPABASE_KEY":
                        has_sub_key_env = True
                        
    # Check if loaded by FastAPI config
    loaded_db = bool(settings.DATABASE_URL)
    loaded_sub_url = bool(settings.SUPABASE_URL)
    loaded_sub_key = bool(settings.SUPABASE_KEY)
    
    print(f"ROOT_ENV_EXISTS: {env_exists}")
    print(f"ENV_HAS_DATABASE_URL: {has_db_url_env}")
    print(f"ENV_HAS_SUPABASE_URL: {has_sub_url_env}")
    print(f"ENV_HAS_SUPABASE_KEY: {has_sub_key_env}")
    print(f"CONFIG_LOADED_DATABASE_URL: {loaded_db}")
    print(f"CONFIG_LOADED_SUPABASE_URL: {loaded_sub_url}")
    print(f"CONFIG_LOADED_SUPABASE_KEY: {loaded_sub_key}")
    
    # Test connection
    result = test_connection()
    print(f"CONNECTION_SUCCESS: {result['success']}")
    if not result['success']:
        print(f"ERROR_CATEGORY: {result.get('error_category')}")

if __name__ == "__main__":
    verify_all()
