"""Engine Patch 2 (ED-DI-002/003/004/005) regression tests.

Scope: implements the S社-approved dispositions in
Energy_Doctor_Design_Issue_Log.md (Decision Record Rev0.1, 2026-09-02) and
V2.3 sheet `78_Web診断Disposition` on top of Corrective Patch 1/1.1. See
../PATCH2_NOTES.md for the full change list and completion-condition
checklist.

ED-DI-002 is a documentation-only change here (see issue_candidate.py's and
guardrail.py's module docstrings referencing V2.3 sheet
`77_WQ-Q_Traceability`) -- no behavior to test beyond "nothing was scored
using a formal Q-ID value", which test_no_formal_q_id_values_are_used below
covers structurally.
"""

from energy_doctor_engine import run_pipeline
from energy_doctor_engine import pipeline as pipeline_module

from .fixtures import TC_A_FORMS_RESPONSE


# ---------------------------------------------------------------------------
# ED-DI-003 point 2: information sufficiency, per KPI
# ---------------------------------------------------------------------------

def test_fully_answered_case_has_full_information_sufficiency():
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    k = result.web_kpi
    assert k.web_edi_information_sufficiency == 1.0
    assert k.web_dri_information_sufficiency == 1.0
    assert k.web_epi_information_sufficiency == 1.0


def test_partial_unknown_reduces_information_sufficiency_by_its_declared_weight():
    """All four WQ-101..104 (Web_EDI's whole 40%-weighted equipment term)
    Unknown at once: that term drops out of Web_EDI entirely, so
    information_sufficiency drops by exactly its declared share (0.40),
    landing at 0.60 -- and Web_EDI is still computed (not None) from the
    remaining 60% of declared weight."""
    partial = dict(TC_A_FORMS_RESPONSE)
    for wq in ("WQ-101", "WQ-102", "WQ-103", "WQ-104"):
        partial[wq] = "不明"
    result = run_pipeline(partial)
    assert abs(result.web_kpi.web_edi_information_sufficiency - 0.60) < 1e-9
    assert result.web_kpi.web_edi == 48  # computed from the remaining 60%
    assert result.diagnosis_status == pipeline_module.DIAGNOSIS_STATUS_OK


# ---------------------------------------------------------------------------
# ED-DI-003 point 3/4: TBC threshold, generalized INSUFFICIENT_DATA
# ---------------------------------------------------------------------------

def test_threshold_is_a_named_constant_marked_tbc():
    """Completion condition 2: the threshold must be a single named constant
    with a TBC (To Be Confirmed) comment -- not a magic number scattered
    across the code. (A bare float can't carry its own `__doc__`, so this
    checks the constant's name and the module source's documented rationale
    instead of a runtime docstring attribute.)"""
    import inspect

    assert hasattr(pipeline_module, "MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC")
    assert 0.0 < pipeline_module.MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC < 1.0
    assert "TBC" in "MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC"
    source = inspect.getsource(pipeline_module)
    assert "TBC (To Be Confirmed)" in source
    assert "S社" in source  # documented as pending S社 confirmation, not a final value


def test_changing_the_threshold_changes_pipeline_behavior(monkeypatch):
    """Completion condition 2: prove the threshold is load-bearing, not
    decorative -- the same input must flip between OK and INSUFFICIENT_DATA
    purely because the module constant changed. Uses the equipment-all-
    unknown fixture above (EDI sufficiency 0.60, DRI sufficiency also <1.0
    since WQ-101/102 feed its 0.30 term and WQ-103/104 feed its 0.25 term)."""
    partial = dict(TC_A_FORMS_RESPONSE)
    for wq in ("WQ-101", "WQ-102", "WQ-103", "WQ-104"):
        partial[wq] = "不明"

    monkeypatch.setattr(pipeline_module, "MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC", 0.1)
    lenient = run_pipeline(partial)
    assert lenient.diagnosis_status == pipeline_module.DIAGNOSIS_STATUS_OK

    monkeypatch.setattr(pipeline_module, "MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC", 0.99)
    strict = run_pipeline(partial)
    assert strict.diagnosis_status == pipeline_module.DIAGNOSIS_STATUS_INSUFFICIENT_DATA


def test_all_unknown_is_the_zero_sufficiency_special_case_of_the_threshold():
    """ED-DI-003 point 4: all-Unknown must not need a separate code path --
    it is simply sufficiency=0.0 for every KPI, which is below any positive
    threshold. This directly checks the generalization, independent of the
    exact TBC threshold value."""
    all_unknown = dict(TC_A_FORMS_RESPONSE)
    for wq in (
        "WQ-101", "WQ-102", "WQ-103", "WQ-104",
        "WQ-201", "WQ-202", "WQ-203", "WQ-204",
        "WQ-301", "WQ-302", "WQ-303",
        "WQ-401", "WQ-402", "WQ-403", "WQ-404", "WQ-405",
    ):
        all_unknown[wq] = "不明"
    result = run_pipeline(all_unknown)
    assert result.web_kpi.web_edi_information_sufficiency == 0.0
    assert result.web_kpi.web_dri_information_sufficiency == 0.0
    assert result.diagnosis_status == pipeline_module.DIAGNOSIS_STATUS_INSUFFICIENT_DATA


# ---------------------------------------------------------------------------
# ED-DI-003 point 5: Issue_Candidate's U is NOT reweighted
# ---------------------------------------------------------------------------

def test_unknown_wq405_no_longer_reweights_top_base_and_still_does_not_crash():
    """Before Engine Patch 2, an Unknown WQ-405 (blank U) made TOP5_Calc
    renormalize every issue's TOP_BASE over the remaining 5 terms (via
    weighted_score()). ED-DI-003 point 5 explicitly rejects that for U:
    U is substituted with 0, weights stay 0.30/0.25/0.20/0.10/0.10/0.05.
    IS-01 in TC_A_FORMS_RESPONSE has I=40, P=40, R=30, C=70, O=60 (fixed,
    independent of U) -- with U=0 substituted, TOP_BASE = 0.30*40 + 0 +
    0.20*40 + 0.10*30 + 0.10*70 + 0.05*60 = 12+0+8+3+7+3 = 33.0 exactly."""
    raw = dict(TC_A_FORMS_RESPONSE)
    raw["WQ-405"] = "不明"
    result = run_pipeline(raw)  # must not raise
    is01_calc = next(r for r in result.top5_calc if r.issue_id == "IS-01")
    assert is01_calc.top_base == 33.0


# ---------------------------------------------------------------------------
# ED-DI-004: domain_status, independent of Web_EDI
# ---------------------------------------------------------------------------

def test_domain_status_matches_web_edi_internal_components():
    """domain_status must reuse exactly the same WQ groupings/averaging as
    Web_EDI's own four weighted terms (see web_kpi.py's compute_web_kpi),
    just reported independently rather than folded into one composite."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    ds = result.domain_status
    assert (ds.equipment, ds.energy, ds.building, ds.management) == (35, 33, 62, 50)


def test_domain_status_is_independent_of_web_edi_when_one_domain_is_unknown():
    """A fully-blank domain still reports its own status as None while the
    others (and Web_EDI itself, computed from the remaining weight) stay
    populated -- domain_status is not gated by Web_EDI's own availability."""
    partial = dict(TC_A_FORMS_RESPONSE)
    for wq in ("WQ-101", "WQ-102", "WQ-103", "WQ-104"):
        partial[wq] = "不明"
    result = run_pipeline(partial)
    assert result.domain_status.equipment is None
    assert result.domain_status.energy == 33
    assert result.domain_status.building == 62
    assert result.domain_status.management == 50
    assert result.web_kpi.web_edi == 48  # still computed, independently


def test_web_edi_weights_are_unchanged():
    """変更禁止: Web_EDIの加重係数・算定式自体. Pin the exact TC-A value so any
    accidental change to the 40/20/20/20 weighting fails this test."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    assert result.web_kpi.web_edi == 43  # unchanged since Task 1A


# ---------------------------------------------------------------------------
# ED-DI-005 point 1: review_items
# ---------------------------------------------------------------------------

def test_review_items_surface_issues_suppressed_by_unknown_answers():
    """Reproduces Task 2's SIM-01 finding exactly: WQ-104 Unknown suppresses
    IS-04, WQ-402 Unknown suppresses MG-02 -- both must now appear as
    review_items instead of vanishing silently."""
    raw = dict(TC_A_FORMS_RESPONSE)
    raw["WQ-104"] = "分からない"
    raw["WQ-402"] = "不明"
    result = run_pipeline(raw)

    review_ids = {item.issue_id: item.reason_wq for item in result.review_items}
    assert review_ids["IS-04"] == ("WQ-104",)
    assert review_ids["MG-02"] == ("WQ-402",)

    # Confirmed still not independently scored (existing fire logic
    # untouched -- ED-DI-005 explicitly requires this). Note EQ-03 in
    # TOP5_Final structurally lists both IS-03 and IS-04 as source_issues
    # regardless of which one fired (see top5_final.py's MAX(IS-03,IS-04)
    # merge) -- fire==0 here is the correct signal that IS-04 itself
    # contributed nothing to that MAX, not "IS-04 absent from source_issues".
    is04 = next(i for i in result.issue_candidates if i.issue_id == "IS-04")
    mg02 = next(i for i in result.issue_candidates if i.issue_id == "MG-02")
    assert is04.fire == 0
    assert mg02.fire == 0
    assert all(row.candidate_id != "MG-02" for row in result.top5_final if row.eligible)


def test_review_items_excludes_issues_that_simply_have_a_good_answer():
    """An issue with fire=0 because the answer was simply *good* (D=100,
    e.g. WQ-101="把握している") must not be listed as a review item -- only
    fire=0 caused by an Unknown main_wq counts."""
    raw = dict(TC_A_FORMS_RESPONSE)
    raw["WQ-101"] = "把握している"  # D=100 -> IS-01 fire=0, but answered, not Unknown
    result = run_pipeline(raw)
    assert all(item.issue_id != "IS-01" for item in result.review_items)


def test_review_items_excludes_cu01_free_text():
    """WQ-501 is optional free text (not part of WQ_Normalize's 16 scored
    questions) -- CU-01 not firing because it's blank must not be reported
    as a review item (see review_items.py's module docstring)."""
    raw = dict(TC_A_FORMS_RESPONSE)
    raw["WQ-501"] = ""
    result = run_pipeline(raw)
    assert all(item.issue_id != "CU-01" for item in result.review_items)


def test_issue_candidate_scoring_logic_is_unchanged():
    """変更禁止 / ED-DI-005: existing issue_candidate.py fire logic must be
    untouched by adding review_items. TC-A's full fired-issue set is pinned."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    fired = sorted(i.issue_id for i in result.issue_candidates if i.fire == 1)
    assert fired == sorted(
        [
            "IS-01", "IS-02", "IS-03", "IS-04",
            "EN-01", "EN-02", "EN-03", "EN-04",
            "BL-01", "BL-02", "BL-03",
            "MG-01", "MG-02", "MG-03",
            "GR-01", "CU-01",
        ]
    )


# ---------------------------------------------------------------------------
# ED-DI-005 point 2: guardrail_pending
# ---------------------------------------------------------------------------

def test_guardrail_pending_true_when_wq404_is_unknown():
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-404"] = spelling
        result = run_pipeline(raw)
        assert result.guardrail_pending is True
        assert result.guardrail_entries == []
        assert result.top_guardrail is None


def test_guardrail_pending_false_and_distinguishable_from_confirmed_clean():
    """guardrail_pending must be False both when a Guardrail actually fires
    (TC-A) and when WQ-404 is a confirmed, answered "ない" -- these two are
    the "not pending" cases that top_guardrail alone can't distinguish from
    "pending" without this separate flag."""
    fired = run_pipeline(TC_A_FORMS_RESPONSE)
    assert fired.guardrail_pending is False
    assert fired.top_guardrail is not None

    clean = dict(TC_A_FORMS_RESPONSE)
    clean["WQ-404"] = "ない"
    clean_result = run_pipeline(clean)
    assert clean_result.guardrail_pending is False
    assert clean_result.top_guardrail is None


# ---------------------------------------------------------------------------
# ED-DI-005 point 3: display hierarchy (Guardrail -> review_items -> TOP5)
# ---------------------------------------------------------------------------

def test_pipeline_result_field_order_reflects_display_hierarchy():
    """Documentation-shaped check: PipelineResult's declared field order
    should read Guardrail fields, then review_items, then TOP5 fields, per
    ED-DI-005's "Guardrail -> 要確認事項 -> TOP5" disposition."""
    from energy_doctor_engine.pipeline import PipelineResult

    fields = list(PipelineResult.__dataclass_fields__.keys())
    assert fields.index("guardrail_pending") < fields.index("review_items")
    assert fields.index("review_items") < fields.index("top5")


# ---------------------------------------------------------------------------
# ED-DI-002: no formal Q-ID value is fabricated or transcribed
# ---------------------------------------------------------------------------

def test_no_formal_q_id_values_are_used():
    """変更禁止: 公開WQ回答から正式Qの個別回答値を自動生成・転記するロジックの追加.
    Structural guard: none of this package's source files should reference a
    formal Q-ID (e.g. "Q101") as an input identifier -- only WQ-* public
    question IDs are valid Forms_Response keys anywhere in the engine."""
    import pathlib
    import re

    package_dir = pathlib.Path(__file__).resolve().parents[1] / "energy_doctor_engine"
    q_id_pattern = re.compile(r'"Q\d{3}"')
    offenders = []
    for path in package_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if q_id_pattern.search(text):
            offenders.append(path.name)
    assert offenders == [], f"formal Q-ID literal found in: {offenders}"
