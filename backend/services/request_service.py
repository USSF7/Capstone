import json

from models import Request
from database import db
from pathlib import Path
import os
from random import choice

def load_equipment_names():
    # .config is in project root
    config_path = Path(__file__).resolve().parents[2] / '.config'
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
        if 'EQUIPMENT_NAMES' in data:
            return data['EQUIPMENT_NAMES']
    # fallback default set, kept as defensive config in case .config is missing
    return [
        'Projector', 'Sound System', 'Microphone', 'Camera', 'Lighting Kit',
        'DJ Booth', 'Tent', 'Tables', 'Chairs', 'Decorations',
        'Amplifier', 'Speaker', 'Mixer', 'Laptop', 'Monitor',
        'Screen', 'Tripod', 'Cables', 'Microphone Stand', 'Power Bank'
    ]

EQUIPMENT_NAMES = load_equipment_names()

class RequestService:
    """Service layer for Request business logic"""

    @staticmethod
    def create_request(requester_id, event_id, name, max_price, count, start_date, end_date, location, min_price=None, comments=None):
        """Create a new request"""
        # event_id can be None (no associated event)
        if not all([requester_id, name, max_price, count, start_date, end_date, location]):
            raise ValueError("All required fields must be provided")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        if count < 1:
            raise ValueError("Count must be at least 1")
        if min_price is not None and min_price < 0:
            raise ValueError("Min price must be non-negative")
        if max_price < 0:
            raise ValueError("Max price must be non-negative")
        if min_price is not None and min_price > max_price:
            raise ValueError("Min price cannot exceed max price")
        
        req = Request(
            requester_id=requester_id,
            event_id=event_id,
            name=name,
            max_price=max_price,
            min_price=min_price,
            count=count,
            start_date=start_date,
            end_date=end_date,
            location=location,
            comments=comments
        )
        db.session.add(req)
        db.session.commit()
        return req

    @staticmethod
    def get_request(request_id):
        """Get a request by ID"""
        return Request.query.get(request_id)

    @staticmethod
    def get_all_requests():
        """Get all requests"""
        # return newest requests first so freshly-seeded rows with locations
        # appear at the top in the API response
        return Request.query.order_by(Request.id.desc()).all()

    @staticmethod
    def get_requests_by_requester(requester_id):
        """Get all requests by a user"""
        return Request.query.filter_by(requester_id=requester_id).all()

    @staticmethod
    def get_requests_by_event(event_id):
        """Get all requests for an event"""
        return Request.query.filter_by(event_id=event_id).all()

    @staticmethod
    def get_requests_by_status(status):
        """Get all requests with a specific status"""
        return Request.query.filter_by(status=status).all()

    @staticmethod
    def update_request(request_id,
                       status=None,
                       max_price=None,
                       count=None,
                       name=None,
                       event_id=None,
                       start_date=None,
                       end_date=None,
                       location=None,
                       min_price=None,
                       comments=None):
        """Update a request

        Only the values passed in will be modified; other fields are left
        untouched.  The validation rules mirror those in ``create_request``.
        """
        req = Request.query.get(request_id)
        if not req:
            raise ValueError("Request not found")

        # update fields if provided
        if status is not None:
            req.status = status
        if max_price is not None:
            req.max_price = max_price
        if count is not None:
            req.count = count
        if name is not None:
            req.name = name
        if event_id is not None:
            req.event_id = event_id
        if start_date is not None:
            req.start_date = start_date
        if end_date is not None:
            req.end_date = end_date
        if location is not None:
            req.location = location
        if min_price is not None:
            req.min_price = min_price
        if comments is not None:
            req.comments = comments

        # basic validation similar to create_request
        if req.end_date <= req.start_date:
            raise ValueError("End date must be after start date")
        if req.count < 1:
            raise ValueError("Count must be at least 1")

        db.session.commit()
        return req

    @staticmethod
    def delete_request(request_id):
        """Delete a request"""
        req = Request.query.get(request_id)
        if not req:
            raise ValueError("Request not found")
        
        db.session.delete(req)
        db.session.commit()
        return True