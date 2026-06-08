"""add_clinical_alerts_table

Revision ID: 1c223a553bb0
Revises: e5f6a7b8c9d0
Create Date: 2026-06-08 07:01:54.073036
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '1c223a553bb0'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('clinical_alerts',
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('profile_uuid', UUID(as_uuid=True), nullable=True),
        sa.Column('consultation_uuid', UUID(as_uuid=True), nullable=True),
        sa.Column('scale_name', sa.String(length=255), nullable=True),
        sa.Column('actual_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('threshold_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('intensity', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('disorder_name', sa.String(length=255), nullable=True),
        sa.Column('probability', sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column('resolved', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['consultation_uuid'], ['clinical.clinical_consultation.consultation_uuid'], ),
        sa.ForeignKeyConstraint(['profile_uuid'], ['clinical.patient_profile.profile_uuid'], ),
        sa.PrimaryKeyConstraint('alert_id'),
        schema='clinical'
    )


def downgrade() -> None:
    op.drop_table('clinical_alerts', schema='clinical')
