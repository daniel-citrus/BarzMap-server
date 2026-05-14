"""Drop users.roles if present (roles live in Auth0 only).

Revision ID: 005_drop_users_roles
Revises: 004_slim_users
Create Date: 2026-05-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_drop_users_roles"
down_revision: Union[str, None] = "004_slim_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS roles")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("roles", sa.String(), nullable=True),
    )
