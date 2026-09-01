"""Unit tests for the Excel-quirk helpers in excel_compat.py, since these are
easy to get subtly wrong and TC-A/B/C alone don't exercise every branch
(none of the three fixtures include an unrecognized/blank answer choice)."""

import pytest

from energy_doctor_engine.excel_compat import (
    ExcelValueError,
    avg_ignore_blank,
    blank_eq,
    blank_ge,
    blank_lt,
    direct,
    excel_round,
    excel_search,
)


def test_blank_lt_treats_none_as_not_less_than_any_number():
    assert blank_lt(None, 100) is False
    assert blank_lt(50, 100) is True
    assert blank_lt(100, 100) is False


def test_blank_ge_treats_none_as_greater_than_any_number():
    assert blank_ge(None, 80) is True
    assert blank_ge(79, 80) is False
    assert blank_ge(80, 80) is True


def test_blank_eq_never_matches_none():
    assert blank_eq(None, 60) is False
    assert blank_eq(60, 60) is True


def test_avg_ignore_blank_skips_none_like_excel_average():
    assert avg_ignore_blank(100, None, 50) == 75


def test_avg_ignore_blank_all_blank_raises():
    with pytest.raises(ExcelValueError):
        avg_ignore_blank(None, None)


def test_direct_raises_on_blank_like_excel_value_error():
    with pytest.raises(ExcelValueError):
        direct(None, "test context")
    assert direct(42, "test context") == 42


def test_excel_search_is_substring_and_blank_safe():
    assert excel_search("安全", "安全、法令") is True
    assert excel_search("安全", "供給継続") is False
    assert excel_search("安全", None) is False
    assert excel_search("安全", "") is False


def test_excel_round_half_away_from_zero():
    # Excel ROUND(17.5,0) = 18, not 18-via-banker's-rounding-by-luck; check a
    # case where Python's default round() would disagree (round(0.5)==0).
    assert excel_round(17.5, 0) == 18
    assert excel_round(0.5, 0) == 1
    assert excel_round(2.5, 0) == 3
