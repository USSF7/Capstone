from models import User
from database import db

class UserService:
    """Service layer for User business logic"""

    @staticmethod
    def create_user(name, email, password, phone, date_of_birth, street_address, city, state, zip_code, vendor, renter):
        """Create a new user"""
        if not name or not email:
            raise ValueError("Name and email are required")
        
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")
        
        if User.query.filter_by(phone=phone).first():
            raise ValueError("Phone number already exists")
        
        user = User(name=name, email=email, phone=phone, date_of_birth=date_of_birth, street_address=street_address, city=city, state=state, zip_code=zip_code, vendor=vendor, renter=renter)
        if password:
            user.set_password(password)

        # Geocode address to lat/lng
        if street_address and city and state and zip_code:
            try:
                from services.location_service import LocationService
                coords = LocationService.geocode_address(street_address, city, state, zip_code)
                if coords:
                    user.latitude, user.longitude = coords
            except Exception:
                pass  # Geocoding failure is non-fatal

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
    def update_user(user_id, name=None, email=None, phone=None, date_of_birth=None, street_address=None, city=None, state=None, zip_code=None, vendor=None, renter=None, max_travel_distance=None):
        """Update a user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        existing = User.query.filter_by(email=email).first()
        if email and existing and existing.id != user_id:
            raise ValueError("Email already exists")

        existing = User.query.filter_by(phone=phone).first()
        if phone and existing and existing.id != user_id:
            raise ValueError("Phone number already exists")
        
        if name:
            user.name = name
        if email:
            user.email = email
        if phone:
            user.phone = phone
        if date_of_birth:
            user.date_of_birth = date_of_birth
        if street_address:
            user.street_address = street_address
        if city:
            user.city = city
        if state:
            user.state = state
        if zip_code:
            user.zip_code = zip_code
        
        user.vendor = vendor
        user.renter = renter
        
        if max_travel_distance is not None:
            user.max_travel_distance = max_travel_distance

        # Re-geocode if address fields changed
        addr = user.street_address
        c = user.city
        s = user.state
        z = user.zip_code
        if addr and c and s and z:
            try:
                from services.location_service import LocationService
                coords = LocationService.geocode_address(addr, c, s, z)
                if coords:
                    user.latitude, user.longitude = coords
            except Exception:
                pass  # Geocoding failure is non-fatal

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