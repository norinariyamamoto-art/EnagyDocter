"""Task 2 -- 5 fictional business-site scenarios for Energy Doctor's public
18-question flow.

Design method (per Handoff Brief Rev0.4 Task 2 instructions): for each case,
a business Profile is written FIRST (industry, size, specific operational
narrative), and the 18-question answers are then derived from that Profile
by asking "what would this specific site plausibly answer to this specific
question" -- never by picking answers to hit a target Web_EDI/DRI/EPI number
or a target TOP5 ranking. No case is deliberately driven to worst-possible
answers on every axis; each mixes strong/weak areas the way a real site
would (see each PROFILE string for the reasoning behind each answer).

Fictional entities only: company/site names below do not correspond to any
real organization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Scenario:
    case_id: str
    company: str
    site: str
    theme: str
    profile: str
    forms_response: Dict[str, str]
    expected_guardrail: str
    expected_top5_focus: str
    expected_edi_direction: str
    expected_dri_direction: str
    expected_epi_direction: str


SCENARIOS = [
    Scenario(
        case_id="SIM-01",
        company="北浜精密工業株式会社",
        site="滋賀第二工場",
        theme="老朽設備型",
        profile=(
            "精密機械加工の第二工場。主要工作機械の多くが導入から20年以上経過しており、"
            "設備が古いこと自体は現場も認識している（WQ-101は『一部把握』-- 大まかな年式は"
            "把握しているが、当時の詳細な導入記録までは追えていない）。日常の故障記録は"
            "つけているが傾向分析まではしていない（WQ-102『記録のみ』）。基幹設備の一部には"
            "代替機があるが全てではない（WQ-103『一部ある』）。ただし、旧式機種の交換部品が"
            "今も供給されているかは、現在の担当者では把握できていない（WQ-104は不明回答の"
            "一つとして『分からない』とした -- 老朽設備特有の『そもそも分からない』を自然に"
            "反映）。電力・エネルギー管理は月次請求書の確認程度で特別な取り組みはない、"
            "建屋は比較的新しく問題なし、部門横断の管理体制は一部あるが、投資の判断基準は"
            "後継者不在の家族経営的な体質もあり、担当者が『不明』と回答した（2件目の"
            "Unknown）。安全・法令・供給継続に関わる重大な未解決課題は特にない。"
        ),
        forms_response={
            "WQ-001": "設備更新／保全",
            "WQ-101": "一部把握",
            "WQ-102": "記録のみ",
            "WQ-103": "一部ある",
            "WQ-104": "分からない",
            "WQ-201": "年数回確認",
            "WQ-202": "全体のみ",
            "WQ-203": "時間をかければ確認",
            "WQ-204": "一部実施",
            "WQ-301": "特になし",
            "WQ-302": "定期点検",
            "WQ-303": "影響なし",
            "WQ-401": "一部ある",
            "WQ-402": "不明",
            "WQ-403": "計画のみ",
            "WQ-404": "ない",
            "WQ-405": "1年以内",
            "WQ-501": "主要生産設備の一部が20年以上稼働しており、部品調達の見通しを確認したい。",
        },
        expected_guardrail="なし",
        expected_top5_focus="設備（年式・故障履歴・代替手段関連）",
        expected_edi_direction="中〜低",
        expected_dri_direction="中",
        expected_epi_direction="中",
    ),
    Scenario(
        case_id="SIM-02",
        company="アオバ紙工株式会社",
        site="千葉工場",
        theme="省エネ型",
        profile=(
            "段ボール原紙を加工する工場。電気料金高騰を受けて省エネに力を入れており、"
            "電力使用量・デマンドは毎月確認し（WQ-201『毎月確認』）、サブメーターで設備別の"
            "使用量まで詳細に把握している（WQ-202『詳細に把握』）。異常発生時も比較的迅速に"
            "原因を特定できる体制がある（WQ-203『迅速に確認』）。ただし省エネ改善そのものは"
            "一部の設備でしか実施できておらず、全社的な展開はこれから（WQ-204『一部実施』）。"
            "設備の年式管理・故障記録は必要最低限（WQ-101『一部把握』、WQ-102『記録のみ』、"
            "WQ-103『一部ある』、WQ-104『一部確認』）。建屋には結露が見られ、品質への影響の"
            "可能性がある程度は認識されている（WQ-301『結露』、WQ-303『影響の可能性』）。"
            "管理体制・投資基準は担当者ベースでの判断にとどまる。安全・法令上の重大な"
            "未解決課題はない。"
        ),
        forms_response={
            "WQ-001": "省エネ／投資優先順位",
            "WQ-101": "一部把握",
            "WQ-102": "記録のみ",
            "WQ-103": "一部ある",
            "WQ-104": "一部確認",
            "WQ-201": "毎月確認",
            "WQ-202": "詳細に把握",
            "WQ-203": "迅速に確認",
            "WQ-204": "一部実施",
            "WQ-301": "結露",
            "WQ-302": "問題時のみ",
            "WQ-303": "影響の可能性",
            "WQ-401": "一部ある",
            "WQ-402": "担当者ごと",
            "WQ-403": "案件ごと",
            "WQ-404": "ない",
            "WQ-405": "6か月以内",
            "WQ-501": "電気料金の高騰を受け、追加の省エネ余地がないか確認したい。",
        },
        expected_guardrail="なし",
        expected_top5_focus="エネルギー（省エネ改善・使用内訳関連）、建屋（結露）",
        expected_edi_direction="中",
        expected_dri_direction="中〜高",
        expected_epi_direction="低〜中",
    ),
    Scenario(
        case_id="SIM-03",
        company="サンライズ食品株式会社",
        site="宮崎第一食品工場",
        theme="建屋課題型",
        profile=(
            "惣菜・加工食品を製造する食品工場。梅雨時期に天井からの雨漏りが増えており、"
            "原材料保管エリアへの影響が心配されている（WQ-301『雨漏り』）。建屋の点検体制は"
            "ほとんど整っておらず（WQ-302『ほとんど未確認』）、品質への明確な影響がすでに"
            "出ている（WQ-303『明確な影響あり』）。この建屋起因の品質リスクは未解決のまま"
            "であり、WQ-404では『品質』を選択した。設備自体は年式・故障記録ともによく"
            "管理されており（WQ-101『把握している』、WQ-102『定期的に確認』、WQ-103"
            "『十分ある』、WQ-104『一部確認』）、電力管理も年数回の確認程度は行っている。"
            "省エネ改善は検討段階。部門横断の管理体制は一部あるが、投資の判断基準は"
            "工場長により『分からない』（担当者交代直後で引き継ぎが未完了という設定）。"
        ),
        forms_response={
            "WQ-001": "建屋・環境／保全",
            "WQ-101": "把握している",
            "WQ-102": "定期的に確認",
            "WQ-103": "十分ある",
            "WQ-104": "一部確認",
            "WQ-201": "年数回確認",
            "WQ-202": "一部把握",
            "WQ-203": "時間をかければ確認",
            "WQ-204": "検討のみ",
            "WQ-301": "雨漏り",
            "WQ-302": "ほとんど未確認",
            "WQ-303": "明確な影響あり",
            "WQ-401": "一部ある",
            "WQ-402": "分からない",
            "WQ-403": "計画のみ",
            "WQ-404": "品質",
            "WQ-405": "3か月以内",
            "WQ-501": "梅雨時期に天井からの雨漏りが増えており、原材料保管エリアへの影響が心配。",
        },
        expected_guardrail="品質・顧客要求 L2",
        expected_top5_focus="Guardrail課題（品質）、建屋（点検・事業影響）",
        expected_edi_direction="中〜低",
        expected_dri_direction="中",
        expected_epi_direction="高",
    ),
    Scenario(
        case_id="SIM-04",
        company="タカマル金属加工株式会社",
        site="岐阜工場",
        theme="BCP型",
        profile=(
            "自動車部品向けの金属プレス加工工場。基幹プレス機が1系統しかなく、故障時の"
            "代替手段が全くない（WQ-103『ない』）。しかもメーカー保守・交換部品の入手性を"
            "現在確認できていない（WQ-104『未確認』）。この供給継続リスクは経営層も把握して"
            "おり、WQ-404では『供給継続』を選択、対応期限も『3か月以内』と緊急性が高い。"
            "一方で、経営管理は比較的しっかりしており、部門横断の管理体制は明確にあり"
            "（WQ-401『明確にある』）、投資判断基準も明文化され（WQ-402『明文化済み』）、"
            "予算付きの中期計画も存在する（WQ-403『予算付き計画あり』）。建屋・環境面の"
            "課題も特になし。電力・エネルギー管理は年数回の確認や部分的な把握にとどまる"
            "平均的な水準（極端に悪くはしていない）。"
        ),
        forms_response={
            "WQ-001": "BCP・停電対策／保全",
            "WQ-101": "一部把握",
            "WQ-102": "記録のみ",
            "WQ-103": "ない",
            "WQ-104": "未確認",
            "WQ-201": "年数回確認",
            "WQ-202": "一部把握",
            "WQ-203": "時間をかければ確認",
            "WQ-204": "一部実施",
            "WQ-301": "特になし",
            "WQ-302": "定期点検",
            "WQ-303": "影響なし",
            "WQ-401": "明確にある",
            "WQ-402": "明文化済み",
            "WQ-403": "予算付き計画あり",
            "WQ-404": "供給継続",
            "WQ-405": "3か月以内",
            "WQ-501": "主力プレス機が1系統しかなく、故障時の生産停止リスクを相談したい。",
        },
        expected_guardrail="BCP・供給継続 L2",
        expected_top5_focus="Guardrail課題（供給継続）、設備（代替手段・EOL）",
        expected_edi_direction="中",
        expected_dri_direction="中〜高",
        expected_epi_direction="高",
    ),
    Scenario(
        case_id="SIM-05",
        company="はるかぜ精密計測株式会社",
        site="浜松テクニカルセンター",
        theme="比較的良好型",
        profile=(
            "精密計測機器の開発・小ロット製造を行うテクニカルセンター。設備の年式・"
            "故障履歴の把握、代替機の確保、保守体制のいずれも良好（WQ-101『把握している』、"
            "WQ-102『定期的に確認』、WQ-103『十分ある』、WQ-104『定期確認』）。部門横断の"
            "管理体制・投資判断基準も明文化されている。ただしエネルギー消費量は業種柄"
            "大きくないため、電力管理はそこまで頻繁ではない（WQ-201『年数回確認』、"
            "WQ-202『一部把握』、WQ-203『時間をかければ確認』、WQ-204『一部実施』）。"
            "建屋・環境に課題はなく、安全・法令上の重大な未解決課題もない。中期の設備投資"
            "計画は正式な予算化はまだで、案件が出るたびに個別検討している段階"
            "（WQ-403『案件ごと』）。特に急いで相談したい事項はない。"
        ),
        forms_response={
            "WQ-001": "投資優先順位／保全",
            "WQ-101": "把握している",
            "WQ-102": "定期的に確認",
            "WQ-103": "十分ある",
            "WQ-104": "定期確認",
            "WQ-201": "年数回確認",
            "WQ-202": "一部把握",
            "WQ-203": "時間をかければ確認",
            "WQ-204": "一部実施",
            "WQ-301": "特になし",
            "WQ-302": "定期点検",
            "WQ-303": "影響なし",
            "WQ-401": "明確にある",
            "WQ-402": "明文化済み",
            "WQ-403": "案件ごと",
            "WQ-404": "ない",
            "WQ-405": "時期未定",
            "WQ-501": "",
        },
        expected_guardrail="なし",
        expected_top5_focus="（B評価以上が少なければ無理に5件表示しない）",
        expected_edi_direction="高",
        expected_dri_direction="中〜高",
        expected_epi_direction="低",
    ),
]
