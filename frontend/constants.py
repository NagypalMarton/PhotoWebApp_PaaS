"""Constants for the frontend application."""
from config import MAX_PHOTO_NAME_LENGTH

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
    "photo_name_required": "A kép neve kötelező.",
    "photo_file_required": "Válassz ki egy képet feltöltésre.",
    "photo_format_unsupported": "A kiválasztott fájl formátuma nem támogatott.",
    "photo_name_invalid": f"A kép neve max 40 karakter lehet.",
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
# MAX_PHOTO_NAME_LENGTH imported from config
