"""Configuration management for the backend application."""
import os


class Config:
    """Application configuration class."""
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "mysql+pymysql://photouser:photopass@localhost:3306/photowebapp"
    )
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-backend-secret")
    
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
    
    # API settings
    API_TIMEOUT = 10  # seconds
    IMAGE_PROXY_TIMEOUT = 20  # seconds
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Validation constants
    MAX_PHOTO_NAME_LENGTH = Config.MAX_PHOTO_NAME_LENGTH
    MAX_USERNAME_LENGTH = Config.MAX_USERNAME_LENGTH
    MIN_USERNAME_LENGTH = Config.MIN_USERNAME_LENGTH
    MIN_PASSWORD_LENGTH = Config.MIN_PASSWORD_LENGTH
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
