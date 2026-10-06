"""backfill collection.collector_id for pre-collector rows

Revision ID: 0004_backfill_collector
Revises: 0003_collector
Create Date: 2026-10-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_backfill_collector"
down_revision: Union[str, None] = "0003_collector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLLECTOR_ID = "4454616f-10ff-426a-a4f3-df4066ecb742"


def upgrade() -> None:
    conn = op.get_bind()
    # Fresh installs have nothing to backfill, so the collector need not exist.
    pending = conn.execute(
        sa.text("SELECT 1 FROM collection WHERE collector_id IS NULL LIMIT 1")
    ).first()
    if not pending:
        return

    exists = conn.execute(
        sa.text("SELECT 1 FROM users WHERE id = CAST(:id AS uuid)"),
        {"id": COLLECTOR_ID},
    ).first()
    if not exists:
        raise RuntimeError(
            f"Backfill collector {COLLECTOR_ID} does not exist in users; "
            "create it before running this migration."
        )

    # only rows created before collectors existed; never overwrite a real one
    conn.execute(
        sa.text(
            "UPDATE collection SET collector_id = CAST(:id AS uuid) "
            "WHERE collector_id IS NULL"
        ),
        {"id": COLLECTOR_ID},
    )


def downgrade() -> None:
    # Irreversible data backfill: we can't tell backfilled rows from rows this
    # collector actually submitted, so leave the data as is.
    pass
