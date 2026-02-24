import os
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

import pymysql
from flask import Flask, jsonify, request, send_from_directory, session
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_CONTENT_LENGTH = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "gallery_user"),
        password=os.getenv("DB_PASSWORD", "gallery_password"),
        database=os.getenv("DB_NAME", "gallery"),
        cursorclass=DictCursor,
        autocommit=True,
    )


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

    def format_photo(row):
        upload_datetime = row["upload_datetime"]
        if isinstance(upload_datetime, datetime):
            upload_datetime = upload_datetime.strftime("%Y-%m-%d %H:%M")
        return {
            "id": row["id"],
            "name": row["name"],
            "upload_datetime": upload_datetime,
            "image_url": f"/uploads/{row['file_path_or_url']}",
            "owner_user_id": row["owner_user_id"],
        }

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/api/health")
    def health():
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            return jsonify({"status": "ok"})
        except Exception as error:
            return jsonify({"status": "error", "message": str(error)}), 500

    @app.post("/api/auth/register")
    def register():
        payload = request.get_json(silent=True) or {}
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""

        if len(username) < 3 or len(username) > 50:
            return jsonify({"message": "A felhasználónév 3-50 karakter legyen."}), 400
        if len(password) < 6:
            return jsonify({"message": "A jelszó minimum 6 karakter legyen."}), 400

        password_hash = generate_password_hash(password)

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, created_at) VALUES (%s, %s, NOW())",
                        (username, password_hash),
                    )
                    user_id = cursor.lastrowid
            session["user_id"] = user_id
            session["username"] = username
            return jsonify({"id": user_id, "username": username}), 201
        except pymysql.err.IntegrityError:
            return jsonify({"message": "A felhasználónév már foglalt."}), 409
        except Exception:
            return jsonify({"message": "Sikertelen regisztráció."}), 500

    @app.post("/api/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""

        if not username or not password:
            return jsonify({"message": "Hiányzó belépési adatok."}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
                    user = cursor.fetchone()

            if not user or not check_password_hash(user["password_hash"], password):
                return jsonify({"message": "Hibás felhasználónév vagy jelszó."}), 401

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return jsonify({"id": user["id"], "username": user["username"]})
        except Exception:
            return jsonify({"message": "Sikertelen bejelentkezés."}), 500

    @app.post("/api/auth/logout")
    def logout():
        session.clear()
        return jsonify({"message": "Kijelentkezve."})

    @app.get("/api/auth/me")
    def me():
        user_id = current_user_id()
        if not user_id:
            return jsonify({"authenticated": False})
        return jsonify({"authenticated": True, "id": user_id, "username": session.get("username")})

    @app.get("/api/photos")
    def list_photos():
        sort = request.args.get("sort", "date").lower()
        order = request.args.get("order", "desc").lower()
        sort_column = "name" if sort == "name" else "upload_datetime"
        sort_order = "ASC" if order == "asc" else "DESC"

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                        SELECT id, owner_user_id, name, upload_datetime, file_path_or_url
                        FROM photos
                        ORDER BY {sort_column} {sort_order}, id DESC
                        """
                    )
                    rows = cursor.fetchall()
            return jsonify([format_photo(row) for row in rows])
        except Exception:
            return jsonify({"message": "Hiba a képek lekérdezése közben."}), 500

    @app.post("/api/photos")
    @login_required
    def upload_photo():
        name = (request.form.get("name") or "").strip()
        file = request.files.get("photo")

        if not name or len(name) > 40:
            return jsonify({"message": "A név kötelező és max. 40 karakter lehet."}), 400

        if not file or not file.filename:
            return jsonify({"message": "Képfájl megadása kötelező."}), 400

        if not allowed_file(file.filename):
            return jsonify({"message": "Nem támogatott fájltípus."}), 400

        ext = file.filename.rsplit(".", 1)[1].lower()
        safe_name = secure_filename(file.filename.rsplit(".", 1)[0]) or "photo"
        final_filename = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
        save_path = UPLOAD_DIR / final_filename

        try:
            file.save(save_path)
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO photos (owner_user_id, name, upload_datetime, file_path_or_url)
                        VALUES (%s, %s, NOW(), %s)
                        """,
                        (current_user_id(), name, final_filename),
                    )
                    photo_id = cursor.lastrowid

                    cursor.execute(
                        "SELECT id, owner_user_id, name, upload_datetime, file_path_or_url FROM photos WHERE id = %s",
                        (photo_id,),
                    )
                    photo = cursor.fetchone()
            return jsonify(format_photo(photo)), 201
        except Exception:
            if save_path.exists():
                save_path.unlink(missing_ok=True)
            return jsonify({"message": "Hiba a feltöltés közben."}), 500

    @app.delete("/api/photos/<int:photo_id>")
    @login_required
    def delete_photo(photo_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, owner_user_id, file_path_or_url FROM photos WHERE id = %s",
                        (photo_id,),
                    )
                    photo = cursor.fetchone()

                    if not photo:
                        return jsonify({"message": "A kép nem található."}), 404

                    if photo["owner_user_id"] != current_user_id():
                        return jsonify({"message": "Nincs jogosultság a törléshez."}), 403

                    cursor.execute("DELETE FROM photos WHERE id = %s", (photo_id,))

            disk_path = UPLOAD_DIR / photo["file_path_or_url"]
            if disk_path.exists():
                disk_path.unlink(missing_ok=True)

            return jsonify({"message": "Sikeres törlés."}), 200
        except Exception:
            return jsonify({"message": "Hiba a törlés közben."}), 500

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"message": "A kért API végpont nem található."}), 404
        return error

    @app.errorhandler(413)
    def payload_too_large(_error):
        if request.path.startswith("/api/"):
            return jsonify({"message": "A feltöltött fájl túl nagy."}), 413
        return jsonify({"message": "A feltöltött fájl túl nagy."}), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
