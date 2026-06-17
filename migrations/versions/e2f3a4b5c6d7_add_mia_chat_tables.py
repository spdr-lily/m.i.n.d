"""add MIA chatbot persistence tables (chat_messages, chat_feedback, mia_knowledge)

Revision ID: e2f3a4b5c6d7
Revises: d7e8f9a0b1c2
Create Date: 2026-06-16 17:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, None] = "d7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS chat")

    op.create_table(
        "chat_messages",
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_uuid", UUID(as_uuid=True), nullable=True),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_uuid"], ["security.users.user_uuid"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("message_id"),
        schema="chat",
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"], schema="chat")
    op.create_index("ix_chat_messages_user_uuid", "chat_messages", ["user_uuid"], schema="chat")

    op.create_table(
        "chat_feedback",
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("user_uuid", UUID(as_uuid=True), nullable=True),
        sa.Column("rating", sa.String(20), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["message_id"], ["chat.chat_messages.message_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_uuid"], ["security.users.user_uuid"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("feedback_id"),
        schema="chat",
    )
    op.create_index("ix_chat_feedback_message_id", "chat_feedback", ["message_id"], schema="chat")

    op.create_table(
        "mia_knowledge",
        sa.Column("knowledge_id", sa.Integer(), nullable=False),
        sa.Column("trigger_terms", sa.Text(), nullable=False),
        sa.Column("response_template", sa.Text(), nullable=False),
        sa.Column("disorder_id", sa.Integer(), nullable=True),
        sa.Column("scale_name", sa.String(255), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), server_default="0.5000"),
        sa.Column("source", sa.String(50), server_default="seed"),
        sa.Column("times_used", sa.Integer(), server_default="0"),
        sa.Column("positive_feedback", sa.Integer(), server_default="0"),
        sa.Column("negative_feedback", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["disorder_id"], ["diagnostic.disorders.disorder_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("knowledge_id"),
        schema="chat",
    )
    op.create_index("ix_mia_knowledge_disorder_id", "mia_knowledge", ["disorder_id"], schema="chat")


def downgrade() -> None:
    op.drop_table("mia_knowledge", schema="chat")
    op.drop_table("chat_feedback", schema="chat")
    op.drop_table("chat_messages", schema="chat")
