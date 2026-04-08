# app/queries/admin_queries.py

def get_admin_stats(conn):
    """Fetch total numbers for readers, publishers, and comics."""
    stats = {}
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as result FROM reader")
        stats['total_readers'] = cur.fetchone()['result']

        cur.execute("SELECT COUNT(*) as result FROM publisher")
        stats['total_publishers'] = cur.fetchone()['result']

        cur.execute("SELECT COUNT(*) as result FROM comic")
        stats['total_comics'] = cur.fetchone()['result']

    return stats


def get_all_comics_admin(conn):
    """Fetch all comics for admin view."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.title, c.description, c.genre, c.status::TEXT as status, 
                   c.created_at, p.name AS publisher_name
            FROM comic c
            JOIN publisher p ON c.publisher_id = p.id
            ORDER BY c.created_at DESC;
        """)
        return cur.fetchall()


def get_all_publishers(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, email, created_at 
            FROM publisher 
            ORDER BY created_at DESC;
        """)
        return cur.fetchall()


def get_all_readers(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, email, created_at 
            FROM reader 
            ORDER BY created_at DESC;
        """)
        return cur.fetchall()
