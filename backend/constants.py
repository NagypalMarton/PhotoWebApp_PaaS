"""Constants for the backend application."""

# Validation constants
MAX_PHOTO_NAME_LENGTH = 40
MAX_USERNAME_LENGTH = 80
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# API endpoints
API_PREFIX = "/api"

# Error messages
ERROR_MESSAGES = {
    "auth_required": "Authentication required",
    "invalid_token": "Invalid or expired token",
    "username_required": "Username is required",
    "username_invalid": f"Username must be between {MIN_USERNAME_LENGTH} and {MAX_USERNAME_LENGTH} characters",
    "password_required": "Password is required",
    "password_invalid": f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
    "username_exists": "Username already exists",
    "invalid_credentials": "Invalid username or password",
    "photo_not_found": "Photo not found",
    "photo_not_owned": "You can only delete your own photos",
    "photo_name_required": "Photo name is required",
    "photo_name_invalid": f"Photo name must be max {MAX_PHOTO_NAME_LENGTH} characters",
    "photo_file_required": "Photo file is required",
    "photo_format_unsupported": "Unsupported file format",
    "backend_unavailable": "A backend jelenleg nem elérhető.",
}

# Success messages
SUCCESS_MESSAGES = {
    "registration": "Sikeres regisztráció. Most jelentkezz be.",
    "login": "Sikeres bejelentkezés.",
    "logout": "Sikeres kijelentkezés.",
    "upload": "Sikeres feltöltés.",
    "delete": "Kép törölve.",
    "bulk_delete": "Képek törölve.",
}

# Flash categories
FLASH_CATEGORIES = {
    "success": "success",
    "error": "danger",
    "warning": "warning",
    "info": "info",
}
