from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import LocationService, RentalService, UserService

location_bp = Blueprint('location', __name__, url_prefix='/api/location')


@location_bp.route('/maps-key', methods=['GET'])
@jwt_required()
def get_maps_key():
    """Return the Google Maps API key for frontend map rendering."""
    key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    if not key:
        return jsonify({'error': 'Google Maps API key is not configured'}), 500
    return jsonify({'key': key}), 200


@location_bp.route('/geocode', methods=['POST'])
@jwt_required()
def geocode():
    """Geocode an address to lat/lng coordinates."""
    data = request.get_json()
    street_address = data.get('street_address')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip_code')

    if not all([street_address, city, state, zip_code]):
        return jsonify({'error': 'street_address, city, state, and zip_code are required'}), 400

    try:
        coords = LocationService.geocode_address(street_address, city, state, zip_code)
        if coords:
            return jsonify({'lat': coords[0], 'lng': coords[1]}), 200
        return jsonify({'error': 'Could not geocode address'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/equipment/search', methods=['GET'])
@jwt_required()
def search_equipment_nearby():
    """Search for equipment near a location."""
    from services import EquipmentService

    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=25, type=float)
    name = request.args.get('name', default=None, type=str)

    if lat is None or lng is None:
        return jsonify({'error': 'lat and lng are required'}), 400

    try:
        results = EquipmentService.search_equipment_nearby(lat, lng, radius, name)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/rental/<int:rental_id>/meeting-suggestions', methods=['GET'])
@jwt_required()
def get_meeting_suggestions(rental_id):
    """Calculate midpoint and suggest safe meeting locations for a rental."""
    rental = RentalService.get_rental(rental_id)
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404

    renter = UserService.get_user(rental.renter_id)
    vendor = UserService.get_user(rental.vendor_id)

    if not renter or not vendor:
        return jsonify({'error': 'Could not find both parties'}), 404

    if not all([renter.latitude, renter.longitude, vendor.latitude, vendor.longitude]):
        return jsonify({'error': 'Both parties must have geocoded addresses'}), 400

    try:
        mid_lat, mid_lng = LocationService.compute_midpoint(
            renter.latitude, renter.longitude,
            vendor.latitude, vendor.longitude
        )
        suggestions = LocationService.find_nearby_places(mid_lat, mid_lng)
        return jsonify({
            'midpoint': {'lat': mid_lat, 'lng': mid_lng},
            'suggestions': suggestions,
            'vendor': {'city': vendor.city, 'state': vendor.state},
            'renter': {'city': renter.city, 'state': renter.state},
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/rental/<int:rental_id>/meeting-location', methods=['POST'])
@jwt_required()
def set_meeting_location(rental_id):
    """Save a selected meeting location to a rental."""
    rental = RentalService.get_rental(rental_id)
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404

    current_user_id = get_jwt_identity()
    if current_user_id not in (rental.renter_id, rental.vendor_id):
        return jsonify({'error': 'Not authorized to modify this rental'}), 403

    data = request.get_json()
    name = data.get('name', '')
    address = data.get('address', '')
    lat = data.get('lat')
    lng = data.get('lng')

    if lat is None or lng is None:
        return jsonify({'error': 'lat and lng are required'}), 400

    location_str = f"{name}, {address}" if address else name
    updated = RentalService.update_rental(
        rental_id,
        location=location_str,
        meeting_lat=lat,
        meeting_lng=lng
    )
    return jsonify(updated.to_dict()), 200
