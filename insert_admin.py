from app.db import get_db

conn = get_db()
try:
    with conn.cursor() as cur:
        # Check if an admin exists
        cur.execute("SELECT id FROM admin LIMIT 1;")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO admin (name, email, password)
                VALUES ('Admin User', 'admin@example.com', 'adminpass');
            """)
            print("Admin inserted!")
        else:
            cur.execute("""
                UPDATE admin 
                SET email = 'admin@example.com', password = 'adminpass'
                WHERE email = 'admin@example.com' OR id = (SELECT id FROM admin LIMIT 1);
            """)
            print("Admin updated/exists! email: admin@example.com, pass: adminpass")
        conn.commit()
finally:
    conn.close()
