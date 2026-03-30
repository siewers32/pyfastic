"""datetime types aangepast

Revision ID: fb4d005a94f8
Revises: b3032cba2cfc
Create Date: 2026-03-27 15:53:19.381386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = 'fb4d005a94f8'
down_revision: Union[str, Sequence[str], None] = 'b3032cba2cfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
