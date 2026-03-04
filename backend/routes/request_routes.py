from flask import Blueprint, request, jsonify
from services import RequestService

request_bp = Blueprint('requests', __name__, url_prefix='/api/requests')

@request_bp.route('/', methods=['GET'])
def get_all_requests():
    """Get all requests"""
    try:
        requests = RequestService.get_all_requests()
        return jsonify([r.to_dict() for r in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Get a request by ID"""
    try:
        req = RequestService.get_request(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        return jsonify(req.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/requester/<int:requester_id>', methods=['GET'])
def get_requests_by_requester(requester_id):
    """Get all requests by a user"""
    try:
        requests = RequestService.get_requests_by_requester(requester_id)
        return jsonify([r.to_dict() for r in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/event/<int:event_id>', methods=['GET'])
def get_requests_by_event(event_id):
    """Get all requests for an event"""
    try:
        requests = RequestService.get_requests_by_event(event_id)
        return jsonify([r.to_dict() for r in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/status/<status>', methods=['GET'])
def get_requests_by_status(status):
    """Get all requests with a specific status"""
    try:
        requests = RequestService.get_requests_by_status(status)
        return jsonify([r.to_dict() for r in requests]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/', methods=['POST'])
def create_request():
    """Create a new request"""
    try:
        data = request.get_json()
        req = RequestService.create_request(
            data.get('requester_id'),
            data.get('event_id'),
            data.get('name'),
            data.get('max_price'),
            data.get('count'),
            data.get('start_date'),
            data.get('end_date'),
            data.get('location')
            ,
            data.get('min_price'),
            data.get('comments')
        )
        return jsonify(req.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    """Update a request"""
    try:
        data = request.get_json()
        req = RequestService.update_request(
            request_id,
            status=data.get('status'),
            max_price=data.get('max_price'),
            count=data.get('count'),
            name=data.get('name'),
            event_id=data.get('event_id'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            location=data.get('location'),
            min_price=data.get('min_price'),
            comments=data.get('comments'),
        )
        return jsonify(req.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@request_bp.route('/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    """Delete a request"""
    try:
        RequestService.delete_request(request_id)
        return jsonify({'message': 'Request deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500