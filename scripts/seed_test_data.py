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
            "name": "Daniel",
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
            "name": "Barras Paralelas",
            "description": "Street workout park with Calisthenics equipment",
            "latitude": Decimal("19.42407612367549"),
            "longitude": Decimal("-99.16170713832499"),
            "address": "Calle niza y av.chapultepec 276, Av Chapultepec 282, Centro Urbano Pdte. Juárez, Roma Nte., Cuauhtémoc, Mexico City, CDMX, Mexico, 06700",
            "status": "approved",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": None,
        },
        {
            "name": "Marina Park",
            "description": "Community park in Rowlett with outdoor fitness equipment and recreational facilities",
            "latitude": Decimal("37.69171309582851"),
            "longitude": Decimal("-122.18448585621984"), 
            "address": "14001 Monarch Bay Drive, San Leandro, CA, USA, 94577",
            "status": "pending",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": None,
        },
        {
            "name": "Southgate Park",
            "description": "Blue turf workout station with calisthenics equipment.",
            "latitude": Decimal("37.63500657572622"),
            "longitude": Decimal("-122.09546165890184"),
            "address": "26874 Contessa Street, Hayward, CA, USA, 94545",
            "status": "pending",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": None,
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
    # Get all equipment by name for reliable lookup
    equipment_map = {}
    all_equipment = db.query(Equipment).all()
    if not all_equipment:
        print("No equipment found. Make sure migrations have run.")
        return
    
    for eq in all_equipment:
        equipment_map[eq.name] = eq
    
    # Define equipment associations by park name and equipment name
    # This is more reliable than using indices
    associations = [
        # Barras Paralelas - Calisthenics park, should have parallel bars, pull-up bars, etc.
        (parks[0].name, ["Parallel Bars", "Pull-up Bar", "Push-up Bars", "Gymnastics Rings"]),
        # Marina Park - Community park with outdoor fitness equipment
        (parks[1].name, ["Pull-up Bar", "Ab Station", "Monkey Bars", "Running Track"]),
        # Southgate Park - Blue turf workout station with calisthenics equipment
        (parks[2].name, ["Parallel Bars", "Pull-up Bar", "Push-up Bars"]),
    ]
    
    # Create a lookup map for parks
    park_map = {park.name: park for park in parks}
    
    for park_name, equipment_names in associations:
        park = park_map.get(park_name)
        if not park:
            print(f"Warning: Park '{park_name}' not found, skipping equipment associations")
            continue
        
        for equipment_name in equipment_names:
            equipment = equipment_map.get(equipment_name)
            if not equipment:
                print(f"Warning: Equipment '{equipment_name}' not found, skipping")
                continue
            
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
            "image_url": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=1200&h=800&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=300&h=300&fit=crop",
            "alt_text": "Pecan Grove Park with outdoor fitness equipment",
            "is_approved": True,
            "is_primary": True,
        },
        {
            "park_id": parks[0].id,
            "uploaded_by": users["testuser2@example.com"].id,
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&h=800&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop",
            "alt_text": "Pecan Grove Park recreational area",
            "is_approved": True,
            "is_primary": False,
        },
        {
            "park_id": parks[1].id,
            "uploaded_by": users["testuser1@example.com"].id,
            "image_url": "https://images.unsplash.com/photo-1519336056116-9e0c57349a24?w=1200&h=800&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1519336056116-9e0c57349a24?w=300&h=300&fit=crop",
            "alt_text": "Springfield Park community space",
            "is_approved": True,
            "is_primary": True,
        },
        {
            "park_id": parks[2].id,
            "uploaded_by": users["testuser1@example.com"].id,
            "image_url": "https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=1200&h=800&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=300&h=300&fit=crop",
            "alt_text": "Barras Insurgentes street workout park with calisthenics equipment",
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
