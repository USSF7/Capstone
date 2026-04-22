"""
Location routes module.

Provides endpoints for geocoding addresses, searching for nearby equipment,
computing meeting-point suggestions between renter and vendor, and saving
meeting locations to rentals.

Routes:
    GET  /api/location/maps-key                             -- Get Google Maps API key (JWT).
    POST /api/location/geocode                              -- Geocode structured address (JWT).
    POST /api/location/geocode-freeform                     -- Geocode freeform address (JWT).
    GET  /api/location/equipment/search                     -- Search nearby equipment (JWT).
    GET  /api/location/rental/<id>/meeting-suggestions      -- Suggest meeting points for a rental (JWT).
    GET  /api/location/meeting-suggestions                  -- Suggest meeting points for arbitrary coords (JWT).
    POST /api/location/rental/<id>/meeting-location         -- Save meeting location to rental (JWT).
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import LocationService, RentalService, UserService

location_bp = Blueprint('location', __name__, url_prefix='/api/location')


@location_bp.route('/maps-key', methods=['GET'])
@jwt_required()
def get_maps_key():
    """Return the Google Maps API key for frontend map rendering.

    Returns:
        200: Dict with ``key``.
        500: API key not configured.
    """
    key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    if not key:
        return jsonify({'error': 'Google Maps API key is not configured'}), 500
    return jsonify({'key': key}), 200


@location_bp.route('/geocode', methods=['POST'])
@jwt_required()
def geocode():
    """Geocode a structured address to lat/lng coordinates.

    Expects JSON body with ``street_address``, ``city``, ``state``, ``zip_code``.

    Returns:
        200: Dict with ``lat`` and ``lng``.
        400: Missing fields or geocoding failure.
    """
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


@location_bp.route('/geocode-freeform', methods=['POST'])
@jwt_required()
def geocode_freeform():
    """Geocode a freeform address string to lat/lng coordinates.

    Expects JSON body with ``address`` (full address string).

    Returns:
        200: Dict with ``lat`` and ``lng``.
        400: Missing address or geocoding failure.
    """
    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({'error': 'address is required'}), 400

    try:
        coords = LocationService.geocode_freeform(address)
        if coords:
            return jsonify({'lat': coords[0], 'lng': coords[1]}), 200
        return jsonify({'error': 'Could not geocode address'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/equipment/search', methods=['GET'])
@jwt_required()
def search_equipment_nearby():
    """Search for equipment near a location.

    Finds equipment whose owners are within a radius of the given
    coordinates. Excludes equipment owned by the authenticated user.
    Supports fuzzy name matching via pg_trgm.

    Query params: ``lat``, ``lng`` (required), ``radius`` (miles, default 25),
    ``name`` (optional text filter).

    Returns:
        200: Dict with ``results`` list of equipment dicts including
            distance, owner info, and ratings.
        400: Missing lat/lng.
    """
    from services import EquipmentService

    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=25, type=float)
    name = request.args.get('name', default=None, type=str)

    if lat is None or lng is None:
        return jsonify({'error': 'lat and lng are required'}), 400

    try:
        current_user_id = int(get_jwt_identity())
        results = EquipmentService.search_equipment_nearby(
            lat,
            lng,
            radius,
            name,
            exclude_owner_id=current_user_id,
        )
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/rental/<int:rental_id>/meeting-suggestions', methods=['GET'])
@jwt_required()
def get_meeting_suggestions(rental_id):
    """Suggest safe, balanced meeting locations for a rental's participants.

    Computes the geographic midpoint between renter and vendor, then
    finds nearby public places (libraries, parks, police stations, etc.)
    that are fair for both parties.

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Dict with ``midpoint``, ``suggestions`` list, and party city/state.
        403: User not part of this rental.
        404: Rental or users not found.
        400: Users missing geocoded addresses.
    """
    rental = RentalService.get_rental(rental_id)
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404

    current_user_id = int(get_jwt_identity())
    if current_user_id not in [rental.renter_id, rental.vendor_id]:
        return jsonify({'error': 'Not authorized to view meeting suggestions for this rental'}), 403

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
        suggestions = LocationService.find_balanced_meeting_places(
            renter.latitude,
            renter.longitude,
            vendor.latitude,
            vendor.longitude,
            max_results=8,
        )
        return jsonify({
            'midpoint': {'lat': mid_lat, 'lng': mid_lng},
            'suggestions': suggestions,
            'vendor': {'city': vendor.city, 'state': vendor.state},
            'renter': {'city': renter.city, 'state': renter.state},
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/meeting-suggestions', methods=['GET'])
@jwt_required()
def get_meeting_suggestions_for_points():
    """Suggest meeting locations using provided renter/vendor coordinates.

    Same logic as the rental-based endpoint but accepts raw coordinates
    instead of looking them up from user profiles.

    Query params: ``renter_lat``, ``renter_lng``, ``vendor_lat``, ``vendor_lng``.

    Returns:
        200: Dict with ``midpoint`` and ``suggestions`` list.
        400: Missing coordinates.
    """
    renter_lat = request.args.get('renter_lat', type=float)
    renter_lng = request.args.get('renter_lng', type=float)
    vendor_lat = request.args.get('vendor_lat', type=float)
    vendor_lng = request.args.get('vendor_lng', type=float)

    if None in (renter_lat, renter_lng, vendor_lat, vendor_lng):
        return jsonify({'error': 'renter_lat, renter_lng, vendor_lat, and vendor_lng are required'}), 400

    try:
        mid_lat, mid_lng = LocationService.compute_midpoint(
            renter_lat,
            renter_lng,
            vendor_lat,
            vendor_lng,
        )
        suggestions = LocationService.find_balanced_meeting_places(
            renter_lat,
            renter_lng,
            vendor_lat,
            vendor_lng,
            max_results=8,
        )
        return jsonify({
            'midpoint': {'lat': mid_lat, 'lng': mid_lng},
            'suggestions': suggestions,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@location_bp.route('/rental/<int:rental_id>/meeting-location', methods=['POST'])
@jwt_required()
def set_meeting_location(rental_id):
    """Save a selected meeting location to a rental.

    Updates the rental's location text, meeting_lat, and meeting_lng.
    Only accessible by the renter or vendor of the rental.

    Expects JSON body with ``name``, ``address``, ``lat``, ``lng``.

    Args:
        rental_id: The rental's primary key.

    Returns:
        200: Updated rental dict.
        400: Missing lat/lng.
        403: User not part of this rental.
        404: Rental not found.
    """
    rental = RentalService.get_rental(rental_id)
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404

    current_user_id = int(get_jwt_identity())
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
        meeting_lng=lng,
        actor_user_id=current_user_id,
    )
    return jsonify(updated.to_dict()), 200
