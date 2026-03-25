from flask import Blueprint, request, jsonify
from services import RentalService

rental_bp = Blueprint('rentals', __name__, url_prefix='/api/rentals')

@rental_bp.route('/', methods=['GET'])
def get_all_rentals():
    """Get all rentals"""
    try:
        rentals = RentalService.get_all_rentals()
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/<int:rental_id>', methods=['GET'])
def get_rental(rental_id):
    """Get a rental by ID"""
    try:
        rental = RentalService.get_rental(rental_id)
        if not rental:
            return jsonify({'error': 'Rental not found'}), 404
        return jsonify(rental.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/renter/<int:renter_id>', methods=['GET'])
def get_rentals_by_renter(renter_id):
    """Get all rentals by a renter"""
    try:
        rentals = RentalService.get_rentals_by_renter(renter_id)
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/vendor/<int:vendor_id>', methods=['GET'])
def get_rentals_by_vendor(vendor_id):
    """Get all rentals offered by a vendor"""
    try:
        rentals = RentalService.get_rentals_by_vendor(vendor_id)
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/status/<status>', methods=['GET'])
def get_rentals_by_status(status):
    """Get all rentals with a specific status"""
    try:
        rentals = RentalService.get_rentals_by_status(status)
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@rental_bp.route('/vendor/<int:vendor_id>/status/<status>', methods=['GET'])
def get_rentals_by_vendor_and_status(vendor_id, status):
    """Get all rentals offered by a vendor with a specific status"""
    try:
        rentals = RentalService.get_rentals_by_vendor_and_status(vendor_id, status)
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/average-price', methods=['GET'])
def get_average_price():
    """Get average price for equipment in a location"""
    try:
        equipment_name = request.args.get('equipment_name')
        location = request.args.get('location')
        
        if not equipment_name or not location:
            return jsonify({'error': 'equipment_name and location are required'}), 400
        
        average_price = RentalService.get_average_price_by_equipment_and_location(equipment_name, location)
        
        if average_price is not None:
            return jsonify({'average_price': round(average_price, 2)}), 200
        else:
            return jsonify({'average_price': None, 'message': 'No data available for this equipment/location combination'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/', methods=['POST'])
def create_rental():
    """Create a new rental"""
    try:
        data = request.get_json()
        rental = RentalService.create_rental(
            data.get('renter_id'),
            data.get('vendor_id'),
            data.get('agreed_price'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('location'),
            data.get('status', 'requesting'),
            data.get('deleted', False)
        )
        return jsonify(rental.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/<int:rental_id>', methods=['PUT'])
def update_rental(rental_id):
    """Update a rental"""
    try:
        data = request.get_json()
        rental = RentalService.update_rental(
            rental_id,
            data.get('status'),
            data.get('location'),
            data.get('agreed_price'),
            data.get('deleted')
        )
        return jsonify(rental.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/<int:rental_id>', methods=['DELETE'])
def delete_rental(rental_id):
    """Delete a rental"""
    try:
        RentalService.delete_rental(rental_id)
        return jsonify({'message': 'Rental deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500