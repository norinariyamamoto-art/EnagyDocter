"""TOP5_Calc sheet -- baseline scoring before dedup/field-cap post-processing.

Source of truth: Engine v1.4 sheet `TOP5_Calc`, rows 4-19.
TOP_BASE = 0.30I + 0.25U + 0.20P + 0.10R + 0.10C + 0.05O (TOP5_Calc!A2).
TOP_SCORE = MIN(100, TOP_BASE + Guard加算).

Note the rank formula here (I column) ranks over ALL 16 rows regardless of
発火(fire) status -- a high-scoring but unfired issue still occupies a rank
slot. Fire is only consulted afterwards for the "TOP5対象" flag (J column).
This differs from TOP5_Final's rank, which ranks only among post-dedup
candidates (see top5_final.py) -- see ISSUES.md ISS-06 for the resulting
edge case this can cause.

Corrective Patch 1 / ISS-03: Issue_Candidate's U column (`WQ_Normalize!E19`,
WQ-405's urgency score) is a *direct* reference shared by all 16 issues, not
wrapped in AVERAGE() -- so an Unknown WQ-405 makes `iss.u` blank for every
single issue, and the naive `0.25*iss.u` term would be Excel's #VALUE! (and
was a Python TypeError here) for all of them simultaneously. TOP_BASE is
computed via weighted_score() below for the same reason Web_KPI's formulas
are (see web_kpi.py) -- this is the only place besides Web_KPI where a
directly-referenced WQ_Normalize value flows into a weighted formula.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .excel_compat import excel_round, weighted_score
from .issue_candidate import IssueCandidate


@dataclass(frozen=True)
class Top5CalcRow:
    issue_id: str
    field: str
    name: str
    top_base: float
    guard_add: float
    top_score: float
    band: str
    fire: int
    rank: "int | None"
    is_top5: bool


def _band(score: float) -> str:
    if score >= 80:
        return "S"
    if score >= 65:
        return "A"
    if score >= 50:
        return "B"
    if score >= 35:
        return "C"
    return "詳細のみ"


def compute_top5_calc(issues: List[IssueCandidate]) -> List[Top5CalcRow]:
    bases = []
    scores = []
    for iss in issues:
        base = excel_round(
            weighted_score(
                [
                    (0.30, iss.i),
                    (0.25, iss.u),
                    (0.20, iss.p),
                    (0.10, iss.r),
                    (0.10, iss.c),
                    (0.05, iss.o),
                ]
            ),
            1,
        )
        score = min(100, base + iss.guard_add)
        bases.append(base)
        scores.append(score)

    rows: List[Top5CalcRow] = []
    for idx, iss in enumerate(issues):
        score = scores[idx]
        if iss.fire == 1:
            # RANK.EQ(F,$F$4:$F$19,0) + COUNTIF($F$4:F,F) - 1
            greater = sum(1 for s in scores if s > score)
            cumulative_ties = sum(1 for j in range(0, idx + 1) if scores[j] == score)
            rank = greater + cumulative_ties
        else:
            rank = None
        is_top5 = bool(iss.fire == 1 and rank is not None and rank <= 5)
        rows.append(
            Top5CalcRow(
                issue_id=iss.issue_id,
                field=iss.field,
                name=iss.name,
                top_base=bases[idx],
                guard_add=iss.guard_add,
                top_score=score,
                band=_band(score),
                fire=iss.fire,
                rank=rank,
                is_top5=is_top5,
            )
        )
    return rows
