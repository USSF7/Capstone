"""
Equipment routes module.

Provides CRUD endpoints for equipment management, picture upload/delete,
owner-based queries, equipment name listing, and owner authorization checks.

Routes:
    GET    /api/equipment/                         -- List all equipment.
    GET    /api/equipment/<id>                     -- Get equipment by ID.
    GET    /api/equipment/owner/<id>               -- Get equipment by owner.
    GET    /api/equipment/owner/<id>/with-rentals  -- Get owner's equipment with active rental info.
    GET    /api/equipment/names                    -- Get static equipment name list from config.
    POST   /api/equipment/                         -- Create new equipment.
    PUT    /api/equipment/<id>                     -- Update equipment (owner only, JWT required).
    DELETE /api/equipment/<id>                     -- Delete equipment.
    POST   /api/equipment/picture                  -- Upload an equipment picture.
    DELETE /api/equipment/picture/delete            -- Delete an equipment picture.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import EquipmentService
from PIL import Image

equipment_bp = Blueprint('equipment', __name__, url_prefix='/api/equipment')


@equipment_bp.route('/', methods=['GET'])
def get_all_equipment():
    """Get all equipment listings.

    Returns:
        200: List of equipment dicts.
    """
    try:
        equipment_list = EquipmentService.get_all_equipment()
        return jsonify([e.to_dict() for e in equipment_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """Get a single equipment listing by ID.

    Args:
        equipment_id: The equipment's primary key.

    Returns:
        200: Equipment dict.
        404: Equipment not found.
    """
    try:
        equipment = EquipmentService.get_equipment(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        return jsonify(equipment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/owner/<int:owner_id>', methods=['GET'])
def get_equipment_by_owner(owner_id):
    """Get all equipment owned by a specific vendor.

    Args:
        owner_id: The owner User's primary key.

    Returns:
        200: List of equipment dicts.
    """
    try:
        equipment_list = EquipmentService.get_equipment_by_owner(owner_id)
        return jsonify([e.to_dict() for e in equipment_list]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/owner/<int:owner_id>/with-rentals', methods=['GET'])
def get_equipment_by_owner_with_rentals(owner_id):
    """Get all equipment owned by a vendor with active rental details.

    Each equipment dict includes an ``active_rental`` object (or null)
    with the renter name and rental dates.

    Args:
        owner_id: The owner User's primary key.

    Returns:
        200: List of equipment dicts with active rental info.
    """
    try:
        result = EquipmentService.get_equipment_by_owner_with_rentals(owner_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@equipment_bp.route('/names', methods=['GET'])
def get_equipment_names():
    """Get the predefined list of equipment names from the .config file.

    Returns:
        200: Dict with an ``equipment_names`` list.
    """
    try:
        names = EquipmentService.get_equipment_names()
        return jsonify({'equipment_names': names}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/', methods=['POST'])
def create_equipment():
    """Create a new equipment listing.

    Expects JSON body with ``owner_id``, ``name``, ``price``, and optional
    ``description``, ``picture``, ``condition``.

    Returns:
        201: Created equipment dict.
        400: Validation error.
    """
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
    """Update an existing equipment listing. Only the owner may update.

    Requires JWT authentication. Verifies the authenticated user is the
    equipment's owner before applying changes.

    Args:
        equipment_id: The equipment's primary key.

    Returns:
        200: Updated equipment dict.
        403: Not authorized (not the owner).
        404: Equipment not found.
    """
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
    """Upload an equipment picture.

    Expects a multipart form with a ``picture_file`` field containing
    a JPEG, PNG, or WebP image.

    Returns:
        200: Success message with the stored file path.
        400: Missing file or invalid image type.
    """
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
    """Delete an equipment picture from disk.

    Expects JSON body with a ``filepath`` field.

    Returns:
        200: Success message.
        400: Missing filepath.
        404: File not found.
    """
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
    """Delete an equipment listing and its associated picture.

    Args:
        equipment_id: The equipment's primary key.

    Returns:
        200: Success message.
        404: Equipment not found.
    """
    try:
        EquipmentService.delete_equipment(equipment_id)
        return jsonify({'message': 'Equipment deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500