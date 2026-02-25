#!/usr/bin/env python
"""
Database initialization script.
Creates all tables from models.
"""

import sys
from sqlalchemy import text
from app import create_app, db

def init_db():
    """Initialize the database by creating all tables"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("Enabling PostGIS extension...")
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            db.session.commit()

            print("Dropping all tables...")
            db.drop_all()
            
            print("Creating all tables...")
            db.create_all()
            
            print("✓ Database initialized successfully!")
            return True
        except Exception as e:
            print(f"✗ Error initializing database: {str(e)}")
            return False

if __name__ == '__main__':
    success = init_db()
    sys.exit(0 if success else 1)