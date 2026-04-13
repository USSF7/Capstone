from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import EquipmentService
from PIL import Image

equipment_bp = Blueprint('equipment', __name__, url_prefix='/api/equipment')

@equipment_bp.route('/', methods=['GET'])
def get_all_equipment():
    """Get all equipment"""
    try:
        equipment_list = EquipmentService.get_all_equipment()
        return jsonify([e.to_dict() for e in equipment_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """Get equipment by ID"""
    try:
        equipment = EquipmentService.get_equipment(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        return jsonify(equipment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/owner/<int:owner_id>', methods=['GET'])
def get_equipment_by_owner(owner_id):
    """Get all equipment owned by a user"""
    try:
        equipment_list = EquipmentService.get_equipment_by_owner(owner_id)
        return jsonify([e.to_dict() for e in equipment_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/owner/<int:owner_id>/with-rentals', methods=['GET'])
def get_equipment_by_owner_with_rentals(owner_id):
    """Get all equipment owned by a user with active rental details"""
    try:
        result = EquipmentService.get_equipment_by_owner_with_rentals(owner_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@equipment_bp.route('/names', methods=['GET'])
def get_equipment_names():
    """Get static set of equipment names from .config"""
    try:
        names = EquipmentService.get_equipment_names()
        return jsonify({'equipment_names': names}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/', methods=['POST'])
def create_equipment():
    """Create new equipment"""
    try:
        data = request.get_json()
        equipment = EquipmentService.create_equipment(
            data.get('owner_id'),
            data.get('name'),
            data.get('price'),
            data.get('description'),
            data.get('picture'),
            data.get('condition')
        )
        return jsonify(equipment.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['PUT'])
@jwt_required()
def update_equipment(equipment_id):
    """Update equipment"""
    try:
        current_user_id = int(get_jwt_identity())
        equipment = EquipmentService.get_equipment(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        if equipment.owner_id != current_user_id:
            return jsonify({'error': 'Not authorized to update this equipment'}), 403
        data = request.get_json()
        equipment = EquipmentService.update_equipment(
            equipment_id,
            data.get('name'),
            data.get('owner_id'),
            data.get('price'),
            data.get('description'),
            data.get('picture'),
            data.get('condition')
        )
        return jsonify(equipment.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@equipment_bp.route('/picture', methods=['POST'])
def upload_equipment_picture():
    try:
        # Checking if the file exists in the request
        if 'picture_file' not in request.files:
            return jsonify({
                'error': 'No picture file in the request',
                'success': False
            }), 400
        
        # Getting the equipment picture file
        equipmentPicture = request.files['picture_file']

        # Checking if the filename is empty
        if equipmentPicture.filename == '':
            return jsonify({
                'error': 'No selected file',
                'success': False
            }), 400
        
        # Checking if the equipment picture is a valid image type
        ALLOWED_FILE_TYPES = {'jpeg', "png", 'webp'}

        image = Image.open(equipmentPicture)
        image.verify()

        fileFormat = image.format.lower()
        equipmentPicture.seek(0)

        if fileFormat not in ALLOWED_FILE_TYPES:
            return jsonify({
                'error': 'Invalid image',
                'success': False
            }), 400
        
        # Storing the picture in the backend
        pictureFilepath = EquipmentService.upload_equipment_picture(equipmentPicture=equipmentPicture)

        return jsonify({
            'message': 'Equipment picture uploaded successfully',
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

@equipment_bp.route('/picture/delete', methods=['DELETE'])
def delete_equipment_picture():
    try:
        # Get the filepath to the picture
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        filepath = data.get('filepath')

        if not filepath:
            return jsonify({'error': 'Missing filepath'}), 400

        # Deleting the picture
        return EquipmentService.delete_equipment_picture(filepath)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    """Delete equipment"""
    try:
        EquipmentService.delete_equipment(equipment_id)
        return jsonify({'message': 'Equipment deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500