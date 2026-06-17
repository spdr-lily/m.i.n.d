"""add user_uuid to healthcare_professionals

Revision ID: 031c8a8ec7b8
Revises: f7b8c9d0e1f2
Create Date: 2026-06-15 12:25:53.171481
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '031c8a8ec7b8'
down_revision: Union[str, None] = 'f7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'healthcare_professionals',
        sa.Column('user_uuid', UUID(), nullable=True),
        schema='clinical',
    )
    op.create_foreign_key(
        'fk_healthcare_professionals_user_uuid',
        'healthcare_professionals', 'users',
        ['user_uuid'], ['user_uuid'],
        source_schema='clinical', referent_schema='security',
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_healthcare_professionals_user_uuid',
        'healthcare_professionals',
        schema='clinical',
        type_='foreignkey',
    )
    op.drop_column('healthcare_professionals', 'user_uuid', schema='clinical')
