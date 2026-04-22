"""
Message model module.

Defines the ``Message`` ORM model for direct messages exchanged between
users within the context of a rental transaction.
"""

from database import db
from datetime import datetime


class Message(db.Model):
    """A direct message sent from one user to another within a rental.

    Attributes:
        id: Primary key.
        sender_id: Foreign key to the User who sent the message.
        receiver_id: Foreign key to the User who receives the message.
        rental_id: Foreign key to the Rental this conversation belongs to.
        data: The message text content.
        send_time: Timestamp when the message was sent.
    """

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), nullable=True)
    data = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Serialize the message to a JSON-compatible dictionary.

        Returns:
            Dict with all message fields, send_time in ISO 8601 format.
        """
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