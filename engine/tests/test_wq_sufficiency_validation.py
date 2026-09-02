"""Tests for WQ-level information sufficiency
(energy_doctor_engine/wq_sufficiency_validation.py).

Originally written for the **Validation** exercise (comparison data only,
structurally disconnected from pipeline.py -- see
`05_Handoff_Brief/WQ_SUFFICIENCY_VALIDATION_INSTRUCTION.md`). ED-DI-003's
**Final Disposition** (2026-09-02, see
`05_Handoff_Brief/ED_DI_003_FINAL_PIPELINE_PATCH_INSTRUCTION.md`) has since
adopted this module's WQ-level granularity and the 50% threshold as the
formal production rule, and pipeline.py now imports and calls
compute_wq_sufficiency() directly -- so the "structurally disconnected"
guard test that used to live here was removed (it would now fail by
design; see PATCH3_NOTES.md). These tests check (1) the flat per-WQ weight
tables are derived correctly from web_kpi.py's actual formula structure,
(2) the sufficiency/threshold arithmetic itself, (3) the 6 boundary-case
patterns' measured values (as a regression guard on those numbers, since
wq_sufficiency_fixtures.py's comments quote them), and (4) that this
module's own historical 40/50/60% comparison function
(compute_wq_sufficiency_validation) still works and agrees with the
production compute_wq_sufficiency() at the 50% column specifically.
"""

from __future__ import annotations

import pytest

from energy_doctor_engine import pipeline as pipeline_module
from energy_doctor_engine import wq_sufficiency_validation as wqsv
from energy_doctor_engine.pipeline import (
    DIAGNOSIS_STATUS_INSUFFICIENT_DATA,
    DIAGNOSIS_STATUS_OK,
    run_pipeline,
)
from energy_doctor_engine.wq_sufficiency_validation import (
    compute_wq_sufficiency_validation,
    compute_wq_sufficiency_validation_from_forms_response,
)

from .fixtures import TC_A_FORMS_RESPONSE, TC_B_FORMS_RESPONSE, TC_C_FORMS_RESPONSE
from .wq_sufficiency_fixtures import (
    PATTERN_1_ALL_ANSWERED,
    PATTERN_2_ABOUT_75_PERCENT,
    PATTERN_3_ABOUT_60_PERCENT,
    PATTERN_4_ABOUT_50_PERCENT,
    PATTERN_5_ABOUT_40_PERCENT,
    PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN,
    PATTERN_6B_EPI_CRITICAL_WQS_UNKNOWN_TC_A_BASE,
)


# --- 1. Flat per-WQ weight tables are a faithful flattening of web_kpi.py ---


def test_edi_weight_table_sums_to_one():
    assert wqsv._EDI_WQ_WEIGHTS == pytest.approx(
        wqsv._EDI_WQ_WEIGHTS, rel=0  # identity, just to use pytest.approx import path
    )
    assert sum(wqsv._EDI_WQ_WEIGHTS.values()) == pytest.approx(1.0)


def test_dri_weight_table_sums_to_one():
    assert sum(wqsv._DRI_WQ_WEIGHTS.values()) == pytest.approx(1.0)


def test_epi_weight_table_sums_to_one():
    assert sum(wqsv._EPI_WQ_WEIGHTS.values()) == pytest.approx(1.0)


def test_dri_wq403_accumulates_both_terms_without_deduplication():
    """ISS-04 (HOLD): WQ-403 appears in Web_DRI's 0.15 term (avg over 3 WQs,
    so 0.05 share) AND again as the standalone 0.10 term -- this validation
    module must accumulate both (0.05 + 0.10 = 0.15), not deduplicate."""
    assert wqsv._DRI_WQ_WEIGHTS["WQ-403"] == pytest.approx(0.15 / 3 + 0.10)
    assert wqsv._DRI_WQ_WEIGHTS["WQ-403"] == pytest.approx(0.15)


def test_edi_weight_table_matches_web_kpi_terms():
    # 0.40 term over 4 WQs, 0.20 terms over 3/3/2 WQs -- see web_kpi.py.
    assert wqsv._EDI_WQ_WEIGHTS["WQ-101"] == pytest.approx(0.10)
    assert wqsv._EDI_WQ_WEIGHTS["WQ-201"] == pytest.approx(0.20 / 3)
    assert wqsv._EDI_WQ_WEIGHTS["WQ-401"] == pytest.approx(0.10)
    assert set(wqsv._EDI_WQ_WEIGHTS) == {
        "WQ-101", "WQ-102", "WQ-103", "WQ-104",
        "WQ-201", "WQ-202", "WQ-204",
        "WQ-301", "WQ-302", "WQ-303",
        "WQ-401", "WQ-403",
    }


def test_epi_weight_table_includes_virtual_wq404_slot():
    assert wqsv._EPI_WQ_WEIGHTS["WQ-404"] == pytest.approx(0.25 / 2)
    assert set(wqsv._EPI_WQ_WEIGHTS) == {
        "WQ-405", "WQ-103", "WQ-303", "WQ-104", "WQ-404", "WQ-204",
    }


# --- 2. Sufficiency / threshold arithmetic ---


def test_fully_answered_gives_100_percent_sufficiency_and_ok_everywhere():
    for forms_response in (TC_A_FORMS_RESPONSE, TC_B_FORMS_RESPONSE, TC_C_FORMS_RESPONSE):
        r = compute_wq_sufficiency_validation_from_forms_response(forms_response)
        assert r.wq_sufficiency_edi == pytest.approx(1.0)
        assert r.wq_sufficiency_dri == pytest.approx(1.0)
        assert r.wq_sufficiency_epi == pytest.approx(1.0)
        for statuses in (r.status_at_40, r.status_at_50, r.status_at_60):
            assert statuses == {
                "web_edi": DIAGNOSIS_STATUS_OK,
                "web_dri": DIAGNOSIS_STATUS_OK,
                "web_epi": DIAGNOSIS_STATUS_OK,
            }


def test_single_unknown_wq_reduces_sufficiency_by_its_own_flat_weight():
    import copy

    fr = copy.deepcopy(TC_B_FORMS_RESPONSE)
    fr["WQ-204"] = "不明"
    r = compute_wq_sufficiency_validation_from_forms_response(fr)
    assert r.wq_sufficiency_edi == pytest.approx(1 - wqsv._EDI_WQ_WEIGHTS["WQ-204"])
    assert r.wq_sufficiency_dri == pytest.approx(1 - wqsv._DRI_WQ_WEIGHTS["WQ-204"])
    assert r.wq_sufficiency_epi == pytest.approx(1 - wqsv._EPI_WQ_WEIGHTS["WQ-204"])


def test_wq403_unknown_removes_its_full_accumulated_weight_from_dri_only():
    """Marking WQ-403 (the ISS-04 double-weighted WQ) Unknown must drop
    Web_DRI's WQ-level sufficiency by its *full* accumulated 0.15, not just
    one of the two terms it appears in -- and must not affect Web_EPI at
    all (WQ-403 is not part of Web_EPI's formula)."""
    import copy

    fr = copy.deepcopy(TC_B_FORMS_RESPONSE)
    fr["WQ-403"] = "分からない"
    r = compute_wq_sufficiency_validation_from_forms_response(fr)
    assert r.wq_sufficiency_dri == pytest.approx(1 - 0.15)
    assert r.wq_sufficiency_epi == pytest.approx(1.0)


def test_threshold_boundary_uses_greater_or_equal():
    norm_all_answered = _norm(TC_B_FORMS_RESPONSE)
    result = compute_wq_sufficiency_validation(norm_all_answered)
    # 1.0 >= any of 0.40/0.50/0.60 -> OK, exercising the boundary operator
    # directly against a value equal to none of the thresholds but this
    # confirms >= (not >) is in effect via the exact-0.50 Pattern 4 case
    # below, which is the real boundary regression guard.
    assert result.status_at_60["web_edi"] == DIAGNOSIS_STATUS_OK


def test_production_pipeline_uses_this_modules_wq_level_sufficiency():
    """ED-DI-003 Final Disposition: pipeline.py's production decision must
    use exactly this module's compute_wq_sufficiency() (same weight tables,
    same numbers) -- not a separately re-implemented calculation. Cross-check
    a case with mixed per-KPI sufficiency (Pattern 6) between the module
    called directly and run_pipeline()'s PipelineResult fields."""
    from energy_doctor_engine.wq_sufficiency_validation import compute_wq_sufficiency

    norm = _norm(PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN)
    direct = compute_wq_sufficiency(norm)
    result = run_pipeline(PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN)
    assert result.web_edi_wq_sufficiency == pytest.approx(direct.web_edi)
    assert result.web_dri_wq_sufficiency == pytest.approx(direct.web_dri)
    assert result.web_epi_wq_sufficiency == pytest.approx(direct.web_epi)


def test_historical_validation_comparison_still_agrees_with_production_at_50_percent():
    """compute_wq_sufficiency_validation() (kept for historical
    reproducibility of the original 40/50/60% comparison) must still agree
    with the production per-KPI status at its status_at_50 column, since
    both are now built from the same compute_wq_sufficiency() values and
    MIN_WQ_SUFFICIENCY_THRESHOLD == 0.50."""
    assert pipeline_module.MIN_WQ_SUFFICIENCY_THRESHOLD == 0.50
    for forms_response in (
        PATTERN_2_ABOUT_75_PERCENT,
        PATTERN_3_ABOUT_60_PERCENT,
        PATTERN_4_ABOUT_50_PERCENT,
        PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN,
    ):
        validation = compute_wq_sufficiency_validation_from_forms_response(forms_response)
        result = run_pipeline(forms_response)
        assert validation.status_at_50["web_edi"] == result.web_edi_status
        assert validation.status_at_50["web_dri"] == result.web_dri_status
        assert validation.status_at_50["web_epi"] == result.web_epi_status


def _norm(forms_response):
    from energy_doctor_engine.forms_adapter import normalize_forms_response
    from energy_doctor_engine.wq_normalize import normalize

    return normalize(normalize_forms_response(forms_response))


# --- 3. The 6 boundary-case patterns: measured values (regression guard) ---


def test_pattern_1_all_answered():
    r = compute_wq_sufficiency_validation_from_forms_response(PATTERN_1_ALL_ANSWERED)
    assert (r.wq_sufficiency_edi, r.wq_sufficiency_dri, r.wq_sufficiency_epi) == (
        pytest.approx(1.0), pytest.approx(1.0), pytest.approx(1.0),
    )
    for statuses in (r.status_at_40, r.status_at_50, r.status_at_60):
        assert all(v == DIAGNOSIS_STATUS_OK for v in statuses.values())


def test_pattern_2_about_75_percent_is_ok_at_all_three_thresholds():
    r = compute_wq_sufficiency_validation_from_forms_response(PATTERN_2_ABOUT_75_PERCENT)
    assert r.wq_sufficiency_edi == pytest.approx(0.7666666666666667)
    assert r.wq_sufficiency_dri == pytest.approx(0.64)
    assert r.wq_sufficiency_epi == pytest.approx(0.8)
    for statuses in (r.status_at_40, r.status_at_50, r.status_at_60):
        assert all(v == DIAGNOSIS_STATUS_OK for v in statuses.values())


def test_pattern_3_about_60_percent_diverges_specifically_at_60():
    r = compute_wq_sufficiency_validation_from_forms_response(PATTERN_3_ABOUT_60_PERCENT)
    assert r.wq_sufficiency_edi == pytest.approx(0.7)
    assert r.wq_sufficiency_dri == pytest.approx(0.54)
    assert r.wq_sufficiency_epi == pytest.approx(0.375)
    # EDI: OK at every threshold.
    assert r.status_at_40["web_edi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_edi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_60["web_edi"] == DIAGNOSIS_STATUS_OK
    # DRI: OK at 40/50, flips to INSUFFICIENT_DATA exactly at 60.
    assert r.status_at_40["web_dri"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_dri"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_60["web_dri"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    # EPI: INSUFFICIENT_DATA at every threshold already.
    assert r.status_at_40["web_epi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    assert r.status_at_50["web_epi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    assert r.status_at_60["web_epi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA


def test_pattern_4_about_50_percent_epi_sits_exactly_on_boundary():
    r = compute_wq_sufficiency_validation_from_forms_response(PATTERN_4_ABOUT_50_PERCENT)
    assert r.wq_sufficiency_edi == pytest.approx(0.40)
    assert r.wq_sufficiency_dri == pytest.approx(0.5933333333333334)
    assert r.wq_sufficiency_epi == pytest.approx(0.50)
    # EPI sits exactly at 0.50 -- the >= rule makes it OK at the 50%
    # threshold specifically (this is the case's whole point).
    assert r.status_at_50["web_epi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_60["web_epi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    # EDI sits (within floating-point noise of) exactly 0.40 -- OK at 40%,
    # INSUFFICIENT_DATA just above it.
    assert r.status_at_40["web_edi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_edi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    # DRI stays comfortably OK at 40/50, and also at 60 in this case.
    assert r.status_at_40["web_dri"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_dri"] == DIAGNOSIS_STATUS_OK


def test_pattern_5_about_40_percent_all_three_thresholds_disagree():
    r = compute_wq_sufficiency_validation_from_forms_response(PATTERN_5_ABOUT_40_PERCENT)
    assert r.wq_sufficiency_edi == pytest.approx(0.43333333333333335)
    assert r.wq_sufficiency_dri == pytest.approx(0.5433333333333333)
    assert r.wq_sufficiency_epi == pytest.approx(0.75)
    # EDI: OK only at 40%.
    assert r.status_at_40["web_edi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_edi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    assert r.status_at_60["web_edi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    # DRI: OK at 40/50, INSUFFICIENT_DATA at 60.
    assert r.status_at_40["web_dri"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_dri"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_60["web_dri"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    # EPI: OK at every threshold.
    assert r.status_at_40["web_epi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_50["web_epi"] == DIAGNOSIS_STATUS_OK
    assert r.status_at_60["web_epi"] == DIAGNOSIS_STATUS_OK


def test_pattern_6_only_epi_becomes_information_insufficient():
    """The core claim Pattern 6 exists to test: concentrating Unknowns on
    Web_EPI-heavy WQs (WQ-405/303/104/404) makes *only* Web_EPI's WQ-level
    sufficiency collapse -- Web_EDI/Web_DRI, which barely use those WQs,
    stay comfortably OK at every threshold. This is not just "25% of
    questions missing" (Pattern 2 also removes 4/16 WQs and stays OK
    everywhere) -- it is specific to *which* WQs are missing."""
    r = compute_wq_sufficiency_validation_from_forms_response(
        PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN
    )
    assert r.wq_sufficiency_edi == pytest.approx(0.8333333333333334)
    assert r.wq_sufficiency_dri == pytest.approx(0.9166666666666667)
    assert r.wq_sufficiency_epi == pytest.approx(0.325)
    for statuses in (r.status_at_40, r.status_at_50, r.status_at_60):
        assert statuses["web_edi"] == DIAGNOSIS_STATUS_OK
        assert statuses["web_dri"] == DIAGNOSIS_STATUS_OK
        assert statuses["web_epi"] == DIAGNOSIS_STATUS_INSUFFICIENT_DATA


def test_pattern_6_is_consistent_with_guardrail_pending_and_review_items():
    """Cross-check against the existing (unmodified) ED-DI-005 outputs:
    WQ-404 being Unknown in this pattern must still set guardrail_pending,
    and the same WQs driving Web_EPI's insufficiency (WQ-104/WQ-303/WQ-404)
    must be exactly the ones surfaced in review_items -- run_pipeline()'s
    own logic is completely untouched by this validation module, so this is
    a consistency check between two independently-computed things, not a
    test of new pipeline.py behavior."""
    result = run_pipeline(PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN)
    assert result.guardrail_pending is True
    reason_wqs = {wq for item in result.review_items for wq in item.reason_wq}
    assert reason_wqs == {"WQ-104", "WQ-303", "WQ-404"}
    # The existing (Engine Patch 2) term-level information_sufficiency for
    # Web_EPI does NOT collapse here (0.7) -- this is the concrete
    # illustration of why term-level vs. WQ-level granularity was a genuine
    # open question: the two metrics disagree on this exact case. ED-DI-003
    # Final Disposition resolved that disagreement in favor of the WQ-level
    # figure below (0.325), which IS what now drives diagnosis_status.
    assert result.web_kpi.web_epi_information_sufficiency == pytest.approx(0.7)


def test_pattern_6_epi_only_insufficient_still_shows_top5_normally():
    """ED-DI-003 Final Pipeline Patch completion condition 3: with Unknowns
    concentrated on Web_EPI's urgency/impact-heavy WQs (WQ-405/303/104/404,
    same set as Pattern 6 above but layered on TC_A_FORMS_RESPONSE, which
    actually has issues that fire -- Pattern 6's own TC_B baseline has every
    answer already at its best choice, so nothing ever fires there and TOP5
    is legitimately empty regardless of information sufficiency, which would
    not exercise this completion condition), Web_EDI/Web_DRI stay
    individually OK (WQ-level sufficiency 0.8333/0.9167, both >= 0.50) while
    Web_EPI alone is INSUFFICIENT_DATA (0.325 < 0.50), so the overall
    diagnosis_status is INSUFFICIENT_DATA -- but TOP5 must still be computed
    and displayed normally, because Web_DRI itself produced a concrete
    web_dri_top5_r (TOP5 eligibility depends only on that, per Final
    Disposition point 5, never on diagnosis_status)."""
    result = run_pipeline(PATTERN_6B_EPI_CRITICAL_WQS_UNKNOWN_TC_A_BASE)

    assert result.web_edi_wq_sufficiency == pytest.approx(0.8333333333333334)
    assert result.web_dri_wq_sufficiency == pytest.approx(0.9166666666666667)
    assert result.web_epi_wq_sufficiency == pytest.approx(0.325)
    assert result.web_edi_status == DIAGNOSIS_STATUS_OK
    assert result.web_dri_status == DIAGNOSIS_STATUS_OK
    assert result.web_epi_status == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    assert result.diagnosis_status == DIAGNOSIS_STATUS_INSUFFICIENT_DATA

    # Sufficient KPIs' own computed values are preserved and displayable
    # (Final Disposition point 4) even though the overall status is not OK.
    assert result.web_kpi.web_edi is not None
    assert result.web_kpi.web_dri is not None

    # TOP5 is populated normally -- not suppressed by the overall
    # INSUFFICIENT_DATA status.
    assert result.web_kpi.web_dri_top5_r is not None
    assert len(result.top5_calc) > 0
    assert len(result.top5) > 0

    # Guardrail / guardrail_pending / review_items remain available, exactly
    # as under Engine Patch 2's existing rules (completion condition 4).
    assert result.guardrail_pending is True
    assert len(result.review_items) > 0
