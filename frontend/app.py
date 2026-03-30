import os

import requests
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for

from constants import ERROR_MESSAGES, SUCCESS_MESSAGES, FLASH_CATEGORIES


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


def api_request(method, endpoint, **kwargs):
    """Helper function for API requests with consistent error handling."""
    url = backend(endpoint)
    headers = kwargs.pop("headers", {})
    headers.update(api_headers())
    kwargs["headers"] = headers
    kwargs.setdefault("timeout", 10)
    
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])
        return None, str(e)


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
        photos = response.json().get("photos", []) if response.ok else []
    except requests.RequestException:
        photos = []
        flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])

    return render_template(
        "index.html",
        photos=photos,
        sort=sort,
        order=order,
        logged_in=bool(session.get("token")),
        username=session.get("username"),
    )


@app.route("/photo/<int:photo_id>")
def photo_view(photo_id: int):
    try:
        response = requests.get(backend(f"/api/photos/{photo_id}"), timeout=10)
        if not response.ok:
            flash("A kép nem található.", "warning")
            return redirect(url_for("index"))
        photo = response.json()
    except requests.RequestException:
        flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])
        return redirect(url_for("index"))

    image_url = url_for("photo_image_proxy", photo_id=photo_id)
    return render_template("photo.html", photo=photo, image_url=image_url)


@app.route("/photo/<int:photo_id>/image")
def photo_image_proxy(photo_id: int):
    try:
        response = requests.get(backend(f"/api/photos/{photo_id}/image"), timeout=20)
    except requests.RequestException:
        flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])
        return redirect(url_for("photo_view", photo_id=photo_id))

    if not response.ok:
        if response.status_code == 404:
            flash("A kép nem található.", "warning")
        else:
            flash("A kép betöltése sikertelen.", "danger")
        return redirect(url_for("photo_view", photo_id=photo_id))

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/octet-stream"),
    )


@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("token"):
        flash(ERROR_MESSAGES["auth_required"], FLASH_CATEGORIES["error"])
        return redirect(url_for("index"))

    name = request.form.get("name", "").strip()
    file = request.files.get("photo")

    if not name:
        flash(ERROR_MESSAGES["photo_name_required"], FLASH_CATEGORIES["error"])
        return redirect(url_for("index"))
    if not file or file.filename == "":
        flash(ERROR_MESSAGES["photo_file_required"], FLASH_CATEGORIES["error"])
        return redirect(url_for("index"))
    if not is_allowed_file(file.filename):
        flash(ERROR_MESSAGES["photo_format_unsupported"], FLASH_CATEGORIES["error"])
        return redirect(url_for("index"))

    # Forward to backend API
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            backend("/api/photos"),
            headers=headers,
            data={"name": name},
            files={"photo": (file.filename, file.stream, file.mimetype)},
            timeout=20
        )
        
        if response.ok:
            flash(SUCCESS_MESSAGES["upload"], FLASH_CATEGORIES["success"])
        else:
            error = response.json().get("error", "Hiba történt a feltöltés közben.")
            flash(error, FLASH_CATEGORIES["error"])
    except requests.RequestException:
        flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])

    return redirect(url_for("index"))


@app.route("/delete/<int:photo_id>", methods=["POST"])
def delete(photo_id: int):
    if not session.get("token"):
        flash(ERROR_MESSAGES["auth_required"], FLASH_CATEGORIES["error"])
        return redirect(url_for("index"))

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(backend(f"/api/photos/{photo_id}"), headers=headers, timeout=10)
        
        if response.ok:
            flash(SUCCESS_MESSAGES["delete"], FLASH_CATEGORIES["success"])
        else:
            error = response.json().get("error", "Hiba történt a törlés közben.")
            flash(error, FLASH_CATEGORIES["error"])
    except requests.RequestException:
        flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])

    return redirect(url_for("index"))


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            response = requests.post(
                backend("/api/register"),
                json={"username": username, "password": password},
                timeout=10,
            )
            if response.status_code == 201:
                flash(SUCCESS_MESSAGES["registration"], FLASH_CATEGORIES["success"])
                return redirect(url_for("login"))
            flash(response.json().get("error", "Regisztráció sikertelen."), FLASH_CATEGORIES["error"])
        except requests.RequestException:
            flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

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
                flash(SUCCESS_MESSAGES["login"], FLASH_CATEGORIES["success"])
                return redirect(url_for("index"))
            flash(response.json().get("error", "Bejelentkezés sikertelen."), FLASH_CATEGORIES["error"])
        except requests.RequestException:
            flash(ERROR_MESSAGES["backend_unavailable"], FLASH_CATEGORIES["error"])

    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    flash(SUCCESS_MESSAGES["logout"], FLASH_CATEGORIES["info"])
    return redirect(url_for("index"))
