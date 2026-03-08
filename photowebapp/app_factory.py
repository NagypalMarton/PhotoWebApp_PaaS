from functools import wraps

import pymysql
from flask import Flask, jsonify, request, session

from .auth_routes import register_auth_routes
from .config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, UPLOAD_DIR, get_required_env
from .db import get_db_connection
from .photo_routes import format_photo_row, register_photo_routes


def current_user_id():
    return session.get("user_id")


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user_id():
            return jsonify({"message": "Bejelentkezés szükséges."}), 401
        return func(*args, **kwargs)

    return wrapper


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = get_required_env("SECRET_KEY")
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @app.get("/api/health")
    def health():
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            return jsonify({"status": "ok"})
        except pymysql.MySQLError as error:
            return jsonify({"status": "error", "message": str(error)}), 500

    @app.get("/api/health/live")
    def health_live():
        return jsonify({"status": "ok"})

    register_auth_routes(app, get_db_connection, current_user_id)
    register_photo_routes(
        app,
        get_db_connection,
        UPLOAD_DIR,
        allowed_file,
        format_photo_row,
        current_user_id,
        login_required,
    )

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"message": "A kért API végpont nem található."}), 404
        return error

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({"message": "A feltöltött fájl túl nagy."}), 413

    return app
