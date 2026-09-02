"""End-to-end pipeline: Forms_Response -> WQ_Normalize -> Web_KPI ->
Issue_Candidate -> TOP5_Calc -> TOP5_Final -> Guardrail.

Source of truth: Engine v1.4 sheet dependency order. Web_KPI must be computed
before Issue_Candidate because every Issue_Candidate row's R column reads
Web_KPI!F6 (Web_DRI's TOP5用R). Guardrail is independent of TOP5 and only
needs WQ_Normalize!C18 (WQ-404's raw answer).

Corrective Patch 1.1 / ED-DI-003: diagnosis_status is the explicit,
inspectable business state this pipeline now returns instead of letting
weighted_score()'s all-blank case surface as an uncaught exception. See
PipelineResult and DIAGNOSIS_STATUS_* below.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .forms_adapter import normalize_forms_response
from .guardrail import GuardrailEntry, evaluate_guardrail, top_guardrail
from .issue_candidate import IssueCandidate, build_issue_candidates
from .top5_calc import Top5CalcRow, compute_top5_calc
from .top5_final import Top5FinalRow, compute_top5_final, top5_list
from .web_kpi import WebKPI, compute_web_kpi
from .wq_normalize import NormalizedWQ, normalize

DIAGNOSIS_STATUS_OK = "OK"
DIAGNOSIS_STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
"""ED-DI-003: set when Web_EDI and/or Web_DRI could not be computed because
every one of their underlying WQ_Normalize scores was Unknown (see
web_kpi.py's weighted_score() calls). This is a normal, expected business
outcome of an (almost) entirely-Unknown submission -- not a bug -- so it is
reported as a status a caller checks, not an exception a caller must catch.
Web_EPI is excluded from this check: its own formula always has at least one
non-blank term (WQ-404's guardrail_urgency branch is never blank), so it
cannot itself become None -- see web_kpi.py."""


@dataclass(frozen=True)
class PipelineResult:
    diagnosis_status: str  # DIAGNOSIS_STATUS_OK or DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    normalized: Dict[str, NormalizedWQ]
    web_kpi: WebKPI
    guardrail_entries: List[GuardrailEntry]
    top_guardrail: "GuardrailEntry | None"
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

    if web_kpi.web_edi is None or web_kpi.web_dri is None:
        # ED-DI-003: with (effectively) every relevant WQ Unknown, Web_DRI's
        # TOP5用R (web_dri_top5_r) is itself undefined, and every
        # Issue_Candidate row depends on it -- there is no meaningful
        # Guardrail/TOP5 to compute from here, so the pipeline stops with an
        # explicit status rather than continuing on undefined inputs. This
        # threshold (and whether Guardrail/TOP5 should ever be attempted
        # from partial data) is exactly what ED-DI-003 asks S社 to decide;
        # this is Corrective Patch 1.1's provisional behavior until then.
        return PipelineResult(
            diagnosis_status=DIAGNOSIS_STATUS_INSUFFICIENT_DATA,
            normalized=normalized,
            web_kpi=web_kpi,
            guardrail_entries=[],
            top_guardrail=None,
            issue_candidates=[],
            top5_calc=[],
            top5_final=[],
            top5=[],
        )

    guardrail_entries = evaluate_guardrail(normalized["WQ-404"].raw)
    winning_guardrail = top_guardrail(guardrail_entries)

    wq001_raw = forms_response.get("WQ-001", "")
    wq501_raw = forms_response.get("WQ-501", "")
    issues = build_issue_candidates(normalized, wq001_raw, wq501_raw, web_kpi.web_dri_top5_r)

    calc_rows = compute_top5_calc(issues)
    final_rows = compute_top5_final(calc_rows)
    top5 = top5_list(final_rows)

    return PipelineResult(
        diagnosis_status=DIAGNOSIS_STATUS_OK,
        normalized=normalized,
        web_kpi=web_kpi,
        guardrail_entries=guardrail_entries,
        top_guardrail=winning_guardrail,
        issue_candidates=issues,
        top5_calc=calc_rows,
        top5_final=final_rows,
        top5=top5,
    )
