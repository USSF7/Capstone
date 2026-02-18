from flask import Blueprint
from .user_routes import user_bp
from .equipment_routes import equipment_bp
from .review_routes import review_bp
from .message_routes import message_bp
from .rental_routes import rental_bp
from .event_routes import event_bp
from .request_routes import request_bp

def register_blueprints(app):
    """Register all route blueprints"""
    app.register_blueprint(user_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(rental_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(request_bp)

__all__ = ['register_blueprints']