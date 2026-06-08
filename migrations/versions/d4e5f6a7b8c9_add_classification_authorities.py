"""add classification authorities + DSM criteria fields

Revision ID: d4e5f6a7b8c9
Revises: c1d2e3f4a5b6
Create Date: 2026-06-07 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ClassificationAuthority
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

    # authority_id FK on icd11_codes
    op.add_column(
        "icd11_codes",
        sa.Column("authority_id", sa.Integer()),
        schema="diagnostic",
    )
    op.create_foreign_key(
        "fk_icd11_codes_authority",
        "icd11_codes", "classification_authorities",
        ["authority_id"], ["authority_id"],
        source_schema="diagnostic", referent_schema="diagnostic",
    )

    # DSM-5-TR fields on disorders
    op.add_column(
        "disorders",
        sa.Column("dsm_criteria", sa.Text()),
        schema="diagnostic",
    )
    op.add_column(
        "disorders",
        sa.Column("dsm_exclusions", sa.Text()),
        schema="diagnostic",
    )
    op.add_column(
        "disorders",
        sa.Column("dsm_differentials", sa.Text()),
        schema="diagnostic",
    )
    op.add_column(
        "disorders",
        sa.Column("icd11_exclusions", sa.Text()),
        schema="diagnostic",
    )
    op.add_column(
        "disorders",
        sa.Column("icd11_differentials", sa.Text()),
        schema="diagnostic",
    )


def downgrade() -> None:
    op.drop_column("disorders", "icd11_differentials", schema="diagnostic")
    op.drop_column("disorders", "icd11_exclusions", schema="diagnostic")
    op.drop_column("disorders", "dsm_differentials", schema="diagnostic")
    op.drop_column("disorders", "dsm_exclusions", schema="diagnostic")
    op.drop_column("disorders", "dsm_criteria", schema="diagnostic")
    op.drop_constraint("fk_icd11_codes_authority", "icd11_codes", schema="diagnostic")
    op.drop_column("icd11_codes", "authority_id", schema="diagnostic")
    op.drop_table("classification_authorities", schema="diagnostic")
