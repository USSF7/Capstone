from flask import Blueprint, request, jsonify
from services import EquipmentService

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
        equipment = EquipmentService.create_equipment(data.get('owner_id'), data.get('name'))
        return jsonify(equipment.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['PUT'])
def update_equipment(equipment_id):
    """Update equipment"""
    try:
        data = request.get_json()
        equipment = EquipmentService.update_equipment(equipment_id, data.get('name'), data.get('owner_id'))
        return jsonify(equipment.to_dict()), 200
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