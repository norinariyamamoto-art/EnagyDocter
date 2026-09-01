"""Excel evaluation quirks reproduced exactly, so the engine matches the source
workbook (02_Diagnosis_Engine/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx)
cell-for-cell rather than "what the formula probably meant".

A WQ_Normalize 状態Score (D) cell that has no matching answer choice evaluates
to Excel's empty string "" (the innermost IF's implicit FALSE branch), not to
a blank/empty cell and not to 0. That distinction matters for three Excel
behaviors reproduced here:
  - "" compared to a number with < or <= is FALSE (text sorts above any number).
  - "" compared to a number with >= or > is TRUE, for the same reason.
  - "" used in a numeric formula (e.g. 0.2*D11) raises #VALUE!, whereas AVERAGE()
    silently ignores non-numeric cells in its range.
"""

from __future__ import annotations


class ExcelValueError(ValueError):
    """Mirrors an Excel #VALUE! error: a blank/text WQ_Normalize score was
    used in an arithmetic formula that does not tolerate blanks (unlike
    AVERAGE, which skips them)."""


def excel_search(needle: str, haystack: str | None) -> bool:
    """ISNUMBER(SEARCH(needle, haystack)). SEARCH is case-insensitive and
    matches substrings; a blank/None haystack never matches."""
    if not haystack:
        return False
    return needle in haystack


def blank_lt(value: float | None, threshold: float) -> bool:
    """Excel `value < threshold` where a blank/"" `value` never compares less
    than a number."""
    if value is None:
        return False
    return value < threshold


def blank_ge(value: float | None, threshold: float) -> bool:
    """Excel `value >= threshold` where a blank/"" `value` always compares
    greater than a number."""
    if value is None:
        return True
    return value >= threshold


def blank_eq(value: float | None, target: float) -> bool:
    """Excel `value = target` where a blank/"" `value` never equals a
    number."""
    if value is None:
        return False
    return value == target


def avg_ignore_blank(*values: float | None) -> float:
    """AVERAGE(range): ignores blank/text members of the range."""
    nums = [v for v in values if v is not None]
    if not nums:
        raise ExcelValueError("AVERAGE of an all-blank range is #DIV/0! in Excel")
    return sum(nums) / len(nums)


def direct(value: float | None, context: str) -> float:
    """A formula that references a single WQ_Normalize score cell directly in
    arithmetic (e.g. `0.20*WQ_Normalize!D11`), not through AVERAGE. A blank
    cell here is #VALUE! in Excel."""
    if value is None:
        raise ExcelValueError(
            f"{context}: referenced WQ_Normalize score is blank ("
            "unrecognized/unmapped answer choice) -- Excel would raise #VALUE! here"
        )
    return value


def excel_round(value: float, digits: int = 0) -> float:
    """Excel ROUND: half away from zero (Python's round() is banker's
    rounding and disagrees on .5 cases, e.g. round(17.5) == 18 in Excel but
    18 in Python 3 too by luck; round(0.5)==0 in Python vs 1 in Excel)."""
    import decimal

    quant = decimal.Decimal(1).scaleb(-digits)
    d = decimal.Decimal(str(value)).quantize(quant, rounding=decimal.ROUND_HALF_UP)
    result = float(d)
    return int(result) if digits <= 0 else result
