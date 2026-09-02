"""Issue_Candidate sheet -- 16 candidate issues feeding TOP5_Calc.

Source of truth: Engine v1.4 sheet `Issue_Candidate`, rows 4-19 (columns
E..L = I/U/P/R/C/O/Guard加算/発火). Each function below corresponds to one
row and is commented with its exact source formula. Column letters in the
comments are Issue_Candidate's own (E=I, F=U, G=P, H=R, I=C, J=O, K=Guard加算,
L=発火) -- not to be confused with this module's Python variable names.

ED-DI-002 Approved: this module's `main_wq` field is the same public-WQ
identity used by V2.3 sheet `77_WQ-Q_Traceability` (now the formal
WQ-ID<->Q-ID mapping authority). That mapping does not change anything here
-- per the Traceability sheet's own header note, public WQ answers are never
auto-generated or transcribed into individual formal Q-ID answers, so this
module continues to score `main_wq` against its own public-WQ-only rules.
See review_items.py, which uses `main_wq` (and issue_id, for BL-03's
two-WQ case) purely to explain *why* an issue didn't fire when the reason is
an Unknown answer -- it does not feed anything back into scoring here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .excel_compat import blank_eq, blank_ge, blank_lt, excel_search
from .wq_normalize import NormalizedWQ

ISSUE_FIELD_EQUIPMENT = "設備"
ISSUE_FIELD_ENERGY = "エネルギー"
ISSUE_FIELD_BUILDING = "建屋"
ISSUE_FIELD_MANAGEMENT = "管理"
ISSUE_FIELD_GUARDRAIL = "Guardrail"
ISSUE_FIELD_CUSTOM = "個別"


@dataclass(frozen=True)
class IssueCandidate:
    issue_id: str
    field: str
    name: str
    main_wq: str
    i: float  # Impact
    u: Optional[float]  # Urgency (WQ_Normalize!E19 -- blank if WQ-405 is Unknown)
    p: float  # Probability/state
    r: Optional[float]  # Risk (Web_DRI's TOP5用R -- see build_issue_candidates)
    c: float  # Confidence/evidence
    o: float  # Opportunity
    guard_add: float
    fire: int


def build_issue_candidates(
    norm: Dict[str, NormalizedWQ],
    wq001_raw: str,
    wq501_raw: str,
    web_dri_top5_r: Optional[float],
) -> List[IssueCandidate]:
    d = {k: v.d for k, v in norm.items()}
    c = {k: v.raw for k, v in norm.items()}
    g = {k: v.evidence_c for k, v in norm.items()}
    e19 = norm["WQ-405"].e  # WQ_Normalize!E19, the cross-cutting urgency factor
    r = web_dri_top5_r  # Web_KPI!F6, referenced by every issue's H(R) column

    wants_energy_saving = excel_search("省エネ", wq001_raw)  # SEARCH("省エネ",Forms_Response!E4)

    issues: List[IssueCandidate] = []

    # IS-01 主要設備の年式・更新履歴整理 (Issue_Candidate row4)
    issues.append(
        IssueCandidate(
            "IS-01", ISSUE_FIELD_EQUIPMENT, "主要設備の年式・更新履歴整理", "WQ-101",
            i=40, u=e19, p=(40 if blank_eq(d["WQ-101"], 60) else 75 if blank_eq(d["WQ-101"], 20) else 0),
            r=r, c=g["WQ-101"], o=60, guard_add=0,
            fire=1 if blank_lt(d["WQ-101"], 100) else 0,
        )
    )
    # IS-02 故障・停止履歴の整理と傾向確認 (row5)
    issues.append(
        IssueCandidate(
            "IS-02", ISSUE_FIELD_EQUIPMENT, "故障・停止履歴の整理と傾向確認", "WQ-102",
            i=40, u=e19, p=(40 if blank_eq(d["WQ-102"], 60) else 75 if blank_eq(d["WQ-102"], 20) else 0),
            r=r, c=g["WQ-102"], o=60, guard_add=0,
            fire=1 if blank_lt(d["WQ-102"], 100) else 0,
        )
    )
    # IS-03 重要設備停止時の代替手段確認 (row6)
    c103 = c["WQ-103"]
    issues.append(
        IssueCandidate(
            "IS-03", ISSUE_FIELD_EQUIPMENT, "重要設備停止時の代替手段確認", "WQ-103",
            i=(75 if c103 == "ない" else 40),
            u=e19,
            p=(75 if c103 == "ない" else 40 if c103 == "一部ある" else 0),
            r=r, c=g["WQ-103"], o=60,
            guard_add=(5 if c103 == "ない" else 0),
            fire=1 if c103 in ("一部ある", "ない") else 0,
        )
    )
    # IS-04 EOL・部品供給状況の確認 (row7)
    c104 = c["WQ-104"]
    issues.append(
        IssueCandidate(
            "IS-04", ISSUE_FIELD_EQUIPMENT, "EOL・部品供給状況の確認", "WQ-104",
            i=40, u=e19,
            p=(75 if c104 == "未確認" else 40 if c104 == "一部確認" else 0),
            r=r, c=g["WQ-104"], o=60,
            guard_add=(5 if c104 == "未確認" else 0),
            fire=1 if c104 in ("一部確認", "未確認") else 0,
        )
    )
    # EN-01 電力使用量・デマンド管理の高度化 (row8)
    issues.append(
        IssueCandidate(
            "EN-01", ISSUE_FIELD_ENERGY, "電力使用量・デマンド管理の高度化", "WQ-201",
            i=40, u=e19,
            p=(40 if blank_eq(d["WQ-201"], 70) else 75 if blank_eq(d["WQ-201"], 35) else 100 if blank_eq(d["WQ-201"], 10) else 0),
            r=r, c=g["WQ-201"], o=(100 if wants_energy_saving else 60), guard_add=0,
            fire=1 if blank_lt(d["WQ-201"], 100) else 0,
        )
    )
    # EN-02 設備・工程別エネルギー使用の把握 (row9)
    issues.append(
        IssueCandidate(
            "EN-02", ISSUE_FIELD_ENERGY, "設備・工程別エネルギー使用の把握", "WQ-202",
            i=40, u=e19,
            p=(40 if blank_eq(d["WQ-202"], 60) else 75 if blank_eq(d["WQ-202"], 30) else 100 if blank_eq(d["WQ-202"], 10) else 0),
            r=r, c=g["WQ-202"], o=(100 if wants_energy_saving else 60), guard_add=0,
            fire=1 if blank_lt(d["WQ-202"], 100) else 0,
        )
    )
    # EN-03 電力異常時の原因特定体制 (row10)
    issues.append(
        IssueCandidate(
            "EN-03", ISSUE_FIELD_ENERGY, "電力異常時の原因特定体制", "WQ-203",
            i=40, u=e19,
            p=(40 if blank_eq(d["WQ-203"], 60) else 75 if blank_eq(d["WQ-203"], 20) else 0),
            r=r, c=g["WQ-203"], o=60, guard_add=0,
            fire=1 if blank_lt(d["WQ-203"], 100) else 0,
        )
    )
    # EN-04 省エネ改善テーマと効果検証の整理 (row11)
    issues.append(
        IssueCandidate(
            "EN-04", ISSUE_FIELD_ENERGY, "省エネ改善テーマと効果検証の整理", "WQ-204",
            i=40, u=e19,
            p=(30 if blank_eq(d["WQ-204"], 60) else 60 if blank_eq(d["WQ-204"], 35) else 75 if blank_eq(d["WQ-204"], 20) else 15),
            r=r, c=g["WQ-204"], o=(100 if wants_energy_saving else 60), guard_add=0,
            fire=1 if blank_lt(d["WQ-204"], 100) else 0,
        )
    )
    # BL-01 建屋・環境課題の確認 (row12) -- I/P reference WQ-303's answer (C14), not WQ-301's.
    c301 = c["WQ-301"]
    c303 = c["WQ-303"]
    issues.append(
        IssueCandidate(
            "BL-01", ISSUE_FIELD_BUILDING, "建屋・環境課題の確認", "WQ-301",
            i=(100 if c303 == "明確な影響あり" else 75 if c303 == "影響の可能性" else 40),
            u=e19,
            p=(75 if c303 == "明確な影響あり" else 40),
            r=r, c=g["WQ-301"], o=60, guard_add=0,
            # ISS-02/03: "UNKNOWN" (forms_adapter.py's canonical sentinel for
            # 不明/分からない/blank) must be excluded here exactly like the
            # original formula excludes a literal "不明", or an Unknown
            # WQ-301 answer would incorrectly fire this issue.
            fire=1 if (c301 != "特になし" and c301 != "不明" and c301 != "UNKNOWN") else 0,
        )
    )
    # BL-02 建屋点検・修繕優先順位の整理 (row13)
    issues.append(
        IssueCandidate(
            "BL-02", ISSUE_FIELD_BUILDING, "建屋点検・修繕優先順位の整理", "WQ-302",
            i=(100 if c303 == "明確な影響あり" else 75),
            u=e19,
            p=(40 if blank_eq(d["WQ-302"], 60) else 75 if blank_eq(d["WQ-302"], 20) else 0),
            r=r, c=g["WQ-302"], o=60, guard_add=0,
            fire=1 if blank_lt(d["WQ-302"], 100) else 0,
        )
    )
    # BL-03 建屋環境による品質・操業影響の優先確認 (row14)
    c18 = c["WQ-404"]
    issues.append(
        IssueCandidate(
            "BL-03", ISSUE_FIELD_BUILDING, "建屋環境による品質・操業影響の優先確認", "WQ-301+303",
            i=(100 if c303 == "明確な影響あり" else 75),
            u=e19,
            p=(75 if c303 == "明確な影響あり" else 60),
            r=r, c=min(g["WQ-301"], g["WQ-303"]), o=60,
            guard_add=(12 if (excel_search("安全", c18) or excel_search("品質", c18)) else 0),
            fire=1 if (c301 != "特になし" and c303 in ("明確な影響あり", "影響の可能性")) else 0,
        )
    )
    # MG-01 部門横断の課題管理体制整備 (row15)
    issues.append(
        IssueCandidate(
            "MG-01", ISSUE_FIELD_MANAGEMENT, "部門横断の課題管理体制整備", "WQ-401",
            i=40, u=e19,
            p=(40 if blank_eq(d["WQ-401"], 60) else 75 if blank_eq(d["WQ-401"], 20) else 0),
            r=r, c=g["WQ-401"], o=60, guard_add=0,
            fire=1 if blank_lt(d["WQ-401"], 100) else 0,
        )
    )
    # MG-02 設備投資の共通優先順位基準の整備 (row16)
    issues.append(
        IssueCandidate(
            "MG-02", ISSUE_FIELD_MANAGEMENT, "設備投資の共通優先順位基準の整備", "WQ-402",
            i=40, u=e19,
            p=(40 if blank_eq(d["WQ-402"], 70) else 60 if blank_eq(d["WQ-402"], 35) else 75 if blank_eq(d["WQ-402"], 20) else 0),
            r=r, c=g["WQ-402"], o=60, guard_add=0,
            fire=1 if blank_lt(d["WQ-402"], 100) else 0,
        )
    )
    # MG-03 3年間の設備・建屋更新ロードマップ整理 (row17)
    issues.append(
        IssueCandidate(
            "MG-03", ISSUE_FIELD_MANAGEMENT, "3年間の設備・建屋更新ロードマップ整理", "WQ-403",
            i=40, u=e19,
            p=(30 if blank_eq(d["WQ-403"], 70) else 60 if blank_eq(d["WQ-403"], 40) else 75 if blank_eq(d["WQ-403"], 20) else 0),
            r=r, c=g["WQ-403"], o=(100 if blank_ge(norm["WQ-405"].e, 75) else 60),
            guard_add=0,
            fire=1 if blank_lt(d["WQ-403"], 100) else 0,
        )
    )
    # GR-01 安全・法令・品質・供給継続の未解決事項確認 (row18)
    issues.append(
        IssueCandidate(
            "GR-01", ISSUE_FIELD_GUARDRAIL, "安全・法令・品質・供給継続の未解決事項確認", "WQ-404",
            i=(100 if (excel_search("安全", c18) or excel_search("法令", c18))
               else 75 if (excel_search("品質", c18) or excel_search("供給継続", c18))
               else 0),
            u=e19,
            p=(0 if c18 == "ない" else 75),
            r=r, c=g["WQ-404"], o=60,
            guard_add=(0 if c18 == "ない" else 12),
            # ISS-02/03: add "UNKNOWN" alongside the original "不明"/""
            # exclusions -- an Unknown WQ-404 answer must not fire this
            # Guardrail-derived issue any more than a literal "不明" already
            # didn't.
            fire=1 if (c18 != "ない" and c18 != "不明" and c18 != "" and c18 != "UNKNOWN") else 0,
        )
    )
    # CU-01 顧客固有課題のヒアリング (row19)
    issues.append(
        IssueCandidate(
            "CU-01", ISSUE_FIELD_CUSTOM, "顧客固有課題のヒアリング", "WQ-501",
            i=40, u=e19, p=40, r=r,
            c=(70 if wq501_raw != "" else 35),
            o=60, guard_add=0,
            fire=1 if wq501_raw != "" else 0,
        )
    )

    return issues
