"""Configuration management for the backend application."""
from config import Config


class Config:
    """Application configuration class - extends shared Config."""
    
    # Database
    DATABASE_URL = Config.DATABASE_URL
    
    # Security
    SECRET_KEY = Config.SECRET_KEY
    
    # File upload
    UPLOAD_FOLDER = Config.UPLOAD_FOLDER
    MAX_PHOTO_SIZE = Config.MAX_PHOTO_SIZE
    
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
