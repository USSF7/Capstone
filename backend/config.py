"""
Application configuration module.

Defines configuration classes for different environments (development,
production). Settings are loaded from environment variables with sensible
defaults for local development. The ``config`` dict at the bottom maps
environment names to their configuration class.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared by all environments.

    Attributes:
        SQLALCHEMY_TRACK_MODIFICATIONS: Disable Flask-SQLAlchemy event tracking.
        SECRET_KEY: Secret key for session signing.
        JWT_SECRET_KEY: Secret key for JWT token encoding.
        GOOGLE_CLIENT_ID: OAuth 2.0 client ID for Google sign-in.
        GOOGLE_CLIENT_SECRET: OAuth 2.0 client secret for Google sign-in.
        GOOGLE_REDIRECT_URI: Callback URL after Google OAuth flow.
        FRONTEND_URL: Base URL of the Vue frontend (used for OAuth redirects).
        GEMINI_API_KEY: API key for Google Gemini AI review summaries.
        GOOGLE_MAPS_API_KEY: API key for Google Maps geocoding and places.
    """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

class DevelopmentConfig(Config):
    """Development configuration with debug mode and local database URL."""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://capstone_user:capstone_password@db:5432/capstone_db'
    )
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration with debug mode disabled."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}