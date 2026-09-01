"""Guardrail sheet -- Decision Guardrail candidate display.

Source of truth: Engine v1.4 sheet `Guardrail`, rows 4-6. Judges WQ-404's raw
answer text (WQ_Normalize!C18) against three category keyword sets. Multiple
categories can match simultaneously (WQ-404 allows multi-select); the sheet
itself doesn't pick a single "winner" but its columns imply the winner for
display purposes is whichever matched category has the highest Priority
Score, which is exactly the base-rank ordering (安全・法令 > 品質・顧客要求 >
BCP・供給継続) since severity/evidence add-ons are identical (+50/+15) across
all three when matched.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .excel_compat import excel_search

_CATEGORIES = [
    ("安全・法令", 600, lambda c18: excel_search("安全", c18) or excel_search("法令", c18)),
    ("品質・顧客要求", 550, lambda c18: excel_search("品質", c18)),
    ("BCP・供給継続", 500, lambda c18: excel_search("供給継続", c18)),
]


@dataclass(frozen=True)
class GuardrailEntry:
    category: str
    base_rank: int
    matched: bool
    severity_add: int
    evidence_add: int
    priority_score: int
    message: str
    level: str


def evaluate_guardrail(wq404_raw: str) -> List[GuardrailEntry]:
    entries = []
    for name, base, match_fn in _CATEGORIES:
        matched = match_fn(wq404_raw)
        severity = 50 if matched else 0
        evidence = 15 if matched else 0
        priority = base + severity + evidence if matched else 0
        message = (
            f"{name}に関する未解決課題が回答されています。内容と対応期限の確認が必要です。"
            if matched
            else ""
        )
        level = "L2" if matched else ""
        entries.append(
            GuardrailEntry(
                category=name,
                base_rank=base,
                matched=matched,
                severity_add=severity,
                evidence_add=evidence,
                priority_score=priority,
                message=message,
                level=level,
            )
        )
    return entries


def top_guardrail(entries: List[GuardrailEntry]) -> Optional[GuardrailEntry]:
    matched = [e for e in entries if e.matched]
    if not matched:
        return None
    return max(matched, key=lambda e: e.priority_score)
