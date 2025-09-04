"""add type and image to events

Revision ID: 4bc1b1ee73fb
Revises: 9e52e554b401
Create Date: 2025-09-04 09:09:39.813806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bc1b1ee73fb'
down_revision: Union[str, Sequence[str], None] = '9e52e554b401'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("events", sa.Column("type", sa.String(), nullable=True))
    op.add_column("events", sa.Column("image", sa.String(), nullable=True))
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("events", "type")
    op.drop_column("events", "image")
