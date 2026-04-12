from database import db

class RentalHasEquipment(db.Model):
    __tablename__ = 'rental_has_equipment'

    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), primary_key=True)
    equipment_reviewed = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            'equipment_id': self.equipment_id,
            'rental_id': self.rental_id,
            'equipment_reviewed': self.equipment_reviewed
        }

    def __repr__(self):
        return f'<RentalHasEquipment {self.equipment_id}-{self.rental_id}>'