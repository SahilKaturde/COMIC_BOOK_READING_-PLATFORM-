# app/__init__.py

from flask import Flask, send_from_directory, redirect, session
from app.routes.auth_routes import auth_bp
from app.routes.comic_routes import comic_bp
from app.routes.admin_routes import admin_bp
import os

DATA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data")


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev_key'  # Replace with actual secret key in production
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(comic_bp)
    app.register_blueprint(admin_bp)

    # Serve uploaded files from Data/ folder
    @app.route("/data/<path:filename>")
    def serve_data(filename):
        return send_from_directory(DATA_ROOT, filename)

    # Fast Flow Index: Redirect to dashboard if logged in
    @app.route("/")
    def index():
        if "user_id" in session:
            role = session.get("user_role")
            if role == "reader":
                return redirect("/reader_home")
            elif role == "publisher":
                return redirect("/publisher_home")
            elif role == "admin":
                return redirect("/admin_home")
        return redirect("/login")

    return app
