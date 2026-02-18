from flask import Blueprint, request, jsonify
from services import EventService

event_bp = Blueprint('events', __name__, url_prefix='/api/events')

@event_bp.route('/', methods=['GET'])
def get_all_events():
    """Get all events"""
    try:
        events = EventService.get_all_events()
        return jsonify([e.to_dict() for e in events]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@event_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get an event by ID"""
    try:
        event = EventService.get_event(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        return jsonify(event.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@event_bp.route('/user/<int:user_id>', methods=['GET'])
def get_events_by_user(user_id):
    """Get all events created by a user"""
    try:
        events = EventService.get_events_by_user(user_id)
        return jsonify([e.to_dict() for e in events]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@event_bp.route('/', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        event = EventService.create_event(data.get('user_id'), data.get('name'), data.get('date'))
        return jsonify(event.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@event_bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an event"""
    try:
        data = request.get_json()
        event = EventService.update_event(event_id, data.get('name'), data.get('date'))
        return jsonify(event.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@event_bp.route('/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        EventService.delete_event(event_id)
        return jsonify({'message': 'Event deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500