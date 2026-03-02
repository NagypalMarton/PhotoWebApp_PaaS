from datetime import datetime
import uuid

import pymysql
from flask import jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

PHOTO_ORDER_BY_SQL = {
    ("date", "desc"): """
        SELECT id, owner_user_id, name, upload_datetime, file_path_or_url
        FROM photos
        ORDER BY upload_datetime DESC, id DESC
    """,
    ("date", "asc"): """
        SELECT id, owner_user_id, name, upload_datetime, file_path_or_url
        FROM photos
        ORDER BY upload_datetime ASC, id DESC
    """,
    ("name", "desc"): """
        SELECT id, owner_user_id, name, upload_datetime, file_path_or_url
        FROM photos
        ORDER BY name DESC, id DESC
    """,
    ("name", "asc"): """
        SELECT id, owner_user_id, name, upload_datetime, file_path_or_url
        FROM photos
        ORDER BY name ASC, id DESC
    """,
}


def register_photo_routes(
    app,
    get_db_connection,
    upload_dir,
    allowed_file,
    format_photo,
    current_user_id,
    login_required,
):
    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/api/photos")
    def list_photos():
        sort = request.args.get("sort", "date").lower()
        order = request.args.get("order", "desc").lower()
        sort_key = "name" if sort == "name" else "date"
        order_key = "asc" if order == "asc" else "desc"
        query = PHOTO_ORDER_BY_SQL[(sort_key, order_key)]

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
            return jsonify([format_photo(row) for row in rows])
        except pymysql.MySQLError:
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
        save_path = upload_dir / final_filename

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
        except (pymysql.MySQLError, OSError):
            if save_path.exists():
                save_path.unlink(missing_ok=True)
            return jsonify({"message": "Hiba a feltöltés közben."}), 500

        return jsonify(format_photo(photo)), 201

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
        except pymysql.MySQLError:
            return jsonify({"message": "Hiba a törlés közben."}), 500

        try:
            disk_path = upload_dir / photo["file_path_or_url"]
            if disk_path.exists():
                disk_path.unlink(missing_ok=True)
        except OSError:
            return jsonify({"message": "Hiba a törlés közben."}), 500

        return jsonify({"message": "Sikeres törlés."}), 200


def format_photo_row(row):
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
