from models import Rental
from database import db

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