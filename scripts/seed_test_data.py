"""
Seed script for adding test data to the database.

This script can be run manually or as part of the test container startup.
It's idempotent - safe to run multiple times.

Usage:
    python scripts/seed_test_data.py
    # Or in docker-compose:
    command: sh -c "python -m alembic upgrade head && python scripts/seed_test_data.py && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from services.Database.PostgresConnection import SessionLocal, engine
from models.database import User, Park, Equipment, ParkEquipment, Image, Review, Event
from decimal import Decimal
from datetime import date, time, timedelta
import uuid


def seed_users(db: Session) -> dict[str, User]:
    """Seed test users and return a dict mapping email to User."""
    users_data = [
        {
            "auth0_id": "auth0|test_user_1",
            "email": "testuser1@example.com",
            "name": "Test User One",
            "role": "user",
            "is_active": True,
        },
        {
            "auth0_id": "auth0|test_user_2",
            "email": "testuser2@example.com",
            "name": "Test User Two",
            "role": "user",
            "is_active": True,
        },
        {
            "auth0_id": "auth0|test_admin",
            "email": "admin@example.com",
            "name": "Test Admin",
            "role": "admin",
            "is_active": True,
        },
        {
            "auth0_id": "auth0|test_moderator",
            "email": "moderator@example.com",
            "name": "Test Moderator",
            "role": "moderator",
            "is_active": True,
        },
    ]
    
    users = {}
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            users[user_data["email"]] = existing_user
            print(f"User {user_data['email']} already exists, skipping...")
        else:
            user = User(**user_data)
            db.add(user)
            db.flush()  # Flush to get the ID
            users[user_data["email"]] = user
            print(f"Created user: {user_data['email']}")
    
    return users


def seed_parks(db: Session, users: dict[str, User]) -> list[Park]:
    """Seed test parks and return list of created parks."""
    parks_data = [
        {
            "name": "Pecan Grove Park",
            "description": "Community park in Rowlett with outdoor fitness equipment and recreational facilities",
            "latitude": Decimal("32.901722222"),
            "longitude": Decimal("-96.548666666"),
            "address": "5300 Main St, Rowlett, TX 75088",
            "city": "Rowlett",
            "state": "TX",
            "country": "USA",
            "postal_code": "75088",
            "status": "approved",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": users["admin@example.com"].id,
        },
        {
            "name": "Springfield Park",
            "description": "Community park in Rowlett with outdoor fitness equipment and recreational facilities",
            "latitude": Decimal("32.9110278"),
            "longitude": Decimal("-96.5901944"),
            "address": "5501 Antioch Dr, Rowlett, TX 75089",
            "city": "Rowlett",
            "state": "TX",
            "country": "USA",
            "postal_code": "75089",
            "status": "approved",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": users["admin@example.com"].id,
        },
        {
            "name": "Barras Insurgentes \"Spartans Streetworkout\"",
            "description": "Street workout park in Mexico City with calisthenics equipment",
            "latitude": Decimal("19.42406778677866"),
            "longitude": Decimal("-99.16194404296651"),
            "address": "Av Chapultepec 276, Roma Nte., Cuauhtémoc, 06700 Ciudad de México, CDMX, Mexico",
            "city": "Ciudad de México",
            "state": "CDMX",
            "country": "Mexico",
            "postal_code": "06700",
            "status": "approved",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": users["admin@example.com"].id,
        },
        {
            "name": "San Leandro Marina Park",
            "description": "Marina park in San Leandro with outdoor fitness equipment and waterfront access",
            "latitude": Decimal("19.42406778677866"),
            "longitude": Decimal("-99.16194404296651"),
            "address": "13791 Monarch Bay Dr, San Leandro, CA 94577",
            "city": "San Leandro",
            "state": "CA",
            "country": "USA",
            "postal_code": "94577",
            "status": "approved",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": users["admin@example.com"].id,
        },
    ]
    
    parks = []
    for park_data in parks_data:
        # Check if park already exists by name
        existing_park = db.query(Park).filter(Park.name == park_data["name"]).first()
        if existing_park:
            parks.append(existing_park)
            print(f"Park {park_data['name']} already exists, skipping...")
        else:
            park = Park(**park_data)
            db.add(park)
            db.flush()  # Flush to get the ID
            parks.append(park)
            print(f"Created park: {park_data['name']}")
    
    return parks


def seed_park_equipment(db: Session, parks: list[Park]):
    """Associate equipment with parks."""
    # Get all equipment
    all_equipment = db.query(Equipment).all()
    if not all_equipment:
        print("No equipment found. Make sure migrations have run.")
        return
    
    # Associate equipment with parks
    associations = [
        (parks[0], [all_equipment[0], all_equipment[1], all_equipment[2]]),  # Golden Gate Park
        (parks[1], [all_equipment[2], all_equipment[3], all_equipment[4]]),  # Dolores Park
        (parks[2], [all_equipment[0], all_equipment[5]]),  # Marina Green
    ]
    
    for park, equipment_list in associations:
        for equipment in equipment_list:
            # Check if association already exists
            existing = db.query(ParkEquipment).filter(
                ParkEquipment.park_id == park.id,
                ParkEquipment.equipment_id == equipment.id
            ).first()
            
            if not existing:
                association = ParkEquipment(
                    park_id=park.id,
                    equipment_id=equipment.id
                )
                db.add(association)
                print(f"Associated {equipment.name} with {park.name}")


def seed_reviews(db: Session, parks: list[Park], users: dict[str, User]):
    """Seed test reviews."""
    reviews_data = [
        {
            "park_id": parks[0].id,
            "user_id": users["testuser1@example.com"].id,
            "rating": 5,
            "comment": "Great park with lots of equipment!",
            "is_approved": True,
        },
        {
            "park_id": parks[0].id,
            "user_id": users["testuser2@example.com"].id,
            "rating": 4,
            "comment": "Nice place, but can get crowded.",
            "is_approved": True,
        },
        {
            "park_id": parks[1].id,
            "user_id": users["testuser1@example.com"].id,
            "rating": 5,
            "comment": "Amazing views and great equipment variety!",
            "is_approved": True,
        },
    ]
    
    for review_data in reviews_data:
        # Check if review already exists
        existing = db.query(Review).filter(
            Review.park_id == review_data["park_id"],
            Review.user_id == review_data["user_id"]
        ).first()
        
        if not existing:
            review = Review(**review_data)
            db.add(review)
            print(f"Created review for park {review_data['park_id']} by user {review_data['user_id']}")


def seed_images(db: Session, parks: list[Park], users: dict[str, User]):
    """Seed test images."""
    images_data = [
        {
            "park_id": parks[0].id,
            "uploaded_by": users["testuser1@example.com"].id,
            "image_url": "https://example.com/images/central-park-1.jpg",
            "thumbnail_url": "https://example.com/images/central-park-1-thumb.jpg",
            "alt_text": "Central Park main entrance",
            "is_approved": True,
            "is_primary": True,
        },
        {
            "park_id": parks[0].id,
            "uploaded_by": users["testuser2@example.com"].id,
            "image_url": "https://example.com/images/central-park-2.jpg",
            "thumbnail_url": "https://example.com/images/central-park-2-thumb.jpg",
            "alt_text": "Central Park equipment area",
            "is_approved": True,
            "is_primary": False,
        },
        {
            "park_id": parks[1].id,
            "uploaded_by": users["testuser1@example.com"].id,
            "image_url": "https://example.com/images/golden-gate-1.jpg",
            "thumbnail_url": "https://example.com/images/golden-gate-1-thumb.jpg",
            "alt_text": "Golden Gate Park view",
            "is_approved": True,
            "is_primary": True,
        },
    ]
    
    for image_data in images_data:
        # Check if image already exists (by URL)
        existing = db.query(Image).filter(
            Image.image_url == image_data["image_url"]
        ).first()
        
        if not existing:
            image = Image(**image_data)
            db.add(image)
            print(f"Created image for park {image_data['park_id']}")


def seed_events(db: Session, parks: list[Park], users: dict[str, User]):
    """Seed events from Bay Area and Garland, TX parks."""
    today = date.today()
    park_lookup = {park.name: park for park in parks}

    def next_weekday(start: date, weekday: int) -> date:
        """Return the next occurrence of the requested weekday (0=Monday)."""
        days_ahead = (weekday - start.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return start + timedelta(days=days_ahead)

    events_data = [
        {
            "park_name": "Golden Gate Park",
            "name": "November Project SF - Kezar Stadium Stairs",
            "description": "Community-led stair repeats and bodyweight circuits on the Kezar Stadium steps.",
            "host": "November Project San Francisco",
            "weekday": 2,  # Wednesday
            "event_time": time(6, 29),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Golden Gate Park",
            "name": "SF Road Runners Club Track Intervals",
            "description": "Coached Tuesday-night interval session on the Kezar track. RSVP required for visitors.",
            "host": "San Francisco Road Runners Club",
            "weekday": 1,  # Tuesday
            "event_time": time(18, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Golden Gate Park",
            "name": "Sunday Roller Disco at Skatin' Place",
            "description": "D. Miles Jr. and the Church of 8 Wheels spin funk and disco for the weekly roller party on JFK Promenade.",
            "host": "Church of 8 Wheels",
            "weekday": 6,  # Sunday
            "event_time": time(12, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Golden Gate Park",
            "name": "Golden Gate Park Band Concert",
            "description": "Free Sunday concert at the Spreckels Temple of Music featuring the Golden Gate Park Band.",
            "host": "Golden Gate Park Band",
            "weekday": 6,  # Sunday
            "event_time": time(13, 0),
            "created_by_email": "admin@example.com",
        },
        {
            "park_name": "Golden Gate Park",
            "name": "DSE Runners Kennedy Drive 5K",
            "description": "Dolphin South End Runners' timed 5K around the JFK Drive loop; open to visitors for a small donation.",
            "host": "Dolphin South End Runners",
            "weekday": 6,  # Sunday
            "event_time": time(9, 0),
            "created_by_email": "moderator@example.com",
        },
        {
            "park_name": "Dolores Park",
            "name": "Mission District Morning Yoga",
            "description": "Free community yoga session every Saturday morning. All levels welcome. Bring your own mat.",
            "host": "Mission Yoga Collective",
            "weekday": 5,  # Saturday
            "event_time": time(9, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Dolores Park",
            "name": "Sunset Fitness Bootcamp",
            "description": "High-intensity interval training session with bodyweight exercises. Meet at the tennis courts.",
            "host": "SF Fitness Bootcamp",
            "weekday": 3,  # Thursday
            "event_time": time(18, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Marina Green",
            "name": "Marina Green Running Club",
            "description": "Weekly group run along the waterfront with views of the Golden Gate Bridge. 3, 5, and 7 mile routes available.",
            "host": "Marina Green Running Club",
            "weekday": 0,  # Monday
            "event_time": time(7, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Marina Green",
            "name": "Outdoor Strength Training",
            "description": "Functional strength training using park equipment and bodyweight exercises. Suitable for all fitness levels.",
            "host": "Bay Area Fitness",
            "weekday": 4,  # Friday
            "event_time": time(17, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Crissy Field",
            "name": "Beach Volleyball Tournament",
            "description": "Weekly beach volleyball games. Teams welcome, or join as a free agent. All skill levels.",
            "host": "Crissy Field Volleyball",
            "weekday": 5,  # Saturday
            "event_time": time(14, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Crissy Field",
            "name": "Sunrise Meditation & Movement",
            "description": "Guided meditation followed by gentle movement and stretching. Start your day with mindfulness.",
            "host": "Golden Gate Wellness",
            "weekday": 0,  # Monday
            "event_time": time(6, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Lake Merritt",
            "name": "Lake Merritt Running Group",
            "description": "Social running group that meets every Wednesday for a 3-mile loop around the lake. All paces welcome.",
            "host": "Lake Merritt Runners",
            "weekday": 2,  # Wednesday
            "event_time": time(18, 30),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Lake Merritt",
            "name": "Outdoor Calisthenics Class",
            "description": "Bodyweight training class focusing on pull-ups, dips, and core work using the park's fitness equipment.",
            "host": "Oakland Calisthenics",
            "weekday": 1,  # Tuesday
            "event_time": time(19, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Cesar Chavez Park",
            "name": "Kite Flying & Picnic Day",
            "description": "Community gathering for kite flying enthusiasts. Bring your own kite or try one of ours. Picnic area available.",
            "host": "Berkeley Kite Club",
            "weekday": 6,  # Sunday
            "event_time": time(11, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Cesar Chavez Park",
            "name": "Waterfront Fitness Circuit",
            "description": "Full-body workout circuit using park equipment and natural features. Great for building strength and endurance.",
            "host": "Berkeley Outdoor Fitness",
            "weekday": 4,  # Friday
            "event_time": time(17, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Memorial Park",
            "name": "Tennis Clinic for Beginners",
            "description": "Free tennis instruction for beginners. Rackets provided. All ages welcome.",
            "host": "Palo Alto Tennis Association",
            "weekday": 5,  # Saturday
            "event_time": time(10, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Memorial Park",
            "name": "Evening Fitness Walk",
            "description": "Guided fitness walk through the park. Perfect for those looking for low-impact exercise.",
            "host": "Palo Alto Wellness Group",
            "weekday": 3,  # Thursday
            "event_time": time(19, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Alameda Beach",
            "name": "Beach Volleyball League",
            "description": "Competitive beach volleyball league. Registration required. Season runs through summer.",
            "host": "Alameda Beach Sports",
            "weekday": 5,  # Saturday
            "event_time": time(15, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Alameda Beach",
            "name": "Sunrise Beach Workout",
            "description": "Early morning beach workout combining running, calisthenics, and beach games. Start your weekend right!",
            "host": "Alameda Fitness Collective",
            "weekday": 6,  # Sunday
            "event_time": time(7, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Presidio of San Francisco",
            "name": "Trail Running Group",
            "description": "Explore the Presidio's extensive trail network with our weekly group run. Various distances available.",
            "host": "Presidio Trail Runners",
            "weekday": 6,  # Sunday
            "event_time": time(8, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Presidio of San Francisco",
            "name": "Outdoor Adventure Fitness",
            "description": "Combine hiking, strength training, and outdoor skills in this unique fitness adventure through the Presidio.",
            "host": "SF Adventure Fitness",
            "weekday": 5,  # Saturday
            "event_time": time(9, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Glen Park",
            "name": "Community Garden & Fitness Day",
            "description": "Join us for gardening followed by a community fitness session. Great way to connect with neighbors while staying active.",
            "host": "Glen Park Community",
            "weekday": 6,  # Sunday
            "event_time": time(10, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Glen Park",
            "name": "Evening Strength Training",
            "description": "Post-work strength training session using the park's outdoor fitness equipment. All fitness levels welcome.",
            "host": "Glen Park Fitness",
            "weekday": 2,  # Wednesday
            "event_time": time(18, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Spring Creek Forest Preserve",
            "name": "Morning Trail Run",
            "description": "Weekly trail running group through the forest preserve. Multiple distance options available.",
            "host": "Garland Trail Runners",
            "weekday": 6,  # Sunday
            "event_time": time(7, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Spring Creek Forest Preserve",
            "name": "Outdoor Fitness Bootcamp",
            "description": "High-intensity workout using natural features and park equipment. All fitness levels welcome.",
            "host": "Garland Fitness Bootcamp",
            "weekday": 3,  # Thursday
            "event_time": time(18, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Audubon Park",
            "name": "Community Walk & Talk",
            "description": "Social walking group that meets every Tuesday. Great for fitness and meeting neighbors.",
            "host": "Garland Community Walkers",
            "weekday": 1,  # Tuesday
            "event_time": time(19, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Audubon Park",
            "name": "Basketball Pickup Games",
            "description": "Weekly pickup basketball games. All skill levels welcome. Bring your own ball if possible.",
            "host": "Garland Basketball League",
            "weekday": 5,  # Saturday
            "event_time": time(9, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Central Park",
            "name": "Saturday Morning Yoga",
            "description": "Free community yoga session in the park. Bring your own mat. All levels welcome.",
            "host": "Garland Yoga Collective",
            "weekday": 5,  # Saturday
            "event_time": time(8, 30),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Central Park",
            "name": "Evening Calisthenics",
            "description": "Bodyweight training session focusing on pull-ups, push-ups, and core work using park equipment.",
            "host": "Garland Calisthenics Club",
            "weekday": 2,  # Wednesday
            "event_time": time(18, 0),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Tuckerville Park",
            "name": "Family Fitness Day",
            "description": "Family-friendly fitness activities for all ages. Includes games, exercises, and fun challenges.",
            "host": "Garland Family Fitness",
            "weekday": 6,  # Sunday
            "event_time": time(10, 0),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Tuckerville Park",
            "name": "Tennis Social",
            "description": "Casual tennis games and socializing. All skill levels welcome. Rackets available for loan.",
            "host": "Garland Tennis Club",
            "weekday": 4,  # Friday
            "event_time": time(17, 30),
            "created_by_email": "testuser2@example.com",
        },
        {
            "park_name": "Waterview Park",
            "name": "Lakeside Running Group",
            "description": "Scenic running group around the lake. 2, 3, and 5 mile routes available. All paces welcome.",
            "host": "Garland Running Club",
            "weekday": 0,  # Monday
            "event_time": time(6, 30),
            "created_by_email": "testuser1@example.com",
        },
        {
            "park_name": "Waterview Park",
            "name": "Sunset Strength Training",
            "description": "Evening strength training with beautiful lake views. Using park equipment and bodyweight exercises.",
            "host": "Waterview Fitness",
            "weekday": 4,  # Friday
            "event_time": time(19, 0),
            "created_by_email": "testuser2@example.com",
        },
    ]

    for event in events_data:
        park = park_lookup.get(event["park_name"])
        if not park:
            print(f"Park {event['park_name']} not found, skipping event {event['name']}.")
            continue

        created_by_user = users.get(event["created_by_email"])
        if not created_by_user:
            print(f"User {event['created_by_email']} not found, skipping event {event['name']}.")
            continue

        event_data = {
            "park_id": park.id,
            "name": event["name"],
            "description": event["description"],
            "host": event["host"],
            "event_date": next_weekday(today, event["weekday"]),
            "event_time": event["event_time"],
            "created_by": created_by_user.id,
        }

        existing = db.query(Event).filter(
            Event.name == event_data["name"],
            Event.park_id == event_data["park_id"]
        ).first()

        if not existing:
            db.add(Event(**event_data))
            print(f"Created event: {event_data['name']} at park {park.name}")


def main():
    """Main seeding function."""
    print("Starting test data seeding...")
    
    db: Session = SessionLocal()
    try:
        # Seed in order (respecting foreign key constraints)
        users = seed_users(db)
        parks = seed_parks(db, users)
        seed_park_equipment(db, parks)
        seed_reviews(db, parks, users)
        seed_images(db, parks, users)
        seed_events(db, parks, users)
        
        # Commit all changes
        db.commit()
        print("\n✅ Test data seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding test data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
