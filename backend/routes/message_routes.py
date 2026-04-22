"""
Message routes module.

Provides endpoints for message management: sending messages, retrieving
inbox/sent messages, fetching conversations between two users, and
querying messages by rental.

Routes:
    GET    /api/messages/                                  -- List all messages.
    GET    /api/messages/<id>                              -- Get message by ID.
    GET    /api/messages/inbox/<user_id>                   -- Get messages received by user.
    GET    /api/messages/sent/<sender_id>                  -- Get messages sent by user.
    GET    /api/messages/conversation/<id1>/<id2>          -- Get conversation between two users.
    GET    /api/messages/rental/<rental_id>                -- Get messages for a rental.
    POST   /api/messages/                                  -- Send a new message.
    DELETE /api/messages/<id>                              -- Delete a message.
"""

from flask import Blueprint, request, jsonify
from services import MessageService

message_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


@message_bp.route('/', methods=['GET'])
def get_all_messages():
    """Get all messages.

    Returns:
        200: List of message dicts.
    """
    try:
        messages = MessageService.get_all_messages()
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """Get a single message by ID.

    Args:
        message_id: The message's primary key.

    Returns:
        200: Message dict.
        404: Message not found.
    """
    try:
        message = MessageService.get_message(message_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify(message.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/inbox/<int:user_id>', methods=['GET'])
def get_messages_for_user(user_id):
    """Get all messages received by a user (inbox).

    Args:
        user_id: The receiver User's primary key.

    Returns:
        200: List of message dicts.
    """
    try:
        messages = MessageService.get_messages_for_user(user_id)
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/sent/<int:sender_id>', methods=['GET'])
def get_messages_from_sender(sender_id):
    """Get all messages sent by a user.

    Args:
        sender_id: The sender User's primary key.

    Returns:
        200: List of message dicts.
    """
    try:
        messages = MessageService.get_messages_from_sender(sender_id)
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/conversation/<int:user_id1>/<int:user_id2>', methods=['GET'])
def get_conversation(user_id1, user_id2):
    """Get the conversation thread between two users.

    Query params: ``rental_id`` (required) to scope the conversation
    to a specific rental.

    Args:
        user_id1: First participant's User ID.
        user_id2: Second participant's User ID.

    Returns:
        200: List of message dicts ordered by send_time ascending.
        400: Missing rental_id.
    """
    try:
        rental_id = request.args.get('rental_id', type=int)
        messages = MessageService.get_conversation(user_id1, user_id2, rental_id=rental_id)
        return jsonify([m.to_dict() for m in messages]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/rental/<int:rental_id>', methods=['GET'])
def get_messages_by_rental(rental_id):
    """Get all messages associated with a rental, ordered chronologically.

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: List of message dicts.
    """
    try:
        messages = MessageService.get_messages_by_rental(rental_id)
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/', methods=['POST'])
def create_message():
    """Send a new message within a rental conversation.

    Expects JSON body with ``sender_id``, ``receiver_id``, ``data`` (text),
    and ``rental_id``.

    Returns:
        201: Created message dict.
        400: Validation error (e.g. missing fields, self-message).
    """
    try:
        data = request.get_json()
        message = MessageService.create_message(
            data.get('sender_id'),
            data.get('receiver_id'),
            data.get('data'),
            data.get('rental_id')
        )
        return jsonify(message.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Permanently delete a message.

    Args:
        message_id: The message's primary key.

    Returns:
        200: Success message.
        404: Message not found.
    """
    try:
        MessageService.delete_message(message_id)
        return jsonify({'message': 'Message deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500