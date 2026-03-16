from flask import Blueprint, request, jsonify
from services import UserService

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = UserService.get_all_users()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a user by ID"""
    try:
        user = UserService.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        user = UserService.create_user(data.get('name'), data.get('email'), data.get('password'), data.get('phone'), data.get('date_of_birth'), data.get('street_address'), data.get('city'), data.get('state'), data.get('zip_code'), data.get('vendor'), data.get('renter'))
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        data = request.get_json()
        user = UserService.update_user(user_id, data.get('name'), data.get('email'), data.get('phone'), data.get('date_of_birth'), data.get('street_address'), data.get('city'), data.get('state'), data.get('zip_code'), data.get('vendor'), data.get('renter'))
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        UserService.delete_user(user_id)
        return jsonify({'message': 'User deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# route to view a user's messages
@user_bp.route('/<int:user_id>/messages', methods=['GET'])
def get_user_messages(user_id):
    """Get messages for a user"""
    try:
        user = UserService.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        messages = user.messages_sent + user.messages_received
        return jsonify([{
            'id': msg.id,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'data': msg.data,
            'send_time': msg.send_time.isoformat()
        } for msg in messages]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

