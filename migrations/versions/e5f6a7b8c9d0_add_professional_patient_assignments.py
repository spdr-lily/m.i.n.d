"""add professional_patient_assignments table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-07 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "professional_patient_assignments",
        sa.Column("assignment_id", sa.Integer(), nullable=False),
        sa.Column("professional_uuid", UUID(as_uuid=True), nullable=False),
        sa.Column("patient_uuid", UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.ForeignKeyConstraint(
            ["professional_uuid"],
            ["clinical.healthcare_professionals.professional_uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["patient_uuid"],
            ["security.patient_identity.patient_uuid"],
        ),
        sa.PrimaryKeyConstraint("assignment_id"),
        sa.UniqueConstraint("professional_uuid", "patient_uuid", name="uq_prof_patient"),
        schema="clinical",
    )


def downgrade() -> None:
    op.drop_table("professional_patient_assignments", schema="clinical")
