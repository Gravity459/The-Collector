"""In-memory stand-ins for Google Sheets and the AI planner."""
from __future__ import annotations

import copy
import csv
import re
from pathlib import Path

from app.integrations.ai.schemas import HouseRow, LayoutMap, MonthColumn
from app.integrations.sheet_grid import (
    Grid,
    col_to_index,
    index_to_col,
    normalize_house,
    parse_month_header,
)

FIXTURE = Path(__file__).parent / "fixtures" / "maintenance_sheet.csv"
HEADER_ROW = 2
TEMPLATE = "Amount ({Mon} {YY})"


def load_fixture_grid() -> Grid:
    with FIXTURE.open(newline="", encoding="utf-8") as f:
        rows = [list(r) for r in csv.reader(f)]
    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]


def correct_layout(grid: Grid) -> LayoutMap:
    """What a good AI answer looks like for this sheet."""
    header = grid[HEADER_ROW - 1]
    house_col = index_to_col(next(i for i, v in enumerate(header) if "House" in v))
    months = [
        MonthColumn(month=m, column=index_to_col(i))
        for i, v in enumerate(header)
        if (m := parse_month_header(v))
    ]
    houses = [
        HouseRow(house=h, row=r)
        for r in range(HEADER_ROW + 1, len(grid) + 1)
        if (h := normalize_house(grid[r - 1][col_to_index(house_col)])) is not None
    ]
    rows = {h.row for h in houses}
    aggregation = [
        r
        for r in range(HEADER_ROW + 1, len(grid) + 1)
        if r not in rows and any(v.strip() for v in grid[r - 1])
    ]
    return LayoutMap(
        header_row=HEADER_ROW,
        house_column=house_col,
        month_columns=months,
        house_rows=houses,
        first_house_row=min(rows),
        last_house_row=max(rows),
        aggregation_rows=aggregation,
        month_header_template=TEMPLATE,
    )


class FakeSheets:
    """Behaves like GoogleSheetsClient over an in-memory grid; records calls."""

    def __init__(self, grid: Grid | None = None) -> None:
        self.grid = grid if grid is not None else load_fixture_grid()
        self.writes: list[tuple[str, str | int]] = []
        self.inserts: list[tuple[int, int]] = []
        self.fail: Exception | None = None

    async def read_grid(self) -> Grid:
        if self.fail:
            raise self.fail
        return copy.deepcopy(self.grid)

    async def insert_columns(self, start_index: int, count: int) -> None:
        if self.fail:
            raise self.fail
        self.inserts.append((start_index, count))
        for row in self.grid:
            row[start_index:start_index] = [""] * count

    async def write_cell(self, a1: str, value: str | int) -> None:
        if self.fail:
            raise self.fail
        m = re.fullmatch(r"([A-Z]+)(\d+)", a1)
        assert m, a1
        r, c = int(m.group(2)) - 1, col_to_index(m.group(1))
        while len(self.grid) <= r:
            self.grid.append([""] * len(self.grid[0]))
        row = self.grid[r]
        if len(row) <= c:
            row.extend([""] * (c + 1 - len(row)))
        row[c] = str(value)
        self.writes.append((a1, value))

    def value(self, a1: str) -> str:
        m = re.fullmatch(r"([A-Z]+)(\d+)", a1)
        assert m
        row = self.grid[int(m.group(2)) - 1]
        c = col_to_index(m.group(1))
        return row[c] if c < len(row) else ""


class FakePlanner:
    """Answers from the grid it last saw, or from queued answers; records calls."""

    def __init__(self, sheets: FakeSheets) -> None:
        self.sheets = sheets
        self.calls: list[tuple[str, str | None]] = []
        self.queued: list[LayoutMap | Exception] = []

    async def build_layout(self, grid_text: str, feedback: str | None = None) -> LayoutMap:
        self.calls.append((grid_text, feedback))
        if self.queued:
            answer = self.queued.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return answer
        return correct_layout(self.sheets.grid)
