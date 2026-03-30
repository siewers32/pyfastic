"""datetime types aangepast

Revision ID: 5b6554974424
Revises: fb4d005a94f8
Create Date: 2026-03-27 15:53:50.114227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '5b6554974424'
down_revision: Union[str, Sequence[str], None] = 'fb4d005a94f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
