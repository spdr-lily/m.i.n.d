"""add_alert_resolved_by_and_notes

Revision ID: b5c6d7e8f9a0
Revises: 4ad39c05ec58
Create Date: 2026-09-04 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b5c6d7e8f9a0"
down_revision: Union[str, None] = "4ad39c05ec58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("CREATE SCHEMA IF NOT EXISTS clinical")
    conn = op.get_bind()
    has_table = conn.execute(
        sa.text("SELECT to_regclass('clinical.clinical_alerts')")
    ).scalar()
    if not has_table:
        return
    op.add_column("clinical_alerts", sa.Column("resolved_by", UUID(as_uuid=True), nullable=True), schema="clinical")
    op.add_column("clinical_alerts", sa.Column("resolution_notes", sa.Text(), nullable=True), schema="clinical")


def downgrade() -> None:
    conn = op.get_bind()
    has_col = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='clinical' AND table_name='clinical_alerts' AND column_name='resolved_by')")
    ).scalar()
    if has_col:
        op.drop_column("clinical_alerts", "resolved_by", schema="clinical")
    has_col2 = conn.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='clinical' AND table_name='clinical_alerts' AND column_name='resolution_notes')")
    ).scalar()
    if has_col2:
        op.drop_column("clinical_alerts", "resolution_notes", schema="clinical")
