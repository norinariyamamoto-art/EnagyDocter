# Energy Doctor｜設計課題ログ（Design Issue Log）

基準日：2026-09-01（初版登録）  
管理範囲：**正本（V2.2 Design Ledger）自体の未整理事項**。Claude Codeの実装作業（Corrective Patch等）とは別枠で、S社側がDispositionするまでOPENのまま保持する。

## 運用ルール

- 本ログの項目（ED-DI-xxx）は、**Claude Codeを含む実装側が独自判断で解消してはならない**。
- 実装側（Claude Code）が正本内の矛盾・欠落に気づいた場合は、実装Issue（ISS-xx）とは別に、このログへの登録候補としてS社側へ報告する。
- Close条件が満たされ、S社側で正式決定した場合のみ、担当者がステータスをCLOSEDにし、決定内容とV2.2改訂履歴（`12_改訂履歴`）へのリンクを記載する。
- 関連：委任の役割分担は `Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`（Task1・Corrective Patch1の実施ルール）、`Energy_Doctor_ClaudeCode_Delegation_Plan_Rev0.3.docx`（Claude Codeへの委任区分）を参照。

---

## ED-DI-001｜Unknown表示文言の正本内不一致

**状態：** OPEN / Design Disposition Required  
**発見経緯：** Task1 Corrective Patch検討時、ISS-02（Forms文言不一致）の裏取り調査で発見。  
**関連実装Issue：** ISS-02（Corrective Patch 1で暫定対応中）

### 事象

V2.2内でUnknown回答の表示文言が統一されていない。

- `02_回答選択肢`：標準選択肢マスタでは表示値「分からない」／内部値 `UNKNOWN`（例：ANS-SEVERITY4, ANS-YESNOUNK 等、複数の選択肢IDで同様）
- `68_公開フォーム最小質問セット`：公開Web質問（WQ-101〜WQ-403等）の選択肢は文言として「不明」

### 暫定実装方針（Corrective Patch 1に反映済み）

- **S社側のForms実装方針として**、公開Formsの表示は `68_公開フォーム最小質問セット` を優先し、「不明」で実装する。
- Microsoft Forms本体のGUI変更は人が行い、Claude Codeの作業範囲外とする。
- Forms Import Adapter / Normalizerでは、次をすべてUnknownとして受理し、内部標準値 `UNKNOWN` へ正規化する：
  - 不明
  - 分からない
  - 空欄

### 変更禁止

`02_回答選択肢` または `68_公開フォーム最小質問セット` を、Corrective Patch 1の判断だけで一方に統一・書き換えしない。

### 最終判断事項

顧客向け表示標準を「不明」とするか「分からない」とするかをS社側で決定し、決定後にV2.2の関連シート（02, 68, 76等）、Forms実装仕様、Engine Adapter仕様を同時改訂する。

### Close条件

1. 正式表示文言の決定
2. V2.2正本内の表記統一（該当シートの改訂）
3. Forms実装仕様の更新
4. Adapter受入値と内部標準値の仕様明文化
5. 回帰試験（TC-A/B/C含む）PASS

---

## ED-DI-002｜公開WQ-IDと正式Q-IDのTraceability不足

**状態：** OPEN / Design Disposition Required  
**発見経緯：** Corrective Patch 1（ISS-03）検討時、`03_採点マトリクス`の質問別「不明時処理」を公開Web質問（WQ-ID）へ適用しようとして発見。  
**関連実装Issue：** ISS-03（Corrective Patch 1で暫定対応中）

### 事象

V2.2内に、公開Web質問ID（WQ-101、WQ-202等）と、正式診断の質問ID（Q101、Q202等、`03_採点マトリクス`で使用）を結びつける対応表が存在しない。両方のID体系が同時に登場するシートはV2.2内に確認できなかった。

### 影響

`03_採点マトリクス`の「不明時処理」列（質問ごとに「スコア除外＋充足率減＋信頼度減」「Guardrail保留表示」「L1扱い」等、内容が異なる）を、公開18問（WQ-ID）のUnknown処理へ正式に適用することができない。類推・目視での対応付けは可能だが、正本による裏付けがない。

したがって、Corrective Patch 1では正式Q-ID側の質問別Unknown処理を公開WQへ推測で移植せず、**既存の公開18問Engine v1.4で定義済みのUnknown処理を維持しながら、Unknown入力で計算エラーが発生しないことを優先する。** 正式Q-ID由来の質問別Unknown処理の全面反映は、本Issue Close後の別Patchとする。

### 変更禁止

WQ-ID⇔Q-IDの対応関係を、実装側（Claude Code含む）が推測で割り当てない。ISS-03の対応では、一意に対応を確認できる場合は根拠を示して報告し、確認できない質問はED-DI-002関連Issueとして残す。

### 最終判断事項

S社側で、WQ-ID⇔Q-IDの正式な対応表を作成し、V2.2内（例：新規シート、または`68_公開フォーム最小質問セット`への列追加）に登録する。あわせて、対応する質問がない場合（公開18問側で簡略化・省略された項目）のUnknown処理方針も定義する。

### Close条件

1. WQ-ID⇔Q-ID対応表の作成・V2.2への登録
2. 対応なし項目のUnknown処理方針の決定
3. Engine実装（Web_KPI／WQ_Normalize等）への反映
4. 回帰試験（TC-A/B/C含む）PASS

---

## 管理区分まとめ（本ログ登録時点）

| 区分 | 内容 |
|---|---|
| Corrective Patch 1（Claude Codeが実装） | ISS-02（Adapterで「不明」「分からない」「空欄」をUnknownとして受理）、ISS-03（既存公開EngineのUnknown処理を維持し、計算エラーを防止。正式Q-ID側ルールの推測移植は禁止）、ISS-06（TOP-R03同一分野最大2件の徹底） |
| 正本側 Design Issue（S社がDisposition、実装側は変更不可） | ED-DI-001（Unknown表示文言の正本内不一致）、ED-DI-002（WQ-ID⇔Q-ID Traceability不足） |
| 設計判断待ち HOLD（実装側は変更不可） | ISS-04（WQ-403二重加重）、ISS-07（Guardrail複数該当時の正式表示順位）、ISS-08（WQ-301複数選択時60点固定） |
