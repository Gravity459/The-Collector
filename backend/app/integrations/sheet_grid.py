"""Pure helpers over a sheet grid. CPU-only and tiny, so they stay sync.

A grid is the sheet's values as rows of strings. Rows are 1-based and columns
are letters everywhere in this module, matching what people see in the sheet.
"""
from __future__ import annotations

import hashlib
import json
import re

from app.integrations.ai.schemas import LayoutMap

Grid = list[list[str]]

MONTH_ABBR = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH_FULL = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)

_HOUSE_RE = re.compile(r"^\s*S\s*[-–]?\s*(\d+)\s*$", re.IGNORECASE)
_MONTH_RE = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?[\s\-'/,]*(\d{4}|\d{2})\b",
    re.IGNORECASE,
)
_PHONE_RE = re.compile(r"^(?:\+?92|0)?3\d{9}$")
_PRIVATE_HEADER_RE = re.compile(r"name|contact|phone|mobile", re.IGNORECASE)
_MAX_CELL_CHARS = 60


# --- addressing ---------------------------------------------------------

def col_to_index(col: str) -> int:
    """Column letter to 0-based index: "A" -> 0, "AA" -> 26."""
    col = col.strip().upper()
    if not col.isalpha() or not col.isascii():
        raise ValueError(f"not a column letter: {col!r}")
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def index_to_col(index: int) -> str:
    """0-based index to column letter: 0 -> "A", 26 -> "AA"."""
    n, out = index + 1, ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def a1(row: int, col: str) -> str:
    return f"{col.upper()}{row}"


def cell(grid: Grid, row: int, col: str) -> str:
    """Value at (1-based row, column letter); "" outside the grid."""
    r, c = row - 1, col_to_index(col)
    if 0 <= r < len(grid) and 0 <= c < len(grid[r]):
        return grid[r][c]
    return ""


# --- parsing ------------------------------------------------------------

def normalize_house(value: str) -> int | None:
    """House id to number: "S-24", "s 24", "S–24" -> 24; anything else -> None."""
    m = _HOUSE_RE.match(value or "")
    return int(m.group(1)) if m else None


def parse_month_header(text: str) -> str | None:
    """Heading to month: "Amount (Sep 26)" -> "2026-09"; None if no month."""
    m = _MONTH_RE.search(text or "")
    if not m:
        return None
    month = MONTH_ABBR.index(m.group(1).title()) + 1
    year = int(m.group(2))
    if year < 100:
        year += 2000
    return f"{year:04d}-{month:02d}"


def next_month(month: str) -> str:
    year, mon = (int(p) for p in month.split("-"))
    return f"{year + mon // 12:04d}-{mon % 12 + 1:02d}"


def render_header(template: str, month: str) -> str:
    year, mon = (int(p) for p in month.split("-"))
    return (
        template.replace("{YYYY}", f"{year:04d}")
        .replace("{YY}", f"{year % 100:02d}")
        .replace("{MM}", f"{mon:02d}")
        .replace("{Month}", MONTH_FULL[mon - 1])
        .replace("{Mon}", MONTH_ABBR[mon - 1])
    )


# --- structure ----------------------------------------------------------

def _trim(values: list[str]) -> list[str]:
    out = [v.strip() for v in values]
    while out and not out[-1]:
        out.pop()
    return out


def fingerprint(grid: Grid, header_row: int, house_column: str) -> str:
    """Hash of the header row + house column: changes when the sheet's
    structure does (rows/columns added, moved or renamed), not when amounts
    are typed in."""
    header = grid[header_row - 1] if 0 < header_row <= len(grid) else []
    houses = [cell(grid, r, house_column) for r in range(1, len(grid) + 1)]
    payload = json.dumps([_trim(header), _trim(houses)], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def redact_for_ai(grid: Grid) -> str:
    """Compact text of the grid for the AI, without residents' personal data.

    - On house rows, name/contact columns (by their heading) are dropped.
    - Elsewhere those columns are kept: sheets reuse them for labels such as
      "Total Collection =", which the AI needs to spot aggregation rows.
    - Every residents' name found on house rows is masked anywhere it appears
      (labels like "Sarfaraz (DON) Previous Remaining"), and anything shaped
      like a phone number is masked.
    Original row numbers and column letters are kept so the answer maps back.
    """
    private: set[int] = set()
    name_cols: set[int] = set()
    for row in grid[:3]:
        for i, value in enumerate(row):
            if _PRIVATE_HEADER_RE.search(value or ""):
                private.add(i)
                if "name" in value.lower():
                    name_cols.add(i)

    house_rows = {
        r for r, row in enumerate(grid) if any(normalize_house(v) is not None for v in row)
    }
    names = {
        token.lower()
        for r in house_rows
        for i in name_cols
        if i < len(grid[r])
        for token in re.findall(r"[^\W\d_]{3,}", grid[r][i])
    }
    name_re = (
        re.compile(r"\b(" + "|".join(map(re.escape, sorted(names))) + r")\b", re.IGNORECASE)
        if names
        else None
    )

    lines = []
    for r, row in enumerate(grid):
        cells = []
        for i, value in enumerate(row):
            value = (value or "").strip()
            if not value or (r in house_rows and i in private):
                continue
            if _PHONE_RE.match(re.sub(r"[\s\-()]", "", value)):
                value = "<phone>"
            elif name_re:
                value = name_re.sub("<name>", value)
            cells.append(f"{index_to_col(i)}={value[:_MAX_CELL_CHARS]}")
        if cells:
            lines.append(f"r{r + 1}: " + " | ".join(cells))
    return "\n".join(lines)


def validate_layout(layout: LayoutMap, grid: Grid) -> list[str]:
    """Check every claim in an AI Layout Map against the real grid.

    Returns human-readable problems (empty = trustworthy). This is the
    guardrail: a map that passes can only point writes at real house rows
    and real month columns.
    """
    errors: list[str] = []
    hdr = layout.header_row
    if not 0 < hdr <= len(grid):
        return [f"header_row {hdr} is outside the sheet (1-{len(grid)})"]
    try:
        col_to_index(layout.house_column)
    except ValueError:
        return [f"house_column {layout.house_column!r} is not a column letter"]

    first, last = layout.first_house_row, layout.last_house_row
    if not hdr < first <= last <= len(grid):
        errors.append(
            f"house rows {first}-{last} must sit below header row {hdr} and inside the sheet"
        )

    # houses: each claimed row really holds that house, and none are missed
    claimed_rows: set[int] = set()
    claimed_houses: set[int] = set()
    for h in layout.house_rows:
        if not first <= h.row <= last:
            errors.append(f"S-{h.house} row {h.row} is outside rows {first}-{last}")
        actual = cell(grid, h.row, layout.house_column)
        if normalize_house(actual) != h.house:
            errors.append(
                f"row {h.row} column {layout.house_column} holds {actual!r}, not S-{h.house}"
            )
        if h.row in claimed_rows or h.house in claimed_houses:
            errors.append(f"S-{h.house} / row {h.row} is listed twice")
        claimed_rows.add(h.row)
        claimed_houses.add(h.house)
    for r in range(max(first, 1), min(last, len(grid)) + 1):
        found = normalize_house(cell(grid, r, layout.house_column))
        if found is not None and r not in claimed_rows:
            errors.append(f"row {r} holds S-{found} but is missing from house_rows")

    # months: each claimed column's heading is that month, in order, none missed
    if not layout.month_columns:
        errors.append("no month columns found")
    claimed_cols: set[str] = set()
    prev_index, prev_month = -1, ""
    template_ok = True
    for mc in layout.month_columns:
        try:
            index = col_to_index(mc.column)
        except ValueError:
            errors.append(f"{mc.column!r} is not a column letter")
            continue
        heading = cell(grid, hdr, mc.column).strip()
        if parse_month_header(heading) != mc.month:
            errors.append(f"column {mc.column} heading {heading!r} is not {mc.month}")
        if index <= prev_index or mc.month <= prev_month:
            errors.append(f"month columns are not in left-to-right date order at {mc.column}")
        prev_index, prev_month = index, mc.month
        claimed_cols.add(mc.column.upper())
        rendered = render_header(layout.month_header_template, mc.month)
        if template_ok and rendered != heading:
            template_ok = False
            errors.append(
                f"month_header_template {layout.month_header_template!r} renders "
                f"{rendered!r}, but column {mc.column} says {heading!r}"
            )
    for i, heading in enumerate(grid[hdr - 1]):
        col = index_to_col(i)
        if parse_month_header(heading) and col not in claimed_cols:
            errors.append(f"column {col} heading {heading!r} is a month but is not listed")

    # aggregation rows never overlap the house table
    for r in layout.aggregation_rows:
        if first <= r <= last or r in claimed_rows:
            errors.append(f"aggregation row {r} overlaps the house table")

    return errors
