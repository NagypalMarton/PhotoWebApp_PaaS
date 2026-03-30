"""Shared configuration for the PhotoWebApp."""
import os


class Config:
    """Shared configuration class for frontend and backend."""
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "mysql+pymysql://photouser:photopass@localhost:3306/photowebapp"
    )
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-backend-secret")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "frontend-dev-secret")
    
    # File upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/data/uploads")
    MAX_PHOTO_SIZE = int(os.getenv("MAX_PHOTO_SIZE", "10485760"))  # 10MB default
    
    # Validation constants
    MAX_PHOTO_NAME_LENGTH = 40
    MAX_USERNAME_LENGTH = 80
    MIN_USERNAME_LENGTH = 3
    MIN_PASSWORD_LENGTH = 6
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    
    # Backend URL (for frontend)
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001")
    
    # API settings
    API_TIMEOUT = 10  # seconds
    IMAGE_PROXY_TIMEOUT = 20  # seconds
