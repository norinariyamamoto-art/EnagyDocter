# WQ単位 情報充足率 Validation レポート

> **追記（2026-09-02、ED-DI-003 Final Pipeline Patch）：** 本レポートが提示した比較データを
> 踏まえ、S社はED-DI-003のFinal Disposition（WQ単位粒度・50%閾値）を確定した。本番
> `pipeline.py`への実装統合は`PATCH3_NOTES.md`を参照。本レポート自体は当時の比較データ・
> 検証記録としてそのまま残し、内容は変更していない。

`05_Handoff_Brief/WQ_SUFFICIENCY_VALIDATION_INSTRUCTION.md`（2026-09-02）に基づく検証結果。
Energy_Doctor_Design_Issue_Log.mdのED-DI-003は現在「Implemented / Pilot Threshold &
Granularity TBC」であり、情報充足率の集計粒度（トップレベル項単位 vs WQ単位）と、
40%/50%/60%のどの閾値を採用するかの2点がPilot前の未決事項として残っている。

**本レポートはS社が粒度・閾値を判断するための比較データであり、正式な決定・実装確定
ではない。** 本番`diagnosis_status`・`MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`
（現行0.5、トップレベル項単位）は本Validationでは一切変更していない。

## 1. 実装したもの

| ファイル | 内容 |
|---|---|
| `energy_doctor_engine/wq_sufficiency_validation.py` | WQ単位情報充足率の算出、40/50/60%3閾値比較（Validation専用、新規） |
| `tests/wq_sufficiency_fixtures.py` | 6パターンの境界ケースForms_Response（新規） |
| `tests/test_wq_sufficiency_validation.py` | 上記の単体テスト18件（新規） |

`pipeline.py` / `web_kpi.py` / `excel_compat.py` を含む既存コードは一切変更していない
（`git diff`で新規ファイル追加のみであることを確認、SHA256SUMS.txtの正本14ファイルも
全てハッシュ一致を再確認済み）。`wq_sufficiency_validation.py`は`pipeline.py`から
importされておらず、`run_pipeline()`も呼び出していない（構造的に非接続であることは
`test_changing_wq_sufficiency_module_never_touches_pipeline_constant`でASTベースに
機械的検証している）。

## 2. WQ単位の有効ウェイトをどう按分したか（完了条件7）

`web_kpi.py`の`compute_web_kpi()`が実際に呼んでいる`weighted_score()`の各トップレベル項を
そのまま展開し、各項の重みをその項に含まれるWQ数で均等分割した。同一WQが同一KPI内の
複数の項に登場する場合は、各項からの配分を**重複排除せず累積**した。

### Web_EDI（12WQ、合計1.0）

| 項（web_kpi.py） | 重み | 対象WQ | 1WQあたり |
|---|---|---|---|
| avg_or_none(WQ-101,102,103,104) | 0.40 | 4件 | 0.10 |
| avg_or_none(WQ-201,202,204) | 0.20 | 3件 | 0.0667 |
| avg_or_none(WQ-301,302,303) | 0.20 | 3件 | 0.0667 |
| avg_or_none(WQ-401,403) | 0.20 | 2件 | 0.10 |

### Web_DRI（12WQ、合計1.0。WQ-403は二重加重＝ISS-04、HOLDのため重複排除しない）

| 項 | 重み | 対象WQ | 1WQあたり |
|---|---|---|---|
| avg_or_none(WQ-101,102,201,202,302) | 0.30 | 5件 | 0.06 |
| avg_or_none(WQ-103,104,203) | 0.25 | 3件 | 0.0833 |
| WQ-204（単独、AVERAGE無し） | 0.20 | 1件 | 0.20 |
| avg_or_none(WQ-401,402,403) | 0.15 | 3件 | 0.05 |
| WQ-403（単独、AVERAGE無し） | 0.10 | 1件 | 0.10 |

→ **WQ-403の最終ウェイト = 0.05（0.15項の取り分）+ 0.10（単独項）= 0.15**（累積、重複排除なし）。
これがISS-04（WQ-403二重加重、HOLD）を今回の指標にもそのまま反映した結果である。

### Web_EPI（6WQ相当、合計1.0）

| 項 | 重み | 対象WQ | 1WQあたり |
|---|---|---|---|
| WQ-405（単独） | 0.30 | 1件 | 0.30 |
| avg_or_none(WQ-103,WQ-303) | 0.25 | 2件 | 0.125 |
| avg_or_none(WQ-104, guardrail_urgency) | 0.25 | 2件 | 0.125 |
| epi_wq204_term（WQ-204由来、単独） | 0.20 | 1件 | 0.20 |

**解釈上の判断（要S社確認）：** `avg_or_none(WQ-104, guardrail_urgency)`の
`guardrail_urgency`はWQ-404の回答文字列から常に何らかの数値（Unknownでも40）が
算出され、値計算上は「空欄」を一切とらない。しかし「情報充足率」が意味するのは
「回答者が実際に情報を提供したか」であり、40はUnknownの代替値であって実際の情報では
ない。そのため本Validationでは、この半分の重み（0.125）を**WQ-404への仮想スロット**
として扱い、`WQ-404`自体が`unknown==1`のときのみ未回答とみなした
（`guardrail_urgency`が常に数値を返すことをもって「回答済み」とはしていない）。
これは指示書が許容する「根拠を示した代替配分」であり、境界ケース6でこの判断の妥当性
（EPIのみが情報不足になるか）を確認している。

## 3. 6パターンの境界ケース × 3閾値 判定結果一覧（完了条件4・6）

全パターンは`tests/fixtures.py`の`TC_B_FORMS_RESPONSE`（18問すべて有効回答、Unknown無し）
を起点に、特定WQのみ「不明」へ置き換えて作成した（`tests/wq_sufficiency_fixtures.py`）。
ちょうど40%/50%/60%を作れない場合は、指示書の許容どおり「実際に構成可能な最も近い
ケース」を採用し、実測値をそのまま記載している（丸めていない）。

| # | パターン | Unknown WQ | 回答率(問数ベース) | EDI充足率 | DRI充足率 | EPI充足率 | 40%判定(EDI/DRI/EPI) | 50%判定 | 60%判定 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 全問回答済み | なし | 100% (16/16) | 1.0000 | 1.0000 | 1.0000 | OK/OK/OK | OK/OK/OK | OK/OK/OK |
| 2 | 約75%回答 | WQ-302,402,401,204 | 75% (12/16) | 0.7667 | 0.6400 | 0.8000 | OK/OK/OK | OK/OK/OK | OK/OK/OK |
| 3 | 約60%回答 | WQ-204,301,302,402,403,404,405 | 56.25%※ (9/16) | 0.7000 | 0.5400 | 0.3750 | OK/OK/**NG** | OK/OK/**NG** | OK/**NG**/**NG** |
| 4 | 約50%回答 | WQ-101,102,103,104,202,302,303,404 | 50% (8/16) | 0.4000 | 0.5933 | 0.5000 | OK/OK/OK | **NG**/OK/OK | **NG**/**NG**/**NG** |
| 5 | 約40%回答 | WQ-102,103,201,202,203,301,302,401,404 | 43.75%※ (7/16) | 0.4333 | 0.5433 | 0.7500 | OK/OK/OK | **NG**/OK/OK | **NG**/**NG**/OK |
| 6 | Web_EPI重要WQ集中Unknown | WQ-405,303,104,404 | 75% (12/16) | 0.8333 | 0.9167 | 0.3250 | OK/OK/**NG** | OK/OK/**NG** | OK/OK/**NG** |

（NG = INSUFFICIENT_DATA。※ = ちょうどの値を構成できず、目標閾値に最も近い実際に構成可能な
ケースを採用し実測値をそのまま記載。パターン3は60%の直下＝56.25%、パターン5は40%の
直上＝43.75%。）

### 観察

- **パターン2 vs パターン6**：どちらも16問中4問がUnknownで「回答率75%」は同一だが、
  結果は大きく異なる（パターン2は3閾値・3KPIすべてOK、パターン6はWeb_EPIのみ
  常にNG）。**単純な「回答済み問数の割合」だけでは判定できず、どのWQがUnknownかに
  よってKPIごとの充足率が独立に変動することが確認できた。** これはWQ単位の情報充足率が
  トップレベル項単位・単純回答率のいずれとも異なる情報を提供することの直接的な証拠。
- **パターン3・4・5**：40%/50%/60%のどの閾値を採用するかによって、同じ入力データに
  対する判定結果（OK/NG）がKPIごとに変わることを確認した。特にパターン4はWeb_EPIの
  実測充足率が0.5000ちょうどとなり、「≧閾値→OK」というルールの境界（50%閾値で
  ちょうどOKになる）を実例で示している。
- **パターン6と既存指標（トップレベル項単位）の乖離**：`run_pipeline()`が返す既存の
  Web_EPI情報充足率（トップレベル項単位、Engine Patch 2実装）はパターン6で0.70
  （現行のTBC閾値0.5以上のためOKのまま）だが、WQ単位ではEPI=0.325となり、40%/50%/60%
  いずれの候補閾値でもNGとなる。**同一の入力データに対して、粒度によって
  「情報不足」の判定結果自体が変わり得ることを実測で確認した** ── これはまさに
  ED-DI-003の残る論点（粒度をどちらにするか）がPilot前に決着すべき理由そのものである。

### パターン6のGuardrail pending / review_itemsとの整合確認

パターン6ではWQ-404もUnknownにしているため、既存ロジック（変更なし）で
`guardrail_pending=True`となり、`review_items`には`IS-04`（起因WQ-104）・`BL-03`
（起因WQ-303）・`GR-01`（起因WQ-404）の3件が計上される。これはWeb_EPIの
WQ単位情報充足率を押し下げているWQ（WQ-104・WQ-303・WQ-404）と完全に一致しており、
新指標と既存のED-DI-005出力（要確認事項／Guardrail判定保留）の間に矛盾がないことを
確認した（`test_pattern_6_is_consistent_with_guardrail_pending_and_review_items`）。

## 4. 既存への影響確認（完了条件5）

```
$ cd engine && python3 -m pytest -q
71 passed
```

内訳：TC-A/B/C・Excel互換関数・Corrective Patch 1（19+17=36件）＋Engine Patch 2（17件）
＝既存53件、すべてPASS維持。今回追加した18件（重みテーブル検証6件＋境界ケース6パターン
×関連アサーション＋構造的非接続ガード1件など）を加えて計71件PASS。

Task2の5シナリオ（`task2/run_scenarios.py`）を再実行し、`task2_results.json`の内容が
本Validation追加の前後で完全に不変であることを`git diff`で確認した（差分なし）。
Web_EDI/DRI/EPIの数値、Guardrail、TOP5、review_itemsのいずれも変化していない。

## 5. 変更禁止事項の遵守確認

- Web_EDI/DRI/EPIの加重係数・算定式（`web_kpi.py`）：無変更（ファイル未編集）。
- TOP5既存順位ロジック・Issue_CandidateのU値処理：無変更（`top5_calc.py`/`top5_final.py`
  未編集）。
- ISS-04/07/08：無変更。ISS-04の二重加重は本Validationでも重複排除せずそのまま反映
  （上記2節参照）。
- 正本ファイル（V2.2/V2.3のxlsx、Forms実装仕様）：無変更。SHA256SUMS.txt記載14ファイル
  すべてハッシュ一致を再確認。
- Unknown表示文言（ED-DI-001）：一切触れていない。
- 40%/50%/60%を「正式な閾値」として確定：していない。本レポートは比較データの提示に
  留まる。
- 本番`diagnosis_status`・`MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`・Pipelineの
  既存判定ロジックへの接続：していない（`wq_sufficiency_validation.py`は
  `pipeline.py`からimportされておらず、`run_pipeline()`も呼び出していない。
  ASTベースの機械的テストで確認済み）。

## 6. 変更したコード・追加したテストの一覧（完了条件8）

**新規追加（既存ファイルの変更なし）：**

- `engine/energy_doctor_engine/wq_sufficiency_validation.py`
  - `_EDI_WQ_WEIGHTS` / `_DRI_WQ_WEIGHTS` / `_EPI_WQ_WEIGHTS`：フラット化済みWQ単位重みテーブル
  - `_wq_level_sufficiency()`：WQ単位情報充足率の算出
  - `_status_at()`：閾値判定（`>=`）
  - `WQSufficiencyValidation`：出力データクラス（`wq_sufficiency_edi/dri/epi`,
    `status_at_40/50/60`）
  - `compute_wq_sufficiency_validation()` / `compute_wq_sufficiency_validation_from_forms_response()`
- `engine/tests/wq_sufficiency_fixtures.py`：6パターンの境界ケースForms_Response
- `engine/tests/test_wq_sufficiency_validation.py`：18件（重みテーブル検証、閾値境界、
  6パターンの実測値回帰、構造的非接続ガード、guardrail_pending/review_items整合確認）
- `engine/WQ_SUFFICIENCY_VALIDATION_REPORT.md`（本ファイル）

**参照のみ（内容変更なし）：**

- `05_Handoff_Brief/Energy_Doctor_Design_Issue_Log.md`（最新版へ更新済み、ED-DI-003の
  Pilot Threshold & Granularity TBC状態を確認）
- `05_Handoff_Brief/WQ_SUFFICIENCY_VALIDATION_INSTRUCTION.md`（本タスクの指示書を格納）

## 7. まとめ・S社への申し送り

- WQ単位の情報充足率は、トップレベル項単位の既存指標や単純な回答率とは異なる判定結果を
  生み得ることを、パターン2 vs 6、およびパターン6 vs 既存Web_EPI情報充足率（0.325 vs
  0.70）で具体的に示した。
- 40%/50%/60%のどれを採用するかによって、同一データの判定結果が変わる境界例
  （パターン3〜5）を提示した。
- Web_EPIのguardrail_urgencyスロット（WQ-404起因）の扱いは本Validation側の解釈上の
  判断であり、S社の確認が必要（2節参照）。
- 上記はいずれも比較データであり、粒度・閾値そのものの決定はS社のPilot前判断に委ねる。
