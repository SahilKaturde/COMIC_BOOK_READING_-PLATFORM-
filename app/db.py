# app/db.py
import psycopg
from psycopg.rows import dict_row

def get_db():
    return psycopg.connect(
        "dbname=Comic_Book_Reading_Platform_db user=postgres password=sahil@1234 host=localhost port=5432",
        row_factory=dict_row
    )

# 👇 ADD THIS TEST BLOCK
if __name__ == "__main__":
    try:
        conn = get_db()
        print("✅ Database connected successfully!")

        conn.close()
    except Exception as e:
        print("❌ Connection failed:", e)