"""Add events table

Revision ID: 002_add_events
Revises: 001_initial
Create Date: 2025-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_events'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add events table."""
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('park_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('host', sa.String(255), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=True),
        sa.Column('event_time', sa.Time(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['park_id'], ['parks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_events_park_id', 'events', ['park_id'])
    op.create_index('idx_events_date', 'events', ['event_date'])
    
    # Create trigger for updated_at
    op.execute("""
        CREATE TRIGGER set_updated_at_events
        BEFORE UPDATE ON events
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    """Remove events table."""
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_events ON events")
    op.drop_table('events')
