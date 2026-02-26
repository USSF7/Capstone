from models import Request
from database import db

class RequestService:
    """Service layer for Request business logic"""

    @staticmethod
    def create_request(requester_id, event_id, name, max_price, count, start_date, end_date, location):
        """Create a new request"""
        if not all([requester_id, event_id, name, max_price, count, start_date, end_date, location]):
            raise ValueError("All fields are required")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        if count < 1:
            raise ValueError("Count must be at least 1")
        
        req = Request(
            requester_id=requester_id,
            event_id=event_id,
            name=name,
            max_price=max_price,
            count=count,
            start_date=start_date,
            end_date=end_date,
            location=location
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
    def update_request(request_id, status=None, max_price=None, count=None):
        """Update a request"""
        req = Request.query.get(request_id)
        if not req:
            raise ValueError("Request not found")
        
        if status:
            req.status = status
        if max_price:
            req.max_price = max_price
        if count:
            req.count = count
        
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