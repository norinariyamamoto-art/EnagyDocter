"""TC-C (物流センター・重大Guardrail型).

Like TC-B, this has no Forms_Response row in the workbook -- see
tests/test_tc_b.py's module docstring and ISSUES.md ISS-01 for why. The
narrative-fixed answers (Mock_Test_Cases!D5: "法令または安全の未解決／代替
なし／管理基準なし／中期計画なし／3か月以内") pin WQ-103/402/403/404/405; the
remaining answers (equipment/energy/building/WQ-401) were found by exhaustive
search over the discrete answer-choice space (~183k combinations) for a
combination that reproduces Mock_Test_Cases!I5 ("EDI27 / DRI22 / EPI91")
exactly. See COMPARISON.md for the search and ISSUES.md ISS-01 for why an
exact hit here is not proof of a unique original input.
"""

from energy_doctor_engine import run_pipeline

from .fixtures import TC_C_FORMS_RESPONSE


def test_web_kpi_matches_narrative_target():
    result = run_pipeline(TC_C_FORMS_RESPONSE)
    assert result.web_kpi.web_edi == 27
    assert result.web_kpi.web_dri == 22
    assert result.web_kpi.web_epi == 91


def test_safety_legal_guardrail_fires_at_highest_priority():
    result = run_pipeline(TC_C_FORMS_RESPONSE)
    top = result.top_guardrail
    assert top is not None
    assert top.category == "安全・法令"
    assert top.level == "L2"
    assert top.priority_score == 665  # highest base_rank (600) of the three categories


def test_safety_legal_guardrail_wins_top5_tie_break():
    """Mock_Test_Cases!C5/K5: '同点条件下でも安全・法令Guardrailを最上位へ'.
    This fixture happens to produce an exact score tie between GR-01 and the
    building-impact issue BL-03 (both 93.0) -- TOP5_Final's TiePriority
    column (Guardrail=1, everything else=2) must still place GR-01 first."""
    result = run_pipeline(TC_C_FORMS_RESPONSE)
    gr01 = next(r for r in result.top5_final if r.candidate_id == "GR-01")
    bl03 = next(r for r in result.top5_final if r.candidate_id == "BL-03")
    assert gr01.score == bl03.score  # confirms this fixture actually exercises the tie
    assert result.top5[0].candidate_id == "GR-01"
    assert result.top5[0].final_rank == 1
