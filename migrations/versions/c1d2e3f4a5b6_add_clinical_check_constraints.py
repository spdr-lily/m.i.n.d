"""add clinical CHECK constraints

Revision ID: c1d2e3f4a5b6
Revises: 41991f22ee27
Create Date: 2026-06-07 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op


revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "41991f22ee27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # patient_profile: birth_date must be past or today
    op.create_check_constraint(
        "ck_patient_profile_birth_date",
        "patient_profile",
        schema="clinical",
        condition="birth_date IS NULL OR birth_date <= CURRENT_DATE",
    )

    # symptom_observation: intensity range 0-10
    op.create_check_constraint(
        "ck_symptom_observation_intensity",
        "symptom_observation",
        schema="clinical",
        condition="intensity IS NULL OR (intensity >= 0 AND intensity <= 10)",
    )

    # symptom_observation: duration_days >= 1
    op.create_check_constraint(
        "ck_symptom_observation_duration_days",
        "symptom_observation",
        schema="clinical",
        condition="duration_days IS NULL OR duration_days >= 1",
    )

    # symptom_observation: frequency must be a known value
    op.create_check_constraint(
        "ck_symptom_observation_frequency",
        "symptom_observation",
        schema="clinical",
        condition=(
            "frequency IS NULL OR frequency IN ("
            "'daily', 'several_times_week', 'weekly', 'several_times_month', "
            "'monthly', 'rarely', 'continuous'"
            ")"
        ),
    )

    # scale_responses: response_value 0-10
    op.create_check_constraint(
        "ck_scale_responses_value",
        "scale_responses",
        schema="clinical",
        condition="response_value IS NULL OR (response_value >= 0 AND response_value <= 10)",
    )

    # diagnostic_inference: probability 0-1
    op.create_check_constraint(
        "ck_inference_probability",
        "diagnostic_inference",
        schema="diagnostic",
        condition="inference_probability IS NULL OR (inference_probability >= 0 AND inference_probability <= 1)",
    )

    # diagnostic_inference: confidence 0-1
    op.create_check_constraint(
        "ck_inference_confidence",
        "diagnostic_inference",
        schema="diagnostic",
        condition="confidence_level IS NULL OR (confidence_level >= 0 AND confidence_level <= 1)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_patient_profile_birth_date", "patient_profile", schema="clinical")
    op.drop_constraint("ck_symptom_observation_intensity", "symptom_observation", schema="clinical")
    op.drop_constraint("ck_symptom_observation_duration_days", "symptom_observation", schema="clinical")
    op.drop_constraint("ck_symptom_observation_frequency", "symptom_observation", schema="clinical")
    op.drop_constraint("ck_scale_responses_value", "scale_responses", schema="clinical")
    op.drop_constraint("ck_inference_probability", "diagnostic_inference", schema="diagnostic")
    op.drop_constraint("ck_inference_confidence", "diagnostic_inference", schema="diagnostic")
