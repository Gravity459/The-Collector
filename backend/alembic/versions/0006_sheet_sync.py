"""sheet sync: sheet_layouts + sheet_sync_jobs

Revision ID: 0006_sheet_sync
Revises: 0005_period_month
Create Date: 2026-10-10

Only creates new tables: the running app never reads them, so this is safe to
apply before the code that uses them is deployed. No jobs are seeded, so
collections approved before the feature is switched on are never pushed into
the sheet.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_sheet_sync"
down_revision: Union[str, None] = "0005_period_month"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _id_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True,
    )


def _timestamp(name: str) -> sa.Column:
    return sa.Column(
        name,
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "sheet_layouts",
        _id_column(),
        sa.Column("spreadsheet_id", sa.String(length=128), nullable=False),
        sa.Column("tab_name", sa.String(length=128), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("layout", postgresql.JSONB(), nullable=False),
        sa.Column("source", sa.String(length=8), nullable=False),
        _timestamp("created_at"),
        sa.CheckConstraint("source in ('ai', 'code')", name="ck_sheet_layouts_source"),
    )
    op.create_index(
        "ix_sheet_layouts_lookup",
        "sheet_layouts",
        ["spreadsheet_id", "tab_name", "created_at"],
    )

    op.create_table(
        "sheet_sync_jobs",
        _id_column(),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=32), nullable=True),
        sa.Column("target_cell", sa.String(length=16), nullable=True),
        sa.Column("existing_value", sa.String(length=255), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "attempts", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        _timestamp("created_at"),
        _timestamp("updated_at"),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collection.id"],
            name="fk_sheet_sync_jobs_collection_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("collection_id", name="uq_sheet_sync_jobs_collection_id"),
        sa.CheckConstraint(
            "status in ('pending', 'done', 'needs_review', 'failed')",
            name="ck_sheet_sync_jobs_status",
        ),
        sa.CheckConstraint(
            "reason is null or reason in ('conflict', 'house_not_in_sheet', "
            "'month_column_missing', 'layout_unreadable')",
            name="ck_sheet_sync_jobs_reason",
        ),
    )
    op.create_index("ix_sheet_sync_jobs_status", "sheet_sync_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_sheet_sync_jobs_status", table_name="sheet_sync_jobs")
    op.drop_table("sheet_sync_jobs")
    op.drop_index("ix_sheet_layouts_lookup", table_name="sheet_layouts")
    op.drop_table("sheet_layouts")
