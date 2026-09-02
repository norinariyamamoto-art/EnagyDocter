"""End-to-end pipeline: Forms_Response -> WQ_Normalize -> Web_KPI ->
Issue_Candidate -> TOP5_Calc -> TOP5_Final -> Guardrail.

Source of truth: Engine v1.4 sheet dependency order. Web_KPI must be computed
before Issue_Candidate because every Issue_Candidate row's R column reads
Web_KPI!F6 (Web_DRI's TOP5用R). Guardrail is independent of TOP5 and only
needs WQ_Normalize!C18 (WQ-404's raw answer).

Display hierarchy (ED-DI-005 Approved Disposition, V2.3 sheet
`78_Web診断Disposition` row 8): **Guardrail -> 要確認事項 (review_items) ->
TOP5**, reflected below both in PipelineResult's field order and in the
order this docstring, and run_pipeline() itself, compute them.

diagnosis_status is the explicit, inspectable business state this pipeline
returns instead of letting an ill-defined KPI surface as an uncaught
exception or a silently-wrong number -- see DIAGNOSIS_STATUS_* and
MIN_WQ_SUFFICIENCY_THRESHOLD below.

ED-DI-003 Final Disposition (S社 Design Disposition Decision Record, "Final
Disposition Approved / Implementation Pending", 2026-09-02; see
Energy_Doctor_Design_Issue_Log.md and
`05_Handoff_Brief/ED_DI_003_FINAL_PIPELINE_PATCH_INSTRUCTION.md`): the
information-sufficiency granularity/threshold question the WQ Sufficiency
Validation exercise produced comparison data for
(`wq_sufficiency_validation.py`, `WQ_SUFFICIENCY_VALIDATION_REPORT.md`) has
been formally decided -- **WQ-level granularity, 50% threshold** -- and is
now wired into this module's production diagnosis_status decision below
(replacing the earlier per-term-level MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC).
Per the Final Disposition's point 5, this decision is deliberately kept
separate from TOP5/Issue_Candidate eligibility, which continues to depend
only on whether Web_DRI's web_dri_top5_r is available -- see the TOP5
section of run_pipeline() below.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .domain_status import DomainStatus, compute_domain_status
from .forms_adapter import normalize_forms_response
from .guardrail import GuardrailEntry, evaluate_guardrail, top_guardrail
from .issue_candidate import IssueCandidate, build_issue_candidates
from .review_items import ReviewItem, compute_review_items
from .top5_calc import Top5CalcRow, compute_top5_calc
from .top5_final import Top5FinalRow, compute_top5_final, top5_list
from .web_kpi import WebKPI, compute_web_kpi
from .wq_normalize import NormalizedWQ, normalize
from .wq_sufficiency_validation import WQSufficiency, compute_wq_sufficiency

DIAGNOSIS_STATUS_OK = "OK"
DIAGNOSIS_STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

MIN_WQ_SUFFICIENCY_THRESHOLD = 0.50
"""**Final value -- ED-DI-003 Final Disposition, S社 Design Disposition
Decision Record ("Final Disposition Approved / Implementation Pending",
2026-09-02).** No longer TBC.

Supersedes the earlier per-term-level `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`
(0.5, provisional; Engine Patch 2 / ED-DI-003 Approved Disposition). That
constant left two things open -- the information-sufficiency *granularity*
(top-level-term vs. WQ) and the *threshold* itself -- as
Energy_Doctor_Design_Issue_Log.md's ED-DI-003 "残る論点" section tracked. The
WQ Sufficiency Validation exercise (`wq_sufficiency_validation.py`,
`WQ_SUFFICIENCY_VALIDATION_REPORT.md`) produced comparison data across 6
boundary-case patterns x three candidate thresholds (40%/50%/60%) for S社 to
decide from; S社's Final Disposition selected **WQ-level granularity at the
50% threshold**, exactly as implemented here.

Judged independently per KPI: Web_EDI/Web_DRI/Web_EPI's WQ-level information
sufficiency (`wq_sufficiency_validation.compute_wq_sufficiency()`) is each
compared against this threshold (`>= 0.50` -> OK, `< 0.50` ->
INSUFFICIENT_DATA) to produce `web_edi_status`/`web_dri_status`/
`web_epi_status`; the overall `diagnosis_status` is INSUFFICIENT_DATA if any
one of the three is (ED-DI-003 Final Disposition point 4). A KPI whose own
WQ-level sufficiency is still >= 0.50 keeps its computed value even when a
*different* KPI drags the overall diagnosis_status to INSUFFICIENT_DATA
(Final Disposition point 4's explicit "50%以上の個別KPI値は保持・表示可能" --
sufficient KPIs are never invalidated just because another one is not).

The earlier top-level-term-level `WebKPI.*_information_sufficiency` fields
(Engine Patch 2) are kept unchanged for historical/comparison record, but
are no longer read by this decision -- see web_kpi.py.
"""


def _wq_status(value: float, threshold: "float | None" = None) -> str:
    """`>= MIN_WQ_SUFFICIENCY_THRESHOLD` -> OK, else INSUFFICIENT_DATA,
    applied independently per KPI (ED-DI-003 Final Disposition point 2).

    `threshold` defaults to None -- resolved to the *current* value of
    MIN_WQ_SUFFICIENCY_THRESHOLD inside the function body, deliberately not
    as this parameter's default value (a default value is bound once at
    function-definition time and would not observe a test monkeypatching
    the module constant afterwards). run_pipeline() always calls this with
    no explicit threshold, so changing the module constant changes
    run_pipeline()'s actual behavior.
    """
    if threshold is None:
        threshold = MIN_WQ_SUFFICIENCY_THRESHOLD
    return DIAGNOSIS_STATUS_OK if value >= threshold else DIAGNOSIS_STATUS_INSUFFICIENT_DATA


@dataclass(frozen=True)
class PipelineResult:
    diagnosis_status: str  # DIAGNOSIS_STATUS_OK or DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    normalized: Dict[str, NormalizedWQ]
    web_kpi: WebKPI
    domain_status: DomainStatus  # ED-DI-004: 設備/エネルギー/建屋/管理, independent of Web_EDI

    # ED-DI-003 Final Disposition: WQ-level information sufficiency and its
    # per-KPI OK/INSUFFICIENT_DATA status, independent per KPI (a single KPI
    # can be INSUFFICIENT_DATA while the other two stay OK -- e.g. Web_EPI
    # alone, when Unknowns concentrate on its urgency/impact-heavy WQs).
    # diagnosis_status above is INSUFFICIENT_DATA whenever any one of these
    # three is, but each KPI's own web_kpi.web_edi/dri/epi value is kept and
    # displayable regardless (see MIN_WQ_SUFFICIENCY_THRESHOLD's docstring).
    web_edi_wq_sufficiency: float
    web_dri_wq_sufficiency: float
    web_epi_wq_sufficiency: float
    web_edi_status: str  # DIAGNOSIS_STATUS_OK or DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    web_dri_status: str
    web_epi_status: str

    # --- display hierarchy below: Guardrail -> 要確認事項 -> TOP5 (ED-DI-005) ---
    guardrail_pending: bool  # ED-DI-005: WQ-404 itself is Unknown (see docstring below)
    guardrail_entries: List[GuardrailEntry]
    top_guardrail: Optional[GuardrailEntry]
    review_items: List[ReviewItem]  # ED-DI-005: issues that didn't fire because Unknown
    issue_candidates: List[IssueCandidate]
    top5_calc: List[Top5CalcRow]
    top5_final: List[Top5FinalRow]
    top5: List[Top5FinalRow]


def run_pipeline(forms_response: Dict[str, str]) -> PipelineResult:
    # Corrective Patch 1 / ISS-02: absorb "不明" / "分からない" / blank before
    # anything else sees the answers. See forms_adapter.py.
    forms_response = normalize_forms_response(forms_response)
    normalized = normalize(forms_response)
    web_kpi = compute_web_kpi(normalized)
    domain_status = compute_domain_status(normalized)  # ED-DI-004

    # ED-DI-003 Final Disposition: WQ-level information sufficiency, judged
    # independently per KPI against MIN_WQ_SUFFICIENCY_THRESHOLD (0.50).
    # This decides diagnosis_status below; it does NOT gate TOP5/Issue_Candidate
    # (see the TOP5 section further down, which depends only on
    # web_kpi.web_dri_top5_r).
    wq_sufficiency = compute_wq_sufficiency(normalized)
    web_edi_status = _wq_status(wq_sufficiency.web_edi)
    web_dri_status = _wq_status(wq_sufficiency.web_dri)
    web_epi_status = _wq_status(wq_sufficiency.web_epi)
    diagnosis_status = (
        DIAGNOSIS_STATUS_OK
        if (
            web_edi_status == DIAGNOSIS_STATUS_OK
            and web_dri_status == DIAGNOSIS_STATUS_OK
            and web_epi_status == DIAGNOSIS_STATUS_OK
        )
        else DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    )

    # --- Guardrail (always evaluated -- ED-DI-005: "重大事項の未確認を非表示にしない") ---
    # ED-DI-005 point 2: WQ-404 itself being Unknown is not the same as a
    # confirmed "ない" -- the closed formal Q-ID list behind WQ-404 (ED-DI-002,
    # V2.3 sheet `77_WQ-Q_Traceability`) is exactly the set of safety/legal/
    # quality/BCP questions a Guardrail decision would otherwise rest on, so
    # an Unknown WQ-404 is reported as a *pending* judgment, never silently
    # folded into "no Guardrail" (guardrail_entries stays empty and
    # top_guardrail stays None either way, but guardrail_pending tells a
    # caller which of the two actually happened).
    guardrail_pending = normalized["WQ-404"].unknown == 1
    if guardrail_pending:
        guardrail_entries: List[GuardrailEntry] = []
        winning_guardrail = None
    else:
        guardrail_entries = evaluate_guardrail(normalized["WQ-404"].raw)
        winning_guardrail = top_guardrail(guardrail_entries)

    # --- Issue_Candidate / 要確認事項 (also always evaluated) ---
    # Fire conditions never depend on web_dri_top5_r (only the *score*, used
    # below, does), so issue_candidates -- and therefore review_items, which
    # only inspects which issues failed to fire and why -- can be computed
    # even when Web_DRI itself is INSUFFICIENT_DATA and web_dri_top5_r is None.
    wq001_raw = forms_response.get("WQ-001", "")
    wq501_raw = forms_response.get("WQ-501", "")
    issues = build_issue_candidates(normalized, wq001_raw, wq501_raw, web_kpi.web_dri_top5_r)
    review_items = compute_review_items(issues, normalized)  # ED-DI-005 point 1

    # --- TOP5 (requires a defined Web_DRI-derived R; skipped otherwise) ---
    # ED-DI-003 Final Disposition point 5: TOP5/Issue_Candidate eligibility
    # depends *only* on whether web_dri_top5_r is available -- NOT on the
    # overall diagnosis_status above. A case where Web_EDI/Web_DRI are both
    # WQ-sufficient but Web_EPI alone is not (diagnosis_status ==
    # INSUFFICIENT_DATA) must still compute and display TOP5 normally, as
    # long as Web_DRI itself produced a concrete R. This is a deliberate
    # decoupling from the pre-Final-Disposition behavior, which gated TOP5
    # on the same term-level sufficiency check that decided diagnosis_status.
    if web_kpi.web_dri_top5_r is not None:
        calc_rows = compute_top5_calc(issues)
        final_rows = compute_top5_final(calc_rows)
        top5 = top5_list(final_rows)
    else:
        # web_dri_top5_r is undefined (Web_DRI itself is None -- every one
        # of its WQ_Normalize terms was blank) -- TOP_BASE's 0.10*R term has
        # nothing to multiply, and ranking issues against each other would
        # not be meaningful, so TOP5 is left empty. Guardrail and
        # review_items are NOT suppressed here (see above).
        calc_rows = []
        final_rows = []
        top5 = []

    return PipelineResult(
        diagnosis_status=diagnosis_status,
        normalized=normalized,
        web_kpi=web_kpi,
        domain_status=domain_status,
        web_edi_wq_sufficiency=wq_sufficiency.web_edi,
        web_dri_wq_sufficiency=wq_sufficiency.web_dri,
        web_epi_wq_sufficiency=wq_sufficiency.web_epi,
        web_edi_status=web_edi_status,
        web_dri_status=web_dri_status,
        web_epi_status=web_epi_status,
        guardrail_pending=guardrail_pending,
        guardrail_entries=guardrail_entries,
        top_guardrail=winning_guardrail,
        review_items=review_items,
        issue_candidates=issues,
        top5_calc=calc_rows,
        top5_final=final_rows,
        top5=top5,
    )
