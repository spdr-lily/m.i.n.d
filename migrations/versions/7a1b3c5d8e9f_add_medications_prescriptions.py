"""add medications and prescriptions tables

Revision ID: 7a1b3c5d8e9f
Revises: 9e4c2f8a1b3d
Create Date: 2026-06-03 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '7a1b3c5d8e9f'
down_revision: Union[str, None] = '9e4c2f8a1b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('medications',
        sa.Column('medication_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('active_ingredient', sa.String(255), nullable=True),
        sa.Column('classification', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('medication_id'),
        schema='clinical'
    )

    op.create_table('prescriptions',
        sa.Column('prescription_uuid', UUID(as_uuid=True), nullable=False),
        sa.Column('consultation_uuid', UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['consultation_uuid'], ['clinical.clinical_consultation.consultation_uuid'], ),
        sa.PrimaryKeyConstraint('prescription_uuid'),
        schema='clinical'
    )

    op.create_table('prescription_items',
        sa.Column('item_uuid', UUID(as_uuid=True), nullable=False),
        sa.Column('prescription_uuid', UUID(as_uuid=True), nullable=False),
        sa.Column('medication_id', sa.Integer(), nullable=False),
        sa.Column('dosage', sa.String(100), nullable=False),
        sa.Column('frequency', sa.String(100), nullable=False),
        sa.Column('route', sa.String(50), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['prescription_uuid'], ['clinical.prescriptions.prescription_uuid'], ),
        sa.ForeignKeyConstraint(['medication_id'], ['clinical.medications.medication_id'], ),
        sa.PrimaryKeyConstraint('item_uuid'),
        schema='clinical'
    )


def downgrade() -> None:
    op.drop_table('prescription_items', schema='clinical')
    op.drop_table('prescriptions', schema='clinical')
    op.drop_table('medications', schema='clinical')
