"""add profession and start_date to healthcare_professionals

Revision ID: a29a8fdd7159
Revises: 2c8a1e3fae51
Create Date: 2026-06-03 13:44:27.443151
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a29a8fdd7159'
down_revision: Union[str, None] = '2c8a1e3fae51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('healthcare_professionals', sa.Column('profession', sa.String(length=100), nullable=True), schema='clinical')
    op.add_column('healthcare_professionals', sa.Column('start_date', sa.Date(), nullable=True), schema='clinical')


def downgrade() -> None:
    op.drop_column('healthcare_professionals', 'start_date', schema='clinical')
    op.drop_column('healthcare_professionals', 'profession', schema='clinical')
