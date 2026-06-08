"""add clinical_notes table (no-op — already exists)

Revision ID: b3c4d5e6f7a8
Revises: a29a8fdd7159
Create Date: 2026-06-03 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import inspect


revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'a29a8fdd7159'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if 'clinical_notes' not in inspector.get_table_names(schema='clinical'):
        op.create_table('clinical_notes',
            sa.Column('note_uuid', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('consultation_uuid', UUID(as_uuid=True), nullable=False),
            sa.Column('chief_complaint', sa.Text(), nullable=True),
            sa.Column('history_present_illness', sa.Text(), nullable=True),
            sa.Column('subjective_findings', sa.Text(), nullable=True),
            sa.Column('objective_findings', sa.Text(), nullable=True),
            sa.Column('clinical_assessment', sa.Text(), nullable=True),
            sa.Column('treatment_plan', sa.Text(), nullable=True),
            sa.Column('follow_up', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['consultation_uuid'], ['clinical.clinical_consultation.consultation_uuid'], ),
            sa.PrimaryKeyConstraint('note_uuid'),
            sa.UniqueConstraint('consultation_uuid'),
            schema='clinical'
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if 'clinical_notes' in inspector.get_table_names(schema='clinical'):
        op.drop_table('clinical_notes', schema='clinical')
