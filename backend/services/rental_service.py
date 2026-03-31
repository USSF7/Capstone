from datetime import datetime, timedelta
from models import Rental
from database import db
from sqlalchemy import func
from models import Equipment
from models import RentalHasEquipment


VALID_RENTAL_STATUSES = {'requesting', 'accepted', 'active', 'returned', 'disputed', 'denied', 'cancelled'}
BLOCKING_STATUSES = {'requesting', 'accepted', 'active'}


class RentalService:
    """Service layer for Rental business logic"""

    @staticmethod
    def _normalize_date(date_value, field_name):
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(f"Invalid {field_name} format. Use YYYY-MM-DD")
        return date_value

    @staticmethod
    def _equipment_has_conflict(equipment_id, start_date, end_date):
        conflict = (
            db.session.query(Rental)
            .join(RentalHasEquipment, Rental.id == RentalHasEquipment.rental_id)
            .filter(
                RentalHasEquipment.equipment_id == equipment_id,
                Rental.deleted.is_(False),
                Rental.status.in_(BLOCKING_STATUSES),
                Rental.start_date <= end_date,
                Rental.end_date >= start_date,
            )
            .first()
        )
        return conflict

    @staticmethod
    def create_rental(
        renter_id,
        vendor_id,
        agreed_price,
        start_date=None,
        end_date=None,
        location=None,
        status='requesting',
        deleted=False,
        equipment_ids=None,
        meeting_lat=None,
        meeting_lng=None,
    ):
        """Create a new rental"""
        if not all([renter_id, vendor_id, agreed_price]):
            raise ValueError("renter_id, vendor_id, and agreed_price are required")
        if renter_id == vendor_id:
            raise ValueError("Renter and vendor cannot be the same user")

        # If dates are omitted by the request flow, default to a 1-day request window.
        if not start_date:
            start_date = datetime.utcnow().date()
        if not end_date:
            end_date = start_date + timedelta(days=1)

        # Normalize string dates from API payloads.
        start_date = RentalService._normalize_date(start_date, 'start_date')
        end_date = RentalService._normalize_date(end_date, 'end_date')

        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        if status not in VALID_RENTAL_STATUSES:
            raise ValueError("Invalid rental status")

        requested_equipment_ids = []
        if equipment_ids and isinstance(equipment_ids, list):
            requested_equipment_ids.extend(equipment_ids)

        # Normalize to integer IDs and flatten any accidental nested lists.
        normalized_equipment_ids = []
        for raw_id in requested_equipment_ids:
            if isinstance(raw_id, list):
                normalized_equipment_ids.extend(raw_id)
            else:
                normalized_equipment_ids.append(raw_id)

        try:
            normalized_equipment_ids = [int(eid) for eid in normalized_equipment_ids]
        except (TypeError, ValueError):
            raise ValueError("equipment_ids must be integers")

        # Deduplicate while preserving order.
        deduped_equipment_ids = list(dict.fromkeys(normalized_equipment_ids))
        selected_equipment = []
        for eid in deduped_equipment_ids:
            equipment = Equipment.query.get(eid)
            if not equipment:
                raise ValueError(f"Equipment not found: {eid}")
            if equipment.owner_id != vendor_id:
                raise ValueError(f"Equipment does not belong to selected vendor: {eid}")
            conflict = RentalService._equipment_has_conflict(equipment.id, start_date, end_date)
            if conflict:
                raise ValueError(f"Equipment is unavailable for selected dates: {equipment.name}")
            selected_equipment.append(equipment)
        
        rental = Rental(
            renter_id=renter_id,
            vendor_id=vendor_id,
            agreed_price=agreed_price,
            start_date=start_date,
            end_date=end_date,
            location=location,
            meeting_lat=meeting_lat,
            meeting_lng=meeting_lng,
            status=status,
            renter_approved=True,
            vendor_approved=False,
            deleted=deleted
        )
        db.session.add(rental)
        db.session.flush()

        for equipment in selected_equipment:
            db.session.add(RentalHasEquipment(equipment_id=equipment.id, rental_id=rental.id))

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
        equipment_ids = [
            row.equipment_id for row in RentalHasEquipment.query.filter_by(rental_id=rental["id"]).all()
        ]
        equipment_info = Equipment.query.filter(Equipment.id.in_(equipment_ids)).all() if equipment_ids else []
        rental["equipment"] = [row.to_dict() for row in equipment_info]

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
            equipment_ids = [
                row.equipment_id for row in RentalHasEquipment.query.filter_by(rental_id=rentals[i]["id"]).all()
            ]
            equipment_info = Equipment.query.filter(Equipment.id.in_(equipment_ids)).all() if equipment_ids else []
            rentals[i]["equipment"] = [row.to_dict() for row in equipment_info]

        return rentals

    @staticmethod
    def get_vendor_equipment_with_availability(vendor_id, start_date, end_date):
        start_date = RentalService._normalize_date(start_date, 'start_date')
        end_date = RentalService._normalize_date(end_date, 'end_date')
        if not start_date or not end_date:
            raise ValueError("start_date and end_date are required")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        equipment_list = Equipment.query.filter_by(owner_id=vendor_id).all()
        result = []
        for equipment in equipment_list:
            conflict = RentalService._equipment_has_conflict(equipment.id, start_date, end_date)
            data = equipment.to_dict()
            data['available'] = conflict is None
            data['unavailable_reason'] = None if conflict is None else (
                f"Booked {conflict.start_date.isoformat()} to {conflict.end_date.isoformat()} ({conflict.status})"
            )
            result.append(data)

        return result

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
    def update_rental(
        rental_id,
        status=None,
        location=None,
        agreed_price=None,
        deleted=None,
        meeting_lat=None,
        meeting_lng=None,
        start_date=None,
        end_date=None,
        actor_user_id=None,
        approve=False,
    ):
        """Update a rental"""
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")

        if actor_user_id is not None and actor_user_id not in [rental.renter_id, rental.vendor_id]:
            raise ValueError("Not authorized to modify this rental")

        old_snapshot = {
            'location': rental.location,
            'agreed_price': float(rental.agreed_price),
            'meeting_lat': rental.meeting_lat,
            'meeting_lng': rental.meeting_lng,
            'start_date': rental.start_date,
            'end_date': rental.end_date,
        }

        if status:
            if status not in VALID_RENTAL_STATUSES:
                raise ValueError("Invalid rental status")

            if status == 'cancelled':
                if actor_user_id is None:
                    raise ValueError("actor_user_id is required when canceling a rental")
                if actor_user_id != rental.renter_id:
                    raise ValueError("Only the renter can cancel a rental request")
                if rental.status not in {'requesting', 'accepted'}:
                    raise ValueError("Only pending rental requests can be canceled")

            if status == 'returned':
                if actor_user_id is None:
                    raise ValueError("actor_user_id is required when marking a rental as returned")
                if actor_user_id != rental.vendor_id:
                    raise ValueError("Only the vendor can mark a rental as returned")
                if rental.status != 'active':
                    raise ValueError("Only active rentals can be marked as returned")

                today = datetime.utcnow().date()
                if today <= rental.end_date:
                    raise ValueError("Rental can only be marked as returned after the end date has passed")

            rental.status = status
        if location:
            rental.location = location
        if agreed_price:
            rental.agreed_price = agreed_price
        if deleted is not None:
            rental.deleted = deleted
        if meeting_lat is not None:
            rental.meeting_lat = meeting_lat
        if meeting_lng is not None:
            rental.meeting_lng = meeting_lng
        if start_date is not None:
            rental.start_date = RentalService._normalize_date(start_date, 'start_date')
        if end_date is not None:
            rental.end_date = RentalService._normalize_date(end_date, 'end_date')

        if rental.end_date <= rental.start_date:
            raise ValueError("End date must be after start date")

        details_changed = any([
            old_snapshot['location'] != rental.location,
            old_snapshot['agreed_price'] != float(rental.agreed_price),
            old_snapshot['meeting_lat'] != rental.meeting_lat,
            old_snapshot['meeting_lng'] != rental.meeting_lng,
            old_snapshot['start_date'] != rental.start_date,
            old_snapshot['end_date'] != rental.end_date,
        ])

        if details_changed:
            # Any details change requires both parties to re-approve.
            rental.renter_approved = False
            rental.vendor_approved = False
            if actor_user_id == rental.renter_id:
                rental.renter_approved = True
            if actor_user_id == rental.vendor_id:
                rental.vendor_approved = True

            if rental.status in {'requesting', 'accepted', 'active'}:
                rental.status = 'requesting'

        if approve:
            if actor_user_id is None:
                raise ValueError("actor_user_id is required when approving")
            if actor_user_id == rental.renter_id:
                rental.renter_approved = True
            if actor_user_id == rental.vendor_id:
                rental.vendor_approved = True

        # Enforce active status only when both parties approved.
        if rental.status == 'active' and not (rental.renter_approved and rental.vendor_approved):
            raise ValueError("Both renter and vendor must approve before rental can be active")

        if rental.status in {'requesting', 'accepted', 'active'}:
            if rental.renter_approved and rental.vendor_approved:
                rental.status = 'active'
            else:
                rental.status = 'requesting'

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