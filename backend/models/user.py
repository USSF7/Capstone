from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.name}>'