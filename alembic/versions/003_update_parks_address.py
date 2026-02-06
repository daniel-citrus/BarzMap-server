"""Update parks address columns

Revision ID: 003_update_parks_address
Revises: 002_add_events
Create Date: 2025-01-27

This migration:
- Replaces address, city, state, country, and postal_code columns with a single address column
- Migrates existing data by concatenating old address fields into the new address column
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_update_parks_address'
down_revision: Union[str, None] = '002_add_events'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace old address columns with a single address column."""
    # Step 1: Rename the old address column to address_old temporarily
    op.alter_column('parks', 'address', new_column_name='address_old')
    
    # Step 2: Add the new address column
    op.add_column('parks', sa.Column('address', sa.Text(), nullable=True))
    
    # Step 3: Migrate existing data by concatenating old address fields
    # This creates a formatted address string from the existing columns
    op.execute("""
        UPDATE parks
        SET address = TRIM(
            CONCAT_WS(', ',
                NULLIF(address_old, ''),
                NULLIF(city, ''),
                NULLIF(state, ''),
                NULLIF(country, ''),
                NULLIF(postal_code, '')
            )
        )
        WHERE address IS NULL;
    """)
    
    # Step 4: Remove the old address columns
    op.drop_column('parks', 'address_old')
    op.drop_column('parks', 'postal_code')
    op.drop_column('parks', 'country')
    op.drop_column('parks', 'state')
    op.drop_column('parks', 'city')


def downgrade() -> None:
    """Restore old address columns."""
    # Step 1: Add back the old address columns
    op.add_column('parks', sa.Column('city', sa.String(255), nullable=True))
    op.add_column('parks', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('parks', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('parks', sa.Column('postal_code', sa.String(20), nullable=True))
    
    # Step 2: Note: We can't perfectly restore the split address fields from address
    # This is a limitation of the downgrade - the old separate fields will be NULL
    # In practice, you might want to set a default or leave them NULL

