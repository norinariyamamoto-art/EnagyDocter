"""WQ_Normalize sheet, transcribed formula-for-formula.

Source of truth: 02_Diagnosis_Engine/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx
sheet `WQ_Normalize`, rows 4-19 (WQ-101..WQ-405). Each WQ's 状態Score (D) /
緊急Score (E) formula is copied below with the exact Japanese answer strings
used in the IF() chains -- these are the strings the engine's Forms_Response
input must contain (see Issue ISS-03 in ../ISSUES.md re: the separately
published Microsoft Forms wording not matching these strings verbatim).

WQ-001 and WQ-501 are not part of this sheet; they are read directly from
Forms_Response elsewhere (Issue_Candidate J-column SEARCH on WQ-001, and the
CU-01 free-text presence check on WQ-501).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

UNKNOWN_VALUES = {"不明", "", "UNKNOWN"}
"""Corrective Patch 1 / ISS-02: "UNKNOWN" is the canonical sentinel produced
by forms_adapter.normalize_forms_response() for any of "不明" / "分からない" /
a blank answer. "不明" and "" are kept here too so this module still behaves
correctly if called directly with raw Japanese text, bypassing the adapter
(e.g. existing Task 1A tests/fixtures)."""

# WQ_Normalize!D4:D19 -- answer text -> 状態Score. A key absent from a WQ's
# table (e.g. an unrecognized answer) reproduces the Excel IF-chain's final
# "" branch, i.e. None here.
_D_TABLES: Dict[str, Dict[str, float]] = {
    "WQ-101": {"把握している": 100, "一部把握": 60, "ほとんど把握していない": 20},
    "WQ-102": {"定期的に確認": 100, "記録のみ": 60, "記録なし": 20},
    "WQ-103": {"十分ある": 100, "一部ある": 60, "ない": 0},
    "WQ-104": {"定期確認": 100, "一部確認": 60, "未確認": 20},
    "WQ-201": {"毎月確認": 100, "年数回確認": 70, "請求額のみ": 35, "未確認": 10},
    "WQ-202": {"詳細に把握": 100, "一部把握": 60, "全体のみ": 30, "未把握": 10},
    "WQ-203": {"迅速に確認": 100, "時間をかければ確認": 60, "困難": 20},
    "WQ-204": {"複数実施": 100, "一部実施": 60, "検討のみ": 35, "未実施": 20},
    # WQ-301: handled specially below (D=100 only for "特になし").
    "WQ-302": {"定期点検": 100, "問題時のみ": 60, "ほとんど未確認": 20},
    "WQ-303": {"明確な影響あり": 25, "影響の可能性": 65, "影響なし": 100},
    "WQ-401": {"明確にある": 100, "一部ある": 60, "ない": 20},
    "WQ-402": {"明文化済み": 100, "慣例で判断": 70, "担当者ごと": 35, "基準なし": 20},
    "WQ-403": {"予算付き計画あり": 100, "計画のみ": 70, "案件ごと": 40, "計画なし": 20},
    # WQ-404: no D formula (Guardrail-only; raw text kept as-is).
    # WQ-405: no D formula (EPI-only via E, below).
}

# WQ_Normalize!E4:E19 -- answer text -> 緊急Score.
_E_TABLES: Dict[str, Dict[str, float]] = {
    "WQ-103": {"十分ある": 15, "一部ある": 40, "ない": 75},
    "WQ-104": {"定期確認": 15, "一部確認": 40, "未確認": 75},
    "WQ-303": {"明確な影響あり": 100, "影響の可能性": 75, "影響なし": 15},
    "WQ-405": {"3か月以内": 100, "6か月以内": 75, "1年以内": 75, "時期未定": 20},
}

NORMALIZE_ORDER = [
    "WQ-101", "WQ-102", "WQ-103", "WQ-104",
    "WQ-201", "WQ-202", "WQ-203", "WQ-204",
    "WQ-301", "WQ-302", "WQ-303",
    "WQ-401", "WQ-402", "WQ-403", "WQ-404", "WQ-405",
]


@dataclass(frozen=True)
class NormalizedWQ:
    wq_id: str
    raw: str
    d: Optional[float]
    e: Optional[float]
    unknown: int
    evidence_c: float


def normalize(forms_response: Dict[str, str]) -> Dict[str, NormalizedWQ]:
    result: Dict[str, NormalizedWQ] = {}
    for wq_id in NORMALIZE_ORDER:
        raw = forms_response.get(wq_id, "")
        # WQ_Normalize!F -- Unknown flag: --(OR(C="不明",C=""))
        unknown = 1 if raw in UNKNOWN_VALUES else 0
        # WQ_Normalize!G -- Evidence C: IF(F=1,35,70)
        evidence_c = 35.0 if unknown == 1 else 70.0

        if wq_id == "WQ-301":
            # WQ_Normalize!D12: IF(C="特になし",100,IF(OR(C="不明",C=""),"",60))
            if raw == "特になし":
                d = 100.0
            elif raw in UNKNOWN_VALUES:
                d = None
            else:
                d = 60.0
            e = None
        else:
            d = _D_TABLES.get(wq_id, {}).get(raw)
            e = _E_TABLES.get(wq_id, {}).get(raw)

        result[wq_id] = NormalizedWQ(
            wq_id=wq_id, raw=raw, d=d, e=e, unknown=unknown, evidence_c=evidence_c
        )
    return result
