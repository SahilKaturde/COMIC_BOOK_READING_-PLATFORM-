# app/routes/admin_routes.py

from flask import Blueprint, request, render_template, redirect, session
from functools import wraps

from app.db import get_db
from app.queries.admin_queries import get_admin_stats, get_all_comics_admin, get_all_publishers, get_all_readers
from app.queries.comic_queries import delete_comic
from app.utils.upload_utils import delete_folder

admin_bp = Blueprint("admin", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("user_role") != role:
                return redirect("/login")
            return f(*args, **kwargs)

        return decorated

    return decorator


@admin_bp.route("/admin_home", methods=["GET"])
@login_required
@role_required("admin")
def admin_home():
    conn = get_db()
    try:
        stats = get_admin_stats(conn)
        comics = get_all_comics_admin(conn)
        publishers = get_all_publishers(conn)
        readers = get_all_readers(conn)

        return render_template(
            "admin_home.html",
            user_name=session.get("user_name", "Admin"),
            stats=stats,
            comics=comics,
            publishers=publishers,
            readers=readers
        )
    finally:
        conn.close()


@admin_bp.route("/admin/delete_comic/<int:comic_id>", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_comic(comic_id):
    conn = get_db()
    try:
        delete_comic(conn, comic_id)
        conn.commit()
        # Remove the entire comic folder from Data/
        delete_folder("comics", str(comic_id))
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    return redirect("/admin_home")
