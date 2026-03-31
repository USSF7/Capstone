#!/usr/bin/env python
"""
Database seeding script.
Populates the database with sample data using Faker.
"""

import json
from datetime import datetime, timedelta
from random import randint, choice
from faker import Faker
from pathlib import Path
from app import create_app, db
from models import User, Equipment, Review, Message, Rental, RentalHasEquipment
import sys


def load_equipment_names():
    # .config is in project root
    config_path = Path(__file__).resolve().parent.parent / '.config'
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
        if 'EQUIPMENT_NAMES' in data:
            return data['EQUIPMENT_NAMES']
    return [
        'Projector', 'Sound System', 'Microphone', 'Camera', 'Lighting Kit',
        'DJ Booth', 'Tent', 'Tables', 'Chairs', 'Decorations',
        'Amplifier', 'Speaker', 'Mixer', 'Laptop', 'Monitor',
        'Screen', 'Tripod', 'Cables', 'Microphone Stand', 'Power Bank'
    ]

EQUIPMENT_NAMES = load_equipment_names()

fake = Faker()


def _build_equipment_review_text(rating):
    positives = [
        "arrived on time",
        "was clean and ready to use",
        "worked reliably throughout the event",
        "matched the listing description",
        "was easy to set up"
    ]
    negatives = [
        "showed more wear than expected",
        "performance was inconsistent throughout the session",
        "was not as comfortable to use for a full event",
        "did not hold up well under normal activity",
        "came with a few missing or worn accessories",
        "quality did not match the listing photos",
    ]

    if rating >= 5:
        return (
            f"Great rental experience. The equipment {choice(positives)} and made the event run smoothly. "
            "I would definitely rent this again."
        )
    if rating == 4:
        return (
            f"Overall very good. The equipment {choice(positives)}, though {choice(negatives)}. "
            "Still a solid option and good value."
        )
    if rating == 3:
        return (
            f"Average experience. The equipment {choice(positives)}, but {choice(negatives)}. "
            "Usable, but there is room for improvement."
        )
    if rating == 2:
        return (
            f"Below expectations. The equipment had issues: {choice(negatives)}. "
            "It worked in parts, but caused unnecessary stress during the event."
        )
    return (
        f"Poor experience. The equipment had multiple problems and {choice(negatives)}. "
        "I would not rent this item again in its current condition."
    )


def _build_user_review_text(rating):
    positives = [
        "communicated clearly and quickly",
        "was punctual for handoff",
        "was professional and courteous",
        "was flexible when plans changed",
        "made the process straightforward"
    ]
    negatives = [
        "responses were delayed",
        "pickup details were unclear",
        "coordination at return was difficult",
        "communication was inconsistent",
        "some expectations were not clearly discussed"
    ]

    if rating >= 5:
        return (
            f"Excellent person to work with. They {choice(positives)} and everything went smoothly. "
            "Highly recommended."
        )
    if rating == 4:
        return (
            f"Good overall interaction. They {choice(positives)}; only small issue was that {choice(negatives)}. "
            "I would work with them again."
        )
    if rating == 3:
        return (
            f"Mixed experience. They {choice(positives)}, but {choice(negatives)}. "
            "Average overall."
        )
    if rating == 2:
        return (
            f"Difficult interaction. {choice(negatives).capitalize()}, and that made the rental process harder than expected. "
            "Needs improvement in communication and coordination."
        )
    return (
        f"Very poor interaction. {choice(negatives).capitalize()}, and multiple parts of the handoff were frustrating. "
        "I would avoid future transactions."
    )

def seed_test_users():
    """Create deterministic test users for development login."""
    print("Creating test users...")
    test_users = []

    renter = User(
        name='Sarah Mitchell',
        email='renter@test.com',
        phone='(555) 234-5678',
        date_of_birth='1994-06-15',
        street_address='742 Evergreen Terrace',
        city='College Station',
        state='Texas',
        zip_code=77840,
        latitude=30.6295,
        longitude=-96.3365,
        vendor=False,
        renter=True
    )
    renter.set_password('password')
    test_users.append(renter)
    db.session.add(renter)

    vendor = User(
        name='Marcus Chen',
        email='vendor@test.com',
        phone='(555) 876-5432',
        date_of_birth='1988-11-23',
        street_address='1200 Lakeshore Drive',
        city='Bryan',
        state='Texas',
        zip_code=77801,
        latitude=30.6728,
        longitude=-96.3687,
        vendor=True,
        renter=False,
        max_travel_distance=10
    )
    vendor.set_password('password')
    test_users.append(vendor)
    db.session.add(vendor)

    db.session.commit()
    print("✓ Created 2 test users (renter@test.com / vendor@test.com, password: password)")
    return test_users


def seed_users(num_users=40):
    """Create sample users"""
    print(f"Creating {num_users} users...")
    users = []
    # Bryan/College Station, Texas area center points with realistic spread
    bryan_cs_area = [
        {'city': 'College Station', 'zip': 77840, 'lat': 30.6295, 'lon': -96.3365},
        {'city': 'Bryan', 'zip': 77801, 'lat': 30.6728, 'lon': -96.3687},
        {'city': 'College Station', 'zip': 77843, 'lat': 30.6250, 'lon': -96.3400},
        {'city': 'Bryan', 'zip': 77802, 'lat': 30.6700, 'lon': -96.3650},
    ]

    for _ in range(num_users):
        randomNum = randint(1, 100)
        isVendor = bool(randomNum % 2)
        isRenter = not isVendor
        location = choice(bryan_cs_area)
        
        # Add random variation to coordinates for realistic spread (approximately 0.01 degrees = ~1km)
        lat_offset = (randint(-100, 100) / 1000)
        lon_offset = (randint(-100, 100) / 1000)

        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.numerify("(###) ###-####"),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            street_address=fake.street_address(),
            city=location['city'],
            state='Texas',
            zip_code=location['zip'],
            latitude=round(location['lat'] + lat_offset, 4),
            longitude=round(location['lon'] + lon_offset, 4),
            vendor=isVendor,
            renter=isRenter,
            max_travel_distance=randint(0, 20) if isVendor else None
        )

        user.set_password(fake.password())
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"✓ Created {num_users} users")
    return users

def seed_equipment(users, num_items=60):
    """Create sample equipment"""
    print(f"Creating {num_items} equipment items...")
    equipment_list = []
    
    # Filter to only vendors
    vendors = [user for user in users if user.vendor]
    
    if not vendors:
        print("! No vendors found; skipping equipment seeding")
        return []
    
    for _ in range(num_items):
        equipment = Equipment(
            owner_id=choice(vendors).id,
            name=choice(EQUIPMENT_NAMES),
            price=round(randint(10, 1000) + randint(0, 99) / 100, 2),
            description=fake.sentence(nb_words=12),
            picture=f"/images/equipment/{fake.uuid4()}.jpg"
        )
        equipment_list.append(equipment)
        db.session.add(equipment)
    
    db.session.commit()
    print(f"✓ Created {num_items} equipment items")
    return equipment_list

def seed_reviews(users, equipment_list, num_reviews=100):
    """Create sample reviews with realistic, rating-aware text"""
    print(f"Creating {num_reviews} reviews...")

    for _ in range(num_reviews):
        submitter = choice(users)
        model_type = choice(['equipment', 'user'])

        if model_type == 'equipment':
            model_id = choice(equipment_list).id
        else:
            target_user = choice([u for u in users if u.id != submitter.id])
            model_id = target_user.id

        rating = randint(1, 5)
        if model_type == 'equipment':
            review_text = _build_equipment_review_text(rating)
        else:
            review_text = _build_user_review_text(rating)

        review = Review(
            submitter_id=submitter.id,
            model_type=model_type,
            model_id=model_id,
            rating=rating,
            review=review_text,
            date=fake.date_time_this_year()
        )
        db.session.add(review)
    
    db.session.commit()
    print(f"✓ Created {num_reviews} reviews")

def seed_messages(rentals, num_messages=50):
    """Create sample messages tied to real rentals and participants"""
    print(f"Creating {num_messages} messages...")

    if not rentals:
        print("! No rentals found; skipping message seeding")
        return
    
    for _ in range(num_messages):
        rental = choice(rentals)

        # Messages are only between the two users participating in the rental.
        if randint(0, 1) == 0:
            sender_id = rental.renter_id
            receiver_id = rental.vendor_id
        else:
            sender_id = rental.vendor_id
            receiver_id = rental.renter_id
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            rental_id=rental.id,
            data=fake.text(max_nb_chars=300),
            send_time=fake.date_time_this_year()
        )
        db.session.add(message)
    
    db.session.commit()
    print(f"✓ Created {num_messages} messages")

def seed_rentals(users, equipment_list, num_rentals=25):
    """Create sample rentals with linked equipment.

    The vendor is always the equipment's owner so the rental and
    equipment views stay consistent.
    """
    print(f"Creating {num_rentals} rentals...")
    rentals = []
    today = datetime.utcnow().date()

    for _ in range(num_rentals):
        equipment = choice(equipment_list)
        vendor_id = equipment.owner_id
        renter = choice([u for u in users if u.id != vendor_id])
        start_date = fake.date_between(start_date='-1y', end_date='+60d')
        end_date = start_date + timedelta(days=randint(1, 7))

        # Status logic based on rental timing:
        # - any rental can be denied
        # - past rentals are returned
        # - future rentals are requesting or active
        # - ongoing rentals are active
        if randint(1, 100) <= 15:
            status = 'denied'
            renter_approved = True
            vendor_approved = False
        elif end_date < today:
            status = 'returned'
            renter_approved = True
            vendor_approved = True
        elif start_date > today:
            status = choice(['requesting', 'active'])
            if status == 'active':
                renter_approved = True
                vendor_approved = True
            else:
                renter_approved = True
                vendor_approved = False
        else:
            status = 'active'
            renter_approved = True
            vendor_approved = True

        rental = Rental(
            renter_id=renter.id,
            vendor_id=vendor_id,
            location=fake.address(),
            agreed_price=round(randint(50, 500) + randint(0, 99) / 100, 2),
            start_date=start_date,
            end_date=end_date,
            status=status,
            renter_approved=renter_approved,
            vendor_approved=vendor_approved,
            deleted=False
        )
        db.session.add(rental)
        db.session.flush()  # populate rental.id before creating the link

        link = RentalHasEquipment(
            equipment_id=equipment.id,
            rental_id=rental.id
        )
        db.session.add(link)
        rentals.append(rental)

    db.session.commit()
    print(f"✓ Created {num_rentals} rentals with equipment links")
    return rentals

def seed_test_rental_between_test_users(test_users, equipment_list):
    """Create one guaranteed rental between renter@test.com and vendor@test.com."""
    print("Creating guaranteed rental between test renter and test vendor...")

    renter = next((user for user in test_users if user.email == 'renter@test.com'), None)
    vendor = next((user for user in test_users if user.email == 'vendor@test.com'), None)

    if not renter or not vendor:
        raise ValueError("Test renter/vendor accounts were not found")

    # Pick equipment owned by the test vendor so vendor_id matches owner_id
    vendor_equipment = [e for e in equipment_list if e.owner_id == vendor.id]
    if not vendor_equipment:
        # Create one if the vendor doesn't own any yet
        equipment = Equipment(
            owner_id=vendor.id,
            name=choice(EQUIPMENT_NAMES),
            price=99.99,
            description='Test equipment for guaranteed rental',
            picture='/images/equipment/test.jpg'
        )
        db.session.add(equipment)
        db.session.flush()
    else:
        equipment = choice(vendor_equipment)

    start_date = datetime.utcnow().date() + timedelta(days=7)  # future rental
    end_date = start_date + timedelta(days=2)

    rental = Rental(
        renter_id=renter.id,
        vendor_id=vendor.id,
        location='123 Test Ave, College Station, TX 77840',
        agreed_price=99.99,
        start_date=start_date,
        end_date=end_date,
        status='requesting',
        deleted=False
    )
    db.session.add(rental)
    db.session.flush()

    link = RentalHasEquipment(
        equipment_id=equipment.id,
        rental_id=rental.id
    )
    db.session.add(link)
    db.session.commit()

    print(f"✓ Created guaranteed test rental (id={rental.id})")
    return rental


def seed_test_active_past_due_rental_between_test_users(test_users, equipment_list):
    """Create one guaranteed active rental between test users with an end date in the past."""
    print("Creating guaranteed active past-due rental between test renter and test vendor...")

    renter = next((user for user in test_users if user.email == 'renter@test.com'), None)
    vendor = next((user for user in test_users if user.email == 'vendor@test.com'), None)

    if not renter or not vendor:
        raise ValueError("Test renter/vendor accounts were not found")

    vendor_equipment = [e for e in equipment_list if e.owner_id == vendor.id]
    if not vendor_equipment:
        equipment = Equipment(
            owner_id=vendor.id,
            name=choice(EQUIPMENT_NAMES),
            price=149.99,
            description='Test equipment for guaranteed active past-due rental',
            picture='/images/equipment/test-active-past-due.jpg'
        )
        db.session.add(equipment)
        db.session.flush()
    else:
        equipment = choice(vendor_equipment)

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=5)
    end_date = today - timedelta(days=1)

    rental = Rental(
        renter_id=renter.id,
        vendor_id=vendor.id,
        location='123 Test Ave, College Station, TX 77840',
        agreed_price=149.99,
        start_date=start_date,
        end_date=end_date,
        status='active',
        renter_approved=True,
        vendor_approved=True,
        deleted=False
    )
    db.session.add(rental)
    db.session.flush()

    link = RentalHasEquipment(
        equipment_id=equipment.id,
        rental_id=rental.id
    )
    db.session.add(link)
    db.session.commit()

    print(f"✓ Created guaranteed active past-due test rental (id={rental.id})")
    return rental


def seed_db():
    """Main seeding function"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("\n" + "="*50)
            print("Starting database seeding...")
            print("="*50 + "\n")
            
            # Seed in order of dependencies
            test_users = seed_test_users()
            users = seed_users(20)
            users = test_users + users
            equipment_list = seed_equipment(users, 30)
            seed_reviews(users, equipment_list, 40)
            rentals = seed_rentals(users, equipment_list, 75)
            test_rental = seed_test_rental_between_test_users(test_users, equipment_list)
            test_active_past_due_rental = seed_test_active_past_due_rental_between_test_users(test_users, equipment_list)
            rentals.append(test_rental)
            rentals.append(test_active_past_due_rental)
            seed_messages(rentals, 50)
            
            print("\n" + "="*50)
            print("✓ Database seeding completed successfully!")
            print("="*50 + "\n")
            return True
            
        except Exception as e:
            print(f"\n✗ Error seeding database: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = seed_db()
    sys.exit(0 if success else 1)