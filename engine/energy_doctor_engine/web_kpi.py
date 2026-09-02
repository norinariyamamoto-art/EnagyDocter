"""Web_KPI sheet -- Web_EDI / Web_DRI / Web_EPI reference values.

Source of truth: Engine v1.4 sheet `Web_KPI`, rows 5-7 (B/C/F columns).

IMPORTANT (see Handoff Brief Rev0.3, "重要：KPIの優先関係"): these are the
*Web* simplified reference KPIs computed from the public 18-question flow.
They are explicitly NOT the formal EDI/DRI/EPI (Frozen KPI) defined in
V2.2/V2.3 sheet `13_算定式・順位ロジック`, and this module must not be
extended to reproduce that sheet's formulas.

Engine Patch 2 / ED-DI-004 Approved Disposition (S社 Design Disposition
Decision Record Rev0.1, 2026-09-02): Web_EDI's fixed weighting (設備40% /
エネルギー20% / 建屋20% / 管理20%) is confirmed unchanged here -- this module
must not alter it. Web_EDI is formally positioned as "事業所全体の総合状態を
示す参考指数" (an overall reference index for the site as a whole): by
construction, a single severely weak domain is averaged against the other
three and will not, on its own, pull Web_EDI down to a correspondingly low
number (confirmed empirically across multiple Task 2 scenarios -- see
Energy_Doctor_Design_Issue_Log.md's ED-DI-004 entry and
../task2/TASK2_REPORT.md's 提案-A). S社 explicitly declined a worst-domain
penalty and instead approved reporting per-domain status independently
alongside Web_EDI -- see domain_status.py -- so a single weak domain is
still visible to the caller even though it will not dominate Web_EDI itself.

Every value/band field below is Optional. A KPI becomes None exactly when
weighted_score() reports every one of its components blank (Unknown) -- see
excel_compat.py's weighted_score() docstring for why that is None, not a
raised exception, and for the information_sufficiency figure now reported
alongside it (Engine Patch 2 / ED-DI-003 Approved Disposition). See
pipeline.py for how these feed the pipeline's overall diagnosis_status.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .excel_compat import avg_or_none, excel_round, weighted_score
from .wq_normalize import NormalizedWQ


@dataclass(frozen=True)
class WebKPI:
    web_edi: Optional[float]
    web_edi_band: Optional[str]
    web_edi_information_sufficiency: float
    web_dri: Optional[float]
    web_dri_band: Optional[str]
    web_dri_top5_r: Optional[float]
    web_dri_information_sufficiency: float
    web_epi: Optional[float]
    web_epi_band: Optional[str]
    web_epi_information_sufficiency: float


def _edi_band(value: "float | None") -> "str | None":
    # Web_KPI!C5
    if value is None:
        return None
    if value >= 80:
        return "良好"
    if value >= 65:
        return "概ね良好"
    if value >= 50:
        return "注意"
    if value >= 35:
        return "要改善"
    return "要優先対応"


def _dri_band(value: "float | None") -> "str | None":
    # Web_KPI!C6
    if value is None:
        return None
    if value >= 80:
        return "判断可能"
    if value >= 65:
        return "概ね判断可能"
    if value >= 50:
        return "判断準備中"
    if value >= 35:
        return "判断困難"
    return "判断保留"


def _dri_top5_r(value: "float | None") -> "float | None":
    # Web_KPI!F6
    if value is None:
        return None
    if value >= 80:
        return 100
    if value >= 65:
        return 80
    if value >= 50:
        return 55
    if value >= 35:
        return 30
    return 10


def _epi_band(value: "float | None") -> "str | None":
    # Web_KPI!C7
    if value is None:
        return None
    if value >= 80:
        return "最優先"
    if value >= 65:
        return "早期対応"
    if value >= 50:
        return "計画対応"
    if value >= 35:
        return "継続監視"
    return "低優先"


def _round_or_none(value: "float | None") -> "float | None":
    return excel_round(value) if value is not None else None


def compute_web_kpi(norm: Dict[str, NormalizedWQ]) -> WebKPI:
    d = {k: v.d for k, v in norm.items()}
    e = {k: v.e for k, v in norm.items()}
    c18 = norm["WQ-404"].raw

    # Web_KPI!B5 = ROUND(0.40*AVERAGE(D4:D7)+0.20*AVERAGE(D8:D9,D11)
    #                     +0.20*AVERAGE(D12:D14)+0.20*AVERAGE(D15,D17), 0)
    # ED-DI-003 Approved Disposition: weighted_score() tolerates a fully-blank
    # AVERAGE() group (all-Unknown) by dropping that term and rescaling the
    # remaining weights, instead of Excel's #DIV/0! for AVERAGE() of nothing,
    # and reports how much of the formula's weight that rescaling relied on.
    edi_result = weighted_score(
        [
            (0.40, avg_or_none(d["WQ-101"], d["WQ-102"], d["WQ-103"], d["WQ-104"])),
            (0.20, avg_or_none(d["WQ-201"], d["WQ-202"], d["WQ-204"])),
            (0.20, avg_or_none(d["WQ-301"], d["WQ-302"], d["WQ-303"])),
            (0.20, avg_or_none(d["WQ-401"], d["WQ-403"])),
        ]
    )
    web_edi = _round_or_none(edi_result.value)

    # Web_KPI!B6 = ROUND(0.30*AVERAGE(D4:D5,D8:D9,D13)+0.25*AVERAGE(D6:D7,D10)
    #                     +0.20*D11+0.15*AVERAGE(D15:D17)+0.10*D17, 0)
    # ED-DI-003 Approved Disposition: the 0.20*D11(WQ-204) and 0.10*D17(WQ-403)
    # terms reference a single WQ_Normalize score directly (no AVERAGE
    # wrapper) -- Excel's #VALUE! when that score is blank/Unknown. Feeding
    # them through weighted_score() alongside the AVERAGE-based terms applies
    # the same "drop blank, rescale remaining weights" treatment uniformly,
    # so an Unknown WQ-204 or WQ-403 answer no longer crashes Web_DRI.
    dri_result = weighted_score(
        [
            (0.30, avg_or_none(d["WQ-101"], d["WQ-102"], d["WQ-201"], d["WQ-202"], d["WQ-302"])),
            (0.25, avg_or_none(d["WQ-103"], d["WQ-104"], d["WQ-203"])),
            (0.20, d["WQ-204"]),
            (0.15, avg_or_none(d["WQ-401"], d["WQ-402"], d["WQ-403"])),
            (0.10, d["WQ-403"]),
        ]
    )
    web_dri = _round_or_none(dri_result.value)

    # Web_KPI!B7 = ROUND(0.30*E19+0.25*AVERAGE(E6,E14)
    #                     +0.25*AVERAGE(E7,IF(C18="ない",15,IF(OR(C18="不明",C18=""),40,75)))
    #                     +0.20*IF(D11>=80,20,IF(D11>=50,60,100)), 0)
    # ISS-02: "UNKNOWN" (this module's canonical Unknown sentinel, see
    # forms_adapter.py) is added alongside "不明"/"" here so a WQ-404 answer
    # normalized from any of the three accepted Unknown spellings still takes
    # this branch, exactly as a literal "不明" already did.
    if c18 == "ない":
        guardrail_urgency = 15
    elif c18 in ("不明", "", "UNKNOWN"):
        guardrail_urgency = 40
    else:
        guardrail_urgency = 75

    # ISS-03: previously this branch relied on blank_ge()'s Excel-faithful
    # "blank text sorts above any number" quirk, which made an Unknown
    # WQ-204 silently resolve to 20 (the >=80 branch) -- a side effect of
    # comparison semantics, not a considered Unknown treatment. Made
    # explicit here as its own weighted_score() term instead, so an Unknown
    # WQ-204 drops out of Web_EPI and rescales like every other blank term,
    # consistent with how it's now handled in Web_DRI above.
    if d["WQ-204"] is None:
        epi_wq204_term = None
    elif d["WQ-204"] >= 80:
        epi_wq204_term = 20
    elif d["WQ-204"] >= 50:
        epi_wq204_term = 60
    else:
        epi_wq204_term = 100

    epi_result = weighted_score(
        [
            (0.30, e["WQ-405"]),
            (0.25, avg_or_none(e["WQ-103"], e["WQ-303"])),
            (0.25, avg_or_none(e["WQ-104"], guardrail_urgency)),
            (0.20, epi_wq204_term),
        ]
    )
    web_epi = _round_or_none(epi_result.value)

    return WebKPI(
        web_edi=web_edi,
        web_edi_band=_edi_band(web_edi),
        web_edi_information_sufficiency=edi_result.information_sufficiency,
        web_dri=web_dri,
        web_dri_band=_dri_band(web_dri),
        web_dri_top5_r=_dri_top5_r(web_dri),
        web_dri_information_sufficiency=dri_result.information_sufficiency,
        web_epi=web_epi,
        web_epi_band=_epi_band(web_epi),
        web_epi_information_sufficiency=epi_result.information_sufficiency,
    )
