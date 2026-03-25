import json

from models import Equipment, Rental, RentalHasEquipment
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
    def create_equipment(owner_id, name):
        """Create new equipment"""
        if not owner_id or not name:
            raise ValueError("Owner ID and name are required")
        
        equipment = Equipment(owner_id=owner_id, name=name)
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
                    'start_date': rental.start_date.isoformat(),
                    'end_date': rental.end_date.isoformat(),
                }
            else:
                data['active_rental'] = None
            result.append(data)
        return result

    @staticmethod
    def update_equipment(equipment_id, name=None, owner_id=None):
        """Update equipment"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            raise ValueError("Equipment not found")
        
        if name:
            equipment.name = name
        if owner_id:
            equipment.owner_id = owner_id
        
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