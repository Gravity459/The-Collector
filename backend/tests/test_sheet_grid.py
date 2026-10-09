"""Pure grid helpers and the Layout Map validator (no DB needed)."""
import copy

import pytest

from app.integrations.sheet_grid import (
    col_to_index,
    fingerprint,
    index_to_col,
    next_month,
    normalize_house,
    parse_month_header,
    redact_for_ai,
    render_header,
    validate_layout,
)
from tests.sheet_fakes import correct_layout, load_fixture_grid


@pytest.fixture
def grid():
    return load_fixture_grid()


def test_columns_round_trip():
    for i in (0, 12, 25, 26, 51, 701, 702):
        assert col_to_index(index_to_col(i)) == i
    assert index_to_col(12) == "M" and col_to_index("AA") == 26
    with pytest.raises(ValueError):
        col_to_index("A1")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("S-24", 24),
        ("s 24", 24),
        (" S–7 ", 7),
        ("S24", 24),
        ("House Number", None),
        ("24", None),
        ("", None),
    ],
)
def test_normalize_house(text, expected):
    assert normalize_house(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Amount (Sep 26)", "2026-09"),
        ("Amount (Sept 2026)", "2026-09"),
        ("October-26", "2026-10"),
        ("Jan'27", "2027-01"),
        ("Contact No.", None),
        ("Month", None),
        ("SEP", None),
    ],
)
def test_parse_month_header(text, expected):
    assert parse_month_header(text) == expected


def test_months_and_templates():
    assert next_month("2026-12") == "2027-01"
    assert next_month("2026-09") == "2026-10"
    assert render_header("Amount ({Mon} {YY})", "2026-10") == "Amount (Oct 26)"
    assert render_header("{Month} {YYYY} ({MM})", "2027-01") == "January 2027 (01)"


def test_correct_layout_passes(grid):
    assert validate_layout(correct_layout(grid), grid) == []


def _broken(grid, mutate):
    layout = correct_layout(grid)
    mutate(layout)
    return validate_layout(layout, grid)


def test_rejects_wrong_house_row(grid):
    errors = _broken(grid, lambda l: setattr(l.house_rows[2], "row", 12))
    assert any("not S-6" in e for e in errors)
    assert any("missing from house_rows" in e for e in errors)


def test_rejects_missing_house(grid):
    errors = _broken(grid, lambda l: l.house_rows.pop())
    assert any("row 33 holds S-62" in e for e in errors)


def test_rejects_wrong_month(grid):
    errors = _broken(grid, lambda l: setattr(l.month_columns[3], "month", "2026-05"))
    assert any("is not 2026-05" in e for e in errors)


def test_rejects_out_of_order_months(grid):
    def swap(layout):
        layout.month_columns[0], layout.month_columns[1] = (
            layout.month_columns[1],
            layout.month_columns[0],
        )

    assert any("date order" in e for e in _broken(grid, swap))


def test_rejects_unlisted_month_column(grid):
    errors = _broken(grid, lambda l: l.month_columns.pop())
    assert any("column M" in e and "not listed" in e for e in errors)


def test_rejects_aggregation_overlapping_houses(grid):
    errors = _broken(grid, lambda l: l.aggregation_rows.append(10))
    assert any("aggregation row 10 overlaps" in e for e in errors)


def test_rejects_wrong_template(grid):
    errors = _broken(grid, lambda l: setattr(l, "month_header_template", "{Mon} {YY}"))
    assert any("month_header_template" in e for e in errors)


def test_rejects_nonsense_bounds(grid):
    assert _broken(grid, lambda l: setattr(l, "header_row", 999))
    assert _broken(grid, lambda l: setattr(l, "house_column", "C3"))


def test_fingerprint_tracks_structure_not_amounts(grid):
    layout = correct_layout(grid)
    base = fingerprint(grid, layout.header_row, layout.house_column)

    amounts = copy.deepcopy(grid)
    amounts[8][12] = "4600"  # S-15 pays September
    assert fingerprint(amounts, layout.header_row, layout.house_column) == base

    new_house = copy.deepcopy(grid)
    new_house[33][2] = "S-99"
    assert fingerprint(new_house, layout.header_row, layout.house_column) != base

    renamed = copy.deepcopy(grid)
    renamed[1][12] = "Amount (Sept 26)"
    assert fingerprint(renamed, layout.header_row, layout.house_column) != base


def test_redaction_masks_names_and_phones(grid):
    grid[36][4] = "0300-1234567"  # a phone typed into an amount column
    text = redact_for_ai(grid)
    assert "Resident" not in text
    assert "0300" not in text and "<phone>" in text
    assert "<name> 20 (DON) Previous Remaining=" in text  # label kept, name masked
    assert "Total Collection =" in text
    assert "r13: A=11 | C=S-24 |" in text  # row numbers and letters preserved
