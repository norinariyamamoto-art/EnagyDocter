"""要確認事項 (review items) -- Engine Patch 2 / ED-DI-005 point 1.

S社 Design Disposition Decision Record Rev0.1 (2026-09-02): an Unknown
answer must not simply vanish from the diagnosis. Before this patch, an
Issue_Candidate whose driving WQ was Unknown just failed its existing fire
condition (e.g. IS-04's `fire=1 if c104 in ("一部確認","未確認") else 0` is
False for "UNKNOWN") and disappeared -- observed concretely in
../task2/TASK2_REPORT.md's SIM-01 (IS-04, MG-02) and SIM-03 (MG-02). ED-DI-005
approved surfacing that same "didn't fire because Unknown" case as an
explicit "要確認事項" (needs confirmation) entry instead of silence, without
changing issue_candidate.py's fire conditions themselves ("既存の
issue_candidate.pyのロジックは壊さず" -- this module only re-reads their
result, never feeds back into scoring).

Display hierarchy (ED-DI-005, V2.3 sheet `78_Web診断Disposition` row 8):
Guardrail -> 要確認事項 (this module's output) -> TOP5. See pipeline.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .issue_candidate import IssueCandidate
from .wq_normalize import NormalizedWQ

# CU-01 (main_wq="WQ-501") is intentionally excluded: WQ-501 is optional free
# text, not one of WQ_Normalize's 16 scored questions (it has no Unknown
# choice and isn't in `normalized`), and per V2.3 sheet
# `77_WQ-Q_Traceability` row for WQ-501, "自由記述は正式Q回答ではなく...
# KPI/TOP5へ直接採点しない" -- there is no Unknown-vs-answered distinction to
# surface for it.


@dataclass(frozen=True)
class ReviewItem:
    issue_id: str
    field: str
    name: str
    reason_wq: "tuple[str, ...]"
    """The WQ_Normalize-scored WQ(s) that are Unknown and caused this issue
    not to fire (e.g. ("WQ-104",); BL-03 can have more than one, e.g.
    ("WQ-301", "WQ-303"))."""


def _main_wqs(issue: IssueCandidate) -> "list[str]":
    # IssueCandidate.main_wq is usually a single WQ ("WQ-104"); BL-03 encodes
    # two as "WQ-301+303" (see issue_candidate.py) -- normalize both shapes.
    parts = issue.main_wq.split("+")
    return [p if p.startswith("WQ-") else f"WQ-{p}" for p in parts]


def compute_review_items(
    issues: "List[IssueCandidate]", normalized: Dict[str, NormalizedWQ]
) -> "List[ReviewItem]":
    items: List[ReviewItem] = []
    for issue in issues:
        if issue.fire == 1:
            continue
        unknown_wqs = tuple(
            wq
            for wq in _main_wqs(issue)
            if wq in normalized and normalized[wq].unknown == 1
        )
        if unknown_wqs:
            items.append(
                ReviewItem(
                    issue_id=issue.issue_id,
                    field=issue.field,
                    name=issue.name,
                    reason_wq=unknown_wqs,
                )
            )
    return items
