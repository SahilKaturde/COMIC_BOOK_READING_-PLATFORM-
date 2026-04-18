import os
import sys
import time

#run.py

# Add the parent directory of "app" to sys.path so we can import "app" as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import create_app
from app.db import get_db

from dotenv import load_dotenv, find_dotenv

def print_banner():
    banner = """
    ==================================================
       COMIC BOOK READING PLATFORM - DEV SERVER
    ==================================================
    """
    print(banner)

def check_dependencies():
    print("Checking dependencies...")
    try:
        import flask
        import PIL
        import psycopg
        import dotenv
        print("[OK] Dependencies verified.")
    except ImportError as e:
        print(f"[FAIL] Missing dependency: {e.name}")
        print("Please run: pip install -r requirements.txt (or use uv sync)")
        sys.exit(1)

def check_db():
    print("Checking database connection...")
    try:
        conn = get_db()
        conn.close()
        print("[OK] Database connected successfully.")
    except Exception as e:
        print(f"[WARN] Database connection failed: {e}")
        print("Make sure PostgreSQL is running and the database exists.")

def seed_admin():
    print("Ensuring default admin exists...")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "adminpass")
    
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Check if an admin exists
            cur.execute("SELECT id FROM admin LIMIT 1;")
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO admin (name, email, password)
                    VALUES ('Admin User', %s, %s);
                """, (admin_email, admin_password))
                print(f"[INFO] Default admin created: {admin_email}")
            else:
                # Ensure the default one is updated/exists
                cur.execute("""
                    UPDATE admin 
                    SET email = %s, password = %s
                    WHERE email = %s OR id = (SELECT id FROM admin LIMIT 1);
                """, (admin_email, admin_password, admin_email))
                print("[OK] Admin account verified.")
            conn.commit()
    except Exception as e:
        print(f"[ERR] Failed to seed admin: {e}")
    finally:
        if conn:
            conn.close()

def main():
    load_dotenv(find_dotenv())
    print_banner()
    check_dependencies()
    check_db()
    seed_admin()
    
    print("\nStarting Flask application...")
    app = create_app()
    
    # Run the application
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()
