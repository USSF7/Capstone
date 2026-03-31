from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
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
    max_travel_distance = db.Column(db.Integer, default=0, nullable=True)

    # Relationships
    equipment = db.relationship('Equipment', foreign_keys='Equipment.owner_id', backref='owner')
    rentals_as_renter = db.relationship('Rental', foreign_keys='Rental.renter_id', backref='renter')
    rentals_as_vendor = db.relationship('Rental', foreign_keys='Rental.vendor_id', backref='vendor')
    reviews = db.relationship('Review', foreign_keys='Review.submitter_id', backref='submitter')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
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
            self.vendor is not None or self.renter is not None,
        ])

    def to_dict(self):
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
            'max_travel_distance': self.max_travel_distance,
            'profile_complete': self.profile_complete,
        }

    def __repr__(self):
        return f'<User {self.name}>'