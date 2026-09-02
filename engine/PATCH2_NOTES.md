# Engine Patch 2（ED-DI-002〜005 承認済み決定の実装）実施報告

`ENGINE_PATCH2_INSTRUCTION.md`に基づき、Corrective Patch 1/1.1適用済みの現行Engine
（`energy_doctor_engine`）に対し、S社承認済み（`Energy_Doctor_Design_Issue_Log.md`
2026-09-02更新版、Decision Record Rev0.1）のED-DI-002〜005を実装した。ED-DI-002は
ドキュメント参照追記のみ（計算ロジック変更なし）。Web_EDI/Web_DRI/Web_EPIの加重係数・
算定式、TOP-R03等TOP5の既存順位ロジック、ISS-04/07/08、V2.2/V2.3の正本ファイルは
一切変更していない。

## 1. 変更したコード・テストの一覧

| ファイル | 変更内容 |
|---|---|
| `energy_doctor_engine/excel_compat.py` | ED-DI-003: `weighted_score()`の戻り値を`WeightedScoreResult(value, information_sufficiency)`に変更。docstringを「暫定実装／S社Disposition待ち」から「ED-DI-003 Approved Disposition（正式仕様として確定）」へ更新し、V2.2/V2.3シート13のCM-02（正式EDI/DRI/EPIの同種ルール）との対応関係を明記。`InsufficientDataError`のdocstringも更新。 |
| `energy_doctor_engine/web_kpi.py` | `WebKPI`に`web_edi_information_sufficiency`・`web_dri_information_sufficiency`・`web_epi_information_sufficiency`（各float, 0〜1）を追加。モジュールdocstringにED-DI-004 Approved Disposition（Web_EDIの位置付け＝「事業所全体の総合状態を示す参考指数」、worst-domain penalty不採用の旨）を明記。加重係数・算定式そのものは無変更。 |
| `energy_doctor_engine/top5_calc.py` | ED-DI-003 point 5: TOP_BASE計算から`weighted_score()`を除去し、U(WQ-405由来)がUnknownの場合は0を代入するだけの素の式に変更（他の重みは再正規化しない）。I/P/R/C/OはUnknownになり得ないため、この式が例外を出すことはない。 |
| `energy_doctor_engine/issue_candidate.py` | `IssueCandidate.r`の型を`Optional[float]`に変更（INSUFFICIENT_DATA時にWeb_DRIのTOP5用Rが未定義でも`build_issue_candidates()`自体は呼べるようにするため）。モジュールdocstringにED-DI-002 Approved（V2.3シート77参照）を追記。既存の発火(fire)判定ロジックは無変更。 |
| `energy_doctor_engine/guardrail.py` | モジュールdocstringにED-DI-002 Approved（WQ-404のGuardrail対象正式Q-IDが`Q101/Q103/Q104/Q106/Q108/Q109/Q110/Q112/Q404/Q408`に閉じたこと、およびそれがguardrail_pendingの根拠であること）を追記。判定ロジック自体は無変更。 |
| `energy_doctor_engine/domain_status.py`（新規） | ED-DI-004: `DomainStatus`（設備/エネルギー/建屋/管理）と`compute_domain_status()`。Web_EDIの算定で使っている4分野の内訳（`avg_or_none`による同一グルーピング）をWeb_EDIとは独立した出力として再計算する。Web_EDIの数式・加重係数には一切影響しない。 |
| `energy_doctor_engine/review_items.py`（新規） | ED-DI-005 point 1: `ReviewItem`と`compute_review_items()`。Issue_Candidateが発火しなかった原因がその課題の主たるWQ（`main_wq`、BL-03のみ2問）のUnknownである場合に限り「要確認事項」として検出する。既存の`issue_candidate.py`のロジックには一切手を加えず、計算済みの`issue_candidates`結果を事後的に読み取るだけ。WQ-501（自由記述、CU-01）は対象外。 |
| `energy_doctor_engine/pipeline.py` | ED-DI-003 point 3/4: `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`（仮値0.5、TBCコメント付き）を新設し、`_meets_information_sufficiency()`で3KPIすべての情報充足率がこの閾値以上かを判定、`diagnosis_status`をこの条件に一般化（全項目Unknownは充足率0という特殊ケースとして自然に包含）。ED-DI-005: `guardrail_pending`（WQ-404がUnknownかどうか）、`review_items`、`domain_status`を`PipelineResult`へ追加。**表示階層（Guardrail→要確認事項→TOP5）を反映し、Guardrail・review_itemsはdiagnosis_statusに関わらず常に計算するよう変更**（Corrective Patch 1.1では全項目Unknown時にGuardrailも非表示にしていたが、ED-DI-005の「重大事項の未確認を非表示にしない」という方針にあわせて変更。TOP5（TOP5_Calc/TOP5_Final）のみ、情報充足率が閾値未満の場合は引き続き空で返す）。 |
| `engine/tests/test_engine_patch2.py`（新規） | ED-DI-002〜005の回帰テスト一式（17件）。詳細は完了条件1〜8を参照。 |
| `engine/tests/test_corrective_patch1.py` | `weighted_score()`の戻り値変更に伴うテスト2件の修正。全項目Unknown時のテストを、Guardrail/review_itemsがもう空にならない新しい挙動に合わせて更新。V2.3ファイルの無改変確認をSHA256突合テストに追加。 |
| `task2/run_scenarios.py`、`task2/task2_results.json`、`task2/TASK2_REPORT.md`、`task2/README.md` | Task2の5シナリオをEngine Patch 2適用後に再実行し、新規フィールド（information_sufficiency、domain_status、guardrail_pending、review_items）の出力を追記・報告。**入力データ（Profile・Forms_Response）自体は変更していない。** |
| `05_Handoff_Brief/`、`01_Core_Design/` | 受領したPatch2指示書・V2.3正本・最新Design Issue Log・S社決定記録をリポジトリに反映（参照用、無改変）。 |
| `SHA256SUMS.txt` | 新規配置したV2.3ファイルのSHA256を追記（今後の無改変確認用）。 |

## 2. 新規出力フィールドの仕様一覧

### `WebKPI`（`web_kpi.py`）

| フィールド | 型 | 説明 |
|---|---|---|
| `web_edi_information_sufficiency` | `float`（0〜1） | Web_EDI算定式の4項（設備40%/エネルギー20%/建屋20%/管理20%）のうち、実際に回答済みだった項の宣言ウェイト比率。1.0＝全項目回答済み、0.0＝全項目Unknown。 |
| `web_dri_information_sufficiency` | `float`（0〜1） | Web_DRI算定式（5項、WQ-403の二重加重含む）についての同様の比率。 |
| `web_epi_information_sufficiency` | `float`（0〜1） | Web_EPI算定式（4項）についての同様の比率。guardrail_urgency項（WQ-404由来）は常に値を持つため、単独では0にならない。 |

**粒度に関する注記（TBCの一部として明記）：** 上記は各KPI算定式の**トップレベルの加重項単位**（例：Web_EDIなら4分野グループ単位）での充足率であり、個々の質問1問単位の充足率ではない。例えばWeb_EDIの設備グループ（WQ-101〜104の4問）のうち1問だけがUnknownでも、そのグループ自体は残り3問の平均値を持つため、information_sufficiencyの計算上は「回答あり」として扱われる（グループ全体がUnknownになって初めてそのグループ分のウェイトが充足率から差し引かれる）。この粒度選択は、Web_KPIの実際の数式構造（入れ子の加重平均）とバイトレベルで一致させ、別建ての質問単位ウェイト表を保守する二重管理リスクを避けるための実装判断であり、S社が確認すべき事項として`excel_compat.py`の`WeightedScoreResult.information_sufficiency`のdocstringに明記した。

### `DomainStatus`（`domain_status.py`、`PipelineResult.domain_status`）

| フィールド | 型 | 説明 |
|---|---|---|
| `equipment` | `Optional[int]` | 設備分野の状態（WQ-101,102,103,104の平均、Web_EDIの40%項と同一グルーピング） |
| `energy` | `Optional[int]` | エネルギー分野の状態（WQ-201,202,204の平均、Web_EDIの20%項と同一） |
| `building` | `Optional[int]` | 建屋分野の状態（WQ-301,302,303の平均、Web_EDIの20%項と同一） |
| `management` | `Optional[int]` | 管理分野の状態（WQ-401,403の平均、Web_EDIの20%項と同一） |

Web_EDIとは独立して算出・出力される（Web_EDI自体の値の有無に関わらず、対応する分野に
1問でも回答があれば値を持つ）。

### `ReviewItem`（`review_items.py`、`PipelineResult.review_items`）

| フィールド | 型 | 説明 |
|---|---|---|
| `issue_id` | `str` | 発火しなかったIssue_CandidateのID（例：`IS-04`） |
| `field` | `str` | 分野（設備／エネルギー／建屋／管理／Guardrail） |
| `name` | `str` | 課題名称 |
| `reason_wq` | `tuple[str, ...]` | Unknownだった原因WQ（通常1件、BL-03のみ最大2件） |

「発火しなかった」かつ「その主たるWQがUnknown」の場合のみ生成される（良好な回答で
発火しなかった場合や、WQ-501自由記述由来のCU-01は対象外）。

### `guardrail_pending`（`pipeline.py`、`PipelineResult.guardrail_pending`）

| 型 | 説明 |
|---|---|
| `bool` | `True`＝WQ-404がUnknown（Adapterで「不明」「分からない」「空欄」から正規化されたもの）であり、Guardrail判定そのものが保留状態。`False`＝WQ-404は回答済み（Guardrailが発動した場合・「ない」で確定して非該当の場合の両方を含む）。`guardrail_entries`・`top_guardrail`だけでは「確定して非該当」と「判定保留」を区別できないため、本フィールドで明示する。 |

### `diagnosis_status`（既存フィールドの判定条件を一般化）

`DIAGNOSIS_STATUS_OK` / `DIAGNOSIS_STATUS_INSUFFICIENT_DATA`の2値は変更していないが、
判定条件を「Web_EDI/Web_DRIがNone」から「Web_EDI・Web_DRI・Web_EPIのいずれかの
information_sufficiencyが`MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`（仮値0.5、
`pipeline.py`で定義、TBCコメント明記）未満」へ一般化した。全項目Unknownはこの条件の
充足率0という特殊ケースとして自然に含まれる。

**表示階層の変更点：** `INSUFFICIENT_DATA`の場合でも、Guardrail関連フィールド
（`guardrail_pending`／`guardrail_entries`／`top_guardrail`）とIssue_Candidate関連
フィールド（`issue_candidates`／`review_items`）は引き続き計算される。空になるのは
`top5_calc`／`top5_final`／`top5`のみ（Web_DRI由来のTOP5用Rが未定義のため）。

## 3. 完了条件（1〜9）への回答

| # | 完了条件 | 回答 |
|---|---|---|
| 1 | 情報充足率（Web_EDI/DRI/EPIごと）を計算・出力する実装 | **実装済み。** `excel_compat.py`の`weighted_score()`が`WeightedScoreResult(value, information_sufficiency)`を返すよう変更し、`web_kpi.py`で3KPIそれぞれの`*_information_sufficiency`として`WebKPI`に格納した。`tests/test_engine_patch2.py::test_fully_answered_case_has_full_information_sufficiency`・`test_partial_unknown_reduces_information_sufficiency_by_its_declared_weight`で確認。 |
| 2 | 情報充足率の最低閾値を仮値として定義し、閾値未満でINSUFFICIENT_DATAになることをテストで確認する（閾値はTBCである旨を明記） | **実装・確認済み。** `pipeline.py`の`MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC = 0.5`（TBCの理由をdocstringで詳述、V2.2/V2.3シート13 CM-03の50%規定を参考にした旨も明記）。`test_threshold_is_a_named_constant_marked_tbc`で名前付き定数であることとTBC表記を確認。`test_changing_the_threshold_changes_pipeline_behavior`で、同一入力に対し閾値を0.1→OK、0.99→INSUFFICIENT_DATAへ変えるだけで実際に`run_pipeline()`の結果が変わることを確認した（デフォルト引数の束縛タイミングの問題を避けるため、関数内で都度モジュール変数を読み直す実装にした）。 |
| 3 | 分野別状態（設備/エネルギー/建屋/管理）をWeb_EDIと独立して出力する実装とテスト | **実装・確認済み。** `domain_status.py`の`DomainStatus`/`compute_domain_status()`を新設し、`PipelineResult.domain_status`として公開。`test_domain_status_matches_web_edi_internal_components`・`test_domain_status_is_independent_of_web_edi_when_one_domain_is_unknown`で、Web_EDIの内部集計と同じ値になること、およびWeb_EDI自体の可否とは独立して個別の分野が算出されることを確認した。`test_web_edi_weights_are_unchanged`でWeb_EDIの加重係数・算定式が無変更であることも回帰確認した。 |
| 4 | review_items（要確認事項）の実装とテスト | **実装・確認済み。** `review_items.py`の`ReviewItem`/`compute_review_items()`を新設。`test_review_items_surface_issues_suppressed_by_unknown_answers`でTask2 SIM-01の実例（IS-04/MG-02）を再現、`test_review_items_excludes_issues_that_simply_have_a_good_answer`で「良好な回答による非発火」は対象外であること、`test_review_items_excludes_cu01_free_text`でWQ-501自由記述由来のCU-01が対象外であることを確認した。`test_issue_candidate_scoring_logic_is_unchanged`で既存の発火ロジック自体が無変更であることも回帰確認した。 |
| 5 | guardrail_pending（Guardrail判定保留）の実装とテスト | **実装・確認済み。** `pipeline.py`に`guardrail_pending`フィールドを追加。`test_guardrail_pending_true_when_wq404_is_unknown`で「不明」「分からない」「空欄」いずれのWQ-404回答でも`True`になることを確認。`test_guardrail_pending_false_and_distinguishable_from_confirmed_clean`で、Guardrail発動時・確定non-該当（「ない」）時のいずれも`False`になり、`top_guardrail`だけでは区別できない両状態を本フィールドが正しく区別することを確認した。 |
| 6 | 既存の全テスト（Task1＋Corrective Patch1/1.1、計36件）が引き続きPASSすること | **確認済み。** `tests/test_tc_a.py`・`test_tc_b.py`・`test_tc_c.py`・`test_excel_compat.py`・`test_corrective_patch1.py`の既存36件（2件はweighted_score()の戻り値変更、1件はGuardrail非表示解除に伴い期待値のみ更新、ロジック自体のテスト意図は維持）はすべてPASS。新規`test_engine_patch2.py`17件を含め、合計53件全PASS。 |
| 7 | Task2の5シナリオを再実行し、新機能が違和感のない値になっているか確認すること（特にSIM-01/03のUnknown事例がreview_itemsに正しく出るか） | **確認済み。** `task2/run_scenarios.py`を再実行し、SIM-01でIS-04(WQ-104)・MG-02(WQ-402)、SIM-03でMG-02(WQ-402)がreview_itemsに正しく出現することを確認した。5ケースすべてでWeb_EDI/DRI/EPIの数値・帯評価・Guardrail判定・TOP5の順位とスコアが、Engine Patch 2適用前と完全に一致することも確認した（加重係数・TOP5ロジック無変更の裏付け）。詳細は`task2/TASK2_REPORT.md`の「追記（2026-09-02）」を参照。 |
| 8 | ED-DI-002〜005について、正本の制約（自動転記禁止、加重係数不変、TOP5ロジック不変）を破っていないことの確認 | **確認済み。** (a) 自動転記禁止：`issue_candidate.py`等のスコアリングロジックは公開WQのみを参照し、正式Q-IDの値を一切生成・参照していない。`test_no_formal_q_id_values_are_used`で、Engine実装ファイル中に正式Q-IDのリテラル（`"Q101"`等）が一切存在しないことを構造的に確認した。(b) 加重係数不変：`test_web_edi_weights_are_unchanged`でTC-AのWeb_EDIが43のまま変わらないことを確認（Web_DRI/EPIも既存のTC-A/B/Cテストで36/80等が無変更のままPASS）。(c) TOP5ロジック不変：`test_tc_a.py::test_top5_order_matches_excel_exactly`、Corrective Patch 1由来の`test_three_way_tie_is_capped_at_two_per_field`等が無変更でPASSしており、TOP-R02/TOP-R03/TiePriority等のロジックに変更がないことを確認した。 |
| 9 | 変更したコード・テストの一覧、新規出力フィールドの仕様一覧をレポートとして提出 | 本ファイル「1. 変更したコード・テストの一覧」「2. 新規出力フィールドの仕様一覧」を参照。 |

## 4. テスト実行結果

```
cd engine
python3 -m pytest -v
```

53件全PASS（Task 1A 19件＋Corrective Patch 1/1.1 17件＋Engine Patch 2 17件）。

## 5. 変更していないことの確認

- Web_EDI/Web_DRI/Web_EPIの加重係数（40/20/20/20等）・算定式自体は一切変更していない。
- TOP-R02（重複統合）・TOP-R03（同一分野最大2件）・TiePriority等、TOP5の既存順位ロジックは
  一切変更していない。
- ISS-04（WQ-403二重加重）・ISS-07（Guardrail複数該当時の表示優先）・ISS-08（WQ-301複数
  選択時60点固定）はいずれもHOLDのまま変更していない。
- `01_Core_Design/...V2.2.xlsx`・`01_Core_Design/...V2_3_Traceability_Approved.xlsx`・
  `03_Microsoft_Forms/...Implementation_Spec_v1.0.xlsx`はいずれも変更していない
  （`test_adapter_does_not_rewrite_v22_or_forms_spec_files`でSHA256突合により保証）。
- 公開WQ回答から正式Qの個別回答値を自動生成・転記するロジックは追加していない
  （ED-DI-002の制約を厳守。`test_no_formal_q_id_values_are_used`で構造的に確認）。

## 6. 未確定のまま残した事項（S社確認が必要）

- `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`の正式な数値（現在0.5を仮置き）。
- information_sufficiencyの粒度（本実装はKPI算定式のトップレベル加重項単位。質問1問単位の
  より細かい充足率が必要かはS社確認事項）。
- 情報充足率・要確認事項・Guardrail判定保留の顧客向け表示文言（V2.3シート78に
  「表示文言の最終調整」として明記されている未確定事項）。
- `Issue_Candidate`のU値への重み再正規化の適用可否（ED-DI-003決定事項2）は、今回
  「適用しない」という明示的な指示に従い実装したが、これがV2.2改訂時の正式仕様として
  そのまま採用されるかはS社確認事項として残る。
