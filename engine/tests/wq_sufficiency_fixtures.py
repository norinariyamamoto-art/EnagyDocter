"""Dedicated boundary-case Forms_Response fixtures for the WQ-level
information-sufficiency **Validation** exercise -- separate from TC-A/B/C
(fixtures.py) and Task2's 5 business-site scenarios (../task2/scenarios.py),
per `05_Handoff_Brief/WQ_SUFFICIENCY_VALIDATION_INSTRUCTION.md` section 4.

Each pattern starts from fixtures.TC_B_FORMS_RESPONSE (a fully-answered, no
-Unknown baseline -- every one of the 16 WQ_Normalize-scored questions has a
valid, non-Unknown answer) and marks a chosen subset of WQs Unknown
("不明"). Which WQs are marked Unknown, and how many, was chosen by
exploring the actually-achievable sufficiency values (see PR description /
WQ_SUFFICIENCY_VALIDATION_REPORT.md for the exploration method) rather than
solving for an exact percentage -- WQ effective weights are not uniform, so
an exact 40%/50%/60% overall figure is not always constructible, and the
instruction explicitly says to use the closest realistically-constructible
case and report the actual measured value rather than forcing a round
number.

Every measured wq_sufficiency_edi/dri/epi value quoted in the comments below
was read off compute_wq_sufficiency_validation_from_forms_response() (see
test_wq_sufficiency_validation.py, which re-asserts each one), not
hand-calculated -- so these comments describe the code's actual output.
"""

from __future__ import annotations

import copy

from .fixtures import TC_B_FORMS_RESPONSE


def _unknown(*wq_ids: str) -> dict:
    fr = copy.deepcopy(TC_B_FORMS_RESPONSE)
    for wq_id in wq_ids:
        fr[wq_id] = "不明"
    return fr


# Pattern 1: all 16 WQs answered -> 100% sufficiency for every KPI.
PATTERN_1_ALL_ANSWERED = _unknown()

# Pattern 2: 4 of 16 WQs Unknown (12/16 = 75% of questions answered),
# spread across WQs used by different KPIs (WQ-302: EDI+DRI, WQ-402:
# DRI-only, WQ-401: EDI+DRI, WQ-204: EDI+DRI+EPI) so no single KPI is hit by
# more than one of them at once. Measured: EDI=0.7667, DRI=0.64, EPI=0.80 --
# all three comfortably >=60%, i.e. OK at all three candidate thresholds,
# matching the instruction's "原則OK" expectation for ~75% answered.
PATTERN_2_ABOUT_75_PERCENT = _unknown("WQ-302", "WQ-402", "WQ-401", "WQ-204")

# Pattern 3: 7 of 16 WQs Unknown (9/16 = 56.25% answered -- the closest
# constructible case just *below* 60%, per the "use the nearest achievable
# case" tolerance). Measured: EDI=0.70, DRI=0.54, EPI=0.375. This spreads
# the three KPIs across three different threshold outcomes at once: EDI
# stays OK even at 60%, DRI is OK at 40%/50% but flips to INSUFFICIENT_DATA
# at 60%, and EPI is already INSUFFICIENT_DATA at all three -- i.e. the
# 60% boundary specifically changes DRI's verdict and nothing else's.
# Also includes WQ-404, so guardrail_pending is True here too (see Pattern 6
# for the dedicated guardrail/review_items cross-check).
PATTERN_3_ABOUT_60_PERCENT = _unknown(
    "WQ-204", "WQ-301", "WQ-302", "WQ-402", "WQ-403", "WQ-404", "WQ-405"
)

# Pattern 4: 8 of 16 WQs Unknown -- exactly 50% of questions answered.
# Measured: EDI=0.40 (also sits almost exactly on the 40% line), DRI=0.5933,
# EPI=0.50 (sits exactly on the 50% line). EPI's exact 0.50 is the pattern's
# main point: with this module's ">= threshold -> OK" rule, EPI is judged
# OK at the 50% threshold precisely at the boundary, not just near it.
PATTERN_4_ABOUT_50_PERCENT = _unknown(
    "WQ-101", "WQ-102", "WQ-103", "WQ-104", "WQ-202", "WQ-302", "WQ-303", "WQ-404"
)

# Pattern 5: 9 of 16 WQs Unknown (7/16 = 43.75% answered -- the closest
# constructible case just *above* 40%). Measured: EDI=0.4333, DRI=0.5433,
# EPI=0.75. This is deliberately the strongest 3-way divergence found: EDI
# is OK only at the 40% threshold (already INSUFFICIENT_DATA at 50%/60%),
# DRI is OK at 40%/50% but INSUFFICIENT_DATA at 60%, and EPI is OK at all
# three -- i.e. all three thresholds (40/50/60) produce a different overall
# picture across the three KPIs for this single case.
PATTERN_5_ABOUT_40_PERCENT = _unknown(
    "WQ-102", "WQ-103", "WQ-201", "WQ-202", "WQ-203", "WQ-301", "WQ-302", "WQ-401", "WQ-404"
)

# Pattern 6: Unknowns concentrated on Web_EPI's urgency/impact-heavy WQs --
# WQ-405 (0.30 of Web_EPI, standalone -- imminence of an energy-related
# decision), WQ-303 (building-impact severity, feeds Web_EPI's 0.25 term),
# WQ-104 (the other half of that same term), and WQ-404 itself (the virtual
# guardrail_urgency slot -- also the Guardrail input, so this pattern
# doubles as a guardrail_pending / review_items cross-check). Only 4 of 16
# WQs are Unknown (12/16 = 75% answered "by question count"), and none of
# them meaningfully overlaps Web_EDI/Web_DRI's own heavily-used WQs.
# Measured: EDI=0.8333, DRI=0.9167 (both comfortably OK at all three
# thresholds), EPI=0.325 (INSUFFICIENT_DATA at all three thresholds) --
# i.e. this is NOT a generic "25% of questions missing" effect (Pattern 2
# also has 4/16 Unknown and stays OK everywhere); it is specific to which
# WQs are missing. guardrail_pending is True (WQ-404 Unknown) and
# review_items surfaces IS-04/BL-03 (driven by WQ-104/WQ-303) plus GR-01
# (driven by WQ-404), consistent with the same four WQs driving both this
# module's EPI-only insufficiency and the existing ED-DI-005 outputs.
PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN = _unknown("WQ-405", "WQ-303", "WQ-104", "WQ-404")
