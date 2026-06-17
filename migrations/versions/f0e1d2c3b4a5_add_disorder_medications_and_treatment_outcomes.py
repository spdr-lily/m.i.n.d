"""add disorder_medications and treatment_outcomes tables

Revision ID: f0e1d2c3b4a5
Revises: e2f3a4b5c6d7
Create Date: 2026-06-16 21:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "f0e1d2c3b4a5"
down_revision: Union[str, None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # disorder_medications table
    op.create_table(
        "disorder_medications",
        sa.Column("dm_id", sa.Integer(), primary_key=True),
        sa.Column("medication_id", sa.Integer(), sa.ForeignKey("clinical.medications.medication_id"), nullable=False),
        sa.Column("disorder_id", sa.Integer(), sa.ForeignKey("diagnostic.disorders.disorder_id"), nullable=False),
        sa.Column("success_rate", sa.Numeric(5, 4)),
        sa.Column("failure_rate", sa.Numeric(5, 4)),
        sa.Column("avg_response_weeks", sa.Numeric(5, 2)),
        sa.Column("line_of_treatment", sa.Integer()),
        sa.Column("recommendation_strength", sa.String(5)),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        schema="clinical",
    )
    op.create_index("ix_disorder_medications_medication", "disorder_medications", ["medication_id"], schema="clinical")
    op.create_index("ix_disorder_medications_disorder", "disorder_medications", ["disorder_id"], schema="clinical")
    op.create_index("ix_disorder_medications_unique", "disorder_medications", ["medication_id", "disorder_id"], unique=True, schema="clinical")

    # treatment_outcomes table
    op.create_table(
        "treatment_outcomes",
        sa.Column("outcome_uuid", UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("patient_uuid", UUID(as_uuid=True), sa.ForeignKey("clinical.patient_profile.profile_uuid"), nullable=False),
        sa.Column("medication_id", sa.Integer(), sa.ForeignKey("clinical.medications.medication_id"), nullable=False),
        sa.Column("disorder_id", sa.Integer(), sa.ForeignKey("diagnostic.disorders.disorder_id"), nullable=False),
        sa.Column("prescription_item_uuid", UUID(as_uuid=True), sa.ForeignKey("clinical.prescription_items.item_uuid"), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("outcome", sa.String(30), nullable=False),
        sa.Column("response_weeks", sa.Numeric(5, 2)),
        sa.Column("side_effects", sa.Text()),
        sa.Column("discontinued_reason", sa.Text()),
        sa.Column("adherence", sa.String(20)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        schema="clinical",
    )
    op.create_index("ix_treatment_outcomes_patient", "treatment_outcomes", ["patient_uuid"], schema="clinical")
    op.create_index("ix_treatment_outcomes_medication", "treatment_outcomes", ["medication_id"], schema="clinical")
    op.create_index("ix_treatment_outcomes_disorder", "treatment_outcomes", ["disorder_id"], schema="clinical")


def downgrade() -> None:
    op.drop_table("treatment_outcomes", schema="clinical")
    op.drop_table("disorder_medications", schema="clinical")
