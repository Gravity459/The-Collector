"""collector role + collection.collector_id

Revision ID: 0003_collector
Revises: 0002_seed_admin
Create Date: 2026-10-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_collector"
down_revision: Union[str, None] = "0002_seed_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint(
        "ck_users_role", "users", "role in ('user', 'admin', 'collector')"
    )

    op.add_column(
        "collection",
        sa.Column("collector_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_collection_collector_id",
        "collection",
        "users",
        ["collector_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_collection_collector_id", "collection", ["collector_id"])


def downgrade() -> None:
    op.drop_index("ix_collection_collector_id", table_name="collection")
    op.drop_constraint("fk_collection_collector_id", "collection", type_="foreignkey")
    op.drop_column("collection", "collector_id")

    op.execute("UPDATE users SET role = 'user' WHERE role = 'collector'")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint("ck_users_role", "users", "role in ('user', 'admin')")
