"""admin_permissions_routes

Revision ID: 005f85846e88
Revises: 05ecbb7b2bc1
Create Date: 2026-06-01 14:44:45.836299
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '005f85846e88'
down_revision: Union[str, None] = '05ecbb7b2bc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS admin")

    op.add_column('audit_logs', sa.Column('status_code', sa.Integer(), nullable=True), schema='audit')
    op.add_column('audit_logs', sa.Column('latency_ms', sa.Integer(), nullable=True), schema='audit')

    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('permission', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role', 'permission', name='uq_role_permission'),
        schema='admin'
    )

    op.create_table('route_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('http_method', sa.String(length=10), nullable=False),
        sa.Column('path_pattern', sa.String(length=255), nullable=False),
        sa.Column('permission_required', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('http_method', 'path_pattern', name='uq_route_method_path'),
        schema='admin'
    )

    op.create_index('ix_role_permissions_role', 'role_permissions', ['role'], schema='admin')
    op.create_index('ix_role_permissions_permission', 'role_permissions', ['permission'], schema='admin')
    op.create_index('ix_route_permissions_path', 'route_permissions', ['path_pattern'], schema='admin')


def downgrade() -> None:
    op.drop_column('audit_logs', 'latency_ms', schema='audit')
    op.drop_column('audit_logs', 'status_code', schema='audit')
    op.drop_index('ix_route_permissions_path', table_name='route_permissions', schema='admin')
    op.drop_index('ix_role_permissions_permission', table_name='role_permissions', schema='admin')
    op.drop_index('ix_role_permissions_role', table_name='role_permissions', schema='admin')
    op.drop_table('route_permissions', schema='admin')
    op.drop_table('role_permissions', schema='admin')
    op.execute("DROP SCHEMA IF EXISTS admin")
