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

Issue_Candidate's U column (`WQ_Normalize!E19`, WQ-405's urgency score) is a
*direct* reference shared by all 16 issues, not wrapped in AVERAGE() -- so an
Unknown WQ-405 makes `iss.u` blank for every single issue at once, and the
naive `0.25*iss.u` term would be Excel's #VALUE! (and was a Python TypeError
here, in Corrective Patch 1) for all of them simultaneously.

Engine Patch 2 / ED-DI-003 point 5 (S社 Design Disposition Decision Record
Rev0.1, 2026-09-02; see Energy_Doctor_Design_Issue_Log.md's ED-DI-003
"Approved Disposition" and V2.3 sheet `78_Web診断Disposition` row 6):
**unlike Web_KPI's formulas, TOP_BASE deliberately does NOT renormalize when
U is blank.** Corrective Patch 1 originally routed this through the same
weighted_score() used for Web_EDI/DRI/EPI, but S社's disposition on
Issue_Candidate's U specifically rejected that: "Unknownはスコアに加算せず"
(an Unknown contributes nothing to the score) rather than having the other
five weights (I/P/R/C/O) rescaled to compensate. A blank U term is instead
substituted with 0 -- weights stay exactly 0.30/0.25/0.20/0.10/0.10/0.05, so
an issue whose urgency input is Unknown does not get a boosted TOP_BASE from
renormalization, and this issue's own resolution of that Unknown (whether it
should be flagged rather than silently scored at all) is delegated to
ED-DI-005's review_items (see review_items.py) rather than handled here.
I/P/R/C/O never carry a blank value by construction (see issue_candidate.py
and web_kpi.py's web_dri_top5_r, which the pipeline already guarantees is
concrete before TOP5_Calc runs), so 0-substitution is needed only for U, and
this formula can no longer raise or return None.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .excel_compat import excel_round
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
        # ED-DI-003 point 5: U substituted with 0 when Unknown, weights
        # otherwise untouched (no renormalization) -- see module docstring.
        u = iss.u if iss.u is not None else 0
        base = excel_round(
            0.30 * iss.i + 0.25 * u + 0.20 * iss.p + 0.10 * iss.r + 0.10 * iss.c + 0.05 * iss.o,
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
