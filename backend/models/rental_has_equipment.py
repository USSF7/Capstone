"""
Rental-Equipment association model module.

Defines the ``RentalHasEquipment`` link table that implements the
many-to-many relationship between rentals and equipment items.
Also tracks whether the renter has reviewed each individual piece
of equipment in the rental.
"""

from database import db


class RentalHasEquipment(db.Model):
    """Association between a Rental and a piece of Equipment.

    Uses a composite primary key of (equipment_id, rental_id).

    Attributes:
        equipment_id: Foreign key to the Equipment item.
        rental_id: Foreign key to the Rental transaction.
        equipment_reviewed: Whether the renter has reviewed this equipment
            for this rental.
    """

    __tablename__ = 'rental_has_equipment'

    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), primary_key=True)
    equipment_reviewed = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        """Serialize the association to a JSON-compatible dictionary.

        Returns:
            Dict with equipment_id, rental_id, and equipment_reviewed flag.
        """
        return {
            'equipment_id': self.equipment_id,
            'rental_id': self.rental_id,
            'equipment_reviewed': self.equipment_reviewed
        }

    def __repr__(self):
        return f'<RentalHasEquipment {self.equipment_id}-{self.rental_id}>'