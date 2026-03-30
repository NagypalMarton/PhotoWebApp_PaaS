"""Configuration for the frontend application."""
# Shared constants from parent config.py
MAX_PHOTO_NAME_LENGTH = 40
MAX_USERNAME_LENGTH = 80
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6

# Backend URL for API calls
BACKEND_URL = "http://backend:5001"

# API settings
API_TIMEOUT = 10  # seconds
IMAGE_PROXY_TIMEOUT = 20  # seconds
