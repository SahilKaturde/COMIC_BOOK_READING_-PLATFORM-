# app/queries/comic_queries.py


def get_all_published_comics(conn):
    """Fetch all comics with status='published' for reader home."""
    with conn.cursor() as cur:
        # Cast status to TEXT for robust comparison with Python strings
        cur.execute("""
            SELECT c.id, c.title, c.description, c.genre, c.poster_url,
                   c.status::TEXT as status, c.created_at, p.name AS publisher_name
            FROM comic c
            JOIN publisher p ON c.publisher_id = p.id
            WHERE c.status::TEXT = 'published'
            ORDER BY c.created_at DESC;
        """)
        return cur.fetchall()


def get_publisher_comics(conn, publisher_id):
    """Fetch all comics belonging to a specific publisher."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, description, genre, poster_url,
                   status::TEXT as status, created_at
            FROM comic
            WHERE publisher_id = %s
            ORDER BY created_at DESC;
        """, (publisher_id,))
        return cur.fetchall()


def create_comic(conn, publisher_id, title, description, genre, poster_url=None):
    """Insert a new comic for a publisher."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO comic (publisher_id, title, description, genre, poster_url, status)
            VALUES (%s, %s, %s, %s, %s, 'draft'::comic_status)
            RETURNING id, title, description, genre, poster_url, status::TEXT as status;
        """, (publisher_id, title, description, genre, poster_url))
        return cur.fetchone()


def update_comic(conn, comic_id, title, description, genre, poster_url=None, status=None):
    """Update an existing comic. (Ownership check removed as requested)"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE comic
            SET title = %s, description = %s, genre = %s, poster_url = %s,
                status = COALESCE(%s::comic_status, status)
            WHERE id = %s
            RETURNING id, title, description, genre, poster_url, status::TEXT as status;
        """, (title, description, genre, poster_url, status, comic_id))
        return cur.fetchone()


def delete_comic(conn, comic_id):
    """Delete a comic. (Ownership check removed as requested)"""
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM comic
            WHERE id = %s
            RETURNING id;
        """, (comic_id,))
        return cur.fetchone() is not None


def get_comic_by_id(conn, comic_id):
    """Fetch a single comic by its ID."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, publisher_id, title, description, genre, poster_url, 
                   status::TEXT as status, created_at
            FROM comic
            WHERE id = %s;
        """, (comic_id,))
        return cur.fetchone()
