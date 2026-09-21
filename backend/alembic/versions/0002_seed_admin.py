"""seed admin user from env

Revision ID: 0002_seed_admin
Revises: 0001_initial
Create Date: 2026-09-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.config import get_settings
from app.core.security import hash_password

revision: str = "0002_seed_admin"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    settings = get_settings()
    conn = op.get_bind()

    existing = conn.execute(
        sa.text("SELECT 1 FROM users WHERE email = :email"),
        {"email": settings.admin_email},
    ).first()
    if existing:
        return  # idempotent: admin already present

    conn.execute(
        sa.text(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (:name, :email, :password, 'admin')
            """
        ),
        {
            "name": settings.admin_name,
            "email": settings.admin_email,
            "password": hash_password(settings.admin_password),
        },
    )


def downgrade() -> None:
    settings = get_settings()
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM users WHERE email = :email AND role = 'admin'"),
        {"email": settings.admin_email},
    )
