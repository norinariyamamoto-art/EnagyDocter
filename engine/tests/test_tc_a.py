"""TC-A (製造工場・混在リスク型) -- exact regression test.

This is the one Mock_Test_Cases scenario Engine v1.4 actually computed (its
answers live in sheet `Forms_Response` row 4, Case_ID=TC-WEB-A). Every
expected value below is copied from that workbook's live formula results, so
every assertion here is an exact equality, not an approximation.

Cross-checked against:
  - Web_KPI!B5:B7 (Web_EDI=43, Web_DRI=36, Web_EPI=80)
  - Guardrail!A6,F6,H6 (BCP・供給継続 matched, Priority Score=565, L2)
  - TOP5_Final!C4:I18 (final ranking order and per-row scores)
  - Mock_Test_Cases!E3:F3 (期待Guardrail / 期待TOP課題 narrative, for the
    ordering assertions)
"""

from energy_doctor_engine import run_pipeline

from .fixtures import TC_A_FORMS_RESPONSE


def test_web_kpi_matches_excel():
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    assert result.web_kpi.web_edi == 43
    assert result.web_kpi.web_edi_band == "要改善"
    assert result.web_kpi.web_dri == 36
    assert result.web_kpi.web_dri_band == "判断困難"
    assert result.web_kpi.web_epi == 80
    assert result.web_kpi.web_epi_band == "最優先"


def test_guardrail_bcp_supply_continuity_fires():
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    top = result.top_guardrail
    assert top is not None
    assert top.category == "BCP・供給継続"
    assert top.level == "L2"
    assert top.priority_score == 565
    # 安全・法令／品質・顧客要求は非該当のまま
    others = {e.category: e.matched for e in result.guardrail_entries if e.category != "BCP・供給継続"}
    assert others == {"安全・法令": False, "品質・顧客要求": False}


def test_top5_order_matches_excel_exactly():
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    ordered = [(row.candidate_id, round(row.score, 1)) for row in result.top5]
    assert ordered == [
        ("GR-01", 81.3),
        ("EQ-03", 74.3),
        ("BL-03", 66.3),
        ("BL-02", 62.3),
        ("EN-01", 60.8),
    ]


def test_top5_does_not_bury_the_critical_issue():
    """Mock_Test_Cases!H3: 'reg重大課題を平均点に埋没させない' -- the Guardrail
    issue must be rank 1 despite most B-band issues clustering around 51-62."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    assert result.top5[0].candidate_id == "GR-01"
    assert result.top5[0].final_rank == 1


def test_bl01_suppressed_by_bl03_merge_rule():
    """TOP-R02 dedup: BL-01 ('建屋・環境課題の確認') is suppressed because the
    more specific BL-03 ('建屋環境による品質・操業影響の優先確認') qualifies
    with the same underlying WQ-301 answer (TOP5_Final!H11)."""
    result = run_pipeline(TC_A_FORMS_RESPONSE)
    bl01 = next(r for r in result.top5_final if r.candidate_id == "BL-01")
    assert bl01.eligible is False
    assert bl01.final_rank is None
