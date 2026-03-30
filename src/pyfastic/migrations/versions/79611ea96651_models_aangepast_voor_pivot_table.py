"""models aangepast voor pivot table

Revision ID: 79611ea96651
Revises: 53460a4577b1
Create Date: 2026-03-28 14:28:51.824021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '79611ea96651'
down_revision: Union[str, Sequence[str], None] = '53460a4577b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
