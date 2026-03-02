import pymysql
from flask import jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash


def register_auth_routes(app, get_db_connection, current_user_id):
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
