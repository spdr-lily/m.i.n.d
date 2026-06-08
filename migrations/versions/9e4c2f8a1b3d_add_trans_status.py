"""add trans_status column to patient_profile

Revision ID: 9e4c2f8a1b3d
Revises: 005f85846e88
Create Date: 2026-06-03 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '9e4c2f8a1b3d'
down_revision: Union[str, None] = '005f85846e88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('patient_profile', sa.Column('trans_status', sa.String(30), nullable=True), schema='clinical')


def downgrade() -> None:
    op.drop_column('patient_profile', 'trans_status', schema='clinical')
