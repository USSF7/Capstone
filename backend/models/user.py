"""
User model module.

Defines the ``User`` ORM model representing application users who can act
as renters, vendors, or both. Handles password hashing, profile completeness
checks, and JSON serialization.
"""

from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """A registered user of the equipment rental marketplace.

    Users may be vendors (list equipment for rent), renters (rent equipment
    from others), or both. Authentication is either local (email + password)
    or via Google OAuth. Latitude/longitude are geocoded from the user's
    address for proximity-based equipment search.

    Attributes:
        id: Primary key.
        name: Display name.
        email: Unique email address used for login.
        password_hash: Bcrypt hash of the user's password (None for Google-only accounts).
        phone: Contact phone number.
        google_id: Google account ID for OAuth users.
        auth_provider: 'local' or 'google'.
        created_at: Account creation timestamp.
        date_of_birth: Date of birth string (YYYY-MM-DD).
        street_address: Street address component.
        city: City name.
        state: State name.
        zip_code: ZIP / postal code.
        latitude: Geocoded latitude of the user's address.
        longitude: Geocoded longitude of the user's address.
        vendor: Whether the user lists equipment for rent.
        renter: Whether the user rents equipment from others.
        picture: Relative path to the user's profile picture.
        ai_review_summary: Cached AI-generated summary of reviews about this user.
        ai_review_summary_updated_at: Timestamp when the AI summary was last refreshed.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    auth_provider = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_birth = db.Column(db.String(10), nullable=True)
    street_address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.Integer, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    vendor = db.Column(db.Boolean, nullable=True)
    renter = db.Column(db.Boolean, nullable=True)
    picture = db.Column(db.String(500), default="", nullable=False)
    ai_review_summary = db.Column(db.Text, nullable=True)
    ai_review_summary_updated_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    equipment = db.relationship('Equipment', foreign_keys='Equipment.owner_id', backref='owner')
    rentals_as_renter = db.relationship('Rental', foreign_keys='Rental.renter_id', backref='renter')
    rentals_as_vendor = db.relationship('Rental', foreign_keys='Rental.vendor_id', backref='vendor')
    reviews = db.relationship('Review', foreign_keys='Review.submitter_id', backref='submitter')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')

    def set_password(self, password):
        """Hash and store a plaintext password.

        Args:
            password: The plaintext password to hash.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash.

        Args:
            password: The plaintext password to check.

        Returns:
            True if the password matches, False otherwise (or if no hash is stored).
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def profile_complete(self):
        """Check if the user has filled in all required profile fields."""
        return all([
            self.phone,
            self.date_of_birth,
            self.street_address,
            self.city,
            self.state,
            self.zip_code is not None,
            self.vendor is not None or self.renter is not None
        ])

    def to_dict(self):
        """Serialize the user to a JSON-compatible dictionary.

        Returns:
            Dict with all public user fields including the computed
            ``profile_complete`` flag.
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'auth_provider': self.auth_provider,
            'created_at': self.created_at.isoformat(),
            'date_of_birth': self.date_of_birth,
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'vendor': self.vendor,
            'renter': self.renter,
            'profile_complete': self.profile_complete,
            'picture': self.picture
        }

    def __repr__(self):
        return f'<User {self.name}>'