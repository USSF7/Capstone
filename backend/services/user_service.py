"""
User service module.

Business logic for user CRUD operations, profile picture management,
and address geocoding on create/update.
"""

import json
import os
import uuid
from models import User
from database import db
from werkzeug.utils import secure_filename
from flask import current_app, jsonify

USERS_PICTURES_FOLDER = 'images/users'
os.makedirs(USERS_PICTURES_FOLDER, exist_ok=True)


class UserService:
    """Business logic for User management.

    All methods are static — no instance state is needed.
    """

    @staticmethod
    def create_user(name, email, password, phone, date_of_birth, street_address, city, state, zip_code, vendor, renter, picture):
        """Create a new user with optional geocoding.

        Validates uniqueness of email and phone, hashes the password if
        provided, and geocodes the address to lat/lng coordinates.

        Args:
            name: Display name (required).
            email: Email address (required, must be unique).
            password: Plaintext password (optional for Google-only users).
            phone: Phone number (must be unique if provided).
            date_of_birth: Date of birth string (YYYY-MM-DD).
            street_address: Street address for geocoding.
            city: City for geocoding.
            state: State for geocoding.
            zip_code: ZIP code for geocoding.
            vendor: Whether user is a vendor.
            renter: Whether user is a renter.
            picture: Relative path to profile picture.

        Returns:
            The created User instance.

        Raises:
            ValueError: If required fields missing or email/phone already taken.
        """
        if not name or not email:
            raise ValueError("Name and email are required")
        
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")
        
        if User.query.filter_by(phone=phone).first():
            raise ValueError("Phone number already exists")
        
        user = User(name=name, email=email, phone=phone, date_of_birth=date_of_birth, street_address=street_address, city=city, state=state, zip_code=zip_code, vendor=vendor, renter=renter, picture=picture)
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
    def update_user(user_id, name=None, email=None, phone=None, date_of_birth=None, street_address=None, city=None, state=None, zip_code=None, vendor=None, renter=None, picture=''):
        """Update an existing user's profile fields.

        Re-geocodes the address if any address fields changed.

        Args:
            user_id: The user's primary key.
            name: New display name.
            email: New email (uniqueness checked).
            phone: New phone (uniqueness checked).
            date_of_birth: New date of birth.
            street_address: New street address.
            city: New city.
            state: New state.
            zip_code: New ZIP code.
            vendor: Whether user is a vendor.
            renter: Whether user is a renter.
            picture: Relative path to profile picture.

        Returns:
            The updated User instance.

        Raises:
            ValueError: If user not found or email/phone already taken.
        """
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
        user.picture = picture

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
    
    @staticmethod
    def upload_user_picture(userPicture):
        """Save an uploaded user profile picture to disk with a unique filename.

        Args:
            userPicture: A Werkzeug FileStorage object from the request.

        Returns:
            The relative file path where the picture was saved.
        """
        # Getting the picture's filename
        pictureFilename = secure_filename(userPicture.filename)
        pictureExtension = os.path.splitext(pictureFilename)[1]

        # Creating a unique filename for the picture
        uniqueFilename = f"{uuid.uuid4()}{pictureExtension}"

        # Saving the picture file in the backend
        pictureFilepath = os.path.join(USERS_PICTURES_FOLDER, uniqueFilename)
        userPicture.save(pictureFilepath)

        return pictureFilepath
    
    @staticmethod
    def delete_user_picture(filepath):
        """Delete a user profile picture from disk.

        Args:
            filepath: Relative path to the picture file.

        Returns:
            JSON response with success or error message.
        """
        # Creating a directory
        pictureFilepath = os.path.join(current_app.root_path, filepath)

        # Checking if the picture file exists
        if os.path.exists(pictureFilepath) == False:
            return jsonify({'error': 'Picture does not exists in the backend'}), 404
        
        # Removing the picture from the backend
        os.remove(pictureFilepath)

        return jsonify({'message': 'Picture has been removed from the backend'}), 200