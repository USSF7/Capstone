#!/usr/bin/env python
"""
Database seeding script.
Populates the database with sample data using Faker.
"""

from datetime import datetime, timedelta
from random import randint, choice
from faker import Faker
from pathlib import Path
from app import create_app, db
from models import User, Equipment, Review, Message, Rental, RentalHasEquipment, Event, Request
import sys


def load_equipment_names():
    # .config is in project root
    config_path = Path(__file__).resolve().parent.parent / '.config'
    if config_path.exists():
        ns = {}
        with open(config_path, 'r') as f:
            exec(f.read(), {}, ns)
        if 'EQUIPMENT_NAMES' in ns:
            return ns['EQUIPMENT_NAMES']
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

def seed_users(num_users=20):
    """Create sample users"""
    print(f"Creating {num_users} users...")
    users = []
    
    for _ in range(num_users):
        randomNum = randint(1, 100)
        isVendor = bool(randomNum % 2)
        isRenter = not isVendor

        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.numerify("(###) ###-####"),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            street_address=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            zip_code=fake.zipcode(),
            vendor=isVendor,
            renter=isRenter
        )

        user.set_password(fake.password())
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"✓ Created {num_users} users")
    return users

def seed_equipment(users, num_items=30):
    """Create sample equipment"""
    print(f"Creating {num_items} equipment items...")
    equipment_list = []
    
    for _ in range(num_items):
        equipment = Equipment(
            owner_id=choice(users).id,
            name=choice(EQUIPMENT_NAMES)
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

def seed_messages(users, num_messages=50):
    """Create sample messages"""
    print(f"Creating {num_messages} messages...")
    
    for _ in range(num_messages):
        sender = choice(users)
        receiver = choice([u for u in users if u.id != sender.id])
        
        message = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            data=fake.text(max_nb_chars=300),
            send_time=fake.date_time_this_year()
        )
        db.session.add(message)
    
    db.session.commit()
    print(f"✓ Created {num_messages} messages")

def seed_events(users, num_events=15):
    """Create sample events"""
    print(f"Creating {num_events} events...")
    events = []
    
    for _ in range(num_events):
        event = Event(
            user_id=choice(users).id,
            name=fake.word(),
            date=fake.date_this_year()
        )
        events.append(event)
        db.session.add(event)
    
    db.session.commit()
    print(f"✓ Created {num_events} events")
    return events

def seed_rentals(users, equipment_list, events, num_rentals=25):
    """Create sample rentals"""
    print(f"Creating {num_rentals} rentals...")
    rentals = []
    
    statuses = ['pending', 'active', 'returned', 'disputed', 'canceled']
    
    for _ in range(num_rentals):
        renter = choice(users)
        vendor = choice([u for u in users if u.id != renter.id])
        start_date = fake.date_between(start_date='-1y', end_date='today')
        end_date = start_date + timedelta(days=randint(1, 7))
        
        rental = Rental(
            renter_id=renter.id,
            vendor_id=vendor.id,
            event_id=choice(events).id if events else None,
            location=fake.address(),
            agreed_price=round(randint(50, 500) + randint(0, 99) / 100, 2),
            start_date=start_date,
            end_date=end_date,
            status=choice(statuses)
        )
        rentals.append(rental)
        db.session.add(rental)
    
    db.session.commit()
    print(f"✓ Created {num_rentals} rentals")
    return rentals

def seed_rental_equipment(rentals, equipment_list):
    """Link exactly one equipment item to each rental"""
    print(f"Creating rental-equipment links...")
    
    for rental in rentals:
        equipment = choice(equipment_list)
        link = RentalHasEquipment(
            equipment_id=equipment.id,
            rental_id=rental.id
        )
        db.session.add(link)
    
    db.session.commit()
    print(f"✓ Created rental-equipment links")

def seed_requests(users, events, num_requests=20):
    """Create sample requests"""
    print(f"Creating {num_requests} requests...")
    
    statuses = ['created', 'completed']
    
    for _ in range(num_requests):
        start_date = fake.date_time_this_year()
        end_date = start_date + timedelta(days=randint(1, 5))
        
        request = Request(
            requester_id=choice(users).id,
            event_id=choice(events).id if events else None,
            name=choice(EQUIPMENT_NAMES),
            max_price=round(randint(100, 1000) + randint(0, 99) / 100, 2),
            count=randint(1, 10),
            start_date=start_date,
            end_date=end_date,
            location=fake.address(),
            status=choice(statuses)
        )
        db.session.add(request)
    
    db.session.commit()
    print(f"✓ Created {num_requests} requests")

def seed_db():
    """Main seeding function"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("\n" + "="*50)
            print("Starting database seeding...")
            print("="*50 + "\n")
            
            # Clear existing requests so reseeding replaces old rows
            # (avoids keeping rows that were created before `location` existed)
            # db.session.execute('TRUNCATE TABLE requests RESTART IDENTITY CASCADE;')
            # db.session.commit()

            # Seed in order of dependencies
            users = seed_users(20)
            equipment_list = seed_equipment(users, 30)
            events = seed_events(users, 15)
            seed_reviews(users, equipment_list, 100)
            seed_messages(users, 50)
            rentals = seed_rentals(users, equipment_list, events, 1000)
            seed_rental_equipment(rentals, equipment_list)
            seed_requests(users, events, 800)
            
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