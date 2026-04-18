# app/routes/auth_routes.py

from flask import Blueprint, request, render_template, redirect, session

from app.db import get_db
from app.services.auth_service import register_user, login_user
from app.utils.upload_utils import allowed_file, save_publisher_logo

auth_bp = Blueprint("auth", __name__)


# Show register page
@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


# Project Info Page
@auth_bp.route("/home", methods=["GET"])
def info_page():
    return render_template("info.html")


# Handle register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form

    conn = get_db()
    try:
        user = register_user(
            conn,
            data["role"],
            data["name"],
            data["email"],
            data["password"],
            None  # logo_url filled after we have ID
        )
        conn.commit()

        # Handle publisher logo upload
        if data["role"] == "publisher":
            logo_file = request.files.get("logo")
            if logo_file and logo_file.filename and allowed_file(logo_file.filename):
                logo_path = save_publisher_logo(logo_file, user["id"])
                # Update logo_url in the database
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE publisher SET logo_url = %s WHERE id = %s;",
                        (logo_path, user["id"])
                    )
                conn.commit()

        return redirect("/login")
#Auth routes part two
    except Exception as e:
        conn.rollback()
        return render_template("register.html", error=str(e))

    finally:
        conn.close()


# Show login page
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# Handle login — role-based redirect
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form
    role = data["role"]

    conn = get_db()
    try:
        user = login_user(conn, role, data["email"], data["password"])

        if not user:
            return render_template("login.html", error="Invalid credentials")

        # Store user info in session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_role"] = role
        if role == "publisher":
            session["user_logo"] = user.get("logo_url")

        # Role-based redirect
        if role == "reader":
            return redirect("/reader_home")
        elif role == "publisher":
            return redirect("/publisher_home")
        elif role == "admin":
            return redirect("/admin_home")
        else:
            return redirect("/login")

    finally:
        conn.close()


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")