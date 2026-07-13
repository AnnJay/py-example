"""add new column for posts

Revision ID: eedadf9583d5
Revises: 00e0b40b20c8
Create Date: 2026-07-10 17:43:15.963259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eedadf9583d5'
down_revision: Union[str, Sequence[str], None] = '00e0b40b20c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
