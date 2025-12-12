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
            "name": "Central Park",
            "description": "A large public park in Manhattan, New York City",
            "latitude": Decimal("40.785091"),
            "longitude": Decimal("-73.968285"),
            "address": "Central Park, New York, NY",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10024",
            "status": "approved",
            "submitted_by": users["testuser1@example.com"].id,
            "approved_by": users["admin@example.com"].id,
        },
        {
            "name": "Golden Gate Park",
            "description": "A large urban park in San Francisco",
            "latitude": Decimal("37.7694"),
            "longitude": Decimal("-122.4862"),
            "address": "Golden Gate Park, San Francisco, CA",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94117",
            "status": "approved",
            "submitted_by": users["testuser2@example.com"].id,
            "approved_by": users["admin@example.com"].id,
        },
        {
            "name": "Lincoln Park",
            "description": "A park in Chicago with lakefront views",
            "latitude": Decimal("41.9256"),
            "longitude": Decimal("-87.6368"),
            "address": "Lincoln Park, Chicago, IL",
            "city": "Chicago",
            "state": "IL",
            "country": "USA",
            "postal_code": "60614",
            "status": "pending",
            "submitted_by": users["testuser1@example.com"].id,
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
        (parks[0], [all_equipment[0], all_equipment[1], all_equipment[2]]),  # Central Park
        (parks[1], [all_equipment[2], all_equipment[3], all_equipment[4]]),  # Golden Gate Park
        (parks[2], [all_equipment[0], all_equipment[5]]),  # Lincoln Park
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
    """Seed Bay Area events pulled from real recurring gatherings."""
    today = date.today()
    park_lookup = {park.name: park for park in parks}

    def next_weekday(start: date, weekday: int) -> date:
        """Return the next occurrence of the requested weekday (0=Monday)."""
        days_ahead = (weekday - start.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return start + timedelta(days=days_ahead)

    bay_area_events = [
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
    ]

    for event in bay_area_events:
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
