"""WQ-level information sufficiency -- **Validation-only** exercise.

Handoff: `05_Handoff_Brief/WQ_SUFFICIENCY_VALIDATION_INSTRUCTION.md` (2026-09-02),
responding to Energy_Doctor_Design_Issue_Log.md's ED-DI-003 status
"Implemented / Pilot Threshold & Granularity TBC". Engine Patch 2 formalized
`weighted_score()`'s exclude-and-renormalize approach and added
`information_sufficiency` at **top-level-term granularity** (see
`web_kpi.py` / `excel_compat.py`). S社's review of Engine Patch 2 flagged
that whether sufficiency should instead be measured at **WQ granularity**
is a genuine open Pilot-blocking question, not an implementation defect.

This module exists solely to produce comparison data -- WQ-level sufficiency
for Web_EDI/Web_DRI/Web_EPI, each judged independently against three
candidate thresholds (40%/50%/60%) -- so S社 can decide the granularity and
threshold question before Pilot. **It decides nothing itself:**

- It does NOT replace, wrap, or feed into `pipeline.py`'s
  `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC` or `diagnosis_status`.
- `pipeline.py` does not import this module, and this module does not call
  `run_pipeline()`. The two are structurally disconnected on purpose.
- It does NOT change `weighted_score()`, `web_kpi.py`'s formulas/weights, or
  Issue_Candidate's U-value handling (ED-DI-003 point 5 / Engine Patch 2).
- It does NOT touch ED-DI-001 (Unknown display wording) in any way.
- 40%/50%/60% are candidate thresholds for comparison only -- none of the
  three is asserted here to be "the" correct value; that is an S社 decision.

Definition (per the handoff instruction, verbatim):

    WQ-level information sufficiency
        = (sum of declared weight for *answered* WQs)
          / (sum of declared weight for *all* WQs the KPI's formula touches)

A WQ counts as "answered" when its post-Adapter-normalization
`NormalizedWQ.unknown == 0` (see `forms_adapter.py` / `wq_normalize.py`) --
i.e. the Unknown/blank check is the same one WQ_Normalize itself already
performs, not a secondary "is D or E populated" test.

How each KPI's flat per-WQ weight table below was derived ("展開方法"),
per completion condition 7
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
answered material.

**When the same WQ appears in more than one term within the same KPI, its
per-term contributions are summed, not deduplicated.** This is the
instructed treatment of Web_DRI's known ISS-04 issue (WQ-403 appears both
in the 0.15 `avg_or_none(WQ-401,402,403)` term and again as the standalone
0.10*D17 term) -- ISS-04 itself stays HOLD and is not corrected here; this
module simply mirrors the existing double-weighting rather than silently
fixing it, so WQ-403's flat weight in Web_DRI is (0.15/3) + 0.10 = 0.15,
not a deduplicated 0.10 or 0.05.

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
a stand-in for "we don't know", not a real urgency reading. This is a
documented interpretive choice (the instruction explicitly allows using a
better-justified alternative to bare equal-split, with rationale stated),
and it is exactly what boundary-case Pattern 6 below is designed to
exercise and cross-check against `guardrail_pending`.

Each KPI's flat table sums to 1.0 (Web_DRI's sum of *term* weights is 1.0;
WQ-403 alone accounts for 0.15 of it via double-counting, as above).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .forms_adapter import normalize_forms_response
from .pipeline import DIAGNOSIS_STATUS_INSUFFICIENT_DATA, DIAGNOSIS_STATUS_OK
from .wq_normalize import NormalizedWQ, normalize

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
"""Candidate comparison thresholds only -- see module docstring. Not a
decision; S社 selects the Pilot threshold from data produced with these."""


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
    return DIAGNOSIS_STATUS_OK if value >= threshold else DIAGNOSIS_STATUS_INSUFFICIENT_DATA


@dataclass(frozen=True)
class WQSufficiencyValidation:
    """Validation-only comparison output. Never constructed by
    pipeline.py / run_pipeline() and never fed back into PipelineResult."""

    wq_sufficiency_edi: float
    wq_sufficiency_dri: float
    wq_sufficiency_epi: float
    status_at_40: Dict[str, str]  # keys: "web_edi", "web_dri", "web_epi"
    status_at_50: Dict[str, str]
    status_at_60: Dict[str, str]


def compute_wq_sufficiency_validation(norm: Dict[str, NormalizedWQ]) -> WQSufficiencyValidation:
    """Compute WQ-level information sufficiency for Web_EDI/Web_DRI/Web_EPI
    and their OK/INSUFFICIENT_DATA status under each of the 40/50/60%
    candidate thresholds, independently per KPI.

    `norm` is the same Dict[str, NormalizedWQ] produced by
    wq_normalize.normalize() (typically after forms_adapter's Unknown
    normalization) -- the same input compute_web_kpi() and run_pipeline()
    use, so this can be run alongside them on the exact same case without
    recomputation drift.
    """
    edi = _wq_level_sufficiency(_EDI_WQ_WEIGHTS, norm)
    dri = _wq_level_sufficiency(_DRI_WQ_WEIGHTS, norm)
    epi = _wq_level_sufficiency(_EPI_WQ_WEIGHTS, norm)

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
    wq_normalize.normalize) and then computes the validation output --
    without calling run_pipeline() itself, keeping this module usable
    standalone by scripts/tests that only have raw Forms_Response input."""
    adapted = normalize_forms_response(forms_response)
    norm = normalize(adapted)
    return compute_wq_sufficiency_validation(norm)
