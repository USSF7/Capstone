from database import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # 'equipment' or 'user'
    model_id = db.Column(db.Integer, nullable=False)  # FK to equipment.id or users.id
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'submitter_id': self.submitter_id,
            'model_type': self.model_type,
            'model_id': self.model_id,
            'rating': self.rating,
            'review': self.review,
            'date': self.date.isoformat()
        }

    def __repr__(self):
        return f'<Review {self.id}>'