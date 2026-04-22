"""
Message service module.

Business logic for message CRUD operations. Messages are always scoped
to a rental conversation between two users.
"""

from models import Message
from database import db


class MessageService:
    """Business logic for Message management.

    All methods are static — no instance state is needed.
    """

    @staticmethod
    def create_message(sender_id, receiver_id, data, rental_id=None):
        """Send a new message within a rental conversation.

        Args:
            sender_id: Primary key of the sending User.
            receiver_id: Primary key of the receiving User.
            data: The message text content.
            rental_id: Primary key of the associated Rental (required).

        Returns:
            The created Message instance.

        Raises:
            ValueError: If required fields missing, self-message, or no rental_id.
        """
        if not all([sender_id, receiver_id, data]):
            raise ValueError("sender_id, receiver_id, and data are required")
        if sender_id == receiver_id:
            raise ValueError("Cannot send message to yourself")
        if rental_id is None:
            raise ValueError("rental_id is required")
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            rental_id=rental_id,
            data=data,
        )
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
    def get_conversation(user_id1, user_id2, rental_id=None):
        """Get the conversation thread between two users for a rental.

        Messages are returned in chronological order (ascending send_time).

        Args:
            user_id1: First participant's User ID.
            user_id2: Second participant's User ID.
            rental_id: Rental ID to scope the conversation (required).

        Returns:
            List of Message instances ordered by send_time.

        Raises:
            ValueError: If rental_id is not provided.
        """
        if rental_id is None:
            raise ValueError("rental_id is required")

        query = Message.query.filter(
            ((Message.sender_id == user_id1) & (Message.receiver_id == user_id2)) |
            ((Message.sender_id == user_id2) & (Message.receiver_id == user_id1))
        )
        if rental_id is not None:
            query = query.filter(Message.rental_id == rental_id)

        return query.order_by(Message.send_time.asc()).all()

    @staticmethod
    def get_messages_by_rental(rental_id):
        """Get all messages associated with a rental, ordered chronologically.

        Args:
            rental_id: The rental's primary key.

        Returns:
            List of Message instances ordered by send_time ascending.
        """
        return Message.query.filter_by(rental_id=rental_id).order_by(Message.send_time.asc()).all()

    @staticmethod
    def delete_message(message_id):
        """Permanently delete a message.

        Args:
            message_id: The message's primary key.

        Returns:
            True on success.

        Raises:
            ValueError: If message not found.
        """
        message = Message.query.get(message_id)
        if not message:
            raise ValueError("Message not found")
        
        db.session.delete(message)
        db.session.commit()
        return True