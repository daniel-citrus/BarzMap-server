"""
Purge all test data from the database.

This script deletes all data from test tables while preserving the schema.
Useful for resetting the test database before re-seeding.

Usage:
    python scripts/purge_test_data.py
    # Or in docker:
    docker compose -f docker-compose.test.yml exec api-test python scripts/purge_test_data.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from services.Database.PostgresConnection import SessionLocal
from models.database import User, Park, Equipment, ParkEquipment, Image, Review, Event


def purge_test_data():
    """Delete all test data from the database."""
    print("Starting test data purge...")
    
    db: Session = SessionLocal()
    try:
        # Delete in reverse order of foreign key dependencies
        # Events first (references parks and users)
        events_deleted = db.query(Event).delete()
        print(f"Deleted {events_deleted} events")
        
        # Reviews (references parks and users)
        reviews_deleted = db.query(Review).delete()
        print(f"Deleted {reviews_deleted} reviews")
        
        # Images (references parks and users)
        images_deleted = db.query(Image).delete()
        print(f"Deleted {images_deleted} images")
        
        # Park Equipment (references parks and equipment)
        park_equipment_deleted = db.query(ParkEquipment).delete()
        print(f"Deleted {park_equipment_deleted} park equipment associations")
        
        # Parks (references users)
        parks_deleted = db.query(Park).delete()
        print(f"Deleted {parks_deleted} parks")
        
        # Note: Equipment is NOT deleted - it's reference data seeded by migrations
        # and should persist across test runs
        
        # Users last (referenced by many tables)
        users_deleted = db.query(User).delete()
        print(f"Deleted {users_deleted} users")
        
        # Commit all deletions
        db.commit()
        print("\n✅ Test data purge completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error purging test data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    purge_test_data()
