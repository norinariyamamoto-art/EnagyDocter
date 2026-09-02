# Energy Doctor｜ED-DI-003 Final Disposition Production Pipeline Patch Instruction

Energy_Doctor_Design_Issue_Log.md（最新）を読んでください。ED-DI-003は
「Final Disposition Approved / Implementation Pending」に確定しました。今回は、
この承認済み仕様を本番Pipelineへ反映するPatchです。粒度・Thresholdの選定作業
（比較検証）は既に完了しており、今回は実装確定のみです。正本ファイル
（V2.2/V2.3、Forms実装仕様）は変更しないでください。ED-DI-001・ISS-04/07/08は
今回のPatchのスコープ外です。

## ED-DI-003 Final Disposition（実装対象）

1. 情報充足率の正式集計粒度は**WQ単位**とする。`wq_sufficiency_validation.py`の
   展開方法（トップレベル項をWQへ均等展開、同一WQが複数項にある場合は累積、
   ISS-04のWQ-403二重加重はHOLDのため重複排除せず維持）をそのまま正式仕様として
   採用してください。

2. Web_EDI／Web_DRI／Web_EPIそれぞれの最低情報充足率Thresholdは**50%**とする。
   判定は「`>= 0.50` → OK、`< 0.50` → INSUFFICIENT_DATA」です。

3. Web_EPIのguardrail_urgencyは**virtual WQ-404**として有効ウェイト0.125を持ち、
   WQ-404がUnknownの場合はその0.125を未充足として扱う、という
   `wq_sufficiency_validation.py`の解釈をそのまま正式仕様とします。

4. 3KPI（EDI/DRI/EPI）のうち1つでも50%未満の場合、全体`diagnosis_status`は
   `INSUFFICIENT_DATA`とする。**ただし50%以上の個別KPI値は保持・表示可能とし、
   不足していないKPIまで無効化しないでください。**

5. **重要：TOP5・Issue_Candidateの計算可否は、従来どおり`web_dri_top5_r`が
   計算可能かどうかにのみ依存させてください。** 今回追加する全体`diagnosis_status`
   のINSUFFICIENT_DATA判定（EDI/EPI側のWQ単位情報不足を含む）を理由に、
   TOP5を抑止・非表示にしないでください。例：Web_EDI/DRIのWQ単位充足率が
   50%以上でWeb_EPIだけ50%未満の場合、全体diagnosis_statusはINSUFFICIENT_DATAに
   なりますが、TOP5は通常どおり計算・表示してください（Web_DRIのterm-level値
   ＝web_dri_top5_rが計算できている限り）。

6. Guardrail・guardrail_pending・review_itemsは、情報不足時にも従来ルールどおり
   保持してください（非表示にしない）。

## やること

1. `wq_sufficiency_validation.py`のWQ単位情報充足率の算出ロジックを、Validation
   専用の切り離された関数から、`pipeline.py`が呼び出す本番経路へ統合してください。
   実装方法（`wq_sufficiency_validation.py`を`pipeline.py`から呼び出す形にするか、
   ロジックを`web_kpi.py`側へ統合するかなど）はあなたの判断で構いません。

2. `MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`（現行0.5、トップレベル項単位）を、
   WQ単位＋Threshold50%の正式ロジックに置き換えてください。定数名から`_TBC`を
   外し（例：`MIN_WQ_SUFFICIENCY_THRESHOLD = 0.50`）、正式値であることが分かる
   コメントにしてください。

3. `PipelineResult`に、EDI/DRI/EPIそれぞれのWQ単位情報充足率、および個別の
   OK/INSUFFICIENT_DATA判定を追加してください（例：
   `web_edi_status`/`web_dri_status`/`web_epi_status`、または同等の構造）。
   全体`diagnosis_status`は、3つのうち1つでもINSUFFICIENT_DATAならば
   INSUFFICIENT_DATAとしてください。

4. 全体`diagnosis_status = INSUFFICIENT_DATA`でも、TOP5計算の条件分岐
   （`web_kpi.web_edi is None or web_kpi.web_dri is None`という既存の判定、
   または`web_dri_top5_r`の有無）を変更しないでください。既存のTC-A/B/C・
   Task2シナリオでこの分岐に触れていないことをテストで確認してください。

5. 既存のトップレベル項単位`information_sufficiency`フィールド（Engine Patch 2で
   追加したもの）は、削除せずそのまま残してください（過去の実装記録として）。
   ただし本番の判定ロジックはWQ単位・50%閾値の方を使用してください。

## 変更禁止

- Web_EDI/Web_DRI/Web_EPIの加重係数・算定式そのもの
- TOP5の既存順位ロジック、Issue_CandidateのU値の扱い
- ISS-04（WQ-403二重加重、今回もHOLDのまま重複排除しない）、ISS-07、ISS-08
- 正本ファイル（V2.2/V2.3のxlsx、Forms実装仕様）
- Unknownの表示文言（「不明」「分からない」等）。ED-DI-001は今回のスコープ外です

## 完了条件

1. WQ単位・50%閾値が本番`diagnosis_status`判定として正式に組み込まれている
2. Web_EDI/DRI/EPI個別の判定結果がPipelineResultから取得できる
3. Web_EPIのみ情報不足のケースで、TOP5が通常どおり表示されることをテストで
   明示的に確認する（Pattern6相当のケースで、EDI/DRI利用可・EPIのみ
   INSUFFICIENT_DATA・全体INSUFFICIENT_DATA・TOP5は通常表示、を1つのテストで
   アサーションする）
4. Guardrail・guardrail_pending・review_itemsが情報不足時にも保持されることの
   回帰確認
5. 既存71テスト全PASS（期待値が変わるテストがあれば、変更理由を一覧化する。
   特にCorrective Patch 1.1由来の全項目Unknownケースのテストは、
   全体diagnosis_statusの判定基準が変わるため、期待値更新が必要になる可能性が
   高い。その場合も、TOP5/Guardrail/review_itemsの扱いが変わっていないことを
   別途明示的に確認する）
6. Task2の5シナリオを再実行し、判定結果に納得性があるか確認する
   （Web_KPI数値・Guardrail・TOP5・review_itemsの数値自体は変えないが、
   新しく追加される個別KPIステータス欄がどう出るかは新規報告する）
7. 変更したコード・追加/変更したテストの一覧
8. `WQ_SUFFICIENCY_VALIDATION_REPORT.md`または新規ドキュメントに、今回Final
   Dispositionとして正式反映した内容を記録する

実在会社名・個人情報は使用しないでください。今回はFinal Disposition済みの実装
Patchですが、実装の過程で正本の解釈に迷う点が新たに出た場合は、独自判断で
決めずIssueとして報告してください。
