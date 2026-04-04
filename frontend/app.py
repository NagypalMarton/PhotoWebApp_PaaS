import base64
import os

import requests
from flask import Flask, Response, jsonify, request, session

from constants import ERROR_MESSAGES, SUCCESS_MESSAGES


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "frontend-dev-secret")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001")


def api_headers():
    token = session.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def backend(path: str) -> str:
    return f"{BACKEND_URL}{path}"


def backend_error_message(response, default_message: str) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            error_message = body.get("error")
            if error_message:
                return error_message
    except ValueError:
        pass

    response_text = (response.text or "").strip()
    if response_text and not response_text.startswith("<"):
        return response_text

    return default_message


def request_data() -> dict:
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()



def json_response(payload: dict, status_code: int = 200):
    response = jsonify(payload)
    response.status_code = status_code
    return response


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/")
def index():
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    try:
        response = requests.get(backend(f"/api/photos?sort={sort}&order={order}"), timeout=10)
        if not response.ok:
            return json_response({"error": backend_error_message(response, "A fotók listája nem kérhető le.")}, response.status_code)
        photos = response.json().get("photos", [])
    except requests.RequestException:
        return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)

    return json_response(
        {
            "photos": photos,
            "sort": sort,
            "order": order,
            "logged_in": bool(session.get("token")),
            "username": session.get("username"),
        }
    )


@app.route("/photo/<int:photo_id>")
def photo_view(photo_id: int):
    try:
        response = requests.get(backend(f"/api/photos/{photo_id}"), timeout=10)
        if not response.ok:
            return json_response({"error": backend_error_message(response, "A kép nem található.")}, response.status_code)
        photo = response.json()
    except requests.RequestException:
        return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)

    return json_response(photo)


@app.route("/photo/<int:photo_id>/image")
def photo_image_proxy(photo_id: int):
    try:
        response = requests.get(backend(f"/api/photos/{photo_id}/image"), timeout=20)
    except requests.RequestException:
        return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)

    if not response.ok:
        default_message = "A kép nem található." if response.status_code == 404 else "A kép betöltése sikertelen."
        return json_response({"error": backend_error_message(response, default_message)}, response.status_code)

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/octet-stream"),
    )


@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("token"):
        return json_response({"error": ERROR_MESSAGES["auth_required"]}, 401)

    data = request_data()
    name = (data.get("name") or "").strip()
    filename = (data.get("filename") or "").strip()
    content_type = (data.get("content_type") or "").strip()
    image_data_base64 = (data.get("image_data_base64") or "").strip()
    file = request.files.get("photo")

    if not name:
        return json_response({"error": ERROR_MESSAGES["photo_name_required"]}, 400)

    if image_data_base64:
        if not filename:
            return json_response({"error": ERROR_MESSAGES["photo_file_required"]}, 400)
        if not is_allowed_file(filename):
            return json_response({"error": ERROR_MESSAGES["photo_format_unsupported"]}, 400)
    else:
        if not file or file.filename == "":
            return json_response({"error": ERROR_MESSAGES["photo_file_required"]}, 400)
        if not is_allowed_file(file.filename):
            return json_response({"error": ERROR_MESSAGES["photo_format_unsupported"]}, 400)

        filename = file.filename
        content_type = file.mimetype or "application/octet-stream"
        image_data = file.read()
        image_data_base64 = base64.b64encode(image_data).decode("ascii")

    try:
        response = requests.post(
            backend("/api/photos"),
            headers=api_headers() | {"Content-Type": "application/json"},
            json={
                "name": name,
                "filename": filename,
                "content_type": content_type,
                "image_data_base64": image_data_base64,
            },
            timeout=20,
        )

        if response.ok:
            return json_response({"message": SUCCESS_MESSAGES["upload"], "id": response.json().get("id")}, 201)

        error_message = backend_error_message(response, "Hiba történt a feltöltés közben.")
        return json_response({"error": error_message}, response.status_code)
    except requests.RequestException:
        return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)


@app.route("/delete/<int:photo_id>", methods=["POST"])
def delete(photo_id: int):
    if not session.get("token"):
        return json_response({"error": ERROR_MESSAGES["auth_required"]}, 401)

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(backend(f"/api/photos/{photo_id}"), headers=headers, timeout=10)
        
        if response.ok:
            return json_response({"message": SUCCESS_MESSAGES["delete"]})

        error_message = backend_error_message(response, "Hiba történt a törlés közben.")
        return json_response({"error": error_message}, response.status_code)
    except requests.RequestException:
        return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return json_response({"mode": "register"})

    if request.method == "POST":
        data = request_data()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        try:
            response = requests.post(
                backend("/api/register"),
                json={"username": username, "password": password},
                timeout=10,
            )
            if response.status_code == 201:
                return json_response({"message": SUCCESS_MESSAGES["registration"]}, 201)

            return json_response({"error": backend_error_message(response, "Regisztráció sikertelen.")}, response.status_code)
        except requests.RequestException:
            return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return json_response({"mode": "login"})

    if request.method == "POST":
        data = request_data()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        try:
            response = requests.post(
                backend("/api/login"),
                json={"username": username, "password": password},
                timeout=10,
            )
            if response.ok:
                body = response.json()
                session["token"] = body["token"]
                session["username"] = body["username"]
                return json_response({"message": SUCCESS_MESSAGES["login"], "username": body["username"]})

            return json_response({"error": backend_error_message(response, "Bejelentkezés sikertelen.")}, response.status_code)
        except requests.RequestException:
            return json_response({"error": ERROR_MESSAGES["backend_unavailable"]}, 503)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return json_response({"message": SUCCESS_MESSAGES["logout"]})
