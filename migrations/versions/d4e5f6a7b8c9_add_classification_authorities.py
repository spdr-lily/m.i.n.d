"""add classification authorities + DSM criteria fields

Revision ID: d4e5f6a7b8c9
Revises: c1d2e3f4a5b6
Create Date: 2026-06-07 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # ClassificationAuthority
    if not inspector.has_table("classification_authorities", schema="diagnostic"):
        op.create_table(
            "classification_authorities",
            sa.Column("authority_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("short_name", sa.String(20), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("website_url", sa.String(500)),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("authority_id"),
            sa.UniqueConstraint("short_name"),
            schema="diagnostic",
        )

    # icd11_codes table (missing from initial migration)
    if not inspector.has_table("icd11_codes", schema="diagnostic"):
        op.create_table(
            "icd11_codes",
            sa.Column("code_id", sa.Integer(), nullable=False),
            sa.Column("disorder_id", sa.Integer(), nullable=False),
            sa.Column("authority_id", sa.Integer()),
            sa.Column("icd11_code", sa.String(20), nullable=False),
            sa.Column("icd11_title", sa.String(500)),
            sa.Column("chapter", sa.String(100)),
            sa.Column("chapter_code", sa.String(20)),
            sa.Column("who_url", sa.String(500)),
            sa.Column("clinical_description", sa.Text()),
            sa.Column("diagnostic_requirements", sa.Text()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(
                ["disorder_id"], ["diagnostic.disorders.disorder_id"],
            ),
            sa.PrimaryKeyConstraint("code_id"),
            sa.UniqueConstraint("icd11_code"),
            schema="diagnostic",
        )

    # authority_id FK on icd11_codes (only if column missing)
    if not inspector.has_table("icd11_codes", schema="diagnostic") or "authority_id" not in {c["name"] for c in inspector.get_columns("icd11_codes", schema="diagnostic")}:
        pass  # column created above as part of table

    # ensure FK exists
    existing_fks = inspector.get_foreign_keys("icd11_codes", schema="diagnostic")
    if not any(fk["name"] == "fk_icd11_codes_authority" for fk in existing_fks):
        op.create_foreign_key(
            "fk_icd11_codes_authority",
            "icd11_codes", "classification_authorities",
            ["authority_id"], ["authority_id"],
            source_schema="diagnostic", referent_schema="diagnostic",
        )

    # DSM-5-TR fields on disorders
    existing_cols = {c["name"] for c in inspector.get_columns("disorders", schema="diagnostic")}
    for col in ("dsm_criteria", "dsm_exclusions", "dsm_differentials", "icd11_exclusions", "icd11_differentials"):
        if col not in existing_cols:
            op.add_column("disorders", sa.Column(col, sa.Text()), schema="diagnostic")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    existing_cols = {c["name"] for c in inspector.get_columns("disorders", schema="diagnostic")}
    for col in ("icd11_differentials", "icd11_exclusions", "dsm_differentials", "dsm_exclusions", "dsm_criteria"):
        if col in existing_cols:
            op.drop_column("disorders", col, schema="diagnostic")

    if inspector.has_table("icd11_codes", schema="diagnostic"):
        existing_fks = inspector.get_foreign_keys("icd11_codes", schema="diagnostic")
        if any(fk["name"] == "fk_icd11_codes_authority" for fk in existing_fks):
            op.drop_constraint("fk_icd11_codes_authority", "icd11_codes", schema="diagnostic")
        op.drop_table("icd11_codes", schema="diagnostic")

    if inspector.has_table("classification_authorities", schema="diagnostic"):
        op.drop_table("classification_authorities", schema="diagnostic")
