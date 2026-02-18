from database import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Relationships
    rentals = db.relationship('Rental', backref='event')
    requests = db.relationship('Request', backref='event')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'date': self.date.isoformat()
        }

    def __repr__(self):
        return f'<Event {self.name}>'