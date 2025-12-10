"""
Database package for BarzMap.
"""
from .connection import (
    engine,
    superuser_engine,
    SessionLocal,
    SuperuserSessionLocal,
    Base,
    get_db,
    get_superuser_db
)
from .UsersRouter import (
    create_user,
    get_user,
    get_user_by_email,
    get_user_by_auth0_id,
    get_all_users,
    update_user,
    delete_user,
)
from .ParksRouter import (
    create_park,
    get_park,
    get_all_parks,
    get_parks_by_status,
    get_parks_by_location,
    update_park,
    delete_park,
)
from .EquipmentRouter import (
    create_equipment,
    get_equipment,
    get_equipment_by_name,
    get_all_equipment,
    update_equipment,
    delete_equipment,
)
from .ImagesRouter import (
    create_image,
    get_image,
    get_images_by_park,
    get_primary_image,
    update_image,
    delete_image,
)
from .ReviewsRouter import (
    create_review,
    get_review,
    get_review_by_park_and_user,
    get_reviews_by_park,
    get_reviews_by_user,
    update_review,
    delete_review,
)
from .ParkEquipmentRouter import (
    add_equipment_to_park,
    remove_equipment_from_park,
    get_park_equipment,
    get_equipment_by_park,
    get_parks_by_equipment,
    remove_all_equipment_from_park,
)

__all__ = [
    # Connection
    "engine",
    "superuser_engine",
    "SessionLocal",
    "SuperuserSessionLocal",
    "Base",
    "get_db",
    "get_superuser_db",
    # Users
    "create_user",
    "get_user",
    "get_user_by_email",
    "get_user_by_auth0_id",
    "get_all_users",
    "update_user",
    "delete_user",
    # Parks
    "create_park",
    "get_park",
    "get_all_parks",
    "get_parks_by_status",
    "get_parks_by_location",
    "update_park",
    "delete_park",
    # Equipment
    "create_equipment",
    "get_equipment",
    "get_equipment_by_name",
    "get_all_equipment",
    "update_equipment",
    "delete_equipment",
    # Images
    "create_image",
    "get_image",
    "get_images_by_park",
    "get_primary_image",
    "update_image",
    "delete_image",
    # Reviews
    "create_review",
    "get_review",
    "get_review_by_park_and_user",
    "get_reviews_by_park",
    "get_reviews_by_user",
    "update_review",
    "delete_review",
    # Park Equipment
    "add_equipment_to_park",
    "remove_equipment_from_park",
    "get_park_equipment",
    "get_equipment_by_park",
    "get_parks_by_equipment",
    "remove_all_equipment_from_park",
]

