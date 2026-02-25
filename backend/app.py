from flask import Flask, jsonify
from flask_cors import CORS
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
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)