"""Configuration management for the backend application."""
import os
from config import Config as SharedConfig


class Config(SharedConfig):
    """Application configuration class - extends shared Config."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", SharedConfig.DATABASE_URL)
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", SharedConfig.SECRET_KEY)
    
    # File upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", SharedConfig.UPLOAD_FOLDER)
    MAX_PHOTO_SIZE = int(os.getenv("MAX_PHOTO_SIZE", SharedConfig.MAX_PHOTO_SIZE))
    
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
