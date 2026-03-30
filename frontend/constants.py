"""Constants for the frontend application."""
from config import Config

# Flash message categories
FLASH_CATEGORIES = {
    "success": "success",
    "error": "danger",
    "warning": "warning",
    "info": "info",
}

# Error messages
ERROR_MESSAGES = {
    "backend_unavailable": "A backend jelenleg nem elérhető.",
    "auth_required": "A művelethez bejelentkezés szükséges.",
    "photo_not_found": "A kép nem található.",
    "upload_failed": "Feltöltés sikertelen.",
    "delete_failed": "Törlés sikertelen.",
}

# Success messages
SUCCESS_MESSAGES = {
    "registration": "Sikeres regisztráció. Most jelentkezz be.",
    "login": "Sikeres bejelentkezés.",
    "logout": "Sikeres kijelentkezés.",
    "upload": "Sikeres feltöltés.",
    "delete": "Kép törölve.",
}

# Validation constants
MAX_PHOTO_NAME_LENGTH = Config.MAX_PHOTO_NAME_LENGTH
