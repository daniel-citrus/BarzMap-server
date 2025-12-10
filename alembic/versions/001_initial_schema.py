"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create extension
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    
    # Create set_updated_at function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at := NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # 1. Users Table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('auth0_id', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('profile_picture_url', sa.Text(), nullable=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='user'),
        sa.Column('join_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("role IN ('user', 'moderator', 'admin')", name='check_role')
    )
    op.create_index('idx_users_role', 'users', ['role'])
    
    # 2. Parks Table
    op.create_table(
        'parks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=False),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(255), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submit_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name='check_status'),
        sa.CheckConstraint("latitude >= -90 AND latitude <= 90", name='parks_latitude_range'),
        sa.CheckConstraint("longitude >= -180 AND longitude <= 180", name='parks_longitude_range'),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_parks_status', 'parks', ['status'])
    op.create_index('idx_parks_location', 'parks', ['latitude', 'longitude'])
    op.create_index('idx_parks_submitted_by', 'parks', ['submitted_by'])
    op.create_index('idx_parks_approved_by', 'parks', ['approved_by'])
    
    # 3. Equipment Table
    op.create_table(
        'equipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'))
    )
    
    # 4. Park_Equipment Table (Junction Table)
    op.create_table(
        'park_equipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('park_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['park_id'], ['parks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('park_id', 'equipment_id', name='uq_park_equipment')
    )
    op.create_index('idx_park_equipment_park_id', 'park_equipment', ['park_id'])
    
    # 5. Images Table
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('park_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('alt_text', sa.String(255), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_inappropriate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('upload_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['park_id'], ['parks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_images_park_id', 'images', ['park_id'])
    op.create_index('idx_images_approved', 'images', ['is_approved'])
    op.create_index('idx_images_uploaded_by', 'images', ['uploaded_by'])
    op.create_index('uq_primary_image_per_park', 'images', ['park_id'], unique=True, postgresql_where=sa.text('is_primary = true'))
    
    # 6. Reviews Table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('park_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name='check_rating'),
        sa.ForeignKeyConstraint(['park_id'], ['parks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('park_id', 'user_id', name='uq_park_user_review')
    )
    op.create_index('idx_reviews_park_id', 'reviews', ['park_id'])
    op.create_index('idx_reviews_user_id', 'reviews', ['user_id'])
    
    # Create triggers for updated_at
    op.execute("""
        CREATE TRIGGER set_updated_at_users
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)
    
    op.execute("""
        CREATE TRIGGER set_updated_at_parks
        BEFORE UPDATE ON parks
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)
    
    op.execute("""
        CREATE TRIGGER set_updated_at_reviews
        BEFORE UPDATE ON reviews
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)
    
    # Insert sample equipment data
    op.execute("""
        INSERT INTO equipment (id, name, description, icon_name) VALUES
            (gen_random_uuid(), 'Pull-up Bar', 'Horizontal bar for pull-ups and chin-ups', 'pull-up-bar'),
            (gen_random_uuid(), 'Gymnastics Rings', 'Suspension rings for advanced bodyweight training', 'gymnastics-rings'),
            (gen_random_uuid(), 'Push-up Bars', 'Elevated handles for push-ups and planks', 'push-up-bars'),
            (gen_random_uuid(), 'Ab Station', 'Station for abdominal and core exercises', 'ab-station'),
            (gen_random_uuid(), 'Parallel Bars', 'Parallel bars for dips, L-sits, and handstands', 'parallel-bars'),
            (gen_random_uuid(), 'Monkey Bars', 'Overhead bars for traversing and pull-ups', 'monkey-bars'),
            (gen_random_uuid(), 'Running Track', 'Designated path for running and jogging', 'running-track');
    """)


def downgrade() -> None:
    """Drop all tables and functions."""
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_reviews ON reviews")
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_parks ON parks")
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_users ON users")
    
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('reviews')
    op.drop_table('images')
    op.drop_table('park_equipment')
    op.drop_table('equipment')
    op.drop_table('parks')
    op.drop_table('users')
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS set_updated_at() CASCADE")
    
    # Drop extension (optional - might be used by other things)
    # op.execute("DROP EXTENSION IF EXISTS pgcrypto")

