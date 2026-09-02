"""Forms Import Adapter / Normalizer -- Corrective Patch 1 / ISS-02.

This sits in front of `wq_normalize.normalize()` and is the *only* place that
absorbs textual differences in how an Unknown answer can arrive. It does not
touch Microsoft Forms itself (out of scope per Handoff Brief Rev0.4 -- GUI
change is S社's responsibility), and it does not rewrite V2.2 or the Forms
implementation spec.

Background (see ../ISSUES.md ISS-02 and Energy_Doctor_Design_Issue_Log.md
ED-DI-001): the source-of-truth spreadsheets originally disagreed on
Unknown's display text --
  - V2.2 `68_公開フォーム最小質問セット` (public 18-question wording, which
    Engine v1.4's own WQ_Normalize formulas are written against) used 不明.
  - V2.2 `02_回答選択肢` (the formal-diagnosis Q-ID answer master) uses
    表示値「分からない」 with internal value UNKNOWN for the equivalent choice.
  - 03_Microsoft_Forms's independently-authored Forms spec also uses
    分からない.

**ED-DI-001 Final Disposition (S社 Design Disposition, 2026-09-02):** the
customer-facing Unknown display standard is now officially **「分からない」**
-- see `05_Handoff_Brief/ED_DI_001_FINAL_PATCH_INSTRUCTION.md`. V2.2/V2.3's
own sheets (`68_公開フォーム最小質問セット`, `76_MicrosoftForms実装仕様`, and a
few compound `02_回答選択肢` display values) are to be revised by S社 to match;
this codebase does not edit those spreadsheets. The internal sentinel stays
`UNKNOWN`. This adapter's accepted-values logic is unchanged by that
decision and was never itself display-wording-dependent: it already
accepted 不明, 分からない, and a blank answer interchangeably (for backward
compatibility across either display convention, or a mixed Forms export
during the transition), and continues to do so now that 分からない is the
confirmed standard.
"""

from __future__ import annotations

from typing import Dict

UNKNOWN = "UNKNOWN"

# Raw text forms that must be recognized as "no answer" / Unknown.
_UNKNOWN_ALIASES = {"不明", "分からない", "わからない"}

# The 16 Choice-type WQs that WQ_Normalize scores (see wq_normalize.py's
# NORMALIZE_ORDER). WQ-001 (multi-select theme picker) and WQ-501 (free
# text) are not part of this set -- they have no Unknown choice and are not
# fed through WQ_Normalize.
_NORMALIZED_WQ_IDS = {
    "WQ-101", "WQ-102", "WQ-103", "WQ-104",
    "WQ-201", "WQ-202", "WQ-203", "WQ-204",
    "WQ-301", "WQ-302", "WQ-303",
    "WQ-401", "WQ-402", "WQ-403", "WQ-404", "WQ-405",
}


def _is_unknown_text(raw: object) -> bool:
    if raw is None:
        return True
    text = str(raw).strip()
    return text == "" or text in _UNKNOWN_ALIASES


def normalize_forms_response(forms_response: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of forms_response where every recognized Unknown-like
    answer to a WQ_Normalize-scored question ("不明", "分からない", or a
    blank/whitespace-only answer) has been replaced with the canonical
    internal value UNKNOWN. Every other field (including WQ-001 and WQ-501)
    passes through unchanged."""
    result = dict(forms_response)
    for wq_id in _NORMALIZED_WQ_IDS:
        if wq_id not in result:
            continue
        if _is_unknown_text(result[wq_id]):
            result[wq_id] = UNKNOWN
    return result
