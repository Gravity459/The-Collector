"""Layout Map: the AI's description of the sheet's structure.

No validation constraints here on purpose: both providers turn this model into
their structured-output schema, and code (sheet_grid.validate_layout) checks
every claim against the real grid before anything is trusted.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class MonthColumn(BaseModel):
    month: str = Field(description="Month as YYYY-MM, e.g. 2026-09")
    column: str = Field(description="Column letter, e.g. M")


class HouseRow(BaseModel):
    house: int = Field(description="House number as an integer: S-24 -> 24")
    row: int = Field(description="1-based row number")


class LayoutMap(BaseModel):
    header_row: int = Field(description="Row holding the column headings")
    house_column: str = Field(description="Column letter holding house ids like S-24")
    month_columns: list[MonthColumn] = Field(
        description="Every column whose heading is a month, left to right"
    )
    house_rows: list[HouseRow] = Field(description="Every row of the house table")
    first_house_row: int
    last_house_row: int
    aggregation_rows: list[int] = Field(
        description="Every other non-empty row below the header: totals, expenses, "
        "fund reserve, participant counts, monthly summary blocks"
    )
    month_header_template: str = Field(
        description="Heading pattern for month columns using {Mon}, {Month}, {MM}, "
        "{YY}, {YYYY}; 'Amount (Sep 26)' -> 'Amount ({Mon} {YY})'"
    )

    def row_for(self, house: int) -> int | None:
        return next((h.row for h in self.house_rows if h.house == house), None)

    def column_for(self, month: str) -> str | None:
        return next((m.column for m in self.month_columns if m.month == month), None)

    def latest_month(self) -> str | None:
        return max((m.month for m in self.month_columns), default=None)
