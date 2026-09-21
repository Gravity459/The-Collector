"""Pagination helper."""
from __future__ import annotations

import math
from typing import TypeVar

from app.schemas.common import Page

T = TypeVar("T")


def build_page(items: list[T], *, total: int, page: int, size: int) -> Page[T]:
    total_pages = math.ceil(total / size) if size else 0
    return Page[T](
        items=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages,
    )
