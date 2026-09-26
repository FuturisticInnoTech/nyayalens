"""Create the NyayaLens document schema.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "documents" not in tables:
        op.create_table(
            "documents",
            sa.Column("id", sa.String(length=80), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("document_type", sa.String(length=120), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("pages", sa.Integer(), nullable=False),
            sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("overview", sa.JSON(), nullable=False),
            sa.Column("obligations", sa.JSON(), nullable=False),
            sa.Column("flags", sa.JSON(), nullable=False),
        )
    if "clauses" not in tables:
        op.create_table(
            "clauses",
            sa.Column("id", sa.String(length=100), primary_key=True),
            sa.Column("document_id", sa.String(length=80), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("category", sa.String(length=120), nullable=False),
            sa.Column("heading", sa.String(length=255), nullable=False),
            sa.Column("page", sa.Integer(), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("clause_order", sa.Integer(), nullable=False),
        )
        op.create_index("ix_clauses_document_id", "clauses", ["document_id"])
    if "obligations" not in tables:
        op.create_table(
            "obligations",
            sa.Column("id", sa.String(length=100), primary_key=True),
            sa.Column("document_id", sa.String(length=80), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("party", sa.String(length=120), nullable=False),
            sa.Column("action", sa.Text(), nullable=False),
            sa.Column("trigger", sa.Text(), nullable=False),
            sa.Column("amount", sa.String(length=120)),
            sa.Column("clause_id", sa.String(length=100), nullable=False),
            sa.Column("certainty", sa.String(length=120), nullable=False),
        )
        op.create_index("ix_obligations_document_id", "obligations", ["document_id"])
    if "attention_flags" not in tables:
        op.create_table(
            "attention_flags",
            sa.Column("id", sa.String(length=100), primary_key=True),
            sa.Column("document_id", sa.String(length=80), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("kind", sa.String(length=80), nullable=False),
            sa.Column("explanation", sa.Text(), nullable=False),
            sa.Column("why", sa.Text(), nullable=False),
            sa.Column("question", sa.Text(), nullable=False),
            sa.Column("clause_ids", sa.JSON(), nullable=False),
        )
        op.create_index("ix_attention_flags_document_id", "attention_flags", ["document_id"])


def downgrade() -> None:
    op.drop_table("attention_flags")
    op.drop_table("obligations")
    op.drop_index("ix_clauses_document_id", table_name="clauses")
    op.drop_table("clauses")
    op.drop_table("documents")
