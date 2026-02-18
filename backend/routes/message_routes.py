from flask import Blueprint, request, jsonify
from services import MessageService

message_bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@message_bp.route('/', methods=['GET'])
def get_all_messages():
    """Get all messages"""
    try:
        messages = MessageService.get_all_messages()
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """Get a message by ID"""
    try:
        message = MessageService.get_message(message_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        return jsonify(message.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/inbox/<int:user_id>', methods=['GET'])
def get_messages_for_user(user_id):
    """Get all messages sent to a user"""
    try:
        messages = MessageService.get_messages_for_user(user_id)
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/sent/<int:sender_id>', methods=['GET'])
def get_messages_from_sender(sender_id):
    """Get all messages sent by a user"""
    try:
        messages = MessageService.get_messages_from_sender(sender_id)
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/conversation/<int:user_id1>/<int:user_id2>', methods=['GET'])
def get_conversation(user_id1, user_id2):
    """Get conversation between two users"""
    try:
        messages = MessageService.get_conversation(user_id1, user_id2)
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/', methods=['POST'])
def create_message():
    """Create a new message"""
    try:
        data = request.get_json()
        message = MessageService.create_message(
            data.get('sender_id'),
            data.get('receiver_id'),
            data.get('data')
        )
        return jsonify(message.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    try:
        MessageService.delete_message(message_id)
        return jsonify({'message': 'Message deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500