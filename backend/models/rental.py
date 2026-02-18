from database import db
from datetime import datetime

class Rental(db.Model):
    __tablename__ = 'rentals'

    id = db.Column(db.Integer, primary_key=True)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    location = db.Column(db.String(500), nullable=True)
    agreed_price = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, active, returned, disputed, canceled

    # Relationships
    equipment_list = db.relationship('RentalHasEquipment', backref='rental')

    def to_dict(self):
        return {
            'id': self.id,
            'renter_id': self.renter_id,
            'vendor_id': self.vendor_id,
            'event_id': self.event_id,
            'location': self.location,
            'agreed_price': float(self.agreed_price),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status
        }

    def __repr__(self):
        return f'<Rental {self.id}>'