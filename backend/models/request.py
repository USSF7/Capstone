from database import db
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    max_price = db.Column(db.Numeric(10, 2), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='created')  # created, completed

    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'event_id': self.event_id,
            'name': self.name,
            'max_price': float(self.max_price),
            'count': self.count,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'location': self.location,
            'status': self.status
        }

    def __repr__(self):
        return f'<Request {self.name}>'