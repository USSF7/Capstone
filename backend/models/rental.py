from datetime import datetime, timezone

from database import db

class Rental(db.Model):
    __tablename__ = 'rentals'

    id = db.Column(db.Integer, primary_key=True)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.Column(db.String(500), nullable=True)
    meeting_lat = db.Column(db.Float, nullable=True)
    meeting_lng = db.Column(db.Float, nullable=True)
    agreed_price = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='requesting')  # requesting, accepted, active, returned, disputed, denied, cancelled
    renter_approved = db.Column(db.Boolean, nullable=False, default=False)
    vendor_approved = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    equipment_list = db.relationship('RentalHasEquipment', backref='rental')

    def to_dict(self):
        def to_utc_iso(value):
            if value is None:
                return None
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
            return value.isoformat().replace('+00:00', 'Z')

        return {
            'id': self.id,
            'renter_id': self.renter_id,
            'vendor_id': self.vendor_id,
            'location': self.location,
            'meeting_lat': self.meeting_lat,
            'meeting_lng': self.meeting_lng,
            'agreed_price': float(self.agreed_price),
            'start_date': to_utc_iso(self.start_date),
            'end_date': to_utc_iso(self.end_date),
            'status': self.status,
            'renter_approved': self.renter_approved,
            'vendor_approved': self.vendor_approved,
            'mutual_approved': self.renter_approved and self.vendor_approved,
            'deleted': self.deleted
        }

    def __repr__(self):
        return f'<Rental {self.id}>'