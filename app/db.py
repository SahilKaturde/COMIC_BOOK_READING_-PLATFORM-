import os
from dotenv import load_dotenv, find_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables from .env file
load_dotenv(find_dotenv())

def get_db():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg.connect(db_url, row_factory=dict_row)
        
    return psycopg.connect(
        dbname=os.environ.get("DB_NAME", "Comic_Book_Reading_Platform_db"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        row_factory=dict_row
    )

# 👇 ADD THIS TEST BLOCK
if __name__ == "__main__":
    try:
        conn = get_db()
        print("[OK] Database connected successfully!")

        conn.close()
    except Exception as e:
        print("[ERROR] Connection failed:", e)