"""
Review model module.

Defines the ``Review`` ORM model for ratings and text reviews that users
submit about equipment or other users. Uses a polymorphic pattern where
``model_type`` ('equipment' or 'user') and ``model_id`` identify the
reviewed entity.
"""

from database import db
from datetime import datetime


class Review(db.Model):
    """A rating and optional text review submitted by a user.

    Reviews are polymorphic: ``model_type`` indicates whether the review
    targets a piece of equipment or another user, and ``model_id`` is
    the corresponding primary key.

    Attributes:
        id: Primary key.
        submitter_id: Foreign key to the User who wrote the review.
        model_type: 'equipment' or 'user' — the type of entity being reviewed.
        model_id: Primary key of the reviewed equipment or user.
        rating: Integer rating from 1 (worst) to 5 (best).
        review: Optional free-text review body.
        date: Timestamp when the review was created.
        deleted: Soft-delete flag; deleted reviews are excluded from queries.
    """

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # 'equipment' or 'user'
    model_id = db.Column(db.Integer, nullable=False)  # FK to equipment.id or users.id
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        """Serialize the review to a JSON-compatible dictionary.

        Returns:
            Dict with all review fields, date in ISO 8601 format.
        """
        return {
            'id': self.id,
            'submitter_id': self.submitter_id,
            'model_type': self.model_type,
            'model_id': self.model_id,
            'rating': self.rating,
            'review': self.review,
            'date': self.date.isoformat(),
            'deleted': self.deleted
        }

    def __repr__(self):
        return f'<Review {self.id}>'