from database import db

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Relationships
    # Note: reviews are accessed via query filter on model_type='equipment' and model_id=equipment.id
    rentals = db.relationship('RentalHasEquipment', backref='equipment')

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'status': 'available' if not self.rentals else 'rented',
            'transaction_id': self.rentals[0].rental_id if self.rentals else None
        }

    def __repr__(self):
        return f'<Equipment {self.name}>'