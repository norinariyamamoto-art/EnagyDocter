# ED-DI-003 Final Pipeline Patch（本番Pipeline統合）実施報告

`ED_DI_003_FINAL_PIPELINE_PATCH_INSTRUCTION.md`に基づき、`Energy_Doctor_Design_Issue_Log.md`
のED-DI-003 Final Disposition（S社 Design Disposition Decision Record、「Final
Disposition Approved / Implementation Pending」、2026-09-02）を本番Pipelineへ実装統合した。
WQ Sufficiency Validation（前段の検証作業、`wq_sufficiency_validation.py`・
`WQ_SUFFICIENCY_VALIDATION_REPORT.md`）が提示した比較データのうち、**WQ単位粒度・50%閾値**
がS社の最終決定として確定し、今回はその実装確定のみを行った。粒度・閾値そのものの再選定は
行っていない。

Web_EDI/Web_DRI/Web_EPIの加重係数・算定式、TOP5の既存順位ロジック、Issue_CandidateのU値の
扱い、ISS-04/07/08、V2.2/V2.3・Forms実装仕様の正本ファイルは一切変更していない。ED-DI-001
（Unknown表示文言）にも一切触れていない。

## 1. Design Issue Logの記述とREADME.txtの記述に食随不一致がある旨の報告（Issue）

今回受領したzip内の`Energy_Doctor_Design_Issue_Log.md`本文は、ED-DI-003セクションの見出しが
依然として **「Implemented / Pilot Threshold & Granularity TBC」** のままであり（「残る論点
（Pilot前に正式決定が必要）」節も本文中に残存）、`README.txt`が述べる「ED-DI-003 status is
Final Disposition Approved / Implementation Pending」という記述と本文が一致していなかった。

`ED_DI_003_FINAL_PIPELINE_PATCH_INSTRUCTION.md`本文がFinal Dispositionの内容（粒度・閾値・
guardrail_urgencyの扱い・TOP5非連動等）を自己完結的に詳細記載していたため、本Patchは
指示書の記載を正として実装した。**ただし、S社側のログ更新作業がこの指示書の発行に追いついて
いない可能性があるため、次回のDesign Issue Log更新時にED-DI-003セクション本文（見出し・
「残る論点」節）を実際に「Final Disposition Approved」相当の記述へ更新することを推奨事項として
報告する。** 実装側で本ログファイルの内容を独自に書き換えることはしていない。

## 2. 変更したコード・テストの一覧

| ファイル | 変更内容 |
|---|---|
| `energy_doctor_engine/wq_sufficiency_validation.py` | モジュールdocstringを「Validation-only」から「ED-DI-003 Final Disposition」へ更新。`WQSufficiency`（`web_edi`/`web_dri`/`web_epi`の3フィールド）と`compute_wq_sufficiency()`を新設 -- `_wq_level_sufficiency()`と既存の3つのフラット重みテーブル（`_EDI_WQ_WEIGHTS`/`_DRI_WQ_WEIGHTS`/`_EPI_WQ_WEIGHTS`、ISS-04のWQ-403累積・virtual WQ-404スロットとも無変更）をそのまま流用。既存の`compute_wq_sufficiency_validation()`（40/50/60%比較）は`compute_wq_sufficiency()`を内部で呼ぶようリファクタしたのみで、シグネチャ・返り値は無変更（既存テストへの影響なし）。`pipeline.py`からの循環importを避けるため、`DIAGNOSIS_STATUS_OK`/`DIAGNOSIS_STATUS_INSUFFICIENT_DATA`の`pipeline`からのimportをやめ、同じ文字列値のローカル定数`_STATUS_OK`/`_STATUS_INSUFFICIENT_DATA`に置き換えた（`pipeline.py`が本モジュールをimportするようになったため、逆方向のimportは循環importになる）。 |
| `energy_doctor_engine/pipeline.py` | **`MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`（0.5、トップレベル項単位、TBC）を削除し、`MIN_WQ_SUFFICIENCY_THRESHOLD = 0.50`（WQ単位、Final Disposition、TBCではない）に置換。** `_meets_information_sufficiency()`（3KPI全ての項単位充足率が閾値以上かのAND判定）を削除し、`_wq_status(value, threshold=None)`（1KPI・1閾値の`>=`判定、モジュール変数を都度読み直す既存パターンを踏襲）に置換。`run_pipeline()`冒頭で`wq_sufficiency_validation.compute_wq_sufficiency()`を呼び、Web_EDI/DRI/EPIそれぞれの`_wq_status()`結果から`web_edi_status`/`web_dri_status`/`web_epi_status`を算出、3つのうち1つでもINSUFFICIENT_DATAなら全体`diagnosis_status`もINSUFFICIENT_DATAとする一般ロジックへ変更。**TOP5の計算可否を`_meets_information_sufficiency(web_kpi)`から`web_kpi.web_dri_top5_r is not None`のみへ変更**（全体diagnosis_statusから完全に独立させた）。`PipelineResult`に`web_edi_wq_sufficiency`/`web_dri_wq_sufficiency`/`web_epi_wq_sufficiency`（各`float`）と`web_edi_status`/`web_dri_status`/`web_epi_status`（各`str`）を追加（`web_kpi`直後、Guardrailセクションより前に配置）。 |
| `tests/test_engine_patch2.py` | `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`を参照していた2テストを更新（下記「3. 期待値が変わったテストの一覧」参照）。それ以外のED-DI-002/004/005関連テスト（domain_status、review_items、guardrail_pending、表示階層、Q-ID不使用等）は無変更のまま全PASS。 |
| `tests/test_wq_sufficiency_validation.py` | 構造的非接続ガードテスト（`test_changing_wq_sufficiency_module_never_touches_pipeline_constant`）を削除（前提そのものがFinal Dispositionにより意図的に覆されたため）。代わりに、本番`run_pipeline()`が`compute_wq_sufficiency()`と同一の値を使っていることを確認する`test_production_pipeline_uses_this_modules_wq_level_sufficiency`、および歴史的な40/50/60%比較関数`compute_wq_sufficiency_validation()`のstatus_at_50列が本番の`web_edi/dri/epi_status`と一致することを確認する`test_historical_validation_comparison_still_agrees_with_production_at_50_percent`を追加。Pattern6の整合性テスト（`test_pattern_6_is_consistent_with_guardrail_pending_and_review_items`）は`diagnosis_status == OK`というEngine Patch 2時点の期待値アサーションを削除（下記参照）。**完了条件3の中核テストとして`test_pattern_6_epi_only_insufficient_still_shows_top5_normally`を新設**（後述）。 |
| `tests/wq_sufficiency_fixtures.py` | `_unknown()`に`base`引数を追加（デフォルトは既存の`TC_B_FORMS_RESPONSE`のまま、既存6パターンは無変更）。新規フィクスチャ`PATTERN_6B_EPI_CRITICAL_WQS_UNKNOWN_TC_A_BASE`を追加 -- Pattern 6と同じWQ-405/303/104/404のUnknown集中だが、`TC_A_FORMS_RESPONSE`（実際に複数の課題が発火するケース）を土台にしたもの。Pattern 6自体の土台（`TC_B_FORMS_RESPONSE`）は全問が最良回答でそもそも1件も発火しないため、「Web_EPIのみ情報不足でもTOP5は通常表示される」ことを実証するには適さないと判明したための追加（詳細は完了条件3の項を参照）。 |
| `task2/run_scenarios.py` | `actual`辞書に`web_edi_wq_sufficiency`/`web_dri_wq_sufficiency`/`web_epi_wq_sufficiency`/`web_edi_status`/`web_dri_status`/`web_epi_status`を追加出力。コンソール出力にもwq_sufficiency行を追加。既存の出力項目（`web_kpi`以下、`guardrail_pending`、`review_items`、`top5`等）は一切変更していない。 |
| `task2/task2_results.json` | 上記スクリプト変更を反映して再生成。**既存フィールドの値はすべて無変更（追加のみ、`git diff`で確認済み）。** |
| `05_Handoff_Brief/Energy_Doctor_Design_Issue_Log.md`、`05_Handoff_Brief/ED_DI_003_FINAL_PIPELINE_PATCH_INSTRUCTION.md` | 受領した指示書一式をリポジトリへ反映（参照用、無改変）。 |
| `PATCH3_NOTES.md`（本ファイル）、`README.md` | 本Patchの変更内容・完了条件チェックリストを記録。READMEのモジュール対応表・実行方法を更新。 |

正本ファイル（V2.2/V2.3のxlsx、Forms実装仕様）は変更しておらず、`SHA256SUMS.txt`記載の
14ファイルすべてハッシュ一致を再確認済み。

## 3. 期待値が変わったテストの一覧（変更理由付き）

完了条件5が特に注意を促していた「全項目Unknownケースの期待値変更」を含め、実際に期待値が
変わったのは次の2件のみ。いずれも**閾値の粒度・数値そのものがFinal Dispositionで変わった
ことに伴う正当な更新**であり、TOP5/Guardrail/review_itemsの扱いには一切影響していない。

| テスト | 変更前 | 変更後 | 変更理由 |
|---|---|---|---|
| `test_threshold_is_a_named_constant_marked_tbc`（→`test_threshold_is_a_named_constant_marked_final`に改名） | `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`が存在し`"TBC"`を含むことを確認 | `MIN_WQ_SUFFICIENCY_THRESHOLD`が存在し`0.50`であること、docstringに`"Final Disposition"`・`"No longer TBC"`が含まれることを確認 | 定数そのものが名称・意味（粒度・TBC状態）ごと置き換わったため、テストの検証対象を新定数に合わせて更新。旧定数はコードから削除済みのため、旧テストのままでは`AttributeError`になる。 |
| `test_changing_the_threshold_changes_pipeline_behavior` | `monkeypatch.setattr(pipeline_module, "MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC", ...)` | 同じWQ-101〜104全Unknownのフィクスチャに対し`monkeypatch.setattr(pipeline_module, "MIN_WQ_SUFFICIENCY_THRESHOLD", ...)`（0.1→OK、0.99→INSUFFICIENT_DATA）へ更新 | 監視対象の定数名が変わったための機械的な追従。フィクスチャ・アサーション構造（閾値を変えるだけでOK/INSUFFICIENT_DATAが実際に反転することを証明する）は同じ。 |

なお、**全項目Unknownケースのテスト（`test_all_unknown_is_the_zero_sufficiency_special_case_of_the_threshold`）は期待値の変更なしでそのままPASSした。** 全項目UnknownはWQ単位でもEDI/DRI/EPIすべての充足率が0.0となり、0.5閾値を下回ることに変わりはないため。同様に`test_partial_unknown_reduces_information_sufficiency_by_its_declared_weight`（WQ-101〜104のみUnknown）も、WQ単位で計算し直した場合のEDI/DRI/EPI充足率（0.60/0.7133/0.75）がいずれも0.50以上のままであるため、`diagnosis_status == OK`という既存の期待値は変更不要だった。

一方、`test_pattern_6_is_consistent_with_guardrail_pending_and_review_items`（WQ
Sufficiency Validationフェーズで追加）は、**`assert result.diagnosis_status ==
DIAGNOSIS_STATUS_OK`という1行のみ削除した**（Web_EPIのみ情報不足になるこのケースで、
全体diagnosis_statusはFinal Disposition下ではINSUFFICIENT_DATAへ正しく変わるため、この
アサーションはFinal Disposition適用後は成立しなくなる）。guardrail_pending・review_items・
term-level information_sufficiencyの値そのものに関するアサーションは変更していない。

## 4. 完了条件（1〜8）への回答

| # | 完了条件 | 回答 |
|---|---|---|
| 1 | WQ単位・50%閾値が本番`diagnosis_status`判定として正式に組み込まれている | **実装済み。** `pipeline.py`の`MIN_WQ_SUFFICIENCY_THRESHOLD = 0.50`と`_wq_status()`、`run_pipeline()`冒頭での`compute_wq_sufficiency()`呼び出しにより実装。`test_production_pipeline_uses_this_modules_wq_level_sufficiency`で、`run_pipeline()`が返す値が`wq_sufficiency_validation.compute_wq_sufficiency()`の直接呼び出しと完全一致することを確認。 |
| 2 | Web_EDI/DRI/EPI個別の判定結果がPipelineResultから取得できる | **実装済み。** `PipelineResult.web_edi_status`/`web_dri_status`/`web_epi_status`（各`"OK"`/`"INSUFFICIENT_DATA"`）と、対応する`web_edi_wq_sufficiency`等の実測充足率を追加。 |
| 3 | Web_EPIのみ情報不足のケースで、TOP5が通常どおり表示されることをテストで明示的に確認する | **実装・確認済み。** `test_pattern_6_epi_only_insufficient_still_shows_top5_normally`（新設）が、WQ-405/303/104/404をUnknownにした`TC_A_FORMS_RESPONSE`ベースのケース（`PATTERN_6B_EPI_CRITICAL_WQS_UNKNOWN_TC_A_BASE`）で、`web_edi_status=="OK"`・`web_dri_status=="OK"`・`web_epi_status=="INSUFFICIENT_DATA"`・`diagnosis_status=="INSUFFICIENT_DATA"`でありながら`len(result.top5) > 0`（実測5件）であることを1つのテストでアサートしている。**注記：** WQ Sufficiency Validationフェーズの`PATTERN_6_EPI_CRITICAL_WQS_UNKNOWN`（`TC_B_FORMS_RESPONSE`ベース）をそのまま使うと、そもそも1件も課題が発火しないため`top5`が常に空になり、この完了条件を検証できないことが判明した（TC_Bは「全問が最良回答」というTOP5検証には向かない土台のため）。そのため、同じWQ-404/104/303/405のUnknown集中パターンを`TC_A_FORMS_RESPONSE`（複数課題が発火する）に適用した新フィクスチャを追加した。 |
| 4 | Guardrail・guardrail_pending・review_itemsが情報不足時にも保持されることの回帰確認 | **確認済み。** 上記`test_pattern_6_epi_only_insufficient_still_shows_top5_normally`内で`guardrail_pending is True`かつ`len(result.review_items) > 0`であることも同時にアサート。既存の`test_guardrail_pending_true_when_wq404_is_unknown`等（Engine Patch 2由来）も無変更のままPASS。 |
| 5 | 既存71テスト全PASS（期待値が変わるテストの一覧化） | **確認済み。** 上記「3. 期待値が変わったテストの一覧」を参照（2件のみ、いずれも定数名・粒度変更への機械的追従）。全項目Unknownケースを含む残り69件は期待値変更なしでPASS。新規テスト2件（`test_production_pipeline_uses_this_modules_wq_level_sufficiency`、`test_historical_validation_comparison_still_agrees_with_production_at_50_percent`、`test_pattern_6_epi_only_insufficient_still_shows_top5_normally`の計3件）を加え、削除1件（構造的非接続ガード、前提が覆されたため）を差し引いて**合計73件全PASS**（`python3 -m pytest -q`で確認）。 |
| 6 | Task2の5シナリオを再実行し、判定結果に納得性があるか確認する | **確認済み。** `task2/run_scenarios.py`を再実行し、5ケースすべてで新設の`web_edi/dri/epi_status`が`OK`となり、既存の`diagnosis_status`（全ケースOK）と整合していることを確認した（SIM-01: EDI=0.90/DRI=0.8667/EPI=0.875、SIM-03: DRI=0.95、他3ケースは全KPI 1.0 -- いずれも50%を大きく上回り、納得性のある結果）。既存フィールド（Web_KPI数値・Guardrail・TOP5・review_items）は`git diff`で追加行のみであることを確認し、数値変化がないことを保証した。 |
| 7 | 変更したコード・追加/変更したテストの一覧 | 本ファイル「2. 変更したコード・テストの一覧」を参照。 |
| 8 | ED-DI-003 Final Dispositionとして正式反映した内容の記録 | 本ファイル全体、および「5. Final Dispositionとして正式反映した内容」を参照。 |

## 5. Final Dispositionとして正式反映した内容

1. **情報充足率の正式集計粒度：WQ単位。** `wq_sufficiency_validation.py`のフラット展開方式
   （トップレベル項の重みをWQへ均等分割、同一WQが複数項にまたがる場合は累積）をそのまま
   正式仕様として採用。
2. **最低情報充足率Threshold：50%。** `pipeline.py`の`MIN_WQ_SUFFICIENCY_THRESHOLD = 0.50`、
   `>= 0.50` → OK、`< 0.50` → INSUFFICIENT_DATA。3KPI独立判定。
3. **Web_EPIのguardrail_urgencyスロット：virtual WQ-404として有効ウェイト0.125。** WQ-404が
   Unknownの場合、この0.125を未充足として扱う解釈を正式仕様として確定。
4. **全体diagnosis_statusと個別KPI値の分離。** 3KPIのいずれか1つでもINSUFFICIENT_DATAなら
   全体`diagnosis_status`もINSUFFICIENT_DATAとするが、50%以上の個別KPI値
   （`web_kpi.web_edi`/`web_dri`/`web_epi`）はそのまま保持・表示可能。
5. **TOP5/Issue_Candidateの計算可否とdiagnosis_statusの非連動。** TOP5・Issue_Candidateの
   計算可否は`web_dri_top5_r`が計算可能かどうかにのみ依存し、新設の全体`diagnosis_status`
   判定（EDI/EPI側の情報不足を含む）では抑止しない。
6. **Guardrail・guardrail_pending・review_itemsは情報不足時にも保持。** Engine Patch 2で
   確立した既存ルールを変更せず維持。

**Close未了事項（README.txtの「Close control」節どおり）：** 本Patchは実装統合のみであり、
ED-DI-003を完全CLOSEにするものではない。V2.2/V2.3側の正本改訂、顧客向け表示文言
（`INSUFFICIENT_DATA`等）の最終確認、および上記1節で報告したDesign Issue Log本文の
Final Disposition反映漏れの解消は、引き続きS社側の作業として残る。

## 6. テスト実行結果

```
cd engine
python3 -m pytest -v
```

73件全PASS（Task 1A 19件＋Corrective Patch 1/1.1 17件＋Engine Patch 2 17件＝既存53件、
＋WQ Sufficiency Validation 18件＝既存71件、＋本Patchでの純増2件（削除1件・新設3件）＝73件）。

## 7. 変更していないことの確認

- Web_EDI/Web_DRI/Web_EPIの加重係数・算定式自体（`web_kpi.py`）は無変更。
- TOP-R02・TOP-R03・TiePriority等、TOP5の既存順位ロジック（`top5_calc.py`/`top5_final.py`）は
  無変更。Issue_CandidateのU値の扱い（Unknown=0代入、再正規化なし）も無変更。
- ISS-04（WQ-403二重加重）・ISS-07・ISS-08はいずれもHOLDのまま変更していない。WQ単位充足率
  でもWQ-403の二重加重は重複排除せず累積のまま。
- 正本ファイル（V2.2/V2.3のxlsx、Forms実装仕様）は変更していない
  （`SHA256SUMS.txt`記載14ファイル、`test_adapter_does_not_rewrite_v22_or_forms_spec_files`
  で確認）。
- ED-DI-001（Unknown表示文言）には一切触れていない。
- 公開WQ回答から正式Qの個別回答値を自動生成・転記するロジックは追加していない
  （`test_no_formal_q_id_values_are_used`で構造的に確認）。

## 8. 残る確認事項（S社確認が必要）

- 上記1節：受領したDesign Issue Log本文がED-DI-003のFinal Disposition確定を反映しておらず、
  README.txtの記述とのみ整合している状態。次回ログ更新時の反映を推奨。
- `INSUFFICIENT_DATA`・個別KPIステータスの顧客向け表示文言（V2.3シート78の「表示文言の
  最終調整」として既に識別されている未確定事項、本Patchでは一切決定していない）。
- ED-DI-003の完全CLOSEに必要な残り作業（V2.2/V2.3正本改訂等）はS社側で継続。
