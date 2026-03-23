from models import Rental
from database import db
from sqlalchemy import func
from models import Equipment

class RentalService:
    """Service layer for Rental business logic"""

    @staticmethod
    def create_rental(renter_id, vendor_id, agreed_price, start_date, end_date, event_id=None, location=None):
        """Create a new rental"""
        if not all([renter_id, vendor_id, agreed_price, start_date, end_date]):
            raise ValueError("renter_id, vendor_id, agreed_price, start_date, and end_date are required")
        if renter_id == vendor_id:
            raise ValueError("Renter and vendor cannot be the same user")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        
        rental = Rental(
            renter_id=renter_id,
            vendor_id=vendor_id,
            agreed_price=agreed_price,
            start_date=start_date,
            end_date=end_date,
            event_id=event_id,
            location=location
        )
        db.session.add(rental)
        db.session.commit()
        return rental

    @staticmethod
    def get_rental(rental_id):
        """Get a rental by ID"""
        return Rental.query.get(rental_id)

    @staticmethod
    def get_all_rentals():
        """Get all rentals"""
        return Rental.query.all()

    @staticmethod
    def get_rentals_by_renter(renter_id):
        """Get all rentals by a renter"""
        return Rental.query.filter_by(renter_id=renter_id).all()

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
    def update_rental(rental_id, status=None, location=None, agreed_price=None):
        """Update a rental"""
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")
        
        if status:
            rental.status = status
        if location:
            rental.location = location
        if agreed_price:
            rental.agreed_price = agreed_price
        
        db.session.commit()
        return rental

    @staticmethod
    def delete_rental(rental_id):
        """Delete a rental"""
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")
        
        db.session.delete(rental)
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