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


def avg_or_none(*values: float | None) -> float | None:
    """Same as avg_ignore_blank, but returns None instead of raising when
    every member is blank -- lets a fully-blank AVERAGE() group compose into
    weighted_score() below instead of aborting the whole formula.
    (Corrective Patch 1 / ISS-03.)"""
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


class InsufficientDataError(ValueError):
    """Every weighted component of a Web_KPI formula was blank (Unknown) --
    there is no defined "score" for zero information, so this is raised
    rather than silently returning 0 (which Corrective Patch 1 / ISS-03
    explicitly says not to do). This is expected to be unreachable for any
    realistic Forms submission (all required WQ answered Unknown); it is not
    Excel's #VALUE! (that failure mode is what this patch removes)."""


def weighted_score(terms: "list[tuple[float, float | None]]") -> float:
    """Evaluate a fixed-weight formula (e.g. Web_DRI's
    0.30*A + 0.25*B + 0.20*C + 0.15*D + 0.10*E, weights summing to 1) while
    tolerating one or more blank (Unknown) terms.

    Corrective Patch 1 / ISS-03: the source workbook already tolerates a
    blank member *inside* an AVERAGE() range (that range's average is simply
    taken over the remaining members -- see avg_or_none above). But several
    Web_KPI terms reference a single WQ_Normalize score directly in
    arithmetic (no AVERAGE wrapper), which is #VALUE! in Excel when that
    score is blank. This function extends the *same* "ignore blank members,
    renormalize over what's left" principle that AVERAGE() already applies
    within one term, to the outer weighted sum across all of a formula's
    terms -- so a directly-referenced blank term drops out and the
    remaining weights are rescaled to sum back to 1, rather than forcing
    that term to 0 (which Corrective Patch 1 explicitly rules out) or
    raising #VALUE!. A term with a fully-blank AVERAGE() group (all of its
    members Unknown) is handled identically once that group has been reduced
    to None via avg_or_none.

    This does not import any question-specific Unknown-handling rule from
    V2.2 sheet `03_採点マトリクス` (see ED-DI-002) -- it is a generic,
    question-agnostic fallback that only activates when a term is blank.
    """
    usable = [(w, v) for w, v in terms if v is not None]
    total_weight = sum(w for w, _ in usable)
    if total_weight == 0:
        raise InsufficientDataError(
            "every weighted component of this formula is Unknown/blank -- "
            "no defined score for zero information"
        )
    return sum(w * v for w, v in usable) / total_weight


def direct(value: float | None, context: str) -> float:
    """A formula that references a single WQ_Normalize score cell directly in
    arithmetic (e.g. `0.20*WQ_Normalize!D11`), not through AVERAGE. A blank
    cell here is #VALUE! in Excel.

    Retained (with its own unit test) as documentation of that original
    Excel-faithful #VALUE! behavior -- see Task 1A's ISSUES.md ISS-03. As of
    Corrective Patch 1, no module in this package calls this any more: every
    formula that used to route through it (Web_KPI's Web_DRI/Web_EPI, and
    Issue_Candidate's shared U column via TOP5_Calc) now uses
    weighted_score() instead, which tolerates the same blank case without
    raising. Kept for reference/tests rather than deleted outright."""
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
