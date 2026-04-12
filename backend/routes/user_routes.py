from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services import UserService
from PIL import Image

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
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
        user = UserService.create_user(data.get('name'), data.get('email'), data.get('password'), data.get('phone'), data.get('date_of_birth'), data.get('street_address'), data.get('city'), data.get('state'), data.get('zip_code'), data.get('vendor'), data.get('renter'), data.get('picture'))
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
        user = UserService.update_user(user_id, data.get('name'), data.get('email'), data.get('phone'), data.get('date_of_birth'), data.get('street_address'), data.get('city'), data.get('state'), data.get('zip_code'), data.get('vendor'), data.get('renter'), data.get('max_travel_distance'), data.get('picture'))
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
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

@user_bp.route('/picture', methods=['POST'])
def upload_user_picture():
    try:
        # Checking if the file exists in the request
        if 'picture_file' not in request.files:
            return jsonify({
                'error': 'No picture file in the request',
                'success': False
            }), 400
        
        # Getting the user's picture file
        userPicture = request.files['picture_file']

        # Checking if the filename is empty
        if userPicture.filename == '':
            return jsonify({
                'error': 'No selected file',
                'success': False
            }), 400
        
        # Checking if the equipment picture is a valid image type
        ALLOWED_FILE_TYPES = {'jpeg', "png", 'webp'}

        image = Image.open(userPicture)
        image.verify()

        fileFormat = image.format.lower()
        userPicture.seek(0)

        if fileFormat not in ALLOWED_FILE_TYPES:
            return jsonify({
                'error': 'Invalid image',
                'success': False
            }), 400
        
        # Storing the picture in the backend
        pictureFilepath = UserService.upload_user_picture(userPicture=userPicture)

        return jsonify({
            'message': 'User picture uploaded successfully',
            'success': True,
            'filename': pictureFilepath
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 404
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@user_bp.route('/picture/delete', methods=['DELETE'])
def delete_user_picture():
    try:
        # Get the filepath to the picture
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        filepath = data.get('filepath')

        if not filepath:
            return jsonify({'error': 'Missing filepath'}), 400

        # Deleting the picture
        return UserService.delete_user_picture(filepath)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500