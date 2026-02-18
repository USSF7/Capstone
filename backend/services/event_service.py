from models import Event
from database import db

class EventService:
    """Service layer for Event business logic"""

    @staticmethod
    def create_event(user_id, name, date):
        """Create a new event"""
        if not all([user_id, name, date]):
            raise ValueError("user_id, name, and date are required")
        
        event = Event(user_id=user_id, name=name, date=date)
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def get_event(event_id):
        """Get an event by ID"""
        return Event.query.get(event_id)

    @staticmethod
    def get_all_events():
        """Get all events"""
        return Event.query.all()

    @staticmethod
    def get_events_by_user(user_id):
        """Get all events created by a user"""
        return Event.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_event(event_id, name=None, date=None):
        """Update an event"""
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found")
        
        if name:
            event.name = name
        if date:
            event.date = date
        
        db.session.commit()
        return event

    @staticmethod
    def delete_event(event_id):
        """Delete an event"""
        event = Event.query.get(event_id)
        if not event:
            raise ValueError("Event not found")
        
        db.session.delete(event)
        db.session.commit()
        return True