import json
from datetime import timezone
from sqlalchemy import func

from models import Equipment, Rental, RentalHasEquipment, Review
from models.user import User
from database import db
from pathlib import Path


def load_equipment_names_from_config():
    # .config is mounted in the app directory in Docker
    config_path = Path(__file__).resolve().parents[1] / '.config'
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
        if 'EQUIPMENT_NAMES' in data and isinstance(data['EQUIPMENT_NAMES'], list):
            return data['EQUIPMENT_NAMES']

    return [
        'Projector', 'Sound System', 'Microphone', 'Camera', 'Lighting Kit',
        'DJ Booth', 'Tent', 'Tables', 'Chairs', 'Decorations',
        'Amplifier', 'Speaker', 'Mixer', 'Laptop', 'Monitor',
        'Screen', 'Tripod', 'Cables', 'Microphone Stand', 'Power Bank'
    ]


class EquipmentService:
    """Service layer for Equipment business logic"""

    @staticmethod
    def create_equipment(owner_id, name, price, description=None, picture=None, condition=None):
        """Create new equipment"""
        if not owner_id or not name:
            raise ValueError("Owner ID and name are required")
        if price is None:
            raise ValueError("Price is required")
        
        equipment = Equipment(
            owner_id=owner_id,
            name=name,
            price=price,
            description=description,
            picture=picture,
            condition=condition
        )
        db.session.add(equipment)
        db.session.commit()
        return equipment

    @staticmethod
    def get_equipment(equipment_id):
        """Get equipment by ID"""
        return Equipment.query.get(equipment_id)

    @staticmethod
    def get_all_equipment():
        """Get all equipment"""
        return Equipment.query.all()

    @staticmethod
    def get_equipment_by_owner(owner_id):
        """Get all equipment owned by a user"""
        return Equipment.query.filter_by(owner_id=owner_id).all()

    @staticmethod
    def get_equipment_names():
        """Get current equipment name pool from .config"""
        return load_equipment_names_from_config()

    @staticmethod
    def get_equipment_by_owner_with_rentals(owner_id):
        """Get all equipment owned by a user with active rental details"""
        equipment_list = Equipment.query.filter_by(owner_id=owner_id).all()
        result = []

        def to_utc_iso(value):
            if value is None:
                return None
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
            return value.isoformat().replace('+00:00', 'Z')

        for equip in equipment_list:
            data = equip.to_dict()
            # Find active rental for this equipment
            active_rental = (
                db.session.query(Rental, User.name)
                .join(RentalHasEquipment, Rental.id == RentalHasEquipment.rental_id)
                .join(User, Rental.renter_id == User.id)
                .filter(
                    RentalHasEquipment.equipment_id == equip.id,
                    Rental.status == 'active'
                )
                .first()
            )
            if active_rental:
                rental, renter_name = active_rental
                data['active_rental'] = {
                    'rental_id': rental.id,
                    'renter_name': renter_name,
                    'start_date': to_utc_iso(rental.start_date),
                    'end_date': to_utc_iso(rental.end_date),
                }
            else:
                data['active_rental'] = None
            result.append(data)
        return result

    @staticmethod
    def search_equipment_nearby(lat, lng, radius_miles=25, name_filter=None):
        """Find equipment whose owner is within radius_miles of (lat, lng).

        When name_filter is provided, results include both exact substring
        matches (via ILIKE) and fuzzy matches (via pg_trgm similarity),
        so typos like "trcktor" still find "Tractor".
        """
        from services.location_service import LocationService

        similarity_threshold = 0.3

        query = db.session.query(Equipment, User).join(User, Equipment.owner_id == User.id)
        query = query.filter(User.latitude.isnot(None), User.longitude.isnot(None))

        if name_filter:
            similarity_score = func.similarity(Equipment.name, name_filter)
            query = query.filter(
                db.or_(
                    Equipment.name.ilike(f'%{name_filter}%'),
                    similarity_score >= similarity_threshold,
                )
            )

        results = []
        for equipment, owner in query.all():
            distance = LocationService.haversine_distance(lat, lng, owner.latitude, owner.longitude)
            if distance <= radius_miles:
                avg_rating, rating_count = (
                    db.session.query(func.avg(Review.rating), func.count(Review.id))
                    .filter(Review.model_type == 'user', Review.model_id == owner.id)
                    .first()
                )

                data = equipment.to_dict()
                data['distance_miles'] = round(distance, 1)
                data['owner_name'] = owner.name
                data['owner_city'] = owner.city
                data['owner_state'] = owner.state
                data['owner_lat'] = round(owner.latitude, 2)
                data['owner_lng'] = round(owner.longitude, 2)
                data['owner_rating'] = round(float(avg_rating), 1) if avg_rating is not None else None
                data['owner_rating_count'] = int(rating_count or 0)
                results.append(data)

        results.sort(key=lambda x: x['distance_miles'])
        return results

    @staticmethod
    def update_equipment(equipment_id, name=None, owner_id=None, price=None, description=None, picture=None, condition=None):
        """Update equipment"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            raise ValueError("Equipment not found")
        
        if name:
            equipment.name = name
        if owner_id:
            equipment.owner_id = owner_id
        if price is not None:
            equipment.price = price
        if description is not None:
            equipment.description = description
        if picture is not None:
            equipment.picture = picture
        if condition is not None:
            equipment.condition = condition
        
        db.session.commit()
        return equipment

    @staticmethod
    def delete_equipment(equipment_id):
        """Delete equipment"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            raise ValueError("Equipment not found")
        
        db.session.delete(equipment)
        db.session.commit()
        return True