"""TC-B (研究所＋事務棟・管理良好型).

Unlike TC-A, this scenario has no Forms_Response row in Engine v1.4 --
Mock_Test_Cases!A7 marks TC-B/TC-C as narrative-only "logic review
conditions". The answer set in fixtures.py is this implementation's own
reconstruction from Mock_Test_Cases!D4 ("設備情報・故障履歴・代替・電力管理・
建屋点検・中期計画が概ね整備／重大未解決なし"): every scored question set to
its best-case answer, WQ-404="ない". See ISSUES.md ISS-01.

That reconstruction happens to reproduce Mock_Test_Cases!I4 ("EDI100 / DRI100
/ EPI18") exactly via the Web_KPI formulas -- not a coincidence, since an
all-100 状態Score input drives every weighted-average term in Web_EDI/Web_DRI
to exactly 100, and Web_EPI's own formula (see web_kpi.py) works out to
17.5 -> ROUND -> 18. That exactness is still a property of this
reconstruction, not an independently verified Excel result -- there is no
live formula in the workbook computing it.
"""

from energy_doctor_engine import run_pipeline

from .fixtures import TC_B_FORMS_RESPONSE


def test_web_kpi_matches_narrative_target():
    result = run_pipeline(TC_B_FORMS_RESPONSE)
    assert result.web_kpi.web_edi == 100
    assert result.web_kpi.web_dri == 100
    assert result.web_kpi.web_epi == 18


def test_no_guardrail_fires():
    result = run_pipeline(TC_B_FORMS_RESPONSE)
    assert result.top_guardrail is None
    assert all(not e.matched for e in result.guardrail_entries)


def test_no_issue_fires_so_top5_is_empty():
    """Mock_Test_Cases!F4: 'B以上が少ない場合は無理に5件表示しない' -- every
    WQ answer being at its ceiling value means every Issue_Candidate's 発火
    condition (typically `D<100`) is false, so TOP5 must show 0 items rather
    than padding to 5."""
    result = run_pipeline(TC_B_FORMS_RESPONSE)
    assert result.top5 == []
    assert all(issue.fire == 0 for issue in result.issue_candidates)
