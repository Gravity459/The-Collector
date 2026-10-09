"""collection.period_month: the month a payment is for

Revision ID: 0005_period_month
Revises: 0004_backfill_collector
Create Date: 2026-10-10

Safe on a live database:
- existing rows are backfilled from created_at, so every current month view
  is unchanged;
- the column then gets a server default, so app code deployed before this
  migration (which never sends period_month) keeps inserting fine;
- duplicates are checked before the unique constraint, and alembic runs the
  whole upgrade in one transaction, so a failure leaves the DB untouched.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_period_month"
down_revision: Union[str, None] = "0004_backfill_collector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CURRENT_MONTH = sa.text("(date_trunc('month', now()))::date")


def upgrade() -> None:
    # No default yet: Postgres would stamp every existing row with *this*
    # month the moment the column is added, before the backfill could run.
    op.add_column("collection", sa.Column("period_month", sa.Date(), nullable=True))

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE collection "
            "SET period_month = (date_trunc('month', created_at))::date "
            "WHERE period_month IS NULL"
        )
    )
    op.alter_column("collection", "period_month", server_default=CURRENT_MONTH)

    duplicates = conn.execute(
        sa.text(
            "SELECT h.house_number, c.period_month, count(*) AS n "
            "FROM collection c JOIN houses h ON h.id = c.house_id "
            "GROUP BY h.house_number, c.period_month "
            "HAVING count(*) > 1 "
            "ORDER BY c.period_month, h.house_number"
        )
    ).all()
    if duplicates:
        found = ", ".join(
            f"S-{house} {month:%Y-%m} (x{n})" for house, month, n in duplicates
        )
        raise RuntimeError(
            "Cannot add one-payment-per-house-per-month rule; duplicate "
            f"collections exist: {found}. Remove the extras, then rerun."
        )

    op.alter_column("collection", "period_month", nullable=False)
    op.create_check_constraint(
        "ck_collection_period_first_day",
        "collection",
        "extract(day from period_month) = 1",
    )
    op.create_unique_constraint(
        "uq_collection_house_period", "collection", ["house_id", "period_month"]
    )
    op.create_index("ix_collection_period_month", "collection", ["period_month"])


def downgrade() -> None:
    # created_at still holds the submission date, so nothing is lost
    op.drop_index("ix_collection_period_month", table_name="collection")
    op.drop_constraint("uq_collection_house_period", "collection", type_="unique")
    op.drop_constraint("ck_collection_period_first_day", "collection", type_="check")
    op.drop_column("collection", "period_month")
