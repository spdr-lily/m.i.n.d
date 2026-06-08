"""add_medical_reports

Revision ID: 2c8a1e3fae51
Revises: 7a1b3c5d8e9f
Create Date: 2026-06-03 12:18:05.528074
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '2c8a1e3fae51'
down_revision: Union[str, None] = '7a1b3c5d8e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('medical_reports',
        sa.Column('report_uuid', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('patient_uuid', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('report_type', sa.String(50), server_default='summary', nullable=False),
        sa.Column('is_pinned', sa.Boolean(), server_default='false'),
        sa.Column('created_by', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['patient_uuid'], ['security.patient_identity.patient_uuid']),
        sa.PrimaryKeyConstraint('report_uuid'),
        schema='clinical'
    )


def downgrade() -> None:
    op.drop_table('medical_reports', schema='clinical')
