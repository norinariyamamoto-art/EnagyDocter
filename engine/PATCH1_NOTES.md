# Corrective Patch 1（ISS-02 / ISS-03 / ISS-06）実施報告

`Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`「Corrective Patch 1 指示」に基づき、
Task 1AでPASS済みの実装に対し、ISS-02・ISS-03・ISS-06のみを修正した。ISS-04・ISS-07・
ISS-08はHOLDのため変更していない。ED-DI-001・ED-DI-002は正本側Design Issueとして
`Energy_Doctor_Design_Issue_Log.md`でOPENのまま扱い、実装側では解消していない。

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
| 4 | Web_KPIで計算エラーが発生しないことを確認する | **確認済み。** `test_unknown_wq204_no_longer_crashes_web_dri_or_web_epi`・`test_unknown_wq403_no_longer_crashes_web_dri`・`test_unknown_wq405_no_longer_crashes_web_epi`で、Patch前に例外（`ExcelValueError`／`TypeError`）が発生していた3箇所（Web_DRIのWQ-204項・WQ-403項、Web_EPIのWQ-405項、およびTOP5_Calc全16行のU列＝WQ-405項）が、いずれもエラーなく計算されることを確認した。単一項目のUnknownに加え、16問すべてをUnknownにする極端なケースも試験し、この場合のみ「情報皆無」を表す専用の`InsufficientDataError`（Excelの#VALUE!とは別の、意図的に型付けされた例外）を送出することを確認した（`test_all_wq_unknown_raises_a_typed_insufficient_data_error`）。これは0点への丸め込みを避けつつ計算エラーを防ぐという指示に沿った、完全な情報欠如時の意図的な残存挙動であり、`ISSUES.md`ISS-03に明記した。 |
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
- **残存する未定義ケース**：16問全てがUnknownの場合、`InsufficientDataError`を送出する
  （0点/100点への強制丸めは行わない）。この場合にA3出力側でどう扱うべきかはビジネス
  ルールの決定事項であり、本Patchのスコープ外として報告のみとした。

ED-DI-001・ED-DI-002は`Energy_Doctor_Design_Issue_Log.md`にてOPENのまま、S社側の
Disposition待ちとして扱っている（実装側では書き換えていない）。
