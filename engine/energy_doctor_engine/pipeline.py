"""End-to-end pipeline: Forms_Response -> WQ_Normalize -> Web_KPI ->
Issue_Candidate -> TOP5_Calc -> TOP5_Final -> Guardrail.

Source of truth: Engine v1.4 sheet dependency order. Web_KPI must be computed
before Issue_Candidate because every Issue_Candidate row's R column reads
Web_KPI!F6 (Web_DRI's TOP5用R). Guardrail is independent of TOP5 and only
needs WQ_Normalize!C18 (WQ-404's raw answer).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .guardrail import GuardrailEntry, evaluate_guardrail, top_guardrail
from .issue_candidate import IssueCandidate, build_issue_candidates
from .top5_calc import Top5CalcRow, compute_top5_calc
from .top5_final import Top5FinalRow, compute_top5_final, top5_list
from .web_kpi import WebKPI, compute_web_kpi
from .wq_normalize import NormalizedWQ, normalize


@dataclass(frozen=True)
class PipelineResult:
    normalized: Dict[str, NormalizedWQ]
    web_kpi: WebKPI
    guardrail_entries: List[GuardrailEntry]
    top_guardrail: "GuardrailEntry | None"
    issue_candidates: List[IssueCandidate]
    top5_calc: List[Top5CalcRow]
    top5_final: List[Top5FinalRow]
    top5: List[Top5FinalRow]


def run_pipeline(forms_response: Dict[str, str]) -> PipelineResult:
    normalized = normalize(forms_response)
    web_kpi = compute_web_kpi(normalized)

    guardrail_entries = evaluate_guardrail(normalized["WQ-404"].raw)
    winning_guardrail = top_guardrail(guardrail_entries)

    wq001_raw = forms_response.get("WQ-001", "")
    wq501_raw = forms_response.get("WQ-501", "")
    issues = build_issue_candidates(normalized, wq001_raw, wq501_raw, web_kpi.web_dri_top5_r)

    calc_rows = compute_top5_calc(issues)
    final_rows = compute_top5_final(calc_rows)
    top5 = top5_list(final_rows)

    return PipelineResult(
        normalized=normalized,
        web_kpi=web_kpi,
        guardrail_entries=guardrail_entries,
        top_guardrail=winning_guardrail,
        issue_candidates=issues,
        top5_calc=calc_rows,
        top5_final=final_rows,
        top5=top5,
    )
