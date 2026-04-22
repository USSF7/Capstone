"""
Rental model module.

Defines the ``Rental`` ORM model representing a rental transaction between
a renter and a vendor. Tracks status lifecycle (requesting -> active ->
returned), mutual approval, meeting location, and review flags.
"""

from datetime import datetime, timezone

from database import db


class Rental(db.Model):
    """A rental transaction between a renter and a vendor.

    Rentals progress through a status lifecycle:
    requesting -> active -> returned (happy path), or may be denied,
    cancelled, or disputed. Both parties must approve before a rental
    becomes active.

    Attributes:
        id: Primary key.
        renter_id: Foreign key to the User renting the equipment.
        vendor_id: Foreign key to the User who owns the equipment.
        location: Text description of the meeting location.
        meeting_lat: Latitude of the agreed meeting point.
        meeting_lng: Longitude of the agreed meeting point.
        agreed_price: Negotiated rental price in USD.
        start_date: When the rental period begins.
        end_date: When the rental period ends.
        status: Current lifecycle status ('requesting', 'active', 'returned',
            'disputed', 'denied', 'cancelled').
        renter_approved: Whether the renter has approved the current terms.
        vendor_approved: Whether the vendor has approved the current terms.
        renter_reviewed: Whether the renter has submitted their review.
        vendor_reviewed: Whether the vendor has submitted their review.
        deleted: Soft-delete flag.
    """

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
    status = db.Column(db.String(50), default='requesting')  # requesting, active, returned, disputed, denied, cancelled
    renter_approved = db.Column(db.Boolean, nullable=False, default=False)
    vendor_approved = db.Column(db.Boolean, nullable=False, default=False)
    renter_reviewed = db.Column(db.Boolean, nullable=False, default=False)
    vendor_reviewed = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    equipment_list = db.relationship('RentalHasEquipment', backref='rental')

    def _get_status_text(self, viewer_id=None):
        """
        Get contextualized status text based on who is viewing the rental.
        If viewer_id is provided, text reflects the viewer's role (renter vs vendor).
        Otherwise, returns generic status text.
        """
        is_renter = viewer_id == self.renter_id if viewer_id else None
        is_vendor = viewer_id == self.vendor_id if viewer_id else None

        if self.status == 'requesting':
            if is_renter:
                return "You have requested the rental"
            elif is_vendor:
                return "A renter has requested your equipment"
            return "Rental request pending"
        elif self.status == 'active':
            def to_utc(value):
                if value is None:
                    return None
                if value.tzinfo is None:
                    return value.replace(tzinfo=timezone.utc)
                return value.astimezone(timezone.utc)

            now = datetime.now(timezone.utc)
            start = to_utc(self.start_date)
            end = to_utc(self.end_date)

            if now < start:
                if is_renter:
                    return "Your rental is confirmed and starts soon"
                elif is_vendor:
                    return "A confirmed rental starts soon"
                return "Rental is confirmed and starts soon"

            if now > end:
                if is_renter:
                    return "Your rental period has ended"
                elif is_vendor:
                    return "This rental period has ended. Please mark as returned"
                return "Rental period has ended"

            if is_renter:
                return "Your rental is currently active"
            elif is_vendor:
                return "Your equipment is currently rented"
            return "Rental is currently active"
        elif self.status == 'returned':
            return "Rental has been completed"
        elif self.status == 'disputed':
            return "Rental is being disputed"
        elif self.status == 'denied':
            if is_renter:
                return "Vendor has denied your request"
            elif is_vendor:
                return "You have denied the request"
            return "Rental request denied"
        elif self.status == 'cancelled':
            if is_renter:
                return "You cancelled this rental"
            elif is_vendor:
                return "Renter cancelled this rental"
            return "Rental cancelled"
        
        return "Rental status updated"

    def to_dict(self, viewer_id=None):
        """Serialize the rental to a JSON-compatible dictionary.

        Args:
            viewer_id: If provided, includes a contextualized ``status_text``
                describing the rental from this user's perspective.

        Returns:
            Dict with all rental fields, dates in ISO 8601 UTC format,
            and the computed ``mutual_approved`` and ``status_text`` fields.
        """
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
            'status_text': self._get_status_text(viewer_id),
            'renter_approved': self.renter_approved,
            'vendor_approved': self.vendor_approved,
            'mutual_approved': self.renter_approved and self.vendor_approved,
            'renter_reviewed': self.renter_reviewed,
            'vendor_reviewed': self.vendor_reviewed,
            'deleted': self.deleted
        }

    def __repr__(self):
        return f'<Rental {self.id}>'