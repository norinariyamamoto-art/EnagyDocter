"""分野別状態 (per-domain status) -- Engine Patch 2 / ED-DI-004.

S社 Design Disposition Decision Record Rev0.1 (2026-09-02) confirmed Web_EDI's
fixed weighting (設備40% / エネルギー20% / 建屋20% / 管理20%) unchanged, and
positioned Web_EDI itself as "事業所全体の総合状態を示す参考指数" -- by
construction, a single severely weak domain will not pull that composite
number down by much (see web_kpi.py's module docstring and
Energy_Doctor_Design_Issue_Log.md's ED-DI-004 entry, evidenced empirically in
../task2/TASK2_REPORT.md across SIM-01/03/04). Rather than introduce a
worst-domain penalty into Web_EDI itself (explicitly declined), S社 approved
reporting each domain's own status independently, so a single weak domain
stays visible to the caller even though it will not dominate Web_EDI.

This module recomputes the same four domain sub-averages Web_EDI's own
formula already builds internally (see web_kpi.py's compute_web_kpi: the
`avg_or_none(...)` call feeding each of Web_EDI's four weighted terms), as a
standalone, independent output rather than a private intermediate value of
Web_EDI's computation. The WQ groupings and the "ignore blank, average over
what's left" treatment are identical to Web_EDI's; only the output shape
differs (four independent numbers instead of one composite). This module
does not alter Web_EDI's own weights or formula in any way.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .excel_compat import avg_or_none, excel_round
from .wq_normalize import NormalizedWQ


@dataclass(frozen=True)
class DomainStatus:
    equipment: Optional[float]  # 設備: WQ-101,102,103,104 (Web_EDI's own 40% group)
    energy: Optional[float]  # エネルギー: WQ-201,202,204 (Web_EDI's own 20% group)
    building: Optional[float]  # 建屋: WQ-301,302,303 (Web_EDI's own 20% group)
    management: Optional[float]  # 管理: WQ-401,403 (Web_EDI's own 20% group)


def _round_or_none(value: "float | None") -> "float | None":
    return excel_round(value) if value is not None else None


def compute_domain_status(norm: Dict[str, NormalizedWQ]) -> DomainStatus:
    d = {k: v.d for k, v in norm.items()}
    return DomainStatus(
        equipment=_round_or_none(
            avg_or_none(d["WQ-101"], d["WQ-102"], d["WQ-103"], d["WQ-104"])
        ),
        energy=_round_or_none(avg_or_none(d["WQ-201"], d["WQ-202"], d["WQ-204"])),
        building=_round_or_none(avg_or_none(d["WQ-301"], d["WQ-302"], d["WQ-303"])),
        management=_round_or_none(avg_or_none(d["WQ-401"], d["WQ-403"])),
    )
