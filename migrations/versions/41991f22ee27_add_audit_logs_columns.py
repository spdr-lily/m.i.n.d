"""no-op — audit_logs columns already exist in initial_schema

Revision ID: 41991f22ee27
Revises: b3c4d5e6f7a8
Create Date: 2026-06-03 11:52:26.217370
"""
from typing import Sequence, Union

revision: str = '41991f22ee27'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
