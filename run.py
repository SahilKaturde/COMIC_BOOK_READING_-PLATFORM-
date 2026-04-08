import os
import sys
import time

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
        print("✅ Dependencies verified.")
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("Please run: pip install -r requirements.txt (or use uv sync)")
        sys.exit(1)

def check_db():
    print("Checking database connection...")
    try:
        from app.db import get_db
        conn = get_db()
        conn.close()
        print("✅ Database connected successfully.")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("Make sure PostgreSQL is running and the database exists.")

if __name__ == "__main__":
    print_banner()
    check_dependencies()
    check_db()
    
    print("\nStarting Flask application...")
    from app import create_app
    app = create_app()
    
    # Run the application
    app.run(debug=True, port=5000)
