#!/usr/bin/env python
"""
Database seeding script.
Populates the database with statistically realistic sample data
derived from a 25-respondent sports equipment rental survey.

All data is hardcoded / deterministic — no Faker, no random calls.
All users are in the greater Austin, TX area with hardcoded lat/lng
so spatial queries work without geocoding API calls.
"""

import sys
from datetime import datetime, timedelta, date
from html import escape
from pathlib import Path
from app import create_app, db
from models import User, Equipment, Review, Message, Rental, RentalHasEquipment


# ---------------------------------------------------------------------------
# Survey-derived constants
# ---------------------------------------------------------------------------
# Equipment popularity from survey (25 respondents, ~70 total mentions):
#   Pickleball 9, Spikeball 7, Tennis 5, Volleyball 5, Golf 5,
#   Basketball 3, Football 3, Kayak 3, Frisbee 3, Bike 2, Ski 2,
#   plus long-tail items (soccer, yoga, skates, climbing, etc.)
#
# Rental price medians from survey:
#   Pickleball $5-10, Spikeball $8-10, Tennis $5-15, Volleyball $5-10,
#   Golf $15-30, Basketball $2-5, Football $5-8, Kayak $20-30,
#   Frisbee $3-5, Bike $15-20, Ski $20

# ---------------------------------------------------------------------------
# Equipment catalog — 45 items, distribution mirrors survey popularity
# ---------------------------------------------------------------------------
EQUIPMENT_CATALOG = [
    # Pickleball — 7 listings (most popular)
    ("Pickleball Paddle Set (2 paddles + balls)", 10.00,
     "Two composite paddles with 4 outdoor pickleballs, great for casual play"),
    ("Pickleball Paddle Set (4 paddles + balls)", 18.00,
     "Four-player set with polymer paddles and 6 balls, perfect for doubles"),
    ("Pickleball Paddles (2-pack)", 8.00,
     "Lightweight graphite paddles, intermediate level"),
    ("Pickleball Net and Paddle Bundle", 25.00,
     "Portable regulation net with 2 paddles and balls included"),
    ("Pickleball Paddle (Single)", 5.00,
     "Single composite paddle, good for beginners"),
    ("Pickleball Paddle (Pro)", 12.00,
     "Carbon fiber face paddle, tournament-grade"),
    ("Pickleball Ball Pack (12)", 3.00,
     "Dozen outdoor pickleballs, USAPA approved"),

    # Spikeball — 5 listings
    ("Spikeball Standard Set", 10.00,
     "3-ball kit with adjustable net, fits in a backpack"),
    ("Spikeball Pro Set", 15.00,
     "Pro-level net with tighter weave and premium balls"),
    ("Spikeball Set (with carrying bag)", 10.00,
     "Standard set including drawstring bag for transport"),
    ("Spikeball Replacement Balls (4-pack)", 3.00,
     "Extra balls compatible with standard and pro nets"),
    ("Spikeball Rookie Set", 8.00,
     "Larger net for beginners and kids"),

    # Tennis — 4 listings
    ("Tennis Racket (Adult)", 10.00,
     "27-inch graphite racket, pre-strung, all-court use"),
    ("Tennis Racket Pair", 15.00,
     "Two rackets with a can of 3 balls, ready to play"),
    ("Tennis Racket (Junior)", 5.00,
     "25-inch racket sized for teens and smaller players"),
    ("Tennis Ball Hopper + Balls (50)", 8.00,
     "Ball hopper with 50 practice balls for drills"),

    # Volleyball — 4 listings
    ("Volleyball Net and Ball", 20.00,
     "Portable outdoor net system with regulation ball"),
    ("Volleyball (Indoor)", 5.00,
     "Molten-style indoor volleyball, game quality"),
    ("Beach Volleyball Set", 25.00,
     "Net, ball, boundary lines, and carrying case for sand play"),
    ("Volleyball (Outdoor)", 3.00,
     "Stitched outdoor volleyball, durable for park use"),

    # Golf — 4 listings
    ("Golf Club Set (Full Bag)", 30.00,
     "14-club set with bag, irons, woods, and putter"),
    ("Golf Clubs (Half Set)", 20.00,
     "7 essential clubs with stand bag, good for casual rounds"),
    ("Golf Putter", 8.00,
     "Blade-style putter, right-handed"),
    ("Disc Golf Disc Set (3)", 5.00,
     "Driver, midrange, and putter discs for disc golf"),

    # Basketball — 3 listings
    ("Basketball (Indoor/Outdoor)", 5.00,
     "Size 7 composite leather basketball"),
    ("Basketball (Official)", 2.00,
     "Rubber outdoor basketball, size 7"),
    ("Portable Basketball Hoop", 25.00,
     "Adjustable 7.5-10 ft hoop with base, wheels for transport"),

    # Football — 2 listings
    ("Football (Leather)", 8.00,
     "Official size composite leather football"),
    ("Football (Recreational)", 5.00,
     "Rubber grip football for casual toss and backyard games"),

    # Kayak — 2 listings
    ("Kayak (Single, Sit-on-Top)", 30.00,
     "10 ft recreational kayak with paddle and life vest"),
    ("Kayak (Tandem)", 20.00,
     "12 ft tandem kayak, includes 2 paddles"),

    # Frisbee — 2 listings
    ("Frisbee (Ultimate)", 3.00,
     "175g regulation ultimate disc, tournament approved"),
    ("Frisbee Golf Starter Set", 15.00,
     "Set of 5 discs covering driver to putter"),

    # Mountain Bike — 2 listings
    ("Mountain Bike (Hardtail)", 20.00,
     "26-inch aluminum frame, front suspension, 21-speed"),
    ("Mountain Bike (Full Suspension)", 30.00,
     "29-inch full-suspension trail bike, hydraulic disc brakes"),

    # Ski / Snowboard — 2 listings
    ("Ski Set (Skis + Boots + Poles)", 25.00,
     "All-mountain skis with boots (state your size) and poles"),
    ("Snowboard + Boots", 20.00,
     "Freestyle board with bindings and boots (state your size)"),

    # Long tail — 1 each
    ("Soccer Ball", 5.00,
     "Size 5 match ball, FIFA-quality replica"),
    ("Yoga Mat (Premium)", 5.00,
     "6mm thick non-slip mat with carrying strap"),
    ("Ice Skates (Pair)", 20.00,
     "Recreational figure skates, multiple sizes available"),
    ("Rock Climbing Shoes", 10.00,
     "Moderate downturn, synthetic upper, great for gym bouldering"),
    ("Skateboard (Complete)", 5.00,
     "7.75-inch deck, 52mm wheels, ABEC-7 bearings"),
    ("Roller Skates (Quad)", 15.00,
     "Classic quad skates with adjustable toe stop"),
    ("Cornhole Board Set", 10.00,
     "Regulation 2x4 ft boards with 8 all-weather bags"),
    ("Badminton Racket Set (4) + Net", 15.00,
     "4 rackets, shuttlecocks, and portable net for backyard play"),
    ("Boxing Gloves (Pair)", 12.00,
     "14 oz training gloves with wrist support"),
]

# ---------------------------------------------------------------------------
# Users — 22 users in greater Austin, TX with hardcoded lat/lng
# 60% both vendor+renter, 25% renter-only, 15% vendor-only
# ---------------------------------------------------------------------------
USERS = [
    # Test users (indices 0 and 1)
    dict(name='Sarah Mitchell', email='renter@test.com', phone='(555) 234-5678',
         dob='1994-06-15', street='742 Evergreen Terrace', city='Austin', state='Texas',
         zip_code=78704, vendor=False, renter=True,
         lat=30.2500, lng=-97.7530),
    dict(name='Marcus Chen', email='vendor@test.com', phone='(555) 876-5432',
         dob='1988-11-23', street='1200 Lakeshore Drive', city='Austin', state='Texas',
         zip_code=78703, vendor=True, renter=False,
         lat=30.2870, lng=-97.7730),

    # Both vendor + renter (13 users — indices 2–14)
    dict(name='Jake Hernandez', email='jake.hernandez@utexas.edu', phone='(512) 555-0101',
         dob='2001-03-12', street='2501 Nueces St', city='Austin', state='Texas',
         zip_code=78705, vendor=True, renter=True,
         lat=30.2880, lng=-97.7440),
    dict(name='Emily Tran', email='emily.tran@utexas.edu', phone='(512) 555-0102',
         dob='2002-07-22', street='910 W 25th St', city='Austin', state='Texas',
         zip_code=78705, vendor=True, renter=True,
         lat=30.2910, lng=-97.7460),
    dict(name='Chris Walker', email='chris.w@gmail.com', phone='(512) 555-0103',
         dob='1996-01-09', street='1600 Barton Springs Rd', city='Austin', state='Texas',
         zip_code=78704, vendor=True, renter=True,
         lat=30.2610, lng=-97.7560),
    dict(name='Priya Patel', email='priya.p@outlook.com', phone='(512) 555-0104',
         dob='2000-11-30', street='4400 N Lamar Blvd', city='Austin', state='Texas',
         zip_code=78756, vendor=True, renter=True,
         lat=30.3120, lng=-97.7410),
    dict(name='Dylan Brooks', email='dylan.brooks@utexas.edu', phone='(512) 555-0105',
         dob='2003-05-18', street='2020 S Congress Ave', city='Austin', state='Texas',
         zip_code=78704, vendor=True, renter=True,
         lat=30.2460, lng=-97.7490),
    dict(name='Sofia Ramirez', email='sofia.r@yahoo.com', phone='(512) 555-0106',
         dob='1998-09-04', street='1100 S Lamar Blvd', city='Austin', state='Texas',
         zip_code=78704, vendor=True, renter=True,
         lat=30.2560, lng=-97.7620),
    dict(name='Jordan Lee', email='jordan.lee@utexas.edu', phone='(512) 555-0107',
         dob='2001-12-27', street='3000 Guadalupe St', city='Austin', state='Texas',
         zip_code=78705, vendor=True, renter=True,
         lat=30.2950, lng=-97.7410),
    dict(name='Megan O\'Connor', email='megan.oc@gmail.com', phone='(512) 555-0108',
         dob='1999-04-15', street='5500 N MoPac Expy', city='Austin', state='Texas',
         zip_code=78731, vendor=True, renter=True,
         lat=30.3530, lng=-97.7630),
    dict(name='Tyler Nguyen', email='tyler.ng@utexas.edu', phone='(512) 555-0109',
         dob='2002-08-01', street='2400 San Jacinto Blvd', city='Austin', state='Texas',
         zip_code=78712, vendor=True, renter=True,
         lat=30.2860, lng=-97.7330),
    dict(name='Rachel Kim', email='rachel.kim@outlook.com', phone='(512) 555-0110',
         dob='1997-02-20', street='800 W 5th St', city='Austin', state='Texas',
         zip_code=78703, vendor=True, renter=True,
         lat=30.2700, lng=-97.7530),
    dict(name='Ben Alvarez', email='ben.alvarez@utexas.edu', phone='(512) 555-0111',
         dob='2000-06-08', street='6700 Burnet Rd', city='Austin', state='Texas',
         zip_code=78757, vendor=True, renter=True,
         lat=30.3400, lng=-97.7380),
    dict(name='Aisha Mohammed', email='aisha.m@gmail.com', phone='(512) 555-0112',
         dob='2001-10-19', street='1200 E Riverside Dr', city='Austin', state='Texas',
         zip_code=78741, vendor=True, renter=True,
         lat=30.2410, lng=-97.7260),
    dict(name='Liam Foster', email='liam.foster@utexas.edu', phone='(512) 555-0113',
         dob='1999-07-03', street='3500 Red River St', city='Austin', state='Texas',
         zip_code=78705, vendor=True, renter=True,
         lat=30.2970, lng=-97.7280),

    # Renter-only (5 users — indices 15–19)
    dict(name='Hannah Sullivan', email='hannah.s@gmail.com', phone='(512) 555-0114',
         dob='2003-01-25', street='11600 Domain Dr', city='Austin', state='Texas',
         zip_code=78758, vendor=False, renter=True,
         lat=30.4020, lng=-97.7250),
    dict(name='Noah Castillo', email='noah.c@utexas.edu', phone='(512) 555-0115',
         dob='2004-03-30', street='2600 Whitis Ave', city='Austin', state='Texas',
         zip_code=78705, vendor=False, renter=True,
         lat=30.2900, lng=-97.7400),
    dict(name='Chloe Davis', email='chloe.d@yahoo.com', phone='(512) 555-0116',
         dob='2002-09-11', street='4800 S Congress Ave', city='Austin', state='Texas',
         zip_code=78745, vendor=False, renter=True,
         lat=30.2170, lng=-97.7830),
    dict(name='Ethan Wright', email='ethan.w@outlook.com', phone='(512) 555-0117',
         dob='2001-04-07', street='3300 Bee Cave Rd', city='Austin', state='Texas',
         zip_code=78746, vendor=False, renter=True,
         lat=30.2720, lng=-97.8050),
    dict(name='Lily Thompson', email='lily.t@utexas.edu', phone='(512) 555-0118',
         dob='2003-08-14', street='2200 Leon St', city='Austin', state='Texas',
         zip_code=78705, vendor=False, renter=True,
         lat=30.2890, lng=-97.7500),

    # Vendor-only (3 users — indices 20–22)
    dict(name='Daniel Park', email='daniel.park@gmail.com', phone='(512) 555-0119',
         dob='1993-05-22', street='9500 S IH 35', city='Austin', state='Texas',
         zip_code=78748, vendor=True, renter=False,
         lat=30.1830, lng=-97.7800),
    dict(name='Olivia Barnes', email='olivia.b@outlook.com', phone='(512) 555-0120',
         dob='1995-12-01', street='1500 E 6th St', city='Austin', state='Texas',
         zip_code=78702, vendor=True, renter=False,
         lat=30.2650, lng=-97.7260),
    dict(name='Samuel Greene', email='sam.greene@utexas.edu', phone='(512) 555-0121',
         dob='1991-08-17', street='12400 N Lamar Blvd', city='Austin', state='Texas',
         zip_code=78753, vendor=True, renter=False,
         lat=30.3920, lng=-97.6930),
]

# Map equipment index -> owner user index (only vendor-capable users)
EQUIPMENT_OWNER_MAP = [
    1,  1,  2,  2,  3,  5,  21,          # Pickleball (7)
    4,  6,  7,  9,  22,                   # Spikeball (5)
    3,  5,  10, 14,                       # Tennis (4)
    6,  8,  11, 22,                       # Volleyball (4)
    1,  21, 13, 7,                        # Golf (4)
    2,  9,  21,                           # Basketball (3)
    4,  11,                               # Football (2)
    22, 14,                               # Kayak (2)
    5,  7,                                # Frisbee (2)
    13, 22,                               # Bike (2)
    21, 14,                               # Ski/Snowboard (2)
    6, 3, 1, 10, 9, 11, 8, 5, 12,        # Long tail (9)
]

# ---------------------------------------------------------------------------
# Reviews — 60 reviews
# Distribution: 24×5-star, 18×4-star, 9×3-star, 6×2-star, 3×1-star
# ---------------------------------------------------------------------------
_EQUIP_POS = [
    "arrived on time and in great condition",
    "was clean, well-maintained, and ready to use",
    "worked perfectly for our whole event",
    "matched the listing description exactly",
    "was easy to set up and start using right away",
    "exceeded my expectations for a rental",
]
_EQUIP_NEG = [
    "showed more wear than the photos suggested",
    "had a minor issue that slowed setup",
    "was usable but not as comfortable as expected",
    "could use some replacement accessories",
    "did not quite match the listing quality",
]
_USER_POS = [
    "was responsive and easy to coordinate with",
    "showed up on time and was very friendly",
    "communicated clearly throughout the process",
    "took excellent care of the equipment",
    "made the whole rental experience smooth",
]
_USER_NEG = [
    "was slow to respond to messages",
    "was late to the agreed meeting time",
    "returned the equipment later than promised",
    "could have communicated more clearly",
]


def _eq_text(rating, idx):
    p = _EQUIP_POS[idx % len(_EQUIP_POS)]
    n = _EQUIP_NEG[idx % len(_EQUIP_NEG)]
    if rating == 5:
        return f"Great rental experience. The equipment {p}. Would definitely rent again."
    if rating == 4:
        return f"Overall very good. The equipment {p}, though {n}. Still solid value."
    if rating == 3:
        return f"Average experience. The equipment {p}, but {n}. Room for improvement."
    if rating == 2:
        return f"Below expectations. The equipment {n}. It worked but caused some stress."
    return f"Poor experience. The equipment {n}. Would not rent this again."


def _usr_text(rating, idx):
    p = _USER_POS[idx % len(_USER_POS)]
    n = _USER_NEG[idx % len(_USER_NEG)]
    if rating == 5:
        return f"Excellent person to deal with. They {p}. Highly recommended."
    if rating == 4:
        return f"Good interaction overall. They {p}, though {n}. Would work with again."
    if rating == 3:
        return f"Okay experience. They {p}, but {n}. Average overall."
    if rating == 2:
        return f"Difficult interaction. They {n}. Needs improvement."
    return f"Very poor interaction. They {n}. Would avoid in the future."


# (submitter_idx, model_type, model_id_idx, rating, date_offset_days_ago)
REVIEWS = [
    # 5-star (24)
    (16, 'equipment', 0,  5, 10), (17, 'equipment', 7,  5, 15),
    (4,  'equipment', 12, 5, 8),  (18, 'equipment', 3,  5, 22),
    (5,  'equipment', 16, 5, 5),  (6,  'equipment', 20, 5, 30),
    (7,  'equipment', 24, 5, 12), (15, 'equipment', 27, 5, 18),
    (8,  'equipment', 30, 5, 25), (9,  'equipment', 33, 5, 3),
    (10, 'equipment', 36, 5, 14), (19, 'equipment', 1,  5, 7),
    (2,  'user', 1,  5, 9),  (4,  'user', 5,  5, 11),
    (16, 'user', 3,  5, 20), (6,  'user', 7,  5, 6),
    (8,  'user', 21, 5, 13), (17, 'user', 2,  5, 16),
    (9,  'user', 14, 5, 19), (15, 'user', 6,  5, 4),
    (3,  'user', 22, 5, 28), (11, 'user', 9,  5, 2),
    (18, 'equipment', 9,  5, 35), (19, 'equipment', 14, 5, 40),
    # 4-star (18)
    (2,  'equipment', 2,  4, 45), (3,  'equipment', 8,  4, 50),
    (10, 'equipment', 4,  4, 11), (12, 'equipment', 17, 4, 23),
    (14, 'equipment', 22, 4, 33), (15, 'equipment', 25, 4, 17),
    (16, 'equipment', 28, 4, 9),  (17, 'equipment', 31, 4, 21),
    (4,  'equipment', 35, 4, 27), (19, 'equipment', 38, 4, 36),
    (5,  'user', 4,  4, 24), (7,  'user', 8,  4, 31),
    (9,  'user', 10, 4, 38), (11, 'user', 13, 4, 44),
    (13, 'user', 2,  4, 48), (3,  'user', 11, 4, 52),
    (6,  'user', 15, 4, 55), (14, 'user', 17, 4, 60),
    # 3-star (9)
    (5,  'equipment', 5,  3, 65), (8,  'equipment', 10, 3, 70),
    (12, 'equipment', 19, 3, 42), (19, 'equipment', 23, 3, 47),
    (13, 'equipment', 29, 3, 56), (2,  'user', 16, 3, 62),
    (10, 'user', 18, 3, 68), (14, 'user', 4,  3, 72),
    (16, 'user', 12, 3, 75),
    # 2-star (6)
    (3,  'equipment', 6,  2, 80), (7,  'equipment', 15, 2, 85),
    (15, 'equipment', 26, 2, 58), (18, 'user', 21, 2, 78),
    (17, 'user', 11, 2, 82), (5,  'user', 19, 2, 88),
    # 1-star (3)
    (12, 'equipment', 11, 1, 90), (16, 'equipment', 34, 1, 95),
    (19, 'user', 20, 1, 100),
]

# ---------------------------------------------------------------------------
# Rentals — 50 rentals
# returned 40%, active 35%, requesting 15%, denied 5%, disputed 5%
# (renter_idx, vendor_idx, equip_idx, price, start_days_ago, duration, status)
# ---------------------------------------------------------------------------
RENTALS = [
    # Returned (20)
    (16, 1,  0,  10.00,  90, 2, 'returned'),
    (17, 2,  7,  10.00,  85, 3, 'returned'),
    (4,  3,  12, 15.00,  80, 1, 'returned'),
    (18, 5,  3,  18.00,  75, 2, 'returned'),
    (15, 6,  16, 20.00,  70, 4, 'returned'),
    (19, 1,  20, 30.00,  65, 2, 'returned'),
    (2,  21, 1,  10.00,  60, 1, 'returned'),
    (7,  4,  24,  5.00,  55, 2, 'returned'),
    (8,  22, 33, 20.00,  50, 5, 'returned'),
    (9,  5,  30,  3.00,  48, 1, 'returned'),
    (10, 7,  36, 20.00,  45, 3, 'returned'),
    (3,  9,  9,  10.00,  42, 2, 'returned'),
    (11, 14, 38, 15.00,  40, 1, 'returned'),
    (16, 21, 22,  8.00,  38, 2, 'returned'),
    (17, 6,  17,  5.00,  35, 1, 'returned'),
    (4,  11, 27,  8.00,  33, 3, 'returned'),
    (18, 13, 14,  5.00,  30, 2, 'returned'),
    (5,  22, 40, 10.00,  28, 1, 'returned'),
    (6,  1,  2,   8.00,  25, 2, 'returned'),
    (15, 10, 35, 25.00,  22, 4, 'returned'),
    # Active (17)
    (16, 3,  13,  5.00,   3, 5, 'active'),
    (19, 5,  4,  12.00,   2, 4, 'active'),
    (2,  7,  25,  2.00,   1, 3, 'active'),
    (17, 22, 31, 30.00,   4, 7, 'active'),
    (8,  9,  8,  15.00,   2, 3, 'active'),
    (4,  21, 21, 20.00,   1, 5, 'active'),
    (10, 6,  28, 20.00,   3, 4, 'active'),
    (18, 14, 37, 25.00,   2, 6, 'active'),
    (15, 11, 39,  5.00,   1, 2, 'active'),
    (7,  1,  6,   3.00,   2, 3, 'active'),
    # Requesting (8)
    (18, 3,  11,  8.00,  -5, 2, 'requesting'),
    (16, 9,  26,  5.00,  -4, 3, 'requesting'),
    (4,  22, 32, 20.00,  -3, 4, 'requesting'),
    (15, 6,  18, 25.00,  -2, 5, 'requesting'),
    (2,  14, 41, 15.00,  -6, 2, 'requesting'),
    (19, 11, 42, 12.00,  -4, 3, 'requesting'),
    (8,  21, 43, 15.00,  -3, 2, 'requesting'),
    (10, 5,  44, 10.00,  -5, 3, 'requesting'),
    # Denied (3)
    (17, 1,  0,  10.00,  15, 2, 'denied'),
    (19, 3,  12, 15.00,  12, 1, 'denied'),
    (16, 5,  7,  10.00,  10, 3, 'denied'),
    # Disputed (2)
    (4,  22, 36, 20.00,  20, 3, 'disputed'),
    (18, 9,  24,  5.00,  18, 2, 'disputed'),
]

# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------
_MSG_TEMPLATES = [
    "Hi, I'm interested in renting this. Is it still available?",
    "Yes it is! When do you need it?",
    "This weekend, Saturday through Monday. Does that work?",
    "That works for me. Where would you like to meet?",
    "How about the parking lot at Zilker Park?",
    "Sounds good. I'll be there at 10 AM.",
    "Great, see you then!",
    "Hey, just confirming we're still on for tomorrow?",
    "Yep, all set. I'll have everything ready.",
    "Thanks! Looking forward to it.",
    "Got it, everything looks good. Thanks!",
    "Let me know when you're ready to return it.",
    "Will do. Planning to drop it off Sunday evening.",
    "I can also meet at the Rec Center if that's easier.",
    "Actually the Rec Center works better for me.",
    "Cool, let's do that then.",
    "What condition is the equipment in?",
    "It's in great shape, barely used.",
    "Would you take $8 instead of $10?",
    "I can do $9, meet in the middle?",
    "Deal, $9 works for me.",
    "Is there a deposit required?",
    "No deposit, just take care of it please.",
    "Absolutely, I'll treat it like my own.",
    "Running about 10 minutes late, sorry!",
    "No worries, I'm here whenever you arrive.",
    "Just picked it up, thanks!",
    "Enjoy! Let me know if you have any issues.",
    "Everything worked great, returning tomorrow.",
    "Awesome, thanks for the update.",
    "Returned and in good condition. Thanks for renting!",
    "Thanks for taking good care of it!",
]

_msg_patterns = [
    (0,  [(True,0,-48), (False,1,-47), (True,2,-46), (False,3,-45), (True,4,-44), (False,5,-43)]),
    (1,  [(True,0,-24), (False,1,-23), (True,7,-2), (False,8,-1)]),
    (2,  [(True,16,-72), (False,17,-71), (True,0,-70), (False,3,-69), (True,6,-68)]),
    (3,  [(True,0,-48), (False,1,-47), (True,18,-46), (False,19,-45), (True,20,-44)]),
    (4,  [(True,0,-96), (False,1,-95), (True,2,-94), (False,5,-93)]),
    (5,  [(True,21,-24), (False,22,-23), (True,23,-22)]),
    (6,  [(True,0,-48), (False,17,-47), (True,6,-46)]),
    (7,  [(True,0,-24), (False,1,-23), (True,26,-1), (False,27,0)]),
    (8,  [(True,16,-72), (False,17,-71), (True,6,-70), (True,28,48), (False,29,49)]),
    (9,  [(True,0,-12), (False,1,-11)]),
    (10, [(True,0,-48), (False,3,-47), (True,13,-46), (False,14,-45), (True,15,-44)]),
    (11, [(True,0,-24), (False,1,-23), (True,2,-22), (False,5,-21)]),
    (12, [(True,0,-12), (False,17,-11), (True,6,-10)]),
    (13, [(True,0,-48), (False,1,-47)]),
    (14, [(True,0,-24), (False,1,-23), (True,6,-22)]),
    (15, [(True,16,-48), (False,17,-47), (True,6,-46)]),
    (16, [(True,0,-24), (False,1,-23)]),
    (17, [(True,0,-12), (False,3,-11), (True,6,-10)]),
    (18, [(True,0,-48), (False,1,-47), (True,24,0), (False,25,1)]),
    (19, [(True,0,-72), (False,1,-71), (True,2,-70), (False,5,-69)]),
    (20, [(True,0,-72), (False,1,-71), (True,2,-70), (False,5,-69), (True,26,0)]),
    (21, [(True,0,-48), (False,1,-47), (True,6,-46)]),
    (22, [(True,0,-24), (False,1,-23)]),
    (23, [(True,0,-96), (False,1,-95), (True,2,-94), (False,5,-93), (True,7,-2), (False,8,-1)]),
    (24, [(True,0,-48), (False,17,-47), (True,6,-46)]),
]

MESSAGES = []
for rental_idx, msgs in _msg_patterns:
    for is_renter, tmpl_idx, h_offset in msgs:
        MESSAGES.append((rental_idx, is_renter, _MSG_TEMPLATES[tmpl_idx], h_offset))

# Austin meetup locations
MEETUP_LOCATIONS = [
    "Zilker Park, 2100 Barton Springs Rd, Austin, TX 78704",
    "Gregory Gym, 2101 Speedway, Austin, TX 78712",
    "Pease Park, 1100 Kingsbury St, Austin, TX 78705",
    "Mueller Lake Park, 4550 Mueller Blvd, Austin, TX 78723",
    "Republic Square, 422 Guadalupe St, Austin, TX 78701",
    "Auditorium Shores, 800 W Riverside Dr, Austin, TX 78704",
    "Commons Ford Ranch, 614 N Commons Ford Rd, Austin, TX 78733",
    "Mary Moore Searight Park, 907 Slaughter Ln W, Austin, TX 78748",
]


# ===========================================================================
# Seeding functions
# ===========================================================================

def equipment_filename(name):
        """Create deterministic image filename slug for an equipment name."""
        return (name.lower()
            .replace(' ', '_')
            .replace('(', '')
            .replace(')', '')
            .replace('/', '_')
            .replace(',', ''))


def equipment_emoji(name):
    """Return a best-effort emoji that matches the equipment name."""
    label = name.lower()

    if 'pickleball' in label or 'tennis' in label or 'badminton' in label:
        return '🎾'
    if 'golf' in label:
        return '⛳'
    if 'basketball' in label:
        return '🏀'
    if 'football' in label:
        return '🏈'
    if 'soccer' in label:
        return '⚽'
    if 'volleyball' in label:
        return '🏐'
    if 'frisbee' in label or 'disc' in label:
        return '🥏'
    if 'kayak' in label:
        return '🛶'
    if 'bike' in label:
        return '🚲'
    if 'ski' in label or 'snowboard' in label or 'skate' in label:
        return '⛷️'
    if 'yoga' in label:
        return '🧘'
    if 'climbing' in label:
        return '🧗'
    if 'boxing' in label or 'gloves' in label:
        return '🥊'
    if 'cornhole' in label:
        return '🎯'
    if 'spikeball' in label:
        return '🏐'

    return '🎒'


def seed_equipment_images_if_missing():
    """Create SVG placeholder images for catalog items if files do not exist."""
    backend_dir = Path(__file__).resolve().parent
    images_dir = backend_dir / 'images' / 'equipment'

    images_dir.mkdir(parents=True, exist_ok=True)

    created_count = 0
    for name, _price, _desc in EQUIPMENT_CATALOG:
        filename = equipment_filename(name)
        image_path = images_dir / f"{filename}.svg"

        if image_path.exists():
            continue

        label = escape(name)
        emoji = equipment_emoji(name)
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450" role="img" aria-label="{label}">
            <defs>
                <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#dbeafe"/>
                <stop offset="100%" stop-color="#bfdbfe"/>
                </linearGradient>
            </defs>
            <rect width="800" height="450" fill="url(#bg)"/>
                <rect x="30" y="30" width="740" height="390" rx="20" fill="#ffffff" fill-opacity="0.8"/>
                <text x="400" y="250" text-anchor="middle" font-size="180" font-family="Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif">{emoji}</text>
            </svg> '''
        image_path.write_text(svg, encoding='utf-8')
        created_count += 1

    print(f"✓ Ensured equipment images at {images_dir} ({created_count} created, {len(EQUIPMENT_CATALOG) - created_count} existing)")



def seed_users():
    """Create all users with hardcoded lat/lng."""
    print("Creating users...")
    users = []
    for u in USERS:
        user = User(
            name=u['name'],
            email=u['email'],
            phone=u['phone'],
            date_of_birth=u['dob'],
            street_address=u['street'],
            city=u['city'],
            state=u['state'],
            zip_code=u['zip_code'],
            vendor=u['vendor'],
            renter=u['renter'],
            latitude=u['lat'],
            longitude=u['lng'],
            picture=''
        )
        user.set_password('password')
        db.session.add(user)
        users.append(user)
    db.session.commit()
    print(f"✓ Created {len(users)} users (test + regular)")
    return users


def seed_equipment(users):
    """Create equipment with survey-realistic names and prices."""
    print("Creating equipment...")
    equipment_list = []
    conditions = ["Mint", "Above Average", "Average", "Below Average"]
    for i, (name, price, desc) in enumerate(EQUIPMENT_CATALOG):
        owner_idx = EQUIPMENT_OWNER_MAP[i]
        filename = equipment_filename(name)
        eq = Equipment(
            owner_id=users[owner_idx].id,
            name=name,
            price=price,
            description=desc,
            picture=f"images/equipment/{filename}.svg",
            condition=conditions[i % len(conditions)],
        )
        db.session.add(eq)
        equipment_list.append(eq)
    db.session.commit()
    print(f"✓ Created {len(equipment_list)} equipment items")
    return equipment_list


def seed_reviews(users, equipment_list):
    """Create reviews with survey-realistic rating distribution."""
    print("Creating reviews...")
    today = datetime.utcnow()
    for i, (sub_idx, model_type, model_id_idx, rating, days_ago) in enumerate(REVIEWS):
        if model_type == 'equipment':
            model_id = equipment_list[model_id_idx].id
            text = _eq_text(rating, i)
        else:
            model_id = users[model_id_idx].id
            text = _usr_text(rating, i)

        review = Review(
            submitter_id=users[sub_idx].id,
            model_type=model_type,
            model_id=model_id,
            rating=rating,
            review=text,
            date=today - timedelta(days=days_ago),
        )
        db.session.add(review)
    db.session.commit()
    print(f"✓ Created {len(REVIEWS)} reviews")


def seed_rentals(users, equipment_list):
    """Create rentals and link equipment."""
    print("Creating rentals...")
    today = date.today()
    rentals = []

    for i, (renter_idx, vendor_idx, equip_idx, price, start_offset, duration, status) in enumerate(RENTALS):
        if start_offset >= 0:
            start_date = today - timedelta(days=start_offset)
        else:
            start_date = today + timedelta(days=abs(start_offset))
        end_date = start_date + timedelta(days=duration)
        location = MEETUP_LOCATIONS[i % len(MEETUP_LOCATIONS)]

        # Set approvals based on status.
        # Only active/returned/disputed rentals should have both approvals.
        renter_approved = status in ('active', 'returned', 'disputed')
        vendor_approved = status in ('active', 'returned', 'disputed')

        rental = Rental(
            renter_id=users[renter_idx].id,
            vendor_id=users[vendor_idx].id,
            location=location,
            agreed_price=price,
            start_date=start_date,
            end_date=end_date,
            status=status,
            deleted=False,
            renter_approved=renter_approved,
            vendor_approved=vendor_approved,
        )
        db.session.add(rental)
        rentals.append(rental)

    db.session.commit()

    for i, (_, _, equip_idx, *_rest) in enumerate(RENTALS):
        link = RentalHasEquipment(
            equipment_id=equipment_list[equip_idx].id,
            rental_id=rentals[i].id,
        )
        db.session.add(link)

    db.session.commit()
    print(f"✓ Created {len(rentals)} rentals with equipment links")
    return rentals


def seed_messages(users, rentals):
    """Create messages tied to real rental participants."""
    print("Creating messages...")

    for rental_idx, is_renter, text, h_offset in MESSAGES:
        rental = rentals[rental_idx]
        sender_id = rental.renter_id if is_renter else rental.vendor_id
        receiver_id = rental.vendor_id if is_renter else rental.renter_id

        base = datetime.combine(rental.start_date, datetime.min.time())
        send_time = base + timedelta(hours=h_offset)

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            rental_id=rental.id,
            data=text,
            send_time=send_time,
        )
        db.session.add(message)

    db.session.commit()
    print(f"✓ Created {len(MESSAGES)} messages")


def seed_db():
    """Main seeding function."""
    app = create_app('development')

    with app.app_context():
        try:
            print("\n" + "=" * 50)
            print("Starting database seeding (survey-derived data)...")
            print("=" * 50 + "\n")

            seed_equipment_images_if_missing()
            users = seed_users()
            equipment_list = seed_equipment(users)
            seed_reviews(users, equipment_list)
            rentals = seed_rentals(users, equipment_list)
            seed_messages(users, rentals)

            print("\n" + "=" * 50)
            print("✓ Database seeding completed successfully!")
            print(f"  Users: {len(USERS)}")
            print(f"  Equipment: {len(EQUIPMENT_CATALOG)}")
            print(f"  Reviews: {len(REVIEWS)}")
            print(f"  Rentals: {len(RENTALS)}")
            print(f"  Messages: {len(MESSAGES)}")
            print("=" * 50 + "\n")
            return True

        except Exception as e:
            print(f"\n✗ Error seeding database: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = seed_db()
    sys.exit(0 if success else 1)