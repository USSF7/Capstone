from models import Rental
from database import db
from sqlalchemy import func
from models import Equipment
from models import RentalHasEquipment


VALID_RENTAL_STATUSES = {'requesting', 'accepted', 'active', 'returned', 'disputed', 'denied'}


class RentalService:
    """Service layer for Rental business logic"""

    @staticmethod
    def create_rental(renter_id, vendor_id, agreed_price, start_date, end_date, location=None, status='requesting', deleted=False):
        """Create a new rental"""
        if not all([renter_id, vendor_id, agreed_price, start_date, end_date]):
            raise ValueError("renter_id, vendor_id, agreed_price, start_date, and end_date are required")
        if renter_id == vendor_id:
            raise ValueError("Renter and vendor cannot be the same user")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        if status not in VALID_RENTAL_STATUSES:
            raise ValueError("Invalid rental status")
        
        rental = Rental(
            renter_id=renter_id,
            vendor_id=vendor_id,
            agreed_price=agreed_price,
            start_date=start_date,
            end_date=end_date,
            location=location,
            status=status,
            deleted=deleted
        )
        db.session.add(rental)
        db.session.commit()
        return rental

    @staticmethod
    def get_rental(rental_id):
        """Get a rental by ID"""
        return Rental.query.get(rental_id)
    
    @staticmethod
    def get_rental_with_equipment(rental_id):
        """Get a rental by ID with equipment"""
        rental = Rental.query.get(rental_id).to_dict()

        """Query the rental_has_equipment table and the equipment table to get the rental's equipment"""
        equipmentID = RentalHasEquipment.query.filter_by(rental_id=rental["id"]).first()
        equipmentInfo = Equipment.query.filter_by(id=equipmentID.equipment_id).all()
        rental["equipment"] = [ row.to_dict() for row in equipmentInfo ]

        return rental

    @staticmethod
    def get_all_rentals():
        """Get all rentals"""
        return Rental.query.all()

    @staticmethod
    def get_rentals_by_renter(renter_id):
        """Get all rentals by a renter"""
        return Rental.query.filter_by(renter_id=renter_id).all()
    
    @staticmethod
    def get_rentals_by_renter_with_equipment(renter_id):
        """Get all rentals by a renter with the corresponding attached equipment"""
        result = Rental.query.filter_by(renter_id=renter_id).all()
        rentals = [row.to_dict() for row in result]

        """Query the rental_has_equipment table and the equipment table to get each rental's equipment"""
        for i in range(0, len(rentals)):
            equipmentID = RentalHasEquipment.query.filter_by(rental_id=rentals[i]["id"]).first()
            equipmentInfo = Equipment.query.filter_by(id=equipmentID.equipment_id).all()
            rentals[i]["equipment"] = [ row.to_dict() for row in equipmentInfo ]

        return rentals

    @staticmethod
    def get_rentals_by_vendor(vendor_id):
        """Get all rentals offered by a vendor"""
        return Rental.query.filter_by(vendor_id=vendor_id).all()

    @staticmethod
    def get_rentals_by_status(status):
        """Get all rentals with a specific status"""
        return Rental.query.filter_by(status=status).all()
    
    @staticmethod
    def get_rentals_by_vendor_and_status(vendor_id, status):
        """Get all rentals offered by a vendor with a specific status"""
        return Rental.query.filter_by(vendor_id=vendor_id, status=status).all()

    @staticmethod
    def update_rental(rental_id, status=None, location=None, agreed_price=None, deleted=None):
        """Update a rental"""
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")
        
        if status:
            if status not in VALID_RENTAL_STATUSES:
                raise ValueError("Invalid rental status")
            rental.status = status
        if location:
            rental.location = location
        if agreed_price:
            rental.agreed_price = agreed_price
        if deleted is not None:
            rental.deleted = deleted
        
        db.session.commit()
        return rental

    @staticmethod
    def delete_rental(rental_id):
        """Delete a rental"""
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")
        
        rental.deleted = True
        db.session.commit()
        return True

    @staticmethod
    def get_average_price_by_equipment_and_location(equipment_name, location):
        """Get average price for equipment in a specific city/state"""
        if not equipment_name or not location:
            return None
        
        # Parse city and state from location string
        # Location format is typically: "Street Address, City, State Zip"
        # We'll extract city and state
        city_state = RentalService._extract_city_state(location)
        if not city_state:
            return None
        
        city, state = city_state
        
        # Query for average price of rentals with this equipment in this city/state
        result = db.session.query(func.avg(Rental.agreed_price))\
            .join(Rental.equipment_list)\
            .join(Equipment)\
            .filter(Equipment.name == equipment_name)\
            .filter(Rental.location.like(f'%{city}%'))\
            .filter(Rental.location.like(f'%{state}%'))\
            .scalar()
        
        return float(result) if result else None

    @staticmethod
    def _extract_city_state(location):
        """Extract city and state from location string"""
        # Handle both comma-separated and newline-separated formats
        if '\n' in location:
            # Multi-line format: "Street\nCity, State ZIP"
            lines = [line.strip() for line in location.split('\n') if line.strip()]
            if len(lines) >= 2:
                # Last line should be "City, State ZIP"
                city_state_line = lines[-1]
                parts = [part.strip() for part in city_state_line.split(',')]
                if len(parts) >= 2:
                    city = parts[0]
                    state_zip = parts[1].split()
                    if state_zip:
                        state = state_zip[0]
                        return city, state
        else:
            # Comma-separated format: "Street, City, State ZIP" or "City, State"
            parts = [part.strip() for part in location.split(',')]
            if len(parts) >= 2:
                if len(parts) >= 3:
                    # "Street, City, State ZIP"
                    city = parts[-2]
                    state_zip = parts[-1].split()
                else:
                    # "City, State"
                    city = parts[0]
                    state_zip = parts[1].split()
                
                if state_zip:
                    state = state_zip[0]
                    return city, state
        return None