"""add practice social columns

Revision ID: a1b2c3d4e5f6
Revises: 9adf5813bad0
Create Date: 2026-04-12 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9adf5813bad0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add practice mode columns to matches
    op.add_column('matches', sa.Column('is_practice', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('matches', sa.Column('difficulty', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('game_type', sa.String(), nullable=True, server_default='chess'))

    # Create comments table
    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), sa.ForeignKey('matches.id'), nullable=True),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)

    # Create match_likes table
    op.create_table('match_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), sa.ForeignKey('matches.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_likes_id'), 'match_likes', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_match_likes_id'), table_name='match_likes')
    op.drop_table('match_likes')
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_column('matches', 'game_type')
    op.drop_column('matches', 'difficulty')
    op.drop_column('matches', 'is_practice')
