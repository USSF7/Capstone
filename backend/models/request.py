from database import db
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    max_price = db.Column(db.Numeric(10, 2), nullable=False)
    min_price = db.Column(db.Numeric(10, 2), nullable=True)
    count = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='created')  # created, completed

    def to_dict(self):
        data = {
            'id': self.id,
            'requester_id': self.requester_id,
            'event_id': self.event_id,
            'name': self.name,
            'max_price': float(self.max_price),
            'min_price': float(self.min_price) if self.min_price is not None else None,
            'count': self.count,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'location': self.location,
            'comments': self.comments,
            'status': self.status
        }
        # include the event name if the relationship is loaded
        try:
            data['event_name'] = self.event.name
        except Exception:
            data['event_name'] = None
        return data

    def __repr__(self):
        return f'<Request {self.name}>'