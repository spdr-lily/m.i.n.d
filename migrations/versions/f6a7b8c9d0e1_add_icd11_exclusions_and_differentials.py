"""add icd11_exclusions and icd11_differentials tables

Revision ID: f6a7b8c9d0e1
Revises: 1c223a553bb0
Create Date: 2026-06-15 11:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = '1c223a553bb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('icd11_exclusions',
        sa.Column('exclusion_id', sa.Integer(), nullable=False),
        sa.Column('code_id', sa.Integer(), nullable=False),
        sa.Column('excluded_code', sa.String(length=20)),
        sa.Column('excluded_title', sa.String(length=500)),
        sa.Column('reason', sa.Text()),
        sa.ForeignKeyConstraint(['code_id'], ['diagnostic.icd11_codes.code_id'], ),
        sa.PrimaryKeyConstraint('exclusion_id'),
        schema='diagnostic'
    )
    op.create_table('icd11_differentials',
        sa.Column('differential_id', sa.Integer(), nullable=False),
        sa.Column('code_id', sa.Integer(), nullable=False),
        sa.Column('differential_code', sa.String(length=20)),
        sa.Column('differential_title', sa.String(length=500)),
        sa.Column('distinguishing_features', sa.Text()),
        sa.ForeignKeyConstraint(['code_id'], ['diagnostic.icd11_codes.code_id'], ),
        sa.PrimaryKeyConstraint('differential_id'),
        schema='diagnostic'
    )


def downgrade() -> None:
    op.drop_table('icd11_differentials', schema='diagnostic')
    op.drop_table('icd11_exclusions', schema='diagnostic')
