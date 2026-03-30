import os
import time
from datetime import datetime
from functools import wraps
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import Config
from constants import ERROR_MESSAGES, SUCCESS_MESSAGES, FLASH_CATEGORIES, MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def token_for_user(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def get_user_id_from_token(token: str):
    try:
        payload = serializer.loads(token, max_age=60 * 60 * 24)
        return payload.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


def get_photo_or_404(photo_id: int):
    """Get photo by ID or return 404 response."""
    photo = Photo.query.get(photo_id)
    if not photo:
        return None, jsonify({"error": ERROR_MESSAGES["photo_not_found"]}), 404
    return photo, None, None


def check_photo_owner(photo, user_id: int):
    """Check if user owns the photo or return 403 response."""
    if photo.owner_id != user_id:
        return jsonify({"error": ERROR_MESSAGES["photo_not_owned"]}), 403
    return None


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": ERROR_MESSAGES["auth_required"]}), 401

        token = auth_header.split(" ", 1)[1].strip()
        user_id = get_user_id_from_token(token)
        if not user_id:
            return jsonify({"error": ERROR_MESSAGES["invalid_token"]}), 401

        request.user_id = user_id
        return func(*args, **kwargs)

    return wrapper


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if len(username) < MIN_USERNAME_LENGTH or len(username) > MAX_USERNAME_LENGTH:
        return jsonify({"error": ERROR_MESSAGES["username_invalid"]}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": ERROR_MESSAGES["password_invalid"]}), 400

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"error": ERROR_MESSAGES["username_exists"]}), 409

    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": SUCCESS_MESSAGES["registration"]}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": ERROR_MESSAGES["invalid_credentials"]}), 401

    token = token_for_user(user.id)
    return jsonify({"token": token, "username": user.username})


@app.route("/api/photos", methods=["GET"])
def list_photos():
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    
    # Use getattr for dynamic column selection - cleaner than nested if-else
    sort_column = Photo.name if sort == "name" else Photo.uploaded_at
    order_func = getattr(sort_column, order)
    query = Photo.query.order_by(order_func())

    photos = [
        {
            "id": photo.id,
            "name": photo.name,
            "uploaded_at": photo.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        }
        for photo in query.all()
    ]
    return jsonify({"photos": photos})


@app.route("/api/photos", methods=["POST"])
@auth_required
def upload_photo():
    name = (request.form.get("name") or "").strip()
    file = request.files.get("photo")

    if not name or len(name) > MAX_PHOTO_NAME_LENGTH:
        return jsonify({"error": ERROR_MESSAGES["photo_name_invalid"]}), 400
    if not file or file.filename == "":
        return jsonify({"error": ERROR_MESSAGES["photo_file_required"]}), 400
    if not is_allowed_file(file.filename):
        return jsonify({"error": ERROR_MESSAGES["photo_format_unsupported"]}), 400

    safe_name = secure_filename(file.filename)
    unique_filename = f"{uuid4().hex}_{safe_name}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(file_path)

    photo = Photo(name=name, filename=unique_filename, owner_id=request.user_id)
    db.session.add(photo)
    db.session.commit()

    return jsonify({"message": SUCCESS_MESSAGES["upload"], "id": photo.id}), 201


@app.route("/api/photos/<int:photo_id>", methods=["DELETE"])
@auth_required
def delete_photo(photo_id: int):
    photo, error_response, status_code = get_photo_or_404(photo_id)
    if error_response:
        return error_response, status_code
    
    owner_error = check_photo_owner(photo, request.user_id)
    if owner_error:
        return owner_error
    
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(photo)
    db.session.commit()

    return jsonify({"message": SUCCESS_MESSAGES["delete"]})


@app.route("/api/photos/<int:photo_id>", methods=["GET"])
def photo_detail(photo_id: int):
    photo, error_response, status_code = get_photo_or_404(photo_id)
    if error_response:
        return error_response, status_code

    return jsonify(
        {
            "id": photo.id,
            "name": photo.name,
            "uploaded_at": photo.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "image_url": f"/api/photos/{photo.id}/image",
        }
    )


@app.route("/api/photos/<int:photo_id>/image", methods=["GET"])
def photo_image(photo_id: int):
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({"error": "Photo not found"}), 404

    return send_from_directory(app.config["UPLOAD_FOLDER"], photo.filename)


def init_db_with_retry(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    last_error = None
    for _ in range(max_attempts):
        try:
            with app.app_context():
                db.create_all()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"Database initialization failed: {last_error}")


init_db_with_retry()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
