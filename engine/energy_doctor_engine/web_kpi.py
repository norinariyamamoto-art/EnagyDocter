"""Web_KPI sheet -- Web_EDI / Web_DRI / Web_EPI reference values.

Source of truth: Engine v1.4 sheet `Web_KPI`, rows 5-7 (B/C/F columns).

IMPORTANT (see Handoff Brief Rev0.3, "重要：KPIの優先関係"): these are the
*Web* simplified reference KPIs computed from the public 18-question flow.
They are explicitly NOT the formal EDI/DRI/EPI (Frozen KPI) defined in
V2.2 sheet `13_算定式・順位ロジック`, and this module must not be extended to
reproduce that sheet's formulas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .excel_compat import avg_ignore_blank, blank_ge, direct, excel_round
from .wq_normalize import NormalizedWQ


@dataclass(frozen=True)
class WebKPI:
    web_edi: float
    web_edi_band: str
    web_dri: float
    web_dri_band: str
    web_dri_top5_r: float
    web_epi: float
    web_epi_band: str


def _edi_band(value: float) -> str:
    # Web_KPI!C5
    if value >= 80:
        return "良好"
    if value >= 65:
        return "概ね良好"
    if value >= 50:
        return "注意"
    if value >= 35:
        return "要改善"
    return "要優先対応"


def _dri_band(value: float) -> str:
    # Web_KPI!C6
    if value >= 80:
        return "判断可能"
    if value >= 65:
        return "概ね判断可能"
    if value >= 50:
        return "判断準備中"
    if value >= 35:
        return "判断困難"
    return "判断保留"


def _dri_top5_r(value: float) -> float:
    # Web_KPI!F6
    if value >= 80:
        return 100
    if value >= 65:
        return 80
    if value >= 50:
        return 55
    if value >= 35:
        return 30
    return 10


def _epi_band(value: float) -> str:
    # Web_KPI!C7
    if value >= 80:
        return "最優先"
    if value >= 65:
        return "早期対応"
    if value >= 50:
        return "計画対応"
    if value >= 35:
        return "継続監視"
    return "低優先"


def compute_web_kpi(norm: Dict[str, NormalizedWQ]) -> WebKPI:
    d = {k: v.d for k, v in norm.items()}
    e = {k: v.e for k, v in norm.items()}
    c18 = norm["WQ-404"].raw

    # Web_KPI!B5 = ROUND(0.40*AVERAGE(D4:D7)+0.20*AVERAGE(D8:D9,D11)
    #                     +0.20*AVERAGE(D12:D14)+0.20*AVERAGE(D15,D17), 0)
    web_edi = excel_round(
        0.40 * avg_ignore_blank(d["WQ-101"], d["WQ-102"], d["WQ-103"], d["WQ-104"])
        + 0.20 * avg_ignore_blank(d["WQ-201"], d["WQ-202"], d["WQ-204"])
        + 0.20 * avg_ignore_blank(d["WQ-301"], d["WQ-302"], d["WQ-303"])
        + 0.20 * avg_ignore_blank(d["WQ-401"], d["WQ-403"])
    )

    # Web_KPI!B6 = ROUND(0.30*AVERAGE(D4:D5,D8:D9,D13)+0.25*AVERAGE(D6:D7,D10)
    #                     +0.20*D11+0.15*AVERAGE(D15:D17)+0.10*D17, 0)
    web_dri = excel_round(
        0.30 * avg_ignore_blank(d["WQ-101"], d["WQ-102"], d["WQ-201"], d["WQ-202"], d["WQ-302"])
        + 0.25 * avg_ignore_blank(d["WQ-103"], d["WQ-104"], d["WQ-203"])
        + 0.20 * direct(d["WQ-204"], "Web_KPI!B6 term 0.20*D11(WQ-204)")
        + 0.15 * avg_ignore_blank(d["WQ-401"], d["WQ-402"], d["WQ-403"])
        + 0.10 * direct(d["WQ-403"], "Web_KPI!B6 term 0.10*D17(WQ-403)")
    )

    # Web_KPI!B7 = ROUND(0.30*E19+0.25*AVERAGE(E6,E14)
    #                     +0.25*AVERAGE(E7,IF(C18="ない",15,IF(OR(C18="不明",C18=""),40,75)))
    #                     +0.20*IF(D11>=80,20,IF(D11>=50,60,100)), 0)
    if c18 == "ない":
        guardrail_urgency = 15
    elif c18 in ("不明", ""):
        guardrail_urgency = 40
    else:
        guardrail_urgency = 75

    if blank_ge(d["WQ-204"], 80):
        epi_wq204_term = 20
    elif blank_ge(d["WQ-204"], 50):
        epi_wq204_term = 60
    else:
        epi_wq204_term = 100

    web_epi = excel_round(
        0.30 * direct(e["WQ-405"], "Web_KPI!B7 term 0.30*E19(WQ-405)")
        + 0.25 * avg_ignore_blank(e["WQ-103"], e["WQ-303"])
        + 0.25 * avg_ignore_blank(e["WQ-104"], guardrail_urgency)
        + 0.20 * epi_wq204_term
    )

    return WebKPI(
        web_edi=web_edi,
        web_edi_band=_edi_band(web_edi),
        web_dri=web_dri,
        web_dri_band=_dri_band(web_dri),
        web_dri_top5_r=_dri_top5_r(web_dri),
        web_epi=web_epi,
        web_epi_band=_epi_band(web_epi),
    )
