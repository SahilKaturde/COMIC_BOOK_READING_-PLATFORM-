# app/services/auth_service.py

from app.queries.auth_queries import create_user, get_user

VALID_ROLES = ["admin", "publisher", "reader"]


def register_user(conn, role, name, email, password, logo_url=None):
    if role not in VALID_ROLES:
        raise ValueError("Role must be admin / publisher / reader")

    return create_user(conn, role, name, email, password, logo_url)


def login_user(conn, role, email, password):
    if role not in VALID_ROLES:
        raise ValueError("Invalid role")

    user = get_user(conn, role, email, password)

    if not user:
        return None

    return user