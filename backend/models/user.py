from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_birth = db.Column(db.String(10), nullable=True)
    street_address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.Integer, nullable=True)
    vendor = db.Column(db.Boolean, nullable=True)
    renter = db.Column(db.Boolean, nullable=True)

    # Relationships
    equipment = db.relationship('Equipment', foreign_keys='Equipment.owner_id', backref='owner')
    events = db.relationship('Event', backref='user')
    rentals_as_renter = db.relationship('Rental', foreign_keys='Rental.renter_id', backref='renter')
    rentals_as_vendor = db.relationship('Rental', foreign_keys='Rental.vendor_id', backref='vendor')
    reviews = db.relationship('Review', foreign_keys='Review.submitter_id', backref='submitter')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')
    requests = db.relationship('Request', foreign_keys='Request.requester_id', backref='requester')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'date_of_birth': self.date_of_birth,
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'vendor': self.vendor,
            'renter': self.renter
        }

    def __repr__(self):
        return f'<User {self.name}>'