"""
Rental service module.

Business logic for the full rental lifecycle: creating requests, mutual
approval, term renegotiation, status transitions (active, returned,
cancelled, denied, disputed), equipment availability checking, review
flag management, and average price computation.
"""

from datetime import date, datetime, time, timedelta, timezone
from models import Rental
from database import db
from sqlalchemy import func
from models import Equipment
from models import RentalHasEquipment

# Valid status values for the rental lifecycle.
VALID_RENTAL_STATUSES = {'requesting', 'active', 'returned', 'disputed', 'denied', 'cancelled'}

# Statuses that block equipment from being rented by others.
BLOCKING_STATUSES = {'requesting', 'active'}


class RentalService:
    """Business logic for Rental management.

    Enforces rules like minimum lead times, mutual approval, ownership
    checks, and date conflict detection.

    Class Attributes:
        MIN_REQUEST_LEAD_TIME: Minimum time between now and the rental start
            date when creating a new request (2 hours).
        MIN_RENEGOTIATION_LEAD_TIME: Minimum time before start date to allow
            renegotiation of an active rental (7 days).
    """

    MIN_REQUEST_LEAD_TIME = timedelta(hours=2)
    MIN_RENEGOTIATION_LEAD_TIME = timedelta(days=7)

    @staticmethod
    def _normalize_datetime(date_value, field_name):
        """Parse and normalize a date/datetime value to a naive UTC datetime.

        Accepts datetime objects, date objects, and ISO 8601 strings.
        Timezone-aware values are converted to UTC and made naive.

        Args:
            date_value: The value to normalize.
            field_name: Name of the field (for error messages).

        Returns:
            A naive datetime in UTC, or None if date_value is None.

        Raises:
            ValueError: If the value cannot be parsed.
        """
        if date_value is None:
            return None

        if isinstance(date_value, datetime):
            value = date_value
        elif isinstance(date_value, date):
            value = datetime.combine(date_value, time.min)
        elif isinstance(date_value, str):
            normalized_value = date_value.strip().replace('Z', '+00:00')
            try:
                value = datetime.fromisoformat(normalized_value)
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"Invalid {field_name} format. Use ISO 8601 datetime values")
                value = datetime.combine(parsed_date, time.min)
        else:
            raise ValueError(f"Invalid {field_name} format. Use ISO 8601 datetime values")

        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)

        return value

    @staticmethod
    def _format_datetime(value):
        """Format a datetime as a human-readable UTC string.

        Args:
            value: A datetime to format.

        Returns:
            String like "Apr 21, 2026, 2:30 PM UTC".
        """
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        hour = value.hour % 12 or 12
        minute = f'{value.minute:02d}'
        period = 'AM' if value.hour < 12 else 'PM'
        return f"{value.strftime('%b')} {value.day}, {value.year}, {hour}:{minute} {period} UTC"

    @staticmethod
    def _equipment_has_conflict(equipment_id, start_date, end_date):
        """Check if an equipment item has a date conflict with existing rentals.

        Looks for non-deleted rentals in blocking statuses (requesting or active)
        that overlap the given date range.

        Args:
            equipment_id: The equipment's primary key.
            start_date: Start of the proposed date range.
            end_date: End of the proposed date range.

        Returns:
            The conflicting Rental instance, or None if no conflict.
        """
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
        """Create a new rental request with equipment.

        Validates participants, dates, equipment ownership, and availability.
        The renter is auto-approved; the vendor must separately approve.

        Args:
            renter_id: Primary key of the renter User.
            vendor_id: Primary key of the vendor User.
            agreed_price: Negotiated price in USD.
            start_date: Rental start (ISO string or datetime, min 2 hours ahead).
            end_date: Rental end (ISO string or datetime, must be after start).
            location: Meeting location text.
            status: Initial status (default 'requesting').
            deleted: Soft-delete flag.
            equipment_ids: List of Equipment primary keys to include.
            meeting_lat: Latitude of meeting point.
            meeting_lng: Longitude of meeting point.

        Returns:
            The created Rental instance.

        Raises:
            ValueError: If validation fails (missing fields, self-rental,
                date conflicts, equipment not found or not owned by vendor).
        """
        if not all([renter_id, vendor_id, agreed_price]):
            raise ValueError("renter_id, vendor_id, and agreed_price are required")
        if renter_id == vendor_id:
            raise ValueError("Renter and vendor cannot be the same user")

        minimum_start_date = datetime.utcnow() + RentalService.MIN_REQUEST_LEAD_TIME

        # If dates are omitted by the request flow, default to a 1-day request window.
        if not start_date:
            start_date = minimum_start_date
        else:
            start_date = RentalService._normalize_datetime(start_date, 'start_date')

        if not end_date:
            end_date = start_date + timedelta(days=1)
        else:
            end_date = RentalService._normalize_datetime(end_date, 'end_date')

        if start_date < minimum_start_date:
            raise ValueError("Start date must be at least 2 hours in the future")

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
            deleted=deleted,
            renter_reviewed=False,
            vendor_reviewed=False
        )
        db.session.add(rental)
        db.session.flush()

        for equipment in selected_equipment:
            db.session.add(RentalHasEquipment(equipment_id=equipment.id, rental_id=rental.id, equipment_reviewed=False))

        db.session.commit()
        return rental

    @staticmethod
    def get_rental(rental_id):
        """Get a rental by ID"""
        return Rental.query.get(rental_id)
    
    @staticmethod
    def get_rental_with_equipment(rental_id):
        """Get a rental dict with its attached equipment list.

        Queries the RentalHasEquipment link table to include each
        equipment item's details and review status.

        Args:
            rental_id: The rental's primary key.

        Returns:
            Rental dict with an ``equipment`` key containing a list of
            equipment dicts (each with ``equipment_reviewed`` flag).
        """
        rental = Rental.query.get(rental_id).to_dict()

        """Query the rental_has_equipment table and the equipment table to get the rental's equipment"""
        RHE_rows = RentalHasEquipment.query.filter_by(rental_id=rental["id"]).all()

        equipment_ids = [
            row.equipment_id for row in RHE_rows
        ]

        equipment_reviewed_status = {
            row.equipment_id: row.equipment_reviewed for row in RHE_rows
        }

        equipment_info = Equipment.query.filter(Equipment.id.in_(equipment_ids)).all() if equipment_ids else []

        rental["equipment"] = []

        for row in equipment_info:
            equipment_dict = row.to_dict()
            equipment_dict["equipment_reviewed"] = equipment_reviewed_status.get(row.id, False)
            rental["equipment"].append(equipment_dict)

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
        """Get all rentals by a renter with the corresponding attached equipment.

        Args:
            renter_id: The renter User's primary key.

        Returns:
            List of rental dicts, each with an ``equipment`` list.
        """
        result = Rental.query.filter_by(renter_id=renter_id).all()
        rentals = [row.to_dict() for row in result]

        """Query the rental_has_equipment table and the equipment table to get each rental's equipment"""
        for i in range(0, len(rentals)):
            RHE_rows = RentalHasEquipment.query.filter_by(rental_id=rentals[i]["id"]).all()

            equipment_ids = [
                row.equipment_id for row in RHE_rows
            ]

            equipment_reviewed_status = {
                row.equipment_id: row.equipment_reviewed for row in RHE_rows
            }

            equipment_info = Equipment.query.filter(Equipment.id.in_(equipment_ids)).all() if equipment_ids else []

            rentals[i]["equipment"] = []

            for row in equipment_info:
                equipment_dict = row.to_dict()
                equipment_dict["equipment_reviewed"] = equipment_reviewed_status.get(row.id, False)
                rentals[i]["equipment"].append(equipment_dict)

        return rentals

    @staticmethod
    def get_vendor_equipment_with_availability(vendor_id, start_date, end_date):
        """Check availability of all vendor equipment for a date range.

        Args:
            vendor_id: The vendor User's primary key.
            start_date: Start of the proposed date range (ISO string or datetime).
            end_date: End of the proposed date range (ISO string or datetime).

        Returns:
            List of equipment dicts, each with ``available`` (bool) and
            ``unavailable_reason`` (string or None).

        Raises:
            ValueError: If dates are missing or invalid.
        """
        start_date = RentalService._normalize_datetime(start_date, 'start_date')
        end_date = RentalService._normalize_datetime(end_date, 'end_date')
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
                f"Booked {RentalService._format_datetime(conflict.start_date)} to {RentalService._format_datetime(conflict.end_date)} ({conflict.status})"
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
    def switch_renter_review_status(rental_id, status):
        """Toggle the renter_reviewed flag on a rental.

        Args:
            rental_id: The rental's primary key.
            status: Boolean-ish value (True, "true", 1 -> True, else False).

        Returns:
            The updated Rental instance.

        Raises:
            ValueError: If rental not found.
        """
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")
        
        statusUpdate = True if status in [True, "true", "True", 1] else False
        rental.renter_reviewed = statusUpdate

        db.session.commit()
        return rental
    
    @staticmethod
    def switch_vendor_review_status(rental_id, status):
        """Toggle the vendor_reviewed flag on a rental.

        Args:
            rental_id: The rental's primary key.
            status: Boolean-ish value (True, "true", 1 -> True, else False).

        Returns:
            The updated Rental instance.

        Raises:
            ValueError: If rental not found.
        """
        rental = Rental.query.get(rental_id)
        if not rental:
            raise ValueError("Rental not found")
        
        statusUpdate = True if status in [True, "true", "True", 1] else False
        rental.vendor_reviewed = statusUpdate

        db.session.commit()
        return rental
    
    @staticmethod
    def switch_equipment_review_status(rental_id, equipment_id, status):
        """Toggle the equipment_reviewed flag for a specific equipment in a rental.

        Args:
            rental_id: The rental's primary key.
            equipment_id: The equipment's primary key.
            status: Boolean-ish value (True, "true", 1 -> True, else False).

        Returns:
            The updated RentalHasEquipment instance.

        Raises:
            ValueError: If the rental-equipment association not found.
        """
        rentalHasEquipment = RentalHasEquipment.query.filter_by(equipment_id=equipment_id, rental_id=rental_id).first()
        if not rentalHasEquipment:
            raise ValueError("Rental not found")
        
        statusUpdate = True if status in [True, "true", "True", 1] else False
        rentalHasEquipment.equipment_reviewed = statusUpdate

        db.session.commit()
        return rentalHasEquipment

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
        """Update a rental's status, terms, and/or approval.

        Handles the full spectrum of rental updates: status transitions,
        term changes (price, dates, location), and approval management.
        When terms change, both parties must re-approve. Enforces business
        rules like cancellation permissions, return timing, and
        renegotiation lead time.

        Args:
            rental_id: The rental's primary key.
            status: New status value.
            location: New meeting location text.
            agreed_price: New agreed price.
            deleted: New soft-delete flag.
            meeting_lat: New meeting latitude.
            meeting_lng: New meeting longitude.
            start_date: New start date (ISO string or datetime).
            end_date: New end date (ISO string or datetime).
            actor_user_id: Primary key of the user performing the update.
            approve: If True, record the actor's approval.

        Returns:
            The updated Rental instance.

        Raises:
            ValueError: If validation fails (unauthorized, invalid status
                transition, date conflicts, etc.).
        """
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
                now = datetime.utcnow()
                if rental.status == 'requesting':
                    if actor_user_id != rental.renter_id:
                        raise ValueError("Only the renter can cancel a rental request")
                elif rental.status == 'active':
                    if actor_user_id not in [rental.renter_id, rental.vendor_id]:
                        raise ValueError("Only rental participants can cancel this rental")
                    if now >= rental.start_date:
                        raise ValueError("Active rentals can only be canceled before they start")
                else:
                    raise ValueError("Only pending or pre-start active rentals can be canceled")

            if status == 'returned':
                if actor_user_id is None:
                    raise ValueError("actor_user_id is required when marking a rental as returned")
                if actor_user_id != rental.vendor_id:
                    raise ValueError("Only the vendor can mark a rental as returned")
                if rental.status != 'active':
                    raise ValueError("Only active rentals can be marked as returned")

                now = datetime.utcnow()
                if now <= rental.end_date:
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
            rental.start_date = RentalService._normalize_datetime(start_date, 'start_date')
        if end_date is not None:
            rental.end_date = RentalService._normalize_datetime(end_date, 'end_date')

        if start_date is not None or end_date is not None:
            minimum_start_date = datetime.utcnow() + RentalService.MIN_REQUEST_LEAD_TIME
            if rental.start_date < minimum_start_date:
                raise ValueError("Start date must be at least 2 hours in the future")

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
            if rental.status == 'active':
                renegotiation_deadline = datetime.utcnow() + RentalService.MIN_RENEGOTIATION_LEAD_TIME
                if rental.start_date <= renegotiation_deadline:
                    raise ValueError("Active rentals can only be renegotiated if they start more than one week from now")

            # Any details change requires both parties to re-approve.
            rental.renter_approved = False
            rental.vendor_approved = False
            if actor_user_id == rental.renter_id:
                rental.renter_approved = True
            if actor_user_id == rental.vendor_id:
                rental.vendor_approved = True

            if rental.status in {'requesting', 'active'}:
                rental.status = 'requesting'

        if approve:
            if actor_user_id is None:
                raise ValueError("actor_user_id is required when approving")
            if rental.status in {'requesting', 'active'}:
                rental.renter_approved = True
            if actor_user_id == rental.vendor_id:
                rental.vendor_approved = True

        # Enforce active status only when both parties approved.
        if rental.status == 'active' and not (rental.renter_approved and rental.vendor_approved):
            raise ValueError("Both renter and vendor must approve before rental can be active")

        if rental.status in {'requesting', 'active'}:
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
        """Get the average rental price for a type of equipment in a location.

        Extracts city and state from the location string and queries
        for matching rentals.

        Args:
            equipment_name: The equipment name to search for.
            location: A location string containing city and state.

        Returns:
            Average price as a float, or None if no matching data.
        """
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
        """Extract city and state from a location string.

        Handles both comma-separated ("Street, City, State ZIP") and
        newline-separated ("Street\\nCity, State ZIP") formats.

        Args:
            location: The location string to parse.

        Returns:
            Tuple of (city, state), or None if parsing fails.
        """
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