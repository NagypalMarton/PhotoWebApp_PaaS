import re

import pymysql
from flask import jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")


def is_password_strong(password: str) -> bool:
    if len(password) < 8:
        return False
    has_letter = any(ch.isalpha() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    return has_letter and has_digit


def register_auth_routes(app, get_db_connection, current_user_id):
    @app.post("/api/auth/register")
    def register():
        payload = request.get_json(silent=True) or {}
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""

        if not USERNAME_PATTERN.fullmatch(username):
            return jsonify({"message": "A felhasználónév 3-50 karakter legyen (betű, szám, ., _, -)."}), 400
        if not is_password_strong(password):
            return jsonify({"message": "A jelszó legalább 8 karakter legyen, tartalmazzon betűt és számot."}), 400

        password_hash = generate_password_hash(password)

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, created_at) VALUES (%s, %s, NOW())",
                        (username, password_hash),
                    )
                    user_id = cursor.lastrowid
        except pymysql.err.IntegrityError:
            return jsonify({"message": "A felhasználónév már foglalt."}), 409
        except pymysql.MySQLError:
            return jsonify({"message": "Sikertelen regisztráció."}), 500

        session["user_id"] = user_id
        session["username"] = username
        return jsonify({"id": user_id, "username": username}), 201

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
        except pymysql.MySQLError:
            return jsonify({"message": "Sikertelen bejelentkezés."}), 500

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"message": "Hibás felhasználónév vagy jelszó."}), 401

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({"id": user["id"], "username": user["username"]})

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
