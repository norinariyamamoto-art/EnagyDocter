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
MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC below.
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

DIAGNOSIS_STATUS_OK = "OK"
DIAGNOSIS_STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC = 0.5
"""**TBC (To Be Confirmed) -- provisional value, not an S社 decision.**

ED-DI-003 Approved Disposition (S社 Design Disposition Decision Record
Rev0.1, 2026-09-02) approved the *existence* of a minimum information-
sufficiency gate below which a KPI is reported as INSUFFICIENT_DATA rather
than a computed number, but explicitly left the numeric threshold itself
undecided -- see Energy_Doctor_Design_Issue_Log.md's ED-DI-003 entry
("最低情報充足率の具体的閾値...はPilot前に確定する") and V2.3 sheet
`78_Web診断Disposition` row 5, which literally states "Threshold TBC" in its
own 状態 column.

0.5 is this implementation's own placeholder, chosen only because it matches
the *formal* EDI/DRI/EPI's own "参考値" threshold in V2.2/V2.3 sheet
`13_算定式・順位ロジック` rule CM-03 ("有効重みカバー率が50%未満の場合、点数
を参考値扱いとする") -- that rule governs the formal KPI, not the Web KPI
this engine computes, so borrowing its number is a convenience starting
point, not evidence that 0.5 is correct here. **S社 must confirm this value
before Pilot** (see ED-DI-003's Close condition 1). Changing this constant
changes run_pipeline()'s behavior directly -- see
tests/test_engine_patch2.py's threshold-sensitivity test, which asserts
exactly that, so a future change to this number is guaranteed to be a
deliberate edit rather than an accidental one.
"""


def _meets_information_sufficiency(
    web_kpi: WebKPI, threshold: "float | None" = None
) -> bool:
    """ED-DI-003 point 4: generalizes Corrective Patch 1.1's "all-Unknown ->
    INSUFFICIENT_DATA" rule to "information sufficiency below the minimum
    threshold -> INSUFFICIENT_DATA" for each of Web_EDI/Web_DRI/Web_EPI. An
    all-Unknown submission drives every one of these to 0.0 sufficiency, so
    it remains covered as the threshold=0 (well, any positive threshold)
    special case of this same check, exactly as ED-DI-003 asks ("全項目
    Unknownはこの条件の特殊ケースとして自然に含まれる形にする") -- no separate
    all-blank branch is needed any more.

    `threshold` defaults to None -- resolved to the *current* value of
    MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC inside the function body,
    deliberately not as this parameter's default value (a default value is
    bound once at function-definition time and would not observe a test
    monkeypatching the module constant afterwards). run_pipeline() always
    calls this with no explicit threshold, so changing the module constant
    changes run_pipeline()'s actual behavior -- see
    tests/test_engine_patch2.py's threshold-sensitivity test.
    """
    if threshold is None:
        threshold = MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC
    return (
        web_kpi.web_edi_information_sufficiency >= threshold
        and web_kpi.web_dri_information_sufficiency >= threshold
        and web_kpi.web_epi_information_sufficiency >= threshold
    )


@dataclass(frozen=True)
class PipelineResult:
    diagnosis_status: str  # DIAGNOSIS_STATUS_OK or DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    normalized: Dict[str, NormalizedWQ]
    web_kpi: WebKPI
    domain_status: DomainStatus  # ED-DI-004: 設備/エネルギー/建屋/管理, independent of Web_EDI

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
    if _meets_information_sufficiency(web_kpi):
        diagnosis_status = DIAGNOSIS_STATUS_OK
        calc_rows = compute_top5_calc(issues)
        final_rows = compute_top5_final(calc_rows)
        top5 = top5_list(final_rows)
    else:
        # ED-DI-003 point 4: below the minimum information-sufficiency
        # threshold (all-Unknown being the extreme case), TOP5_Calc's R term
        # (web_dri_top5_r) is undefined and ranking issues against each
        # other would not be meaningful -- so TOP5 is left empty. Guardrail
        # and review_items are NOT suppressed here (see above): this is a
        # deliberate change from Corrective Patch 1.1, which had also
        # emptied Guardrail in this branch, per ED-DI-005's explicit
        # disposition that Unknown/incomplete data must not hide Guardrail.
        diagnosis_status = DIAGNOSIS_STATUS_INSUFFICIENT_DATA
        calc_rows = []
        final_rows = []
        top5 = []

    return PipelineResult(
        diagnosis_status=diagnosis_status,
        normalized=normalized,
        web_kpi=web_kpi,
        domain_status=domain_status,
        guardrail_pending=guardrail_pending,
        guardrail_entries=guardrail_entries,
        top_guardrail=winning_guardrail,
        review_items=review_items,
        issue_candidates=issues,
        top5_calc=calc_rows,
        top5_final=final_rows,
        top5=top5,
    )
