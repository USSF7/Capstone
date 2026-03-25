from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from config import config
from database import db
from routes import register_blueprints

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    app.url_map.strict_slashes = False
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'}), 200

    @app.route('/health/postgis', methods=['GET'])
    def health_postgis():
        try:
            result = db.session.execute(text("SELECT PostGIS_Version()")).scalar()
            return jsonify({'status': 'ok', 'postgis_version': result}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # Create database tables and add any missing columns
    with app.app_context():
        db.create_all()

        # Add auth columns to users table if they don't exist
        columns_to_add = [
            ("password_hash", "VARCHAR(255)"),
            ("phone", "VARCHAR(20)"),
            ("google_id", "VARCHAR(120) UNIQUE"),
            ("auth_provider", "VARCHAR(20)"),
            ("date_of_birth", "VARCHAR(10)"),
            ("street_address", "VARCHAR(200)"),
            ("city", "VARCHAR(100)"),
            ("state", "VARCHAR(100)"),
            ("zip_code", "INTEGER"),
            ("vendor", "BOOLEAN"),
            ("renter", "BOOLEAN"),
        ]
        for col_name, col_type in columns_to_add:
            try:
                db.session.execute(text(
                    f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()

        equipment_columns_to_add = [
            ("price", "NUMERIC(10,2) DEFAULT 0"),
            ("description", "VARCHAR(1000)"),
            ("picture", "VARCHAR(500)"),
        ]
        for col_name, col_type in equipment_columns_to_add:
            try:
                db.session.execute(text(
                    f"ALTER TABLE equipment ADD COLUMN {col_name} {col_type}"
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()

        try:
            db.session.execute(text(
                "ALTER TABLE rentals ADD COLUMN deleted BOOLEAN DEFAULT FALSE"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)