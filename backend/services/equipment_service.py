from models import Equipment
from database import db

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