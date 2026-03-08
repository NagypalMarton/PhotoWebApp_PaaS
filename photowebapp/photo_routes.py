from datetime import datetime
import uuid

import pymysql
from flask import jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

PHOTO_LIST_SQL = """
    SELECT id, owner_user_id, name, upload_datetime, file_path_or_url
    FROM photos
    ORDER BY {order_column} {order_direction}, id DESC
"""

PHOTO_SORT_COLUMNS = {
    "date": "upload_datetime",
    "name": "name",
}


def build_photo_list_query(sort_key: str, order_key: str) -> str:
    order_column = PHOTO_SORT_COLUMNS[sort_key]
    order_direction = "ASC" if order_key == "asc" else "DESC"
    return PHOTO_LIST_SQL.format(order_column=order_column, order_direction=order_direction)


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
        query = build_photo_list_query(sort_key, order_key)

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

        stem, dot, ext = file.filename.rpartition(".")
        if not dot:
            return jsonify({"message": "Hibas fajlnev."}), 400

        ext = ext.lower()
        safe_name = secure_filename(stem) or "photo"
        file_token = uuid.uuid4().hex
        final_filename = f"{file_token}_{safe_name}.{ext}"
        temp_filename = f"{final_filename}.uploading"
        save_path = upload_dir / final_filename
        temp_path = upload_dir / temp_filename
        photo_id = None

        try:
            file.save(temp_path)
        except OSError:
            return jsonify({"message": "Hiba a feltöltés közben."}), 500

        try:
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

            temp_path.replace(save_path)
        except pymysql.MySQLError:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            return jsonify({"message": "Hiba az adatbázis művelet közben."}), 500
        except OSError:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            if save_path.exists():
                save_path.unlink(missing_ok=True)
            if photo_id is not None:
                try:
                    with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("DELETE FROM photos WHERE id = %s", (photo_id,))
                except pymysql.MySQLError:
                    pass
            return jsonify({"message": "Hiba a feltöltés közben."}), 500

        return jsonify(format_photo(photo)), 201

    @app.delete("/api/photos/<int:photo_id>")
    @login_required
    def delete_photo(photo_id):
        photo = None
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
        except pymysql.MySQLError:
            return jsonify({"message": "Hiba a törlés közben."}), 500

        try:
            disk_path = upload_dir / photo["file_path_or_url"]
            if disk_path.exists():
                disk_path.unlink(missing_ok=True)
        except OSError:
            return jsonify({"message": "Hiba a törlés közben."}), 500

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM photos WHERE id = %s", (photo_id,))
        except pymysql.MySQLError:
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
