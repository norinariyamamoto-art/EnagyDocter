"""TOP5_Final sheet -- final TOP5 selection after dedup (TOP-R02) and
same-field-max-2 capping (TOP-R03).

Source of truth: Engine v1.4 sheet `TOP5_Final`, rows 4-18 (15 rows).
TOP_SCORE values are not recalculated here (TOP5_Final!A2: "既存TOP_SCOREを
変更せず") -- only structural merging and eligibility are applied on top of
TOP5_Calc's output:

  - EQ-03 replaces IS-03/IS-04 as a single row: Score = MAX of whichever of
    the two fired (TOP5_Final!E6).
  - BL-01 is suppressed outright whenever BL-03 also qualifies (Score>=35):
    TOP5_Final!H11 special-cases BL-01, unlike every other row's default
    candidacy rule. This is the one place TOP-R02 (dedup) is encoded as a
    conditional rather than a row merge -- see ISSUES.md ISS-05.
  - TOP-R03 (max 2 candidates per field) is enforced via a per-field rank
    (G column, ties share a rank) filtered to <=2, with 安全・法令
    (field="Guardrail") exempted from the cap entirely.
  - Final rank (I column) breaks ties by TiePriority (K column: Guardrail=1,
    everything else=2) before falling back to original row order.

Corrective Patch 1 / ISS-06: the G-column field rank above is a direct port
of TOP5_Final!G's own formula, `COUNTIFS(field, score>own)+1` -- and that
formula only counts *strictly greater* scores, so when 3+ rows in the same
non-Guardrail field are tied, every one of them gets the same field_rank
(e.g. rank 2), and all of them pass the "<=2" candidacy check. That
reproduces the workbook's formula exactly, but it lets more than 2 same-field
candidates through the H column when there's a tie -- undermining TOP-R03's
own "same-field max 2" rule (TOP5_Final!A2) in exactly the tie scenario the
rule exists for. `_enforce_field_cap` below is a second pass applied strictly
*after* the (unmodified) per-row eligibility above: for any non-Guardrail
field where more than 2 rows are eligible, only the top 2 -- ranked by score
descending, then TiePriority, then original sheet order, the same tie-break
already used for the real Final Rank below -- are kept eligible; the rest
are demoted. This does not change field_rank, TiePriority, TOP_SCORE, the
Guardrail exemption, or the BL-01/BL-03 special case above; it only adds a
final cap-enforcement step for the specific case those existing rules don't
already resolve on their own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .top5_calc import Top5CalcRow

# TOP5_Final row order exactly as in the sheet (rows 4-18).
_ROW_ORDER = [
    ("EQ-01", "設備", "主要設備の年式・更新履歴整理", ["IS-01"]),
    ("EQ-02", "設備", "故障・停止履歴の整理と傾向確認", ["IS-02"]),
    ("EQ-03", "設備", "重要設備のEOL・復旧リスク確認", ["IS-03", "IS-04"]),
    ("EN-01", "エネルギー", "電力使用量・デマンド管理の高度化", ["EN-01"]),
    ("EN-02", "エネルギー", "設備・工程別エネルギー使用の把握", ["EN-02"]),
    ("EN-03", "エネルギー", "電力異常時の原因特定体制", ["EN-03"]),
    ("EN-04", "エネルギー", "省エネ改善テーマと効果検証の整理", ["EN-04"]),
    ("BL-01", "建屋", "建屋・環境課題の確認", ["BL-01"]),
    ("BL-02", "建屋", "建屋点検・修繕優先順位の整理", ["BL-02"]),
    ("BL-03", "建屋", "建屋環境による品質・操業影響の優先確認", ["BL-03"]),
    ("MG-01", "管理", "部門横断の課題管理体制整備", ["MG-01"]),
    ("MG-02", "管理", "設備投資の共通優先順位基準の整備", ["MG-02"]),
    ("MG-03", "管理", "3年間の設備・建屋更新ロードマップ整理", ["MG-03"]),
    ("GR-01", "Guardrail", "安全・法令・品質・供給継続の未解決事項確認", ["GR-01"]),
    ("CU-01", "個別", "顧客固有課題のヒアリング", ["CU-01"]),
]


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


@dataclass(frozen=True)
class Top5FinalRow:
    candidate_id: str
    field: str
    name: str
    source_issues: List[str]
    score: float
    band: str
    field_rank: int
    eligible: bool
    final_rank: "int | None"
    is_top5: bool
    tie_priority: int


_FIELD_CAP = 2


def _enforce_field_cap(base_rows: List[dict]) -> None:
    """Corrective Patch 1 / ISS-06: cap each non-Guardrail field at
    _FIELD_CAP eligible rows even when 3+ rows tie for the field's rank
    boundary. Mutates each row's "eligible" in place; already-ineligible
    rows (score<35, BL-01 suppressed by BL-03, etc.) are left untouched."""
    by_field: Dict[str, List[dict]] = {}
    for row in base_rows:
        if row["eligible"] and row["field"] != "Guardrail":
            by_field.setdefault(row["field"], []).append(row)

    for rows in by_field.values():
        if len(rows) <= _FIELD_CAP:
            continue
        # Same tie-break the real Final Rank uses: score desc, then
        # TiePriority asc, then original sheet order (rows is already in
        # sheet order, and Python's sort is stable, so a plain sort on
        # (-score, tie_priority) preserves that order for any remaining tie).
        ranked = sorted(rows, key=lambda r: (-r["score"], r["tie_priority"]))
        for demoted in ranked[_FIELD_CAP:]:
            demoted["eligible"] = False


def compute_top5_final(calc_rows: List[Top5CalcRow]) -> List[Top5FinalRow]:
    by_id: Dict[str, Top5CalcRow] = {r.issue_id: r for r in calc_rows}

    base_rows = []
    for candidate_id, field, name, sources in _ROW_ORDER:
        if len(sources) == 1:
            src = by_id[sources[0]]
            score = src.top_score if src.fire == 1 else 0
        else:
            # EQ-03: MAX(IF(fire3,score3,0), IF(fire4,score4,0))
            score = max(
                by_id[s].top_score if by_id[s].fire == 1 else 0 for s in sources
            )
        base_rows.append(
            {
                "candidate_id": candidate_id,
                "field": field,
                "name": name,
                "sources": sources,
                "score": score,
                "band": _band(score),
                "tie_priority": 1 if field == "Guardrail" else 2,
            }
        )

    scores_by_field: Dict[str, List[float]] = {}
    for row in base_rows:
        scores_by_field.setdefault(row["field"], []).append(row["score"])

    bl03_score = next(r["score"] for r in base_rows if r["candidate_id"] == "BL-03")

    for row in base_rows:
        # G column: COUNTIFS(field members, score > own) + 1
        field_scores = scores_by_field[row["field"]]
        row["field_rank"] = sum(1 for s in field_scores if s > row["score"]) + 1

        # H column (candidacy)
        if row["score"] < 35:
            row["eligible"] = False
        elif row["candidate_id"] == "BL-01":
            # TOP5_Final!H11: suppressed whenever BL-03 also qualifies.
            if bl03_score >= 35:
                row["eligible"] = False
            else:
                row["eligible"] = row["field_rank"] <= 2
        elif row["field"] == "Guardrail":
            row["eligible"] = True
        else:
            row["eligible"] = row["field_rank"] <= 2

    _enforce_field_cap(base_rows)

    eligible_rows = [r for r in base_rows if r["eligible"]]
    for row in base_rows:
        if not row["eligible"]:
            row["final_rank"] = None
            continue
        score = row["score"]
        tie = row["tie_priority"]
        greater = sum(1 for r in eligible_rows if r["score"] > score)
        better_tie = sum(1 for r in eligible_rows if r["score"] == score and r["tie_priority"] < tie)
        # Stable tie-break: count same-score/same-tie-priority rows up to and
        # including this one, in original sheet order.
        cumulative = 0
        for r in base_rows:
            if r["score"] == score and r["tie_priority"] == tie and r["eligible"]:
                cumulative += 1
            if r is row:
                break
        row["final_rank"] = greater + better_tie + cumulative

    return [
        Top5FinalRow(
            candidate_id=row["candidate_id"],
            field=row["field"],
            name=row["name"],
            source_issues=row["sources"],
            score=row["score"],
            band=row["band"],
            field_rank=row["field_rank"],
            eligible=row["eligible"],
            final_rank=row["final_rank"],
            is_top5=bool(row["eligible"] and row["final_rank"] is not None and row["final_rank"] <= 5),
            tie_priority=row["tie_priority"],
        )
        for row in base_rows
    ]


def top5_list(final_rows: List[Top5FinalRow]) -> List[Top5FinalRow]:
    top5 = [r for r in final_rows if r.is_top5]
    return sorted(top5, key=lambda r: r.final_rank)
