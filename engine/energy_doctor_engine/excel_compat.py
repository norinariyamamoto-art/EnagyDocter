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

from dataclasses import dataclass


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
    """Not raised by weighted_score() (see its docstring) -- kept as a class
    in case a future, stricter caller wants to opt into treating "every term
    blank" as a hard failure rather than the normal INSUFFICIENT_DATA
    business state that weighted_score() signals via its
    WeightedScoreResult.value being None (see pipeline.py's
    diagnosis_status, which generalizes this to an information-sufficiency
    threshold as of Engine Patch 2 / ED-DI-003)."""


@dataclass(frozen=True)
class WeightedScoreResult:
    value: "float | None"
    """The weighted average over non-blank terms, renormalized so their
    weights sum to 1. None exactly when every term was blank
    (information_sufficiency == 0)."""

    information_sufficiency: float
    """回答済み有効ウェイト ÷ 全対象ウェイト (Engine Patch 2 / ED-DI-003 Approved
    Disposition, per Energy_Doctor_Design_Issue_Log.md and V2.3 sheet
    `78_Web診断Disposition`): the fraction of this formula's declared weight
    that came from a non-blank term, in [0, 1]. 1.0 means every term had an
    answer; 0.0 means every term was Unknown (mirrors WeightedScoreResult.value
    being None). This is reported to the caller alongside the value itself --
    see WebKPI's *_information_sufficiency fields and
    pipeline.py's MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC -- rather than
    being silently absorbed into the renormalized value, so a KPI computed
    from little information doesn't look identical to one computed from a
    complete answer set.

    Granularity note (also TBC, like the threshold itself): `terms` here are
    each KPI's own top-level weighted components (e.g. Web_EDI's four
    40/20/20/20 domain terms), not every individual WQ. A domain term counts
    as fully "answered" as soon as at least one of its member WQs has an
    answer (matching Excel AVERAGE()'s own "average over what's left"
    behavior for that term's *value*), so this ratio moves in coarse,
    per-term steps rather than continuously per individual question. This
    was chosen because it is the same weight structure already validated
    against the source workbook's formulas (zero risk of a separately
    maintained per-question weight table drifting out of sync with them),
    not because a finer per-question ratio was considered and rejected --
    S社 should confirm whether this term-level granularity is acceptable or
    a finer per-question figure is required, alongside confirming the
    threshold itself."""


def weighted_score(terms: "list[tuple[float, float | None]]") -> WeightedScoreResult:
    """Evaluate a fixed-weight formula (e.g. Web_DRI's
    0.30*A + 0.25*B + 0.20*C + 0.15*D + 0.10*E, weights summing to 1) while
    tolerating one or more blank (Unknown) terms, and report how much of the
    formula's weight was actually backed by an answer.

    ED-DI-003 Approved Disposition (S社 Design Disposition Decision Record
    Rev0.1, 2026-09-02; see Energy_Doctor_Design_Issue_Log.md and V2.3 sheet
    `78_Web診断Disposition`): excluding blank terms and renormalizing the
    remaining weights to sum back to 1 is now the **formal, adopted**
    Unknown-aggregation rule for Web_EDI/Web_DRI/Web_EPI -- not a provisional
    Corrective Patch 1 stand-in awaiting S社 review. This mirrors V2.2/V2.3
    sheet `13_算定式・順位ロジック` rule CM-02 for the *formal* EDI/DRI/EPI
    ("Score = Σ(w_i×s_i) ÷ Σ(w_i)", unanswerable items excluded from the
    denominator), which is why S社 approved the same treatment for the Web
    KPIs. The source workbook already applies the same "ignore blank
    members" principle *inside* an AVERAGE() range (see avg_or_none above);
    this function extends it to the outer weighted sum across a whole
    formula's terms, covering the terms that reference a single
    WQ_Normalize score directly (no AVERAGE wrapper), which would otherwise
    be Excel's #VALUE! when that score is blank.

    ED-DI-003 also approved tracking **information sufficiency** as a
    companion figure precisely because renormalization on its own can make a
    KPI computed from very little information look as confident as one
    computed from a complete answer set. See WeightedScoreResult above.

    Approved Disposition still leaves two things open (S社 Design
    Disposition Decision Record Rev0.1, `78_Web診断Disposition` row 6, and
    Energy_Doctor_Design_Issue_Log.md's ED-DI-003 "Approved Disposition"
    section): the minimum information-sufficiency threshold itself is
    "Threshold TBC" (see pipeline.py's
    MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC), and whether this same
    renormalization should extend to Issue_Candidate's U column is deferred
    to ED-DI-005 -- Engine Patch 2 answers that specific question by
    *not* extending it there (see top5_calc.py's TOP_BASE computation,
    which no longer calls this function).

    This does not import any question-specific Unknown-handling rule from
    V2.2 sheet `03_採点マトリクス` (see ED-DI-002 and its formal Traceability,
    V2.3 sheet `77_WQ-Q_Traceability`) -- it is a generic, question-agnostic
    aggregation rule that only activates when a term is blank, independent
    of which public WQ or formal Q it came from.
    """
    declared_weight = sum(w for w, _ in terms)
    usable = [(w, v) for w, v in terms if v is not None]
    used_weight = sum(w for w, _ in usable)
    sufficiency = (used_weight / declared_weight) if declared_weight else 0.0
    if used_weight == 0:
        return WeightedScoreResult(value=None, information_sufficiency=sufficiency)
    value = sum(w * v for w, v in usable) / used_weight
    return WeightedScoreResult(value=value, information_sufficiency=sufficiency)


def direct(value: float | None, context: str) -> float:
    """A formula that references a single WQ_Normalize score cell directly in
    arithmetic (e.g. `0.20*WQ_Normalize!D11`), not through AVERAGE. A blank
    cell here is #VALUE! in Excel.

    Retained (with its own unit test) as documentation of that original
    Excel-faithful #VALUE! behavior -- see Task 1A's ISSUES.md ISS-03. As of
    Corrective Patch 1, no module in this package calls this for Web_KPI's
    Web_DRI/Web_EPI any more -- those use weighted_score() instead, which
    tolerates the same blank case without raising. Issue_Candidate's shared
    U column (TOP5_Calc's TOP_BASE) also no longer routes through this or
    weighted_score() as of Engine Patch 2 / ED-DI-003 point 5 -- see
    top5_calc.py, which substitutes 0 for a blank U term without
    renormalizing the other weights, rather than raising #VALUE! or
    reweighting. Kept for reference/tests rather than deleted outright."""
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
