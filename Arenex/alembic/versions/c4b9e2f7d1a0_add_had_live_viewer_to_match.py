"""add had_live_viewer to match

Revision ID: c4b9e2f7d1a0
Revises: 823bfa2f6ce1
Create Date: 2026-04-13 16:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4b9e2f7d1a0'
down_revision: Union[str, Sequence[str], None] = '823bfa2f6ce1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'matches',
        sa.Column('had_live_viewer', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('matches', 'had_live_viewer')
