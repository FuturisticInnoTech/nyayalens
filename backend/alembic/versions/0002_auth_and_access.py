"""Add users, sessions, and document ownership mappings.

Revision ID: 0002_auth_and_access
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_auth_and_access"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = set(inspect(op.get_bind()).get_table_names())
    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=80), primary_key=True),
            sa.Column("email", sa.String(length=255), nullable=False, unique=True),
            sa.Column("display_name", sa.String(length=120), nullable=False),
            sa.Column("password_hash", sa.String(length=255)),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    if "sessions" not in tables:
        op.create_table(
            "sessions",
            sa.Column("token_hash", sa.String(length=64), primary_key=True),
            sa.Column("user_id", sa.String(length=80), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    if "document_access" not in tables:
        op.create_table(
            "document_access",
            sa.Column("document_id", sa.String(length=80), sa.ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("user_id", sa.String(length=80), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        )


def downgrade() -> None:
    op.drop_table("document_access")
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("users")
