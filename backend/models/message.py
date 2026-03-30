from database import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), nullable=True)
    data = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'rental_id': self.rental_id,
            'data': self.data,
            'send_time': self.send_time.isoformat()
        }

    def __repr__(self):
        return f'<Message {self.id}>'