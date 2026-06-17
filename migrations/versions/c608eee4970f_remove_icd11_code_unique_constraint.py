"""remove icd11_code unique constraint

Revision ID: c608eee4970f
Revises: 031c8a8ec7b8
Create Date: 2026-06-16 16:03:33.775835
"""
from typing import Sequence, Union
from alembic import op

revision: str = "c608eee4970f"
down_revision: Union[str, None] = "031c8a8ec7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("icd11_codes_icd11_code_key", "icd11_codes", schema="diagnostic", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("icd11_codes_icd11_code_key", "icd11_codes", schema="diagnostic", columns=["icd11_code"])
