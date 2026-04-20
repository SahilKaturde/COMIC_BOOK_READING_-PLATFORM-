# app/init_db.py

import os
import sys

# Ensure the project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.db import get_db

def init_db():
    print("Initializing database...")
    
    # Path to the SQL schema file
    schema_path = os.path.join(PROJECT_ROOT, "docs", "comic_platform_database.sql")
    
    if not os.path.exists(schema_path):
        print(f"Error: Schema file not found at {schema_path}")
        return

    with open(schema_path, "r") as f:
        sql = f.read()

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Execute the multi-statement SQL
            cur.execute(sql)
        conn.commit()
        print("[OK] Database initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
