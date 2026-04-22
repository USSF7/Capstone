"""
Service layer package.

Re-exports all service classes so they can be imported directly from
``services`` (e.g. ``from services import UserService``). Each service
encapsulates the business logic for its domain, keeping routes thin.
"""

from .user_service import UserService
from .equipment_service import EquipmentService
from .review_service import ReviewService
from .message_service import MessageService
from .rental_service import RentalService
from .auth_service import AuthService
from .ai_service import AIService
from .location_service import LocationService

__all__ = ['UserService', 'EquipmentService', 'ReviewService', 'MessageService', 'RentalService', 'EventService', 'RequestService', 'AuthService', 'AIService', 'LocationService']