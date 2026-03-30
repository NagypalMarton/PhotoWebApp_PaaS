"""Constants for the backend application."""
from config import Config

# Validation constants
MAX_PHOTO_NAME_LENGTH = Config.MAX_PHOTO_NAME_LENGTH
MAX_USERNAME_LENGTH = Config.MAX_USERNAME_LENGTH
MIN_USERNAME_LENGTH = Config.MIN_USERNAME_LENGTH
MIN_PASSWORD_LENGTH = Config.MIN_PASSWORD_LENGTH

# Allowed file extensions
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS

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
}

# Flash categories
FLASH_CATEGORIES = {
    "success": "success",
    "error": "danger",
    "warning": "warning",
    "info": "info",
}
