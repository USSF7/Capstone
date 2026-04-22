"""
Route blueprint package.

Imports all Flask blueprints and exposes ``register_blueprints()`` to
attach them to the application in the factory.
"""

from flask import Blueprint
from .user_routes import user_bp
from .equipment_routes import equipment_bp
from .review_routes import review_bp
from .message_routes import message_bp
from .rental_routes import rental_bp
from .auth_routes import auth_bp
from .ai_routes import ai_bp
from .location_routes import location_bp
from .images_routes import images_bp


def register_blueprints(app):
    """Register all route blueprints with the Flask application.

    Args:
        app: The Flask application instance.
    """
    app.register_blueprint(user_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(rental_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(images_bp)

__all__ = ['register_blueprints']