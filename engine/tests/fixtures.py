"""Forms_Response fixtures for TC-A/B/C.

TC-A is transcribed verbatim from Engine v1.4 sheet `Forms_Response` row 4
(Case_ID=TC-WEB-A) -- this is the one case the source workbook actually
computed, so its expected values below are copied from the live formula
results in that workbook (Web_KPI!B5:B7, Guardrail!A6/H6, TOP5_Final!I4:I18),
not from the Mock_Test_Cases narrative column.

TC-B and TC-C have NO corresponding Forms_Response row in the workbook.
Mock_Test_Cases!A7 states outright that these two are "logic review
conditions" pending real Forms input, and only describes them narratively
(sheet `Mock_Test_Cases`, columns D/E/F/G). The answer sets below are this
implementation's own construction, built to satisfy that narrative
(D column: 主要回答条件) and checked against the target KPI values Excel's
author wrote in column I (実測KPI) -- see ISSUES.md ISS-01 for why this is a
reconstruction rather than a verified fixture, and COMPARISON.md for exactly
how each value was matched.
"""

from __future__ import annotations

TC_A_FORMS_RESPONSE = {
    "WQ-001": "設備更新／省エネ／投資優先順位",
    "WQ-101": "一部把握",
    "WQ-102": "記録のみ",
    "WQ-103": "ない",
    "WQ-104": "未確認",
    "WQ-201": "請求額のみ",
    "WQ-202": "全体のみ",
    "WQ-203": "困難",
    "WQ-204": "検討のみ",
    "WQ-301": "結露／暑熱",
    "WQ-302": "問題時のみ",
    "WQ-303": "影響の可能性",
    "WQ-401": "一部ある",
    "WQ-402": "担当者ごと",
    "WQ-403": "案件ごと",
    "WQ-404": "供給継続",
    "WQ-405": "1年以内",
    "WQ-501": "受変電設備の更新時期と停電対策が気になっている",
}

# Reconstructed to satisfy Mock_Test_Cases!D4: "設備情報・故障履歴・代替・
# 電力管理・建屋点検・中期計画が概ね整備／重大未解決なし" -- i.e. every
# scored answer at its best choice, WQ-404="ない", WQ-405="時期未定" (no
# particular urgency, consistent with "管理良好型").
TC_B_FORMS_RESPONSE = {
    "WQ-001": "保全／投資優先順位",
    "WQ-101": "把握している",
    "WQ-102": "定期的に確認",
    "WQ-103": "十分ある",
    "WQ-104": "定期確認",
    "WQ-201": "毎月確認",
    "WQ-202": "詳細に把握",
    "WQ-203": "迅速に確認",
    "WQ-204": "複数実施",
    "WQ-301": "特になし",
    "WQ-302": "定期点検",
    "WQ-303": "影響なし",
    "WQ-401": "明確にある",
    "WQ-402": "明文化済み",
    "WQ-403": "予算付き計画あり",
    "WQ-404": "ない",
    "WQ-405": "時期未定",
    "WQ-501": "",
}

# Reconstructed to satisfy Mock_Test_Cases!D5: "法令または安全の未解決／
# 代替なし／管理基準なし／中期計画なし／3か月以内". The remaining answers
# (equipment/energy/building/WQ-401) were not specified by the narrative and
# were chosen by exhaustive search over the discrete answer-choice space so
# that Web_EDI/Web_DRI/Web_EPI land exactly on Mock_Test_Cases!I5's
# "EDI27 / DRI22 / EPI91" -- see COMPARISON.md for the search and ISSUES.md
# ISS-01 for why this exact match is not itself proof of a unique original
# input (a search over ~183k combinations found this as one exact hit).
TC_C_FORMS_RESPONSE = {
    "WQ-001": "BCP・停電対策／保全",
    "WQ-101": "一部把握",
    "WQ-102": "記録なし",
    "WQ-103": "ない",
    "WQ-104": "未確認",
    "WQ-201": "請求額のみ",
    "WQ-202": "全体のみ",
    "WQ-203": "困難",
    "WQ-204": "未実施",
    "WQ-301": "結露",
    "WQ-302": "ほとんど未確認",
    "WQ-303": "明確な影響あり",
    "WQ-401": "ない",
    "WQ-402": "基準なし",
    "WQ-403": "計画なし",
    "WQ-404": "安全",
    "WQ-405": "3か月以内",
    "WQ-501": "",
}
