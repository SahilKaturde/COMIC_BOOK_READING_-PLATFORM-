# app/queries/chapter_queries.py


def create_chapter(conn, comic_id, chapter_number, title=None):
    """Insert a new chapter for a comic."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO chapter (comic_id, chapter_number, title)
            VALUES (%s, %s, %s)
            RETURNING id, comic_id, chapter_number, title;
        """, (comic_id, chapter_number, title))
        return cur.fetchone()


def get_chapters_for_comic(conn, comic_id):
    """List all chapters for a comic, ordered by chapter_number."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, comic_id, chapter_number, title, published_at
            FROM chapter
            WHERE comic_id = %s
            ORDER BY chapter_number ASC;
        """, (comic_id,))
        return cur.fetchall()


def get_chapter(conn, chapter_id):
    """Fetch a single chapter by ID."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, comic_id, chapter_number, title
            FROM chapter
            WHERE id = %s;
        """, (chapter_id,))
        return cur.fetchone()


def get_chapter_by_number(conn, comic_id, chapter_number):
    """Fetch a chapter by comic_id and chapter_number."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, comic_id, chapter_number, title
            FROM chapter
            WHERE comic_id = %s AND chapter_number = %s;
        """, (comic_id, chapter_number))
        return cur.fetchone()


def delete_chapter(conn, chapter_id):
    """Delete a chapter and its cascaded pages."""
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM chapter WHERE id = %s RETURNING id, comic_id, chapter_number;
        """, (chapter_id,))
        return cur.fetchone()


# --- Page queries ---

def create_page(conn, chapter_id, page_number, image_url):
    """Insert a page record."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO page (chapter_id, page_number, image_url)
            VALUES (%s, %s, %s)
            RETURNING id, chapter_id, page_number, image_url;
        """, (chapter_id, page_number, image_url))
        return cur.fetchone()


def get_pages_for_chapter(conn, chapter_id):
    """List all pages for a chapter, ordered by page_number."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, chapter_id, page_number, image_url
            FROM page
            WHERE chapter_id = %s
            ORDER BY page_number ASC;
        """, (chapter_id,))
        return cur.fetchall()


def get_next_page_number(conn, chapter_id):
    """Get the next available page number for a chapter."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(MAX(page_number), 0) + 1
            FROM page
            WHERE chapter_id = %s;
        """, (chapter_id,))
        row = cur.fetchone()
        # dict_row returns a dict, so get the value
        return list(row.values())[0] if row else 1
