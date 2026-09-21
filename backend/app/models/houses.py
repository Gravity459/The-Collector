"""House model."""
from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class House(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "houses"

    house_number: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True, index=True
    )

    collections: Mapped[list["Collection"]] = relationship(  # noqa: F821
        back_populates="house"
    )
