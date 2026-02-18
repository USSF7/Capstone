from models import User
from database import db

class UserService:
    """Service layer for User business logic"""

    @staticmethod
    def create_user(name, email):
        """Create a new user"""
        if not name or not email:
            raise ValueError("Name and email are required")
        
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")
        
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user(user_id):
        """Get a user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_all_users():
        """Get all users"""
        return User.query.all()

    @staticmethod
    def update_user(user_id, name=None, email=None):
        """Update a user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        if email and User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")
        
        if name:
            user.name = name
        if email:
            user.email = email
        
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        db.session.delete(user)
        db.session.commit()
        return True