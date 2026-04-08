# app/queries/auth_queries.py

VALID_TABLES = ["admin", "publisher", "reader"]


def create_user(conn, table, name, email, password, logo_url=None):
    if table not in VALID_TABLES:
        raise ValueError("Invalid role")

    with conn.cursor() as cur:
        if table == "publisher":
            cur.execute(
                f"""
                INSERT INTO {table} (name, email, password, logo_url)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, email, logo_url;
                """,
                (name, email, password, logo_url)
            )
        else:
            cur.execute(
                f"""
                INSERT INTO {table} (name, email, password)
                VALUES (%s, %s, %s)
                RETURNING id, name, email;
                """,
                (name, email, password)
            )
        return cur.fetchone()


def get_user(conn, table, email, password):
    if table not in VALID_TABLES:
        raise ValueError("Invalid role")

    with conn.cursor() as cur:
        if table == "publisher":
            cur.execute(
                f"""
                SELECT id, name, email, logo_url
                FROM {table}
                WHERE email = %s AND password = %s;
                """,
                (email, password)
            )
        else:
            cur.execute(
                f"""
                SELECT id, name, email
                FROM {table}
                WHERE email = %s AND password = %s;
                """,
                (email, password)
            )
        return cur.fetchone()


def get_publisher_by_id(conn, publisher_id):
    """Retrieve full publisher details, including logo_url."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, name, email, logo_url
            FROM publisher
            WHERE id = %s;
            """,
            (publisher_id,)
        )
        return cur.fetchone()