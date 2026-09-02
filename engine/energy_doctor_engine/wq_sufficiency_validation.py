"""WQ-level information sufficiency -- ED-DI-003 **Final Disposition**
(S社 Design Disposition Decision Record, "Final Disposition Approved /
Implementation Pending", 2026-09-02).

History: this module began as a **Validation-only** exercise (see
`05_Handoff_Brief/WQ_SUFFICIENCY_VALIDATION_INSTRUCTION.md`, 2026-09-02)
responding to ED-DI-003's then-open "Implemented / Pilot Threshold &
Granularity TBC" status. Engine Patch 2 had formalized
`weighted_score()`'s exclude-and-renormalize approach and added
`information_sufficiency` at **top-level-term granularity** (see
`web_kpi.py` / `excel_compat.py`). The Validation exercise built the WQ-level
weight tables below and a 6-pattern x 40/50/60% comparison
(`compute_wq_sufficiency_validation`, `WQ_SUFFICIENCY_VALIDATION_REPORT.md`)
so S社 could decide the granularity and threshold question before Pilot.

**That decision has now been made** (see
`05_Handoff_Brief/ED_DI_003_FINAL_PIPELINE_PATCH_INSTRUCTION.md` and
Energy_Doctor_Design_Issue_Log.md's ED-DI-003 entry): **WQ-level granularity,
50% threshold**, exactly as implemented below and exercised by the
Validation exercise's Pattern 2/6 comparison. This module's weight tables
and `_wq_level_sufficiency()` are therefore now the single source of truth
for information sufficiency used both:

- by `compute_wq_sufficiency()` below, which `pipeline.py` imports and calls
  on every `run_pipeline()` invocation to decide each of Web_EDI/Web_DRI/
  Web_EPI's individual status and the overall `diagnosis_status` (see
  `pipeline.py`'s `MIN_WQ_SUFFICIENCY_THRESHOLD`), and
- by `compute_wq_sufficiency_validation()`, kept unchanged for historical
  reproducibility of the original 40%/50%/60% three-threshold comparison
  report -- production code does not call it; only the formal 50% path
  (`compute_wq_sufficiency()`) is wired into `pipeline.py`.

Definition (unchanged from the Validation exercise, now formal):

    WQ-level information sufficiency
        = (sum of declared weight for *answered* WQs)
          / (sum of declared weight for *all* WQs the KPI's formula touches)

A WQ counts as "answered" when its post-Adapter-normalization
`NormalizedWQ.unknown == 0` (see `forms_adapter.py` / `wq_normalize.py`) --
i.e. the Unknown/blank check is the same one WQ_Normalize itself already
performs, not a secondary "is D or E populated" test.

How each KPI's flat per-WQ weight table below was derived ("展開方法")
-----------------------------------------------------------------------
Each KPI's weight table is produced by walking `web_kpi.py`'s
`weighted_score()` call for that KPI term by term, *exactly as written*,
and splitting each term's declared weight evenly across the WQs that
appear inside that term (an `avg_or_none(...)` term with N distinct WQs
gives each of them term_weight/N; a term that references a single WQ
directly, e.g. Web_DRI's `0.20*D11`, gives that WQ the whole term weight).
This is a literal flattening of the existing formula structure, not an
independent re-weighting over "the set of unique WQs" -- so a WQ used by
three different-sized terms is not treated as "one WQ, one equal share";
it is treated as "whatever the existing formula already implies its total
influence to be", which is what "情報充足率" should track if it is meant
to describe how much of the *existing scoring formula's* weight rests on
answered material. This flattening method is itself part of the ED-DI-003
Final Disposition (see the handoff instruction's point 1) -- not just the
resulting numbers -- so `web_kpi.py`'s term structure remains the sole
source of truth this table must be kept in sync with by inspection.

**When the same WQ appears in more than one term within the same KPI, its
per-term contributions are summed, not deduplicated.** This is the
instructed treatment of Web_DRI's known ISS-04 issue (WQ-403 appears both
in the 0.15 `avg_or_none(WQ-401,402,403)` term and again as the standalone
0.10*D17 term) -- ISS-04 itself stays HOLD and is not corrected here (ED-DI-003
Final Disposition explicitly reaffirms this), so WQ-403's flat weight in
Web_DRI is (0.15/3) + 0.10 = 0.15, not a deduplicated 0.10 or 0.05.

Web_EPI's guardrail_urgency / WQ-404 slot: `web_kpi.py`'s third Web_EPI
term is `avg_or_none(e["WQ-104"], guardrail_urgency)`, where
`guardrail_urgency` is a value *always* derived from WQ-404's raw answer
text but is never itself `None` -- even an Unknown WQ-404 resolves it to a
concrete fallback of 40 (see `web_kpi.py`'s `elif c18 in ("不明", "",
"UNKNOWN")` branch). Taken completely literally, this term's value
computation "never sees a blank" for that half. This module instead
treats that half of the term as a **virtual WQ-404 weight slot** (0.25/2 =
0.125), counted as *answered* only when `normalized["WQ-404"].unknown ==
0` -- not merely because `guardrail_urgency` always evaluates to a number.
Rationale: "information sufficiency" is meant to describe whether the
respondent actually supplied information, not whether the point-value
formula happens to have a fallback constant for missing information; 40 is
a stand-in for "we don't know", not a real urgency reading. **ED-DI-003
Final Disposition point 3 explicitly adopts this virtual-WQ-404-slot
interpretation as the formal production rule** (this was surfaced during
the Validation exercise for S社's confirmation, and has now been confirmed).

Each KPI's flat table sums to 1.0 (Web_DRI's sum of *term* weights is 1.0;
WQ-403 alone accounts for 0.15 of it via double-counting, as above).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .forms_adapter import normalize_forms_response
from .wq_normalize import NormalizedWQ, normalize

# Local copies of the two diagnosis-status label strings, matching
# pipeline.py's DIAGNOSIS_STATUS_OK / DIAGNOSIS_STATUS_INSUFFICIENT_DATA
# verbatim. Defined here rather than imported from pipeline.py to avoid a
# circular import (pipeline.py imports compute_wq_sufficiency() from this
# module for its production decision) -- this module only needs the two
# label strings for its own status_at_40/50/60 comparison output, not any
# of pipeline.py's decision logic itself.
_STATUS_OK = "OK"
_STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

# --- Flat per-WQ weight tables -------------------------------------------
# Derived from web_kpi.py's compute_web_kpi() term-by-term, as documented
# above. web_kpi.py itself is NOT imported or modified here -- these tables
# are a hand-flattened transcription of its current weighted_score() calls,
# kept in sync by inspection whenever web_kpi.py's formulas change (they are
# not protected/forbidden to touch this way, since this module does not
# read web_kpi.py's structure at runtime; a future change to web_kpi.py's
# term structure would need this table updated to match, but would not
# silently desync in a way that affects web_kpi.py's own output).

_EDI_WQ_WEIGHTS: Dict[str, float] = {
    # 0.40 * avg_or_none(WQ-101, WQ-102, WQ-103, WQ-104)
    "WQ-101": 0.40 / 4,
    "WQ-102": 0.40 / 4,
    "WQ-103": 0.40 / 4,
    "WQ-104": 0.40 / 4,
    # 0.20 * avg_or_none(WQ-201, WQ-202, WQ-204)
    "WQ-201": 0.20 / 3,
    "WQ-202": 0.20 / 3,
    "WQ-204": 0.20 / 3,
    # 0.20 * avg_or_none(WQ-301, WQ-302, WQ-303)
    "WQ-301": 0.20 / 3,
    "WQ-302": 0.20 / 3,
    "WQ-303": 0.20 / 3,
    # 0.20 * avg_or_none(WQ-401, WQ-403)
    "WQ-401": 0.20 / 2,
    "WQ-403": 0.20 / 2,
}

_DRI_WQ_WEIGHTS: Dict[str, float] = {
    # 0.30 * avg_or_none(WQ-101, WQ-102, WQ-201, WQ-202, WQ-302)
    "WQ-101": 0.30 / 5,
    "WQ-102": 0.30 / 5,
    "WQ-201": 0.30 / 5,
    "WQ-202": 0.30 / 5,
    "WQ-302": 0.30 / 5,
    # 0.25 * avg_or_none(WQ-103, WQ-104, WQ-203)
    "WQ-103": 0.25 / 3,
    "WQ-104": 0.25 / 3,
    "WQ-203": 0.25 / 3,
    # 0.20 * WQ-204 (standalone, no AVERAGE)
    "WQ-204": 0.20,
    # 0.15 * avg_or_none(WQ-401, WQ-402, WQ-403)
    "WQ-401": 0.15 / 3,
    "WQ-402": 0.15 / 3,
    # 0.15/3 (from the term above) + 0.10 (standalone WQ-403 term below),
    # ACCUMULATED not deduplicated -- see ISS-04 discussion in the module
    # docstring. Written as a literal sum, not pre-collapsed, so the two
    # contributions stay individually traceable.
    "WQ-403": 0.15 / 3 + 0.10,
}

_EPI_WQ_WEIGHTS: Dict[str, float] = {
    # 0.30 * WQ-405 (standalone)
    "WQ-405": 0.30,
    # 0.25 * avg_or_none(WQ-103, WQ-303)
    "WQ-103": 0.25 / 2,
    "WQ-303": 0.25 / 2,
    # 0.25 * avg_or_none(WQ-104, guardrail_urgency[WQ-404]) -- see module
    # docstring for why the guardrail_urgency half is attributed to WQ-404
    # as a virtual slot, gated on WQ-404's own Unknown flag.
    "WQ-104": 0.25 / 2,
    "WQ-404": 0.25 / 2,
    # 0.20 * epi_wq204_term (derived from WQ-204, standalone)
    "WQ-204": 0.20,
}

THRESHOLDS = (0.40, 0.50, 0.60)
"""The three candidate thresholds compared during the Validation exercise.
50% (the middle value) is the one ED-DI-003 Final Disposition formally
adopted -- see pipeline.py's MIN_WQ_SUFFICIENCY_THRESHOLD. This tuple is
kept only so compute_wq_sufficiency_validation() can still reproduce the
original three-way comparison for historical reference; it is not read by
any production decision path."""


def _wq_level_sufficiency(weights: Dict[str, float], norm: Dict[str, NormalizedWQ]) -> float:
    """回答済みWQの有効ウェイト合計 ÷ 当該KPI対象WQの全ウェイト合計.

    "Answered" = NormalizedWQ.unknown == 0 (the Adapter-normalized Unknown
    flag WQ_Normalize itself already computes), not "d/e is not None" --
    e.g. WQ-301's d is None for a "特になし" *answer* too (WQ_Normalize's
    "" branch is reused for a legitimate non-Unknown answer there), so
    checking d/e directly would misclassify an answered WQ as Unknown.
    """
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    answered_weight = sum(
        weight for wq_id, weight in weights.items() if norm[wq_id].unknown == 0
    )
    return answered_weight / total_weight


def _status_at(value: float, threshold: float) -> str:
    return _STATUS_OK if value >= threshold else _STATUS_INSUFFICIENT_DATA


@dataclass(frozen=True)
class WQSufficiency:
    """ED-DI-003 Final Disposition: the formal, production WQ-level
    information sufficiency for each of Web_EDI/Web_DRI/Web_EPI, computed
    independently. See compute_wq_sufficiency() below -- this is what
    pipeline.py actually uses to decide diagnosis_status."""

    web_edi: float
    web_dri: float
    web_epi: float


def compute_wq_sufficiency(norm: Dict[str, NormalizedWQ]) -> WQSufficiency:
    """Formal production WQ-level information sufficiency (ED-DI-003 Final
    Disposition, 2026-09-02) for Web_EDI/Web_DRI/Web_EPI, computed
    independently per KPI -- one KPI can be information-insufficient while
    the others are not (e.g. Web_EPI alone, when Unknowns concentrate on
    its urgency/impact-heavy WQs; see the Validation exercise's Pattern 6).

    `pipeline.py`'s `run_pipeline()` calls this on every invocation and
    compares each of the three returned values against
    `MIN_WQ_SUFFICIENCY_THRESHOLD` (0.50) to decide `web_edi_status` /
    `web_dri_status` / `web_epi_status` and the overall `diagnosis_status`.
    """
    return WQSufficiency(
        web_edi=_wq_level_sufficiency(_EDI_WQ_WEIGHTS, norm),
        web_dri=_wq_level_sufficiency(_DRI_WQ_WEIGHTS, norm),
        web_epi=_wq_level_sufficiency(_EPI_WQ_WEIGHTS, norm),
    )


@dataclass(frozen=True)
class WQSufficiencyValidation:
    """Historical: the original three-threshold (40%/50%/60%) comparison
    output from the Validation exercise, kept only so that comparison can
    still be reproduced (e.g. re-running WQ_SUFFICIENCY_VALIDATION_REPORT.md's
    figures). ED-DI-003 Final Disposition settled on 50% -- production code
    (pipeline.py) does not call this function; it calls compute_wq_sufficiency()
    directly and applies only the formal 50% threshold."""

    wq_sufficiency_edi: float
    wq_sufficiency_dri: float
    wq_sufficiency_epi: float
    status_at_40: Dict[str, str]  # keys: "web_edi", "web_dri", "web_epi"
    status_at_50: Dict[str, str]
    status_at_60: Dict[str, str]


def compute_wq_sufficiency_validation(norm: Dict[str, NormalizedWQ]) -> WQSufficiencyValidation:
    """Reproduce the original Validation exercise's OK/INSUFFICIENT_DATA
    status under each of the 40/50/60% candidate thresholds, independently
    per KPI. Not used by pipeline.py -- see WQSufficiencyValidation's
    docstring.

    `norm` is the same Dict[str, NormalizedWQ] produced by
    wq_normalize.normalize() (typically after forms_adapter's Unknown
    normalization) -- the same input compute_web_kpi() and run_pipeline()
    use, so this can be run alongside them on the exact same case without
    recomputation drift.
    """
    sufficiency = compute_wq_sufficiency(norm)
    edi, dri, epi = sufficiency.web_edi, sufficiency.web_dri, sufficiency.web_epi

    def statuses_at(threshold: float) -> Dict[str, str]:
        return {
            "web_edi": _status_at(edi, threshold),
            "web_dri": _status_at(dri, threshold),
            "web_epi": _status_at(epi, threshold),
        }

    return WQSufficiencyValidation(
        wq_sufficiency_edi=edi,
        wq_sufficiency_dri=dri,
        wq_sufficiency_epi=epi,
        status_at_40=statuses_at(0.40),
        status_at_50=statuses_at(0.50),
        status_at_60=statuses_at(0.60),
    )


def compute_wq_sufficiency_validation_from_forms_response(
    forms_response: Dict[str, str]
) -> WQSufficiencyValidation:
    """Convenience wrapper: applies the same Adapter normalization step
    run_pipeline() uses (forms_adapter.normalize_forms_response ->
    wq_normalize.normalize) and then computes the historical 40/50/60%
    comparison output -- without calling run_pipeline() itself, keeping this
    usable standalone by scripts/tests that only have raw Forms_Response
    input. See WQSufficiencyValidation's docstring: not used by pipeline.py."""
    adapted = normalize_forms_response(forms_response)
    norm = normalize(adapted)
    return compute_wq_sufficiency_validation(norm)
