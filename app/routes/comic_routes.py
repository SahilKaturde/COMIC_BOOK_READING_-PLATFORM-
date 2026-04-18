# app/routes/comic_routes.py

from flask import Blueprint, request, render_template, redirect, session
from functools import wraps

from app.db import get_db
from app.queries.comic_queries import (
    get_all_published_comics,
    get_publisher_comics,
    create_comic,
    update_comic,
    delete_comic,
    get_comic_by_id,
)
from app.queries.chapter_queries import (
    create_chapter,
    get_chapters_for_comic,
    get_chapter,
    get_chapter_by_number,
    delete_chapter,
    create_page,
    get_pages_for_chapter,
    get_next_page_number,
)
from app.utils.upload_utils import (
    allowed_file,
    save_poster,
    save_page_image,
    delete_folder,
)

comic_bp = Blueprint("comic", __name__)


# --- Auth decorators ---

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


# ============================================
# READER ROUTES
# ============================================

@comic_bp.route("/reader_home")
@login_required
@role_required("reader")
def reader_home():
    conn = get_db()
    try:
        comics = get_all_published_comics(conn)
        return render_template(
            "reader_home.html",
            comics=comics,
            user_name=session.get("user_name", "Reader"),
        )
    finally:
        conn.close()


@comic_bp.route("/read/<int:comic_id>")
@login_required
@role_required("reader")
def read_comic_entry(comic_id):
    """Entry point for reading a comic. Finds the first available chapter."""
    conn = get_db()
    try:
        comic = get_comic_by_id(conn, comic_id)
        if not comic or comic["status"] != "published":
            return redirect("/reader_home")

        chapters = get_chapters_for_comic(conn, comic_id)
        if not chapters:
            return render_template(
                "reader_no_content.html",
                comic=comic,
                user_name=session.get("user_name", "Reader"),
            )

        # Redirect to the first available chapter
        first_chapter = chapters[0]
        return redirect(f"/read/{comic_id}/{first_chapter['chapter_number']}")
    finally:
        conn.close()

#3
@comic_bp.route("/read/<int:comic_id>/<int:chapter_number>")
@login_required
@role_required("reader")
def read_comic(comic_id, chapter_number):
    conn = get_db()
    try:
        comic = get_comic_by_id(conn, comic_id)
        if not comic or comic["status"] != "published":
            return redirect("/reader_home")

        chapter = get_chapter_by_number(conn, comic_id, chapter_number)
        if not chapter:
            # If a specific chapter is requested but missing, show the "No Content" page
            return render_template(
                "reader_no_content.html",
                comic=comic,
                user_name=session.get("user_name", "Reader"),
            )

        pages = get_pages_for_chapter(conn, chapter["id"])
        chapters = get_chapters_for_comic(conn, comic_id)

        return render_template(
            "reader_comic.html",
            comic=comic,
            chapter=chapter,
            pages=pages,
            chapters=chapters,
            user_name=session.get("user_name", "Reader"),
        )
    finally:
        conn.close()


# ============================================
# PUBLISHER ROUTES
# ============================================

@comic_bp.route("/publisher_home")
@login_required
@role_required("publisher")
def publisher_home():
    conn = get_db()
    try:
        comics = get_publisher_comics(conn, session["user_id"])
        return render_template(
            "publisher_home.html",
            comics=comics,
            user_name=session.get("user_name", "Publisher"),
            user_logo=session.get("user_logo", ""),
        )
    finally:
        conn.close()


#FOUR ___
# --- Create Comic (with poster upload) ---

@comic_bp.route("/publisher/create", methods=["POST"])
@login_required
@role_required("publisher")
def publisher_create_comic():
    data = request.form
    conn = get_db()
    try:
        # Create comic record first (poster_url blank)
        comic = create_comic(
            conn,
            session["user_id"],
            data["title"],
            data.get("description", ""),
            data.get("genre", ""),
            None,  # poster_url set after we have the ID
        )
        conn.commit()

        # Handle poster upload
        poster_file = request.files.get("poster")
        if poster_file and poster_file.filename and allowed_file(poster_file.filename):
            poster_path = save_poster(poster_file, comic["id"])
            update_comic(conn, comic["id"], data["title"], data.get("description", ""),
                         data.get("genre", ""), poster_path, None)
            conn.commit()

        return redirect("/publisher_home")
    except Exception as e:
        conn.rollback()
        return redirect("/publisher_home")
    finally:
        conn.close()


# --- Edit Comic (show form) ---

@comic_bp.route("/publisher/edit/<int:comic_id>", methods=["GET"])
@login_required
@role_required("publisher")
def publisher_edit_form(comic_id):
    conn = get_db()
    try:
        comic = get_comic_by_id(conn, comic_id)
        if not comic:
            return redirect("/publisher_home")
        return render_template(
            "publisher_edit.html",
            comic=comic,
            user_name=session.get("user_name", "Publisher"),
        )
    finally:
        conn.close()

#FIVE
# --- Update Comic (with optional poster re-upload) ---

@comic_bp.route("/publisher/edit/<int:comic_id>", methods=["POST"])
@login_required
@role_required("publisher")
def publisher_update_comic(comic_id):
    data = request.form
    conn = get_db()
    try:
        # Check for new poster upload
        poster_file = request.files.get("poster")
        poster_url = None
        if poster_file and poster_file.filename and allowed_file(poster_file.filename):
            poster_url = save_poster(poster_file, comic_id)
        else:
            # Keep existing poster
            existing = get_comic_by_id(conn, comic_id)
            poster_url = existing["poster_url"] if existing else None

        update_comic(
            conn,
            comic_id,
            data["title"],
            data.get("description", ""),
            data.get("genre", ""),
            poster_url,
            data.get("status", None),
        )
        conn.commit()
        return redirect("/publisher_home")
    except Exception as e:
        conn.rollback()
        return redirect("/publisher_home")
    finally:
        conn.close()

#six
# --- Delete Comic (with cascade folder cleanup) ---

@comic_bp.route("/publisher/delete/<int:comic_id>", methods=["POST"])
@login_required
@role_required("publisher")
def publisher_delete_comic(comic_id):
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
    return redirect("/publisher_home")


# ============================================
# CHAPTER MANAGEMENT
# ============================================

@comic_bp.route("/publisher/comic/<int:comic_id>/chapters")
@login_required
@role_required("publisher")
def publisher_chapters(comic_id):
    conn = get_db()
    try:
        comic = get_comic_by_id(conn, comic_id)
        if not comic:
            return redirect("/publisher_home")

        chapters = get_chapters_for_comic(conn, comic_id)

        # For each chapter, attach its pages
        chapters_with_pages = []
        for ch in chapters:
            pages = get_pages_for_chapter(conn, ch["id"])
            chapters_with_pages.append({**ch, "pages": pages})

        return render_template(
            "publisher_chapters.html",
            comic=comic,
            chapters=chapters_with_pages,
            user_name=session.get("user_name", "Publisher"),
        )
    finally:
        conn.close()

#SEVEN
@comic_bp.route("/publisher/comic/<int:comic_id>/chapter/create", methods=["POST"])
@login_required
@role_required("publisher")
def publisher_create_chapter(comic_id):
    data = request.form
    conn = get_db()
    try:
        create_chapter(
            conn,
            comic_id,
            int(data["chapter_number"]),
            data.get("title", ""),
        )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    return redirect(f"/publisher/comic/{comic_id}/chapters")


@comic_bp.route("/publisher/comic/<int:comic_id>/chapter/<int:chapter_num>/upload", methods=["POST"])
@login_required
@role_required("publisher")
def publisher_upload_pages(comic_id, chapter_num):
    conn = get_db()
    try:
        chapter = get_chapter_by_number(conn, comic_id, chapter_num)
        if not chapter:
            return redirect(f"/publisher/comic/{comic_id}/chapters")

        files = request.files.getlist("pages")
        next_num = get_next_page_number(conn, chapter["id"])

        for f in files:
            if f and f.filename and allowed_file(f.filename):
                image_path = save_page_image(f, comic_id, chapter_num, next_num)
                create_page(conn, chapter["id"], next_num, image_path)
                next_num += 1

        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    return redirect(f"/publisher/comic/{comic_id}/chapters")

#eight
@comic_bp.route("/publisher/chapter/<int:chapter_id>/delete", methods=["POST"])
@login_required
@role_required("publisher")
def publisher_delete_chapter(chapter_id):
    conn = get_db()
    try:
        chapter = get_chapter(conn, chapter_id)
        if chapter:
            comic_id = chapter["comic_id"]
            chapter_num = chapter["chapter_number"]
            delete_chapter(conn, chapter_id)
            conn.commit()
            # Remove chapter folder
            delete_folder("comics", str(comic_id), "chapters", str(chapter_num))
            return redirect(f"/publisher/comic/{comic_id}/chapters")
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    return redirect("/publisher_home")
