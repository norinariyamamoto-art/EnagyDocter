"""Corrective Patch 1 (ISS-02 / ISS-03 / ISS-06) and Corrective Patch 1.1
(ED-DI-003's two implementation-side fixes) regression tests.

See ../ISSUES.md for the original findings, ../PATCH1_NOTES.md for the fix
list and completion-condition checklist, and Energy_Doctor_Design_Issue_Log.md
(ED-DI-001, ED-DI-002, ED-DI-003) for the parts of this left OPEN for S社's
disposition -- notably, ED-DI-003 leaves the *choice* of Unknown-weight
renormalization (vs. not renormalizing, vs. treating the KPI as unavailable,
vs. a lowered-confidence value) undecided; this patch only changes how the
current provisional choice is *reported* (status instead of an exception),
not the choice itself.

ISS-04 (WQ-403 double weighting in Web_DRI), ISS-07 (Guardrail multi-match
display priority), and ISS-08 (WQ-301 flat 60pt for any non-"特になし"
multi-select) are explicitly HOLD in Rev0.4 and are NOT touched by this
patch -- test_iss_04_07_08_are_unchanged below pins their pre-patch behavior
so a future change to them shows up as a failing test here, not a silent
regression.
"""

from energy_doctor_engine import (
    DIAGNOSIS_STATUS_INSUFFICIENT_DATA,
    DIAGNOSIS_STATUS_OK,
    run_pipeline,
)
from energy_doctor_engine.excel_compat import weighted_score
from energy_doctor_engine.forms_adapter import UNKNOWN, normalize_forms_response

from .fixtures import FIELD_CAP_TIE_FORMS_RESPONSE, TC_A_FORMS_RESPONSE


# ---------------------------------------------------------------------------
# ISS-02: Adapter/Normalizer accepts 不明 / 分からない / blank interchangeably
# ---------------------------------------------------------------------------

def test_adapter_normalizes_all_three_unknown_spellings():
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-101"] = spelling
        normalized = normalize_forms_response(raw)
        assert normalized["WQ-101"] == UNKNOWN


def test_adapter_leaves_known_answers_and_non_scored_fields_untouched():
    normalized = normalize_forms_response(TC_A_FORMS_RESPONSE)
    assert normalized == TC_A_FORMS_RESPONSE  # TC-A has no Unknown answers
    # WQ-001/WQ-501 are outside WQ_Normalize's 16 scored questions and must
    # never be rewritten by this adapter even if they happen to contain the
    # literal text "不明" or "分からない" as free text/theme content.
    raw = dict(TC_A_FORMS_RESPONSE)
    raw["WQ-501"] = "分からない点が多いので相談したい"
    normalized = normalize_forms_response(raw)
    assert normalized["WQ-501"] == "分からない点が多いので相談したい"


def test_adapter_does_not_rewrite_v22_or_forms_spec_files():
    """ED-DI-001 stays OPEN: this patch must not resolve the display-text
    disagreement between V2.2's two sheets by editing either of them (nor
    the separately-authored Forms implementation spec). Verified by
    re-hashing both workbooks against the checksums recorded in
    SHA256SUMS.txt at repo root (captured from the original, untouched
    handoff package) rather than merely checking the files still exist."""
    import hashlib
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    guarded_paths = [
        "01_Core_Design/Energy_Doctor_LP_SelfDiagnosis_Design_V2.2.xlsx",
        "03_Microsoft_Forms/Energy_Doctor_Microsoft_Forms_Implementation_Spec_v1.0.xlsx",
        # Engine Patch 2: V2.3 (WQ-Q Traceability Approved) must stay
        # untouched too -- see "変更禁止: 正本ファイル（V2.2/V2.3のxlsx...）".
        "01_Core_Design/Energy_Doctor_LP_SelfDiagnosis_Design_V2_3_Traceability_Approved.xlsx",
    ]

    recorded = {}
    with open(repo_root / "SHA256SUMS.txt", encoding="utf-8") as f:
        for line in f:
            digest, _, name = line.strip().partition("  ")
            if name:
                recorded[name] = digest

    for rel_path in guarded_paths:
        assert rel_path in recorded, f"{rel_path} not tracked in SHA256SUMS.txt"
        actual = hashlib.sha256((repo_root / rel_path).read_bytes()).hexdigest()
        assert actual == recorded[rel_path], f"{rel_path} was modified"


# ---------------------------------------------------------------------------
# ISS-03: Unknown no longer raises #VALUE!-equivalent, and isn't forced to 0
# ---------------------------------------------------------------------------

def test_unknown_wq204_no_longer_crashes_web_dri_or_web_epi():
    """Before this patch, an Unknown WQ-204 answer raised ExcelValueError
    from Web_KPI!B6's bare `0.20*D11` term (and silently mis-scored
    Web_KPI!B7 via a comparison-semantics quirk). Both must now compute."""
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-204"] = spelling
        result = run_pipeline(raw)  # must not raise
        assert isinstance(result.web_kpi.web_dri, int)
        assert isinstance(result.web_kpi.web_epi, int)


def test_unknown_wq403_no_longer_crashes_web_dri():
    """Web_KPI!B6's bare `0.10*D17(WQ-403)` term was the other #VALUE! path."""
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-403"] = spelling
        result = run_pipeline(raw)  # must not raise
        assert isinstance(result.web_kpi.web_dri, int)


def test_unknown_wq405_no_longer_crashes_web_epi():
    """Web_KPI!B7's bare `0.30*E19(WQ-405)` term was the third #VALUE! path."""
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-405"] = spelling
        result = run_pipeline(raw)  # must not raise
        assert isinstance(result.web_kpi.web_epi, int)


def test_all_wq_unknown_returns_insufficient_data_status_not_an_exception():
    """Corrective Patch 1.1 / ED-DI-003: every one of the 16 scored WQs
    answered Unknown at once leaves every weighted term of Web_EDI (and
    Web_DRI) blank -- there is genuinely no information to compute those two
    KPIs from. This used to propagate as an uncaught InsufficientDataError
    (Corrective Patch 1's original behavior); ED-DI-003's review flagged
    that as effectively an unhandled crash from the caller's point of view.
    It is now a normal, inspectable pipeline result instead: diagnosis_status
    signals it and the affected KPIs are None ("該当KPIはnull相当").

    Engine Patch 2 / ED-DI-005 note: unlike Corrective Patch 1.1, Guardrail
    and Issue_Candidate/review_items are no longer forced empty here --
    ED-DI-005's disposition ("重大事項の未確認を非表示にしない") means
    Guardrail must stay visible (as guardrail_pending, since WQ-404 is also
    Unknown in this fixture) even when the rest of the diagnosis is
    INSUFFICIENT_DATA. Only TOP5 (which needs a defined Web_DRI-derived R)
    stays empty. See tests/test_engine_patch2.py for the dedicated
    ED-DI-003/004/005 test suite."""
    all_unknown = dict(TC_A_FORMS_RESPONSE)
    for wq in (
        "WQ-101", "WQ-102", "WQ-103", "WQ-104",
        "WQ-201", "WQ-202", "WQ-203", "WQ-204",
        "WQ-301", "WQ-302", "WQ-303",
        "WQ-401", "WQ-402", "WQ-403", "WQ-404", "WQ-405",
    ):
        all_unknown[wq] = "不明"

    result = run_pipeline(all_unknown)  # must not raise

    assert result.diagnosis_status == DIAGNOSIS_STATUS_INSUFFICIENT_DATA
    assert result.web_kpi.web_edi is None
    assert result.web_kpi.web_dri is None
    assert result.guardrail_pending is True
    assert result.guardrail_entries == []
    assert result.top_guardrail is None
    assert result.top5_calc == []
    assert result.top5_final == []
    assert result.top5 == []


def test_known_tc_a_still_reports_ok_status():
    """Regression guard: a normal, fully-answered submission must still
    report diagnosis_status OK, not just avoid crashing."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    assert result.diagnosis_status == DIAGNOSIS_STATUS_OK
    assert result.web_kpi.web_edi is not None
    assert result.web_kpi.web_dri is not None
    assert result.top5 != []


def test_unknown_is_not_collapsed_to_a_zero_score():
    """Corrective Patch 1 instructions: 'Unknownを一律に0点として扱わない'.
    An Unknown WQ-204 must not silently drag Web_DRI down to what forcing
    that term to a literal 0 would produce; weighted_score() instead drops
    the blank term and rescales the remaining weights.

    TC_A_FORMS_RESPONSE's other Web_DRI!B6 components are known
    (avg(D101,D102,D201,D202,D302)=49, avg(D103,D104,D203)=13.33,
    avg(D401,D402,D403)=45, D403=40), so both outcomes can be computed by
    hand: reweighting the remaining 0.80 of weight gives round(35.98)=36
    (coincidentally equal to the known-answer TC-A result, 36, because
    WQ-204's own D=35 in TC-A happens to sit close to the reweighted
    average); forcing the blank term to 0 without rescaling would instead
    give round(28.78)=29. The two must differ, and the code's output must
    match the reweighted figure, not the 0-substituted one.
    """
    unknown = dict(TC_A_FORMS_RESPONSE)
    unknown["WQ-204"] = "不明"

    dri_unknown = run_pipeline(unknown).web_kpi.web_dri
    reweighted_expected = 36
    zero_substituted_equivalent = 29
    assert reweighted_expected != zero_substituted_equivalent
    assert dri_unknown == reweighted_expected
    assert dri_unknown != zero_substituted_equivalent


def test_unknown_wq404_does_not_fire_guardrail_or_gr01():
    """GR-01's fire condition explicitly excludes "不明" (and now "UNKNOWN")
    alongside "ない" -- this pins that an Unknown WQ-404 answer behaves like
    the pre-existing "不明" case, not like a positive Guardrail trigger."""
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-404"] = spelling
        result = run_pipeline(raw)
        assert result.top_guardrail is None
        gr01 = next(i for i in result.issue_candidates if i.issue_id == "GR-01")
        assert gr01.fire == 0


def test_unknown_wq301_does_not_fire_bl01():
    """Regression guard for the bug this patch actually introduced-and-fixed
    mid-development: before adding "UNKNOWN" to BL-01's fire condition, an
    Unknown WQ-301 answer incorrectly fired BL-01 (only "特になし" and the
    literal "不明" were excluded; "UNKNOWN" was not)."""
    for spelling in ("不明", "分からない", ""):
        raw = dict(TC_A_FORMS_RESPONSE)
        raw["WQ-301"] = spelling
        result = run_pipeline(raw)
        bl01 = next(i for i in result.issue_candidates if i.issue_id == "BL-01")
        assert bl01.fire == 0


def test_weighted_score_excludes_blank_and_rescales():
    # 0.5*100 + 0.5*None -> the blank term drops out and the remaining
    # weight (0.5) is rescaled to 1.0, leaving the visible term's own value.
    # Engine Patch 2 / ED-DI-003: weighted_score() now returns a
    # WeightedScoreResult(value, information_sufficiency) instead of a bare
    # float -- see excel_compat.py.
    result = weighted_score([(0.5, 100.0), (0.5, None)])
    assert result.value == 100.0
    assert result.information_sufficiency == 0.5

    result = weighted_score([(0.3, 60.0), (0.7, 60.0)])
    assert result.value == 60.0
    assert result.information_sufficiency == 1.0


def test_weighted_score_all_blank_returns_none_not_an_exception():
    """Corrective Patch 1.1 / ED-DI-003: weighted_score() used to raise
    InsufficientDataError here (Corrective Patch 1's original behavior).
    It now returns a WeightedScoreResult with value=None instead -- an
    all-blank formula is a defined, non-exceptional outcome ("no score
    computable from zero information"), not an error condition -- so callers
    can check for it explicitly (see web_kpi.py's _round_or_none and
    pipeline.py's diagnosis_status) instead of needing a try/except that, in
    practice, was never added anywhere. information_sufficiency is 0.0 in
    this case, consistent with every term being blank."""
    result = weighted_score([(0.5, None), (0.5, None)])
    assert result.value is None
    assert result.information_sufficiency == 0.0


# ---------------------------------------------------------------------------
# ISS-06: TOP-R03 same-field-max-2 must hold even under a 3-way (or more) tie
# ---------------------------------------------------------------------------

def test_three_way_tie_is_capped_at_two_per_field():
    result = run_pipeline(FIELD_CAP_TIE_FORMS_RESPONSE)
    management_rows = [r for r in result.top5_final if r.field == "管理"]
    assert len(management_rows) == 3
    scores = {r.score for r in management_rows}
    assert scores == {52.0}, "fixture must produce an exact 3-way tie to exercise ISS-06"

    eligible = [r for r in management_rows if r.eligible]
    assert len(eligible) == 2, "TOP-R03 same-field-max-2 must hold even at a 3-way tie"

    # Original sheet order (MG-01 before MG-02 before MG-03) breaks the tie,
    # matching the same row-order tie-break TOP5_Final's Final Rank already
    # uses elsewhere -- not a new precedence rule.
    kept = {r.candidate_id for r in eligible}
    assert kept == {"MG-01", "MG-02"}
    demoted = next(r for r in management_rows if r.candidate_id == "MG-03")
    assert demoted.eligible is False
    assert demoted.final_rank is None


def test_field_cap_does_not_touch_guardrail_or_bl01_bl03_special_case():
    """The cap enforcement must only apply to ordinary fields -- Guardrail
    stays exempt (TOP5_Final!H column's own IF(field="Guardrail",1,...)
    branch), and BL-01's existing suppression-by-BL-03 rule (ISS-05) is
    untouched."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    gr01 = next(r for r in result.top5_final if r.candidate_id == "GR-01")
    assert gr01.eligible is True
    bl01 = next(r for r in result.top5_final if r.candidate_id == "BL-01")
    assert bl01.eligible is False  # suppressed by BL-03, as in Task 1A


def test_top5_regression_tc_a_unchanged_after_patch():
    """TC-A's own TOP5 (the only Excel-verified case) must be byte-for-byte
    the same after this patch, since none of its fields hit a 3+ way tie at
    the field-cap boundary."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    ordered = [(row.candidate_id, round(row.score, 1)) for row in result.top5]
    assert ordered == [
        ("GR-01", 81.3),
        ("EQ-03", 74.3),
        ("BL-03", 66.3),
        ("BL-02", 62.3),
        ("EN-01", 60.8),
    ]


# ---------------------------------------------------------------------------
# HOLD items must be unchanged by this patch
# ---------------------------------------------------------------------------

def test_iss_04_07_08_are_unchanged():
    """Rev0.4: ISS-04/07/08 are explicitly HOLD (design decision pending at
    S社) and must not be touched by Corrective Patch 1."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)

    # ISS-04: WQ-403 (中期計画) is still double-weighted in Web_DRI
    # (0.15*AVERAGE(D15:D17) *and* 0.10*D17 again) -- unchanged formula.
    assert result.web_kpi.web_dri == 36

    # ISS-07: Guardrail multi-match display priority is still "highest
    # Priority Score wins" (this implementation's original interpretation;
    # not re-derived or altered by this patch).
    assert result.top_guardrail.category == "BCP・供給継続"
    assert result.top_guardrail.priority_score == 565

    # ISS-08: WQ-301 (建屋環境) still scores a flat 60 for any answer other
    # than "特になし"/Unknown, regardless of how many options were selected.
    single_selection = dict(TC_A_FORMS_RESPONSE)
    single_selection["WQ-301"] = "結露"
    multi_selection = dict(TC_A_FORMS_RESPONSE)
    multi_selection["WQ-301"] = "結露／暑熱／粉じん・臭気"
    single_result = run_pipeline(single_selection)
    multi_result = run_pipeline(multi_selection)
    assert single_result.web_kpi.web_edi == multi_result.web_kpi.web_edi
