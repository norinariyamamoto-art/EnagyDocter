# Energy Doctor 診断Engine（Task 1A + Corrective Patch 1 実装）

`Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.3.md` の **Task 1** を実施した成果物。
その後、Rev0.4の **Corrective Patch 1**（ISS-02・ISS-03・ISS-06のみ）を適用した。
Patch 1の修正内容・完了条件チェックリストは `PATCH1_NOTES.md` を参照。
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
    web_kpi.py            Web_KPIシート（Web_EDI / Web_DRI / Web_EPI）
    issue_candidate.py   Issue_Candidateシート（16課題のI/U/P/R/C/O、発火判定）
    guardrail.py           Guardrailシート（安全・法令／品質・顧客要求／BCP・供給継続）
    top5_calc.py           TOP5_Calcシート（TOP_BASE→TOP_SCORE→暫定順位）
    top5_final.py          TOP5_Finalシート（重複統合TOP-R02・分野上限TOP-R03・最終順位）
    pipeline.py             上記を正しい依存順序で実行する end-to-end 関数（Adapter適用含む）
  tests/
    fixtures.py             TC-A/B/Cの入力データ＋ISS-06検証用の3件同点フィクスチャ
    test_tc_a.py             TC-A: Excel実測値との厳密一致テスト
    test_tc_b.py             TC-B: 文章条件＋記載目標値の再現テスト
    test_tc_c.py             TC-C: 同上（安全・法令Guardrailの同点優先を含む）
    test_excel_compat.py    Excelの計算クセ共通関数の単体テスト
    test_corrective_patch1.py  Corrective Patch 1（ISS-02/03/06）の回帰テスト
  ISSUES.md                判断に迷った点・矛盾に見えた点の一覧
  COMPARISON.md             TC-A/B/CのExcel期待値とコード結果の比較表
  PATCH1_NOTES.md           Corrective Patch 1の修正内容・完了条件チェックリスト
```

## 実行方法

```bash
cd engine
pip install pytest
python3 -m pytest -v
```

35件のテストがすべてPASSすることを確認済み（Task 1Aの19件＋Corrective Patch 1の16件）。

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

## Issue一覧・比較表

- 判断に迷った点・矛盾に見えた点 → `ISSUES.md`
- TC-A/B/CのExcel期待値とコード結果の比較 → `COMPARISON.md`

診断ロジック・しきい値・文言は一切変更していない。矛盾や解釈の分かれる箇所は
すべて`ISSUES.md`に列挙し、コード側で独自判断による修正は行っていない。
