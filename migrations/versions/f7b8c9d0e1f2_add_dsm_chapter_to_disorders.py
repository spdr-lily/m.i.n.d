"""add dsm_chapter column to disorders

Revision ID: f7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-06-15 11:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('disorders', sa.Column('dsm_chapter', sa.String(100)), schema='diagnostic')


def downgrade() -> None:
    op.drop_column('disorders', 'dsm_chapter', schema='diagnostic')
