# Corrective Patch 1（ISS-02 / ISS-03 / ISS-06）実施報告

`Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`「Corrective Patch 1 指示」に基づき、
Task 1AでPASS済みの実装に対し、ISS-02・ISS-03・ISS-06のみを修正した。ISS-04・ISS-07・
ISS-08はHOLDのため変更していない。ED-DI-001・ED-DI-002は正本側Design Issueとして
`Energy_Doctor_Design_Issue_Log.md`でOPENのまま扱い、実装側では解消していない。

**2026-09-02追記：** Corrective Patch 1のレビュー結果（`Energy_Doctor_Design_Issue_Log.md`
2026-09-02更新版）を受け、ISS-02・ISS-06はRESOLVED、ISS-03はPARTIALLY RESOLVED / Design
Disposition Required（設計判断部分は新規`ED-DI-003`へ切り出し）と判定された。これに対応する
**Corrective Patch 1.1**（`ED-DI-003`のうち実装側で対応可能な2点のみ）の内容は、本ファイル末尾の
「Corrective Patch 1.1」セクションを参照。

## 1. 修正したコード一式（差分サマリ）

| ファイル | 変更内容 |
|---|---|
| `energy_doctor_engine/forms_adapter.py`（新規） | ISS-02: Forms Import Adapter / Normalizer。「不明」「分からない」「空欄」を内部標準値`"UNKNOWN"`へ正規化する`normalize_forms_response()`。WQ_Normalizeが採点する16問のみが対象（WQ-001/WQ-501は対象外）。 |
| `energy_doctor_engine/pipeline.py` | `run_pipeline()`冒頭で`normalize_forms_response()`を呼ぶよう変更。 |
| `energy_doctor_engine/wq_normalize.py` | `UNKNOWN_VALUES`に`"UNKNOWN"`を追加（既存の`"不明"`/`""`はそのまま維持）。 |
| `energy_doctor_engine/excel_compat.py` | ISS-03: `avg_or_none()`（全項目空欄なら例外でなくNoneを返す）、`weighted_score()`（空欄項を除外しウェイトを再正規化する汎用加重平均）、`InsufficientDataError`（全項目空欄の場合の専用例外）を新設。既存の`direct()`は未使用化したが、Task1Aの挙動記録として残置（テストも維持）。 |
| `energy_doctor_engine/web_kpi.py` | Web_EDI/Web_DRI/Web_EPIの計算を`weighted_score()`経由に変更。WQ-204/WQ-403/WQ-405の単独直接参照項が空欄でも例外を出さず、該当項を除外してウェイト再正規化するようにした。Web_EPIのWQ-204分岐も、空欄時に`blank_ge`の副作用（比較演算のテキスト優先ルール）に頼らず明示的にNoneとして`weighted_score`に渡すよう変更。guardrail_urgency分岐に`"UNKNOWN"`を追加。 |
| `energy_doctor_engine/top5_calc.py` | ISS-03関連の追加発見：Issue_CandidateのU列（全16課題が`WQ_Normalize!E19`を直接参照）も同種の空欄リスクがあったため、TOP_BASE計算を`weighted_score()`経由に変更。 |
| `energy_doctor_engine/issue_candidate.py` | BL-01・GR-01の発火(fire)条件に`"UNKNOWN"`除外を追加（従来の`"不明"`/`""`除外と同じ扱いにするため）。`IssueCandidate.u`の型を`float | None`に変更。 |
| `energy_doctor_engine/top5_final.py` | ISS-06: `_enforce_field_cap()`を新設。非Guardrail分野で候補(eligible)が2件を超える場合、スコア降順→TiePriority→シート記載順で上位2件のみ残す後処理。既存の分野内順位(G列)・候補判定(H列)・Final Rank・TiePriority・Guardrail例外・BL-01/BL-03特例は変更していない。 |
| `tests/fixtures.py` | ISS-06検証用の3件同点フィクスチャ`FIELD_CAP_TIE_FORMS_RESPONSE`を追加。 |
| `tests/test_corrective_patch1.py`（新規） | ISS-02/03/06の回帰テスト一式（詳細は完了条件2〜5を参照）。 |
| `ISSUES.md` | ISS-02/03/06に対応済みの旨を追記。ISS-04/07/08にHOLD・変更禁止の旨を明記。新規ISS-09（WQ-ID⇔Q-ID対応の確認結果、ED-DI-002関連）を追加。 |
| `05_Handoff_Brief/Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`、`Energy_Doctor_Design_Issue_Log.md`（リポジトリ直下） | 今回受領した最新の指示書・設計課題ログをリポジトリに反映（参照用）。 |

`01_Core_Design/...V2.2.xlsx`・`03_Microsoft_Forms/...Implementation_Spec_v1.0.xlsx`は
一切変更していない（`tests/test_corrective_patch1.py::test_adapter_does_not_rewrite_v22_or_forms_spec_files`
でSHA256突合により保証）。

## 2. 完了条件（1〜7）への回答

| # | 完了条件 | 回答 |
|---|---|---|
| 1 | ISS-02/03/06の修正内容を一覧化する | 上記「1. 修正したコード一式」の表を参照。各Issueの詳細な経緯・判断根拠は`ISSUES.md`の該当節（「Corrective Patch 1での対応」）に記載。 |
| 2 | TC-A/B/Cを再実行し、既存の期待値・順位が維持されることを確認する | **確認済み。** `tests/test_tc_a.py`（Excel実測値との厳密一致）・`test_tc_b.py`・`test_tc_c.py`は全てPatch適用後も無変更で全PASS。特にTC-Aについては`tests/test_corrective_patch1.py::test_top5_regression_tc_a_unchanged_after_patch`で、TOP5の並び・スコアがPatch前と1件も変わっていないことを重ねて確認した。 |
| 3 | 「不明」「分からない」「空欄」のUnknown入力テストを追加する | **追加済み。** `tests/test_corrective_patch1.py`内、`test_adapter_normalizes_all_three_unknown_spellings`ほか複数のテストで、WQ-101/WQ-204/WQ-301/WQ-403/WQ-404/WQ-405の各項目に対し「不明」「分からない」「空欄（""）」の3表記すべてを個別に投入し、いずれも同一の`UNKNOWN`正規化・同一の既定動作になることを確認した。 |
| 4 | Web_KPIで計算エラーが発生しないことを確認する | **確認済み。** `test_unknown_wq204_no_longer_crashes_web_dri_or_web_epi`・`test_unknown_wq403_no_longer_crashes_web_dri`・`test_unknown_wq405_no_longer_crashes_web_epi`で、Patch前に例外（`ExcelValueError`／`TypeError`）が発生していた3箇所（Web_DRIのWQ-204項・WQ-403項、Web_EPIのWQ-405項、およびTOP5_Calc全16行のU列＝WQ-405項）が、いずれもエラーなく計算されることを確認した。単一項目のUnknownに加え、16問すべてをUnknownにする極端なケースも試験した。**この極端なケースの扱い（Corrective Patch 1時点では`InsufficientDataError`という例外を送出していた）は、レビューで`ED-DI-003`の一部として指摘され、Corrective Patch 1.1で例外throwから正常系の`diagnosis_status`へ変更した。詳細は本ファイル末尾の「Corrective Patch 1.1」セクションを参照。** |
| 5 | TOP-R03の同点ケースで、同一分野最大2件になることを確認する | **確認済み。** `test_three_way_tie_is_capped_at_two_per_field`で、管理分野の3課題（MG-01/02/03）を意図的に完全同点（52.0）にした新規フィクスチャ`FIELD_CAP_TIE_FORMS_RESPONSE`を用い、候補(eligible)が2件（MG-01, MG-02）に制限され、3件目（MG-03）が除外されることを確認した。`test_field_cap_does_not_touch_guardrail_or_bl01_bl03_special_case`で、Guardrail分野の例外とBL-01/BL-03特例（ISS-05）が本修正の影響を受けていないことも確認した。 |
| 6 | 公開WQ-ID⇔正式Q-ID対応に不明点があればIssueとして報告する | **報告済み。** `ISSUES.md`ISS-09を新設。V2.2内にWQ-IDとQ-IDを結びつける正式な対応表は存在しないことを確認した（`ED-DI-002`の記載と一致）。名称類似から気づいた参考情報（例：WQ-103↔Q109、WQ-204↔Q224が完全同名）はISS-09に記録したが、正式な対応関係としては採用せず、実装（Unknown処理含む）には一切反映していない。 |
| 7 | ISS-04/07/08を変更していないことを明記する | **明記済み。** `tests/test_corrective_patch1.py::test_iss_04_07_08_are_unchanged`で、(a) Web_DRIのWQ-403二重加重（ISS-04）によりTC-AのWeb_DRIが36のまま変わらないこと、(b) Guardrail複数該当時の採用ロジック（ISS-07、Priority Score最大を採用する本実装の解釈）がTC-AでBCP・供給継続のまま変わらないこと、(c) WQ-301の複数選択時60点固定（ISS-08）が単一選択と複数選択で同一のWeb_EDIになることを回帰テストで固定した。`ISSUES.md`の該当節にもHOLD・変更禁止である旨を追記した。 |

## 3. テスト実行結果

```
cd engine
python3 -m pytest -v
```

35件全PASS（Task 1Aの19件＋Corrective Patch 1の16件）。内訳：
- `tests/test_tc_a.py`（5件）／`test_tc_b.py`（3件）／`test_tc_c.py`（3件）／`test_excel_compat.py`（8件）：Task 1Aから無変更で全PASS。
- `tests/test_corrective_patch1.py`（16件）：本Patchの新規テスト、全PASS。

## 4. 新たに見つかった不整合・解釈が必要な箇所（Issue一覧）

`ISSUES.md`を参照。今回新規に追加・更新した項目：

- **ISS-09（新規）**：公開WQ-ID⇔正式Q-IDの一意な対応はV2.2内で確認できなかった（`ED-DI-002`関連）。
- **ISS-03の追加判明事項**：Issue_CandidateのU列（全16課題が`WQ_Normalize!E19`を直接参照）も
  同種の#VALUE!リスクを抱えていたことが、Corrective Patch 1のテスト作成中に判明した（当初の
  Task1A時点のISS-03報告はWeb_KPIの3項目のみを対象としていたが、実際にはTOP5_Calc全体にも
  波及する、より広範な問題だった）。
- **`ED-DI-003`（新規・レビューで判明）**：`weighted_score()`の「Unknown項目を除外し残り
  ウェイトを再正規化する」方式は、V2.2が定めた唯一の仕様ではなく、S社Disposition待ちの
  暫定実装であることが判明した。正本側Design Issueとして切り出し、実装側では再正規化方式
  自体を決定・変更していない。詳細は`ISSUES.md`ISS-03節および本ファイル末尾の
  「Corrective Patch 1.1」セクションを参照。

ED-DI-001・ED-DI-002・ED-DI-003は`Energy_Doctor_Design_Issue_Log.md`にてOPENのまま、S社側の
Disposition待ちとして扱っている（実装側では書き換えていない）。

---

# Corrective Patch 1.1（`ED-DI-003`のうち実装側で対応可能な2点のみ）実施報告

`Energy_Doctor_Design_Issue_Log.md`の`ED-DI-003`「暫定実装方針」に記載された推奨
（「例外ではなく`diagnosis_status = INSUFFICIENT_DATA`のような正常な業務状態として返す設計に
変更することを推奨する（Corrective Patch 1.1で対応予定）」）に基づき、`ED-DI-003`の4決定事項
（①ウェイト再正規化方式の正式採否、②Issue_CandidateのU値への適用可否、③全項目Unknown時の
挙動、④最低情報充足率の設定要否）のうち、**③（全項目Unknown時の挙動）に含まれる「例外か
正常系状態か」という実装スタイルの問題のみ**を対応した。①②④、および再正規化方式そのもの
（重みの配分ロジック）は一切決定・変更していない。

## 1. 修正したコード・テストの一覧

| ファイル | 変更内容 |
|---|---|
| `energy_doctor_engine/excel_compat.py` | **修正1：** `weighted_score()`が全項目Unknown（ウェイト合計0）の場合に送出していた`InsufficientDataError`（例外throw）を、`None`を返す方式に変更。**修正2：** `weighted_score()`・`InsufficientDataError`のdocstringに、この再正規化方式が`ED-DI-003`としてS社Disposition待ちの暫定仕様であり、他の代替案（非正規化・情報不足扱い・信頼度低下表示）も同様に成立し得る旨を明記。 |
| `energy_doctor_engine/web_kpi.py` | `WebKPI`の全フィールドを`Optional`化。`_edi_band`/`_dri_band`/`_dri_top5_r`/`_epi_band`を`None`セーフに変更（`None`入力時は`None`を返す）。`_round_or_none()`を新設し、`weighted_score()`が`None`を返した場合に`excel_round(None)`を呼ばないようにした。モジュールdocstringに`ED-DI-003`への参照を追記。 |
| `energy_doctor_engine/pipeline.py` | `DIAGNOSIS_STATUS_OK`（`"OK"`）・`DIAGNOSIS_STATUS_INSUFFICIENT_DATA`（`"INSUFFICIENT_DATA"`）を新設。`PipelineResult`に`diagnosis_status`フィールドを追加。Web_EDIまたはWeb_DRIが`None`（算出不能）の場合、Guardrail評価・Issue_Candidate生成・TOP5計算を一切行わず、`diagnosis_status=INSUFFICIENT_DATA`・Guardrail/TOP5関連フィールドを空リスト/`None`として返すよう変更。 |
| `energy_doctor_engine/__init__.py` | `DIAGNOSIS_STATUS_OK`・`DIAGNOSIS_STATUS_INSUFFICIENT_DATA`をパッケージのpublic APIとしてエクスポート。 |
| `tests/test_corrective_patch1.py` | `test_weighted_score_all_blank_raises`→`test_weighted_score_all_blank_returns_none_not_an_exception`に置き換え（`None`が返ることを確認）。`test_all_wq_unknown_raises_a_typed_insufficient_data_error`→`test_all_wq_unknown_returns_insufficient_data_status_not_an_exception`に置き換え（例外が発生せず、`diagnosis_status`・各KPI・Guardrail/TOP5が仕様どおりになることを確認）。`test_known_tc_a_still_reports_ok_status`を新規追加（通常入力では`diagnosis_status=="OK"`になることの回帰確認）。 |
| `ISSUES.md` | ISS-02/06を**RESOLVED**、ISS-03を**PARTIALLY RESOLVED / Design Disposition Required**に更新。新規`ED-DI-003`節を追加し、Corrective Patch 1.1の対応内容を明記。ISS-09を「独立Design Issueではなく`ED-DI-002`の実装側確認結果」という位置づけに合わせて微修正（内容自体は変更なし）。 |
| `PATCH1_NOTES.md`（本ファイル） | 本セクションおよび冒頭の追記を新規作成。 |
| `05_Handoff_Brief/Energy_Doctor_Design_Issue_Log.md` | S社から受領した更新版（`ED-DI-003`追加・ISS-02/03/06のステータス更新版）に差し替え。 |

`weighted_score()`による再正規化の計算方式自体、および`top5_calc.py`（Issue_CandidateのU値への
適用範囲）は一切変更していない。`ISS-04`/`ISS-07`/`ISS-08`、`V2.2`・Forms実装仕様の各ファイルも
引き続き変更していない。

## 2. 完了条件（1〜4）への回答

| # | 完了条件 | 回答 |
|---|---|---|
| 1 | 全項目Unknown時の挙動が、例外ではなく判定可能な正常結果になっていることをテストで示す | **確認済み。** `tests/test_corrective_patch1.py::test_all_wq_unknown_returns_insufficient_data_status_not_an_exception`で、16問すべてUnknownの入力に対し`run_pipeline()`が例外を送出せず、`result.diagnosis_status == "INSUFFICIENT_DATA"`、`result.web_kpi.web_edi is None`、`result.web_kpi.web_dri is None`、`result.guardrail_entries == []`、`result.top_guardrail is None`、`result.issue_candidates == []`、`result.top5_calc == []`、`result.top5_final == []`、`result.top5 == []`をすべて確認した。あわせて`tests/test_corrective_patch1.py::test_weighted_score_all_blank_returns_none_not_an_exception`で、`weighted_score()`単体が例外ではなく`None`を返すことも直接確認した。 |
| 2 | 既存のTC-A/B/C、Corrective Patch 1の16テストが引き続き全てPASSすること | **確認済み。** `tests/test_tc_a.py`・`test_tc_b.py`・`test_tc_c.py`・`test_excel_compat.py`・Corrective Patch 1由来の既存16テストはすべて無変更でPASS。加えて`tests/test_corrective_patch1.py::test_known_tc_a_still_reports_ok_status`を新規追加し、通常入力（TC-A）では`diagnosis_status=="OK"`になることも回帰確認した。合計テスト数は36件（詳細は下記セクション3）。 |
| 3 | 変更したコード・テストの一覧 | 上記「1. 修正したコード・テストの一覧」の表を参照。 |
| 4 | docstring / ISSUES.md / PATCH1_NOTES.mdへのED-DI-003参照追記箇所の一覧 | **`excel_compat.py`**：`weighted_score()`のdocstring（"IMPORTANT -- ED-DI-003"の段落と"All-blank"の段落）、`InsufficientDataError`のクラスdocstring。**`web_kpi.py`**：モジュール冒頭のdocstring。**`pipeline.py`**：モジュール冒頭のdocstringと`DIAGNOSIS_STATUS_INSUFFICIENT_DATA`のdocstring。**`ISSUES.md`**：「現在の状況」表（ED-DI-003の行を追加）、ISS-03節の見出しと本文（新設した`### ED-DI-003｜...`小節と`### Corrective Patch 1.1での対応`小節）。**`PATCH1_NOTES.md`**：本ファイル冒頭の追記、および本セクション全体。 |

## 3. テスト実行結果

```
cd engine
python3 -m pytest -v
```

36件全PASS（Task 1Aの19件＋Corrective Patch 1の16件＋Corrective Patch 1.1で1件純増
［既存2件を置き換え、新規1件`test_known_tc_a_still_reports_ok_status`を追加］）。

## 4. 変更していないことの確認

- 再正規化の計算方式自体（`weighted_score()`が空欄項を除外し残りウェイトを合計1に
  再正規化するロジック）は一切変更していない。
- `Issue_Candidate`のU値（`top5_calc.py`での`weighted_score()`適用）への同ルールの適用範囲は
  今回拡張・変更していない。
- `ISS-04`（WQ-403二重加重）・`ISS-07`（Guardrail複数該当時の表示優先）・`ISS-08`（WQ-301複数
  選択時60点固定）はいずれも変更していない（`test_iss_04_07_08_are_unchanged`で回帰確認済み、
  Corrective Patch 1.1でも無変更）。
- `01_Core_Design/...V2.2.xlsx`・`03_Microsoft_Forms/...Implementation_Spec_v1.0.xlsx`は
  一切変更していない（`test_adapter_does_not_rewrite_v22_or_forms_spec_files`でSHA256突合により
  保証、Corrective Patch 1.1でも無変更）。
