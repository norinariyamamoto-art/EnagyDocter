# Energy Doctor 診断Engine（Task 1A + Corrective Patch 1/1.1 + Engine Patch 2 + ED-DI-003 Final Pipeline Patch + ED-DI-001 Final Patch 実装）

`Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.3.md` の **Task 1** を実施した成果物。
その後、Rev0.4の **Corrective Patch 1**（ISS-02・ISS-03・ISS-06のみ）、そのレビューで
`ED-DI-003`として切り出された事項のうち実装側のみで対応可能な2点を適用した
**Corrective Patch 1.1**、そしてTask2のレビューで新規登録された`ED-DI-004`/`ED-DI-005`を
含むED-DI-002〜005のS社承認済み決定（Decision Record Rev0.1）を実装した
**Engine Patch 2**（情報充足率・分野別状態・要確認事項・Guardrail判定保留）を適用した。
その後、ED-DI-003の残る論点（情報充足率の集計粒度・閾値）についてS社が判断するための
比較データを作る **WQ Sufficiency Validation** を実施し、S社のFinal Disposition
（WQ単位粒度・50%閾値）確定を受けて、それを本番`diagnosis_status`判定へ統合する
**ED-DI-003 Final Pipeline Patch** を適用した。さらに、顧客向けUnknown表示標準を
「分からない」に正式統一するED-DI-001 Final Disposition（S社承認）を受け、V2.3正本内の
改訂対象箇所の特定（(A)/(B)区分）とコード側のInterim期記述の更新を行う
**ED-DI-001 Final Patch** を適用した（正本Excel自体の改訂はS社側作業）。各Patch/Validation
の修正内容・完了条件チェックリストは `PATCH1_NOTES.md` / `PATCH2_NOTES.md` /
`WQ_SUFFICIENCY_VALIDATION_REPORT.md` / `PATCH3_NOTES.md` / `PATCH4_NOTES.md` を参照。
`02_Diagnosis_Engine/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx`
（Engine v1.4）の `Web_EDI` / `Web_DRI` / `Web_EPI`、`Guardrail`、`TOP5_Calc` /
`TOP5_Final` のロジックを、Excelの数式のとおりにPythonで再現したもの。

**V2.2（`01_Core_Design/...V2.2.xlsx`）の正式EDI/DRI/EPI（Frozen KPI、シート
`13_算定式・順位ロジック`）はここでは実装していない。** Brief記載の「重要：KPIの
優先関係」のとおり、本実装が扱うのはEngine v1.4の公開18問による参考値
（Web_EDI/Web_DRI/Web_EPI）のみ。

## 構成

```
engine/
  energy_doctor_engine/
    excel_compat.py     Excelの計算クセ（空欄比較、AVERAGE、ROUND等）と、Unknown混在時
                         でも計算エラーを起こさない加重平均 weighted_score() を再現する共通関数
    forms_adapter.py     Forms Import Adapter / Normalizer（Corrective Patch 1 / ISS-02）
    wq_normalize.py      WQ_Normalizeシート（状態Score/緊急Score/Unknown/Evidence C）
    web_kpi.py            Web_KPIシート（Web_EDI / Web_DRI / Web_EPI、Engine Patch 2で
                           情報充足率(*_information_sufficiency)を追加）
    domain_status.py       Engine Patch 2 / ED-DI-004: 分野別状態（設備/エネルギー/建屋/管理）
    issue_candidate.py   Issue_Candidateシート（16課題のI/U/P/R/C/O、発火判定）
    review_items.py        Engine Patch 2 / ED-DI-005: 要確認事項（Unknownで発火しなかった課題）
    guardrail.py           Guardrailシート（安全・法令／品質・顧客要求／BCP・供給継続）
    top5_calc.py           TOP5_Calcシート（TOP_BASE→TOP_SCORE→暫定順位。Engine Patch 2で
                           U列の重み再正規化を廃止しUnknown=0代入方式へ変更）
    top5_final.py          TOP5_Finalシート（重複統合TOP-R02・分野上限TOP-R03・最終順位）
    pipeline.py             上記を正しい依存順序で実行する end-to-end 関数（Adapter適用、
                           ED-DI-003 Final Disposition: WQ単位情報充足率50%閾値によるdiagnosis_status
                           判定、TOP5はweb_dri_top5_rのみに依存し非連動、Guardrail→要確認事項→
                           TOP5の表示階層を含む）
    wq_sufficiency_validation.py  ED-DI-003 Final Disposition: WQ単位情報充足率の算出
                           （compute_wq_sufficiency()、pipeline.pyが本番判定に使用）。
                           40/50/60%3閾値比較（compute_wq_sufficiency_validation()）は
                           Validation当時の歴史的関数として維持（本番からは未使用）
  tests/
    fixtures.py             TC-A/B/Cの入力データ＋ISS-06検証用の3件同点フィクスチャ
    test_tc_a.py             TC-A: Excel実測値との厳密一致テスト
    test_tc_b.py             TC-B: 文章条件＋記載目標値の再現テスト
    test_tc_c.py             TC-C: 同上（安全・法令Guardrailの同点優先を含む）
    test_excel_compat.py    Excelの計算クセ共通関数の単体テスト
    test_corrective_patch1.py  Corrective Patch 1（ISS-02/03/06）の回帰テスト
    test_engine_patch2.py      Engine Patch 2（ED-DI-002/003/004/005）の回帰テスト
    wq_sufficiency_fixtures.py  WQ Sufficiency Validationの6境界ケース＋Final Patch検証用
                           Forms_Response
    test_wq_sufficiency_validation.py  WQ Sufficiency ValidationおよびED-DI-003 Final
                           Pipeline Patchの回帰テスト
  ISSUES.md                判断に迷った点・矛盾に見えた点の一覧
  COMPARISON.md             TC-A/B/CのExcel期待値とコード結果の比較表
  PATCH1_NOTES.md           Corrective Patch 1/1.1の修正内容・完了条件チェックリスト
  PATCH2_NOTES.md           Engine Patch 2の修正内容・新規フィールド仕様・完了条件チェックリスト
  WQ_SUFFICIENCY_VALIDATION_REPORT.md  WQ Sufficiency Validationの比較データ・重み按分根拠
  PATCH3_NOTES.md           ED-DI-003 Final Pipeline Patchの修正内容・完了条件チェックリスト
  PATCH4_NOTES.md           ED-DI-001 Final Patchの(A)/(B)一覧・Forms Implementation Spec整合確認・完了条件チェックリスト
  ED_DI_001_V2_3_VERIFICATION_REPORT.md  S社改訂後のV2.3正本の差分検証結果（31セル一致確認）
```

## 実行方法

```bash
cd engine
pip install pytest
python3 -m pytest -v
```

73件のテストがすべてPASSすることを確認済み（Task 1Aの19件＋Corrective Patch 1/1.1の17件＋
Engine Patch 2の17件＝既存53件、＋WQ Sufficiency Validationの18件＝既存71件、＋ED-DI-003
Final Pipeline Patchでの純増2件）。

## 正本との突合範囲

- **数式の抽出元：** `02_Diagnosis_Engine/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx`
  のシート `Forms_Response` / `WQ_Normalize` / `Issue_Candidate` / `Guardrail` /
  `Web_KPI` / `TOP5_Calc` / `TOP5_Final` / `Mock_Test_Cases`（openpyxlで
  `data_only=False`（数式）と`data_only=True`（値）の両方を読み、数式とその
  実際の計算結果を突き合わせた）。
- **入力語彙の裏取り：** `01_Core_Design/Energy_Doctor_LP_SelfDiagnosis_Design_V2.2.xlsx`
  シート `68_公開フォーム最小質問セット`（Engine v1.4の判定文字列と完全一致することを確認）。
- **参考確認（実装対象外）：** V2.2シート `04_Guardrail判定`（正式Guardrail、実装せず）、
  `03_Microsoft_Forms/...Implementation_Spec_v1.0.xlsx` シート `02_Questions` /
  `04_Engine_Mapping`（Forms選択肢文言の裏取り。Engine v1.4との不一致をISS-02として報告）。

## 各モジュールとExcelシートの対応（詳細はモジュール冒頭のdocstring）

| モジュール | Excelシート | 備考 |
|---|---|---|
| `wq_normalize.py` | `WQ_Normalize` | 状態Score(D)/緊急Score(E)の選択肢別マッピングをそのまま辞書化 |
| `web_kpi.py` | `Web_KPI` | Web_EDI/Web_DRI/Web_EPIの重み付き平均式をそのまま実装 |
| `issue_candidate.py` | `Issue_Candidate` | 16課題（IS/EN/BL/MG/GR/CU）のI/U/P/R/C/O/Guard加算/発火 |
| `guardrail.py` | `Guardrail` | 3カテゴリの該当判定・Priority Score |
| `top5_calc.py` | `TOP5_Calc` | TOP_BASE/TOP_SCORE/暫定順位（全16件対象のランキング） |
| `top5_final.py` | `TOP5_Final` | TOP-R02重複統合・TOP-R03分野上限（Corrective Patch 1で同点時も最大2件を徹底）・最終順位（候補のみのランキング） |
| `forms_adapter.py` | （Engine v1.4のシートに対応なし。Corrective Patch 1の新規Adapter層） | 「不明」「分からない」「空欄」を内部標準値`UNKNOWN`へ正規化 |
| `domain_status.py` | （Engine v1.4のシートに対応なし。Engine Patch 2の新規出力） | Web_EDIの分野内訳と同一グルーピングを独立出力（ED-DI-004） |
| `review_items.py` | （Engine v1.4のシートに対応なし。Engine Patch 2の新規出力） | Unknownで発火しなかった課題を「要確認事項」として検出（ED-DI-005） |
| `wq_sufficiency_validation.py` | （Engine v1.4のシートに対応なし。ED-DI-003 Final Disposition実装モジュール） | WQ単位情報充足率（本番`diagnosis_status`が使用）。40/50/60%比較は歴史的関数として維持 |

## Issue一覧・比較表

- 判断に迷った点・矛盾に見えた点 → `ISSUES.md`
- TC-A/B/CのExcel期待値とコード結果の比較 → `COMPARISON.md`
- Engine Patch 2の新規フィールド仕様・完了条件 → `PATCH2_NOTES.md`
- WQ Sufficiency Validation（ED-DI-003残論点の比較データ）→ `WQ_SUFFICIENCY_VALIDATION_REPORT.md`
- ED-DI-003 Final Pipeline Patch（本番統合の完了条件・変更点）→ `PATCH3_NOTES.md`
- ED-DI-001 Final Patch（顧客向けUnknown表示標準「分からない」への統一・改訂対象箇所の特定）→ `PATCH4_NOTES.md`
- ED-DI-001 V2.3正本改訂後の差分検証結果 → `ED_DI_001_V2_3_VERIFICATION_REPORT.md`

診断ロジック・しきい値・文言は一切変更していない。矛盾や解釈の分かれる箇所は
すべて`ISSUES.md`に列挙し、コード側で独自判断による修正は行っていない。
