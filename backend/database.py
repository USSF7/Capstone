"""
Database initialization module.

Provides the shared SQLAlchemy instance used by all models and services.
The instance is initialized with the Flask app via ``db.init_app(app)``
inside the application factory in ``app.py``.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()