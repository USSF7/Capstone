"""
Rental routes module.

Provides endpoints for rental lifecycle management: creating rental requests,
approving/denying, updating terms, marking as returned, cancelling, and
querying rentals by renter, vendor, or status. Also supports equipment
availability checks and average price lookups.

Routes:
    GET    /api/rentals/                                    -- List all rentals.
    GET    /api/rentals/<id>                                -- Get rental by ID.
    GET    /api/rentals/rental_equipment/<id>               -- Get rental with equipment (JWT).
    GET    /api/rentals/renter/<id>                         -- Get rentals by renter (JWT).
    GET    /api/rentals/renter_equipment/<id>               -- Get renter's rentals with equipment (JWT).
    GET    /api/rentals/vendor/<id>                         -- Get rentals by vendor (JWT).
    GET    /api/rentals/status/<status>                     -- Get rentals by status.
    GET    /api/rentals/vendor/<id>/status/<status>         -- Get vendor's rentals by status (JWT).
    GET    /api/rentals/vendor/<id>/equipment-availability  -- Check equipment availability (JWT).
    GET    /api/rentals/average-price                       -- Get average rental price for equipment.
    POST   /api/rentals/                                    -- Create a new rental request (JWT).
    PUT    /api/rentals/<id>                                -- Update a rental (JWT).
    PUT    /api/rentals/switch-renter-review-status/<id>    -- Toggle renter review flag (JWT).
    PUT    /api/rentals/switch-vendor-review-status/<id>    -- Toggle vendor review flag (JWT).
    PUT    /api/rentals/switch-equipment-review-status/<id> -- Toggle equipment review flag (JWT).
    DELETE /api/rentals/<id>                                -- Soft-delete a rental.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import RentalService

rental_bp = Blueprint('rentals', __name__, url_prefix='/api/rentals')


@rental_bp.route('/', methods=['GET'])
def get_all_rentals():
    """Get all rentals.

    Returns:
        200: List of rental dicts.
    """
    try:
        rentals = RentalService.get_all_rentals()
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/<int:rental_id>', methods=['GET'])
def get_rental(rental_id):
    """Get a single rental by ID.

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Rental dict.
        404: Rental not found.
    """
    try:
        rental = RentalService.get_rental(rental_id)
        if not rental:
            return jsonify({'error': 'Rental not found'}), 404
        return jsonify(rental.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@rental_bp.route('/rental_equipment/<int:rental_id>', methods=['GET'])
@jwt_required()
def get_rental_with_equipment(rental_id):
    """Get a rental with its attached equipment list.

    Only accessible by the renter or vendor of the rental. Includes
    contextualized status text for the authenticated user.

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Rental dict with an ``equipment`` list and ``status_text``.
        403: User is not a participant in this rental.
        404: Rental not found.
    """
    try:
        current_user_id = int(get_jwt_identity())
        rental_record = RentalService.get_rental(rental_id)
        if not rental_record:
            return jsonify({'error': 'Rental not found'}), 404

        if current_user_id not in [rental_record.renter_id, rental_record.vendor_id]:
            return jsonify({'error': 'Forbidden: You are not part of this rental'}), 403

        rental = RentalService.get_rental_with_equipment(rental_id)
        if not rental:
            return jsonify({'error': 'Rental not found'}), 404
        # Add status_text to the response
        rental['status_text'] = rental_record._get_status_text(current_user_id)
        return jsonify(rental), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/renter/<int:renter_id>', methods=['GET'])
@jwt_required()
def get_rentals_by_renter(renter_id):
    """Get all rentals where the given user is the renter.

    Args:
        renter_id: The renter User's primary key.

    Returns:
        200: List of rental dicts with viewer-contextualized status text.
    """
    try:
        current_user_id = int(get_jwt_identity())
        rentals = RentalService.get_rentals_by_renter(renter_id)
        return jsonify([r.to_dict(viewer_id=current_user_id) for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@rental_bp.route('/renter_equipment/<int:renter_id>', methods=['GET'])
@jwt_required()
def get_rentals_with_equipment_by_renter(renter_id):
    """Get all rentals by a renter with their attached equipment lists.

    Each rental dict includes an ``equipment`` list and ``status_text``.

    Args:
        renter_id: The renter User's primary key.

    Returns:
        200: List of rental dicts with equipment and status text.
    """
    try:
        current_user_id = int(get_jwt_identity())
        rentals = RentalService.get_rentals_by_renter_with_equipment(renter_id)
        # Add status_text to each rental in the response
        for rental_dict in rentals:
            rental_id = rental_dict.get('id')
            rental_obj = RentalService.get_rental(rental_id)
            if rental_obj:
                rental_dict['status_text'] = rental_obj._get_status_text(current_user_id)
        return jsonify(rentals), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/vendor/<int:vendor_id>', methods=['GET'])
@jwt_required()
def get_rentals_by_vendor(vendor_id):
    """Get all rentals where the given user is the vendor.

    Args:
        vendor_id: The vendor User's primary key.

    Returns:
        200: List of rental dicts with viewer-contextualized status text.
    """
    try:
        current_user_id = int(get_jwt_identity())
        rentals = RentalService.get_rentals_by_vendor(vendor_id)
        return jsonify([r.to_dict(viewer_id=current_user_id) for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/status/<status>', methods=['GET'])
def get_rentals_by_status(status):
    """Get all rentals matching a specific status.

    Args:
        status: Rental status string (e.g. 'requesting', 'active', 'returned').

    Returns:
        200: List of rental dicts.
    """
    try:
        rentals = RentalService.get_rentals_by_status(status)
        return jsonify([r.to_dict() for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@rental_bp.route('/vendor/<int:vendor_id>/status/<status>', methods=['GET'])
@jwt_required()
def get_rentals_by_vendor_and_status(vendor_id, status):
    """Get all rentals for a vendor filtered by status.

    Args:
        vendor_id: The vendor User's primary key.
        status: Rental status to filter by.

    Returns:
        200: List of rental dicts.
    """
    try:
        current_user_id = int(get_jwt_identity())
        rentals = RentalService.get_rentals_by_vendor_and_status(vendor_id, status)
        return jsonify([r.to_dict(viewer_id=current_user_id) for r in rentals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/vendor/<int:vendor_id>/equipment-availability', methods=['GET'])
@jwt_required()
def get_vendor_equipment_availability(vendor_id):
    """Check availability of a vendor's equipment for a date range.

    Query params: ``start_date``, ``end_date`` (ISO 8601).

    Args:
        vendor_id: The vendor User's primary key.

    Returns:
        200: Dict with ``equipment`` list, each item includes ``available``
            boolean and optional ``unavailable_reason``.
        400: Missing or invalid date parameters.
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        equipment = RentalService.get_vendor_equipment_with_availability(vendor_id, start_date, end_date)
        return jsonify({'equipment': equipment}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/average-price', methods=['GET'])
def get_average_price():
    """Get the average rental price for a type of equipment in a location.

    Query params: ``equipment_name``, ``location``.

    Returns:
        200: Dict with ``average_price`` (float or null).
        400: Missing required query parameters.
    """
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
@jwt_required()
def create_rental():
    """Create a new rental request.

    The authenticated user becomes the renter. Expects JSON body with
    ``vendor_id``, ``agreed_price``, ``start_date``, ``end_date``,
    ``equipment_ids``, and optional ``location``, ``meeting_lat``,
    ``meeting_lng``.

    Returns:
        201: Created rental dict.
        400: Validation error (e.g. same renter/vendor, date conflicts).
    """
    try:
        data = request.get_json()
        renter_id = int(get_jwt_identity())
        rental = RentalService.create_rental(
            renter_id,
            data.get('vendor_id'),
            data.get('agreed_price'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('location'),
            'requesting',
            data.get('deleted', False),
            data.get('equipment_ids'),
            data.get('meeting_lat'),
            data.get('meeting_lng')
        )
        return jsonify(rental.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/switch-renter-review-status/<int:rental_id>', methods=['PUT'])
@jwt_required()
def switch_renter_review_status(rental_id):
    """Toggle the renter_reviewed flag on a rental.

    Expects JSON body with ``renter_review_status`` (boolean).

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Updated rental dict.
    """
    try:
        data = request.get_json()
        rental = RentalService.switch_renter_review_status(rental_id, data.get("renter_review_status"))
        return jsonify(rental.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@rental_bp.route('/switch-vendor-review-status/<int:rental_id>', methods=['PUT'])
@jwt_required()
def switch_vendor_review_status(rental_id):
    """Toggle the vendor_reviewed flag on a rental.

    Expects JSON body with ``vendor_review_status`` (boolean).

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Updated rental dict.
    """
    try:
        data = request.get_json()
        rental = RentalService.switch_vendor_review_status(rental_id, data.get("vendor_review_status"))
        return jsonify(rental.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@rental_bp.route('/switch-equipment-review-status/<int:rental_id>', methods=['PUT'])
@jwt_required()
def switch_equipment_review_status(rental_id):
    """Toggle the equipment_reviewed flag for a specific equipment in a rental.

    Expects JSON body with ``equipment_id`` and ``equipment_review_status`` (boolean).

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Updated rental dict.
    """
    try:
        data = request.get_json()
        rental = RentalService.switch_equipment_review_status(rental_id, data.get("equipment_id"), data.get("equipment_review_status"))
        return jsonify(rental.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/<int:rental_id>', methods=['PUT'])
@jwt_required()
def update_rental(rental_id):
    """Update a rental's status, terms, or approval.

    Handles status transitions (approve, deny, cancel, return), term
    renegotiation, and meeting location updates. The authenticated user
    is the actor whose permissions are checked.

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Updated rental dict.
        400: Validation error (e.g. unauthorized transition, date conflicts).
    """
    try:
        data = request.get_json()
        actor_user_id = int(get_jwt_identity())
        rental = RentalService.update_rental(
            rental_id,
            data.get('status'),
            data.get('location'),
            data.get('agreed_price'),
            data.get('deleted'),
            data.get('meeting_lat'),
            data.get('meeting_lng'),
            data.get('start_date'),
            data.get('end_date'),
            actor_user_id,
            data.get('approve', False)
        )
        return jsonify(rental.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/<int:rental_id>', methods=['DELETE'])
def delete_rental(rental_id):
    """Soft-delete a rental (sets the deleted flag to True).

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Success message.
        404: Rental not found.
    """
    try:
        RentalService.delete_rental(rental_id)
        return jsonify({'message': 'Rental deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500