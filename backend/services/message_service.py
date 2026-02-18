from models import Message
from database import db

class MessageService:
    """Service layer for Message business logic"""

    @staticmethod
    def create_message(sender_id, receiver_id, data):
        """Create a new message"""
        if not all([sender_id, receiver_id, data]):
            raise ValueError("sender_id, receiver_id, and data are required")
        if sender_id == receiver_id:
            raise ValueError("Cannot send message to yourself")
        
        message = Message(sender_id=sender_id, receiver_id=receiver_id, data=data)
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def get_message(message_id):
        """Get a message by ID"""
        return Message.query.get(message_id)

    @staticmethod
    def get_all_messages():
        """Get all messages"""
        return Message.query.all()

    @staticmethod
    def get_messages_for_user(user_id):
        """Get all messages sent to a user"""
        return Message.query.filter_by(receiver_id=user_id).all()

    @staticmethod
    def get_messages_from_sender(sender_id):
        """Get all messages sent by a user"""
        return Message.query.filter_by(sender_id=sender_id).all()

    @staticmethod
    def get_conversation(user_id1, user_id2):
        """Get conversation between two users"""
        return Message.query.filter(
            ((Message.sender_id == user_id1) & (Message.receiver_id == user_id2)) |
            ((Message.sender_id == user_id2) & (Message.receiver_id == user_id1))
        ).all()

    @staticmethod
    def delete_message(message_id):
        """Delete a message"""
        message = Message.query.get(message_id)
        if not message:
            raise ValueError("Message not found")
        
        db.session.delete(message)
        db.session.commit()
        return True