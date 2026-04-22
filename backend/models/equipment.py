"""
Equipment model module.

Defines the ``Equipment`` ORM model representing items that vendors list
for rent. Each piece of equipment belongs to a single owner (User) and
can be associated with rentals through the ``RentalHasEquipment`` link table.
"""

from database import db
from sqlalchemy import func

from models.review import Review


class Equipment(db.Model):
    """A piece of equipment listed for rent on the marketplace.

    Attributes:
        id: Primary key.
        owner_id: Foreign key to the vendor User who owns this equipment.
        name: Display name / title of the equipment listing.
        price: Daily rental price in USD.
        description: Free-text description of the equipment.
        picture: Relative path to the equipment image.
        condition: Condition label (e.g. 'Mint', 'Above Average', 'Average', 'Below Average').
        ai_review_summary: Cached AI-generated summary of reviews for this equipment.
        ai_review_summary_updated_at: Timestamp when the AI summary was last refreshed.
    """

    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    description = db.Column(db.String(1000), nullable=True)
    picture = db.Column(db.String(500), nullable=True)
    condition = db.Column(db.String(50), nullable=False)
    ai_review_summary = db.Column(db.Text, nullable=True)
    ai_review_summary_updated_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    # Note: reviews are accessed via query filter on model_type='equipment' and model_id=equipment.id
    rentals = db.relationship('RentalHasEquipment', backref='equipment')

    def to_dict(self):
        """Serialize the equipment to a JSON-compatible dictionary.

        Computes the average rating and review count on the fly by querying
        the ``reviews`` table filtered to this equipment's ID.

        Returns:
            Dict with equipment fields plus computed ``average_rating``,
            ``rating_count``, ``status``, and ``transaction_id``.
        """
        avg_rating, rating_count = (
            db.session.query(func.avg(Review.rating), func.count(Review.id))
            .filter(
                Review.model_type == 'equipment',
                Review.model_id == self.id,
                Review.deleted == False,
            )
            .first()
        )

        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'price': float(self.price),
            'description': self.description,
            'picture': self.picture,
            'condition': self.condition,
            'status': 'available' if not self.rentals else 'rented',
            'transaction_id': self.rentals[0].rental_id if self.rentals else None,
            'average_rating': round(float(avg_rating), 1) if avg_rating is not None else None,
            'rating_count': int(rating_count or 0),
        }

    def __repr__(self):
        return f'<Equipment {self.name}>'