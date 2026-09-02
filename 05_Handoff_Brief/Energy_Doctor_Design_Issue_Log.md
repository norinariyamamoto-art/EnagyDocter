# Energy Doctor｜設計課題ログ（Design Issue Log）

基準日：2026-09-01（初版登録）／2026-09-02更新（ED-DI-003追加）
管理範囲：**正本（V2.2 Design Ledger）自体の未整理事項**。Claude Codeの実装作業（Corrective Patch等）とは別枠で、S社側がDispositionするまでOPENのまま保持する。

## 運用ルール

- 本ログの項目（ED-DI-xxx）は、**Claude Codeを含む実装側が独自判断で解消してはならない**。
- 実装側（Claude Code）が正本内の矛盾・欠落に気づいた場合は、実装Issue（ISS-xx）とは別に、このログへの登録候補としてS社側へ報告する。
- Close条件が満たされ、S社側で正式決定した場合のみ、担当者がステータスをCLOSEDにし、決定内容とV2.2改訂履歴（`12_改訂履歴`）へのリンクを記載する。
- 関連：委任の役割分担は `Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`（Task1・Corrective Patch1の実施ルール）、`Energy_Doctor_ClaudeCode_Delegation_Plan_Rev0.3.docx`（Claude Codeへの委任区分）を参照。

---

## ED-DI-001｜Unknown表示文言の正本内不一致

**状態：** OPEN / Interim Operational Disposition Applied（2026-09-02）
**発見経緯：** Task1 Corrective Patch検討時、ISS-02（Forms文言不一致）の裏取り調査で発見。
**関連実装Issue：** ISS-02（Corrective Patch 1でRESOLVED。暫定運用として継続適用）

### 事象

V2.2内でUnknown回答の表示文言が統一されていない。

- `02_回答選択肢`：標準選択肢マスタでは表示値「分からない」／内部値 `UNKNOWN`（例：ANS-SEVERITY4, ANS-YESNOUNK 等、複数の選択肢IDで同様）
- `68_公開フォーム最小質問セット`：公開Web質問（WQ-101〜WQ-403等）の選択肢は文言として「不明」

### Interim Operational Disposition（2026-09-02決定・暫定運用）

Microsoft Forms本体の作成をS社側で並行進行させる必要があるため、Full Dispositionを待たず、次の暫定運用のみを決定した。

- Microsoft Formsの公開画面におけるUnknown選択肢の表示文言は、当面、V2.2 `68_公開フォーム最小質問セット` を優先し、**「不明」**で統一する。
- Forms Import Adapter / Normalizerは、**「不明」「分からない」「空欄」**をすべて内部標準値 `UNKNOWN` として受理する（Corrective Patch 1で実装済み・継続適用）。
- 本決定はForms作成を進めるための暫定運用上の決定であり、V2.2 `02_回答選択肢` と `68_公開フォーム最小質問セット` の**正本内表記統一を意味しない**。
- 正本の恒久的な表示文言統一、関連シート・Forms実装仕様・Adapter仕様の同時改訂は、ED-DI-001 **Full Disposition**時に実施する。

この暫定運用の適用により、本Issueは「未解決ではあるが、Forms作業・Task2の着手を止める理由ではない」ものとして扱う。

### 変更禁止

`02_回答選択肢` または `68_公開フォーム最小質問セット` を、Interim Operational Dispositionの範囲を超えて一方に統一・書き換えしない（Full Disposition時にまとめて改訂する）。

### 最終判断事項（Full Disposition時）

顧客向け表示標準を「不明」とするか「分からない」とするかをS社側で決定し、決定後にV2.2の関連シート（02, 68, 76等）、Forms実装仕様、Engine Adapter仕様を同時改訂する。

### Close条件（Full Disposition Close条件）

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

### 関連実装確認（2026-09-02追記）

Corrective Patch 1でClaude Codeが本Issueの実装側裏取りを実施し、`ISSUES.md`のISS-09としてV2.2内にWQ-ID⇔Q-ID対応表が存在しないことを再確認した（名称類似のWQ-103↔Q109等は参考情報として記録のみ、実装には不採用）。**ISS-09はED-DI-002と別の独立Design Issueに昇格させず、本Issueの実装側確認結果（Status：OPEN / Blocked by ED-DI-002）として扱う。**

---

## ED-DI-003｜公開Web KPI／TOP5算定におけるUnknown時の集約・再正規化ルール

**状態：** OPEN / Design Disposition Required
**発見経緯：** Corrective Patch 1（ISS-03）のレビュー時に判明。Claude Codeが選定した「Unknown項目を除外し残りウェイトを再正規化する」実装が、正本に明記された唯一の解釈ではないことが分かった。
**関連実装Issue：** ISS-03（Corrective Patch 1で暫定対応済み）

### 事象

Web_EDI/Web_DRI/Web_EPI（`Web_KPI`シート）の一部項目は、AVERAGEでラップされず単一セルを直接加重する数式になっている（例：Web_DRIの「0.20×D11」「0.10×D17」）。該当項目がUnknownの場合、Excel原本では#VALUE!になる（=想定外の入力であり、正本はこのケースの挙動を定義していない）。

Corrective Patch 1では、この場合に「Unknown項目を除外し、残りの項目でウェイトを100%に再正規化する」方式（`weighted_score()`）を実装した。この方式はAVERAGE内での欠損値の扱いと整合的で合理的だが、次のような他の設計も同様に成立し得るため、**正本が定めた唯一の正式仕様とは言えない**。

- 残り項目を100%へ再正規化する（Corrective Patch 1の暫定実装）
- Unknown部分のみ除外し、元のウェイトのまま評価する（合計が1未満になる）
- 該当KPI自体を「情報不足」として算出しない
- 参考値は出しつつ、診断信頼度（confidence）を下げて表示する

また、`Issue_Candidate`のU列（TOP5_Calcの基礎スコア）についても同じ思想を適用してよいか、および全16問Unknownの場合にどう返すか（例外か、正常系のINSUFFICIENT_DATA状態か）も、本Issueに含めて整理する。

### 暫定実装方針（Corrective Patch 1に反映済み・仮運用）

`energy_doctor_engine/excel_compat.py`の`weighted_score()`により、Web_KPI・TOP5_CalcのUnknown項目を除外・残りウェイト再正規化する方式を暫定実装として採用している。ソースコードのdocstringにも「V2.2 `03_採点マトリクス`由来のルールではなく、汎用フォールバックである」旨を明記済み。

全16問Unknownの場合は、`InsufficientDataError`（Pythonの例外）を送出する実装になっている。ただし現状、この例外はどこでもキャッチされておらず、呼び出し側（将来のForms連携部分）から見ると異常終了になり得る。**公開サービスとしては、例外ではなく`diagnosis_status = INSUFFICIENT_DATA`のような正常な業務状態として返す設計に変更することを推奨する（Corrective Patch 1.1で対応予定）。**

### 変更禁止

`weighted_score()`による再正規化方式を、S社Disposition前に「正式仕様」として文書化・恒久化しない。他の実装（例：ウェイトを再正規化しない方式）への変更も、S社側の決定を待たずに行わない。

### 最終判断事項

S社側で、Web_KPI（および必要であればTOP5_Calc）のUnknown時集約ルールを正式決定する。決定事項には最低限、次を含める。

1. Unknown項目のウェイト再正規化を正式仕様とするか、他方式にするか
2. `Issue_Candidate`のU値（TOP5_Calcの基礎スコア）にも同じルールを適用するか
3. 全項目Unknown時の挙動（例外か、正常系のINSUFFICIENT_DATA状態か。顧客表示文言含む）
4. KPIを算出・表示してよい最低回答数／最低情報充足率の設定要否

### Close条件

1. 上記4項目の正式決定
2. V2.2への正式仕様の追記（該当シートまたは新規シート）
3. Engine実装への反映（暫定実装からの置き換え、または正式採用の明記）
4. 回帰試験（TC-A/B/C含む）PASS

---

## 管理区分まとめ（2026-09-02更新）

| 区分 | 内容 |
|---|---|
| Corrective Patch 1（Claude Codeが実装・実装Issueとして解決） | ISS-02（**RESOLVED**：Adapterで「不明」「分からない」「空欄」をUnknownとして受理、正本ファイル無改変）、ISS-06（**RESOLVED**：TOP-R03同一分野最大2件を同点時も含め徹底、Guardrail/BL-01/03特例は無変更） |
| Corrective Patch 1（実装Issue・一部設計判断待ち） | ISS-03（**PARTIALLY RESOLVED / Design Disposition Required**：計算エラー防止・例外排除はCorrective Patch 1.1で達成。ウェイト再正規化方式の正式採否はED-DI-003へ切り出し） |
| 正本側 Design Issue（S社がDisposition、実装側は変更不可） | ED-DI-001（**OPEN / Interim Operational Disposition Applied**：Forms表示は当面「不明」、AdapterがUnknown表記を吸収。Forms作業のブロッカーではない）、ED-DI-002（OPEN。ISS-09は本Issueの実装側確認結果として統合管理）、ED-DI-003（OPEN・新規登録） |
| 設計判断待ち HOLD（実装側は変更不可） | ISS-04（WQ-403二重加重）、ISS-07（Guardrail複数該当時の正式表示順位）、ISS-08（WQ-301複数選択時60点固定） |
| Task 1 | Task 1A＝PASS維持／Task 1B＝PENDING維持 |

### 今後の進め方（2026-09-02合意）

1. 今すぐ：ED-DI-001のInterim Operational DispositionをFormsチームへ通知（本ログの内容で通知済みとする）
2. 着手：Task 2（5模擬案件シナリオの作成・Engine投入）
3. 並行：ED-DI-002／ED-DI-003の設計判断を整理（Task 2の結果を判断材料として活用）
4. Task 3着手前またはPilot前：ED-DI-002／ED-DI-003を正式Disposition
5. その後：実Forms出力でTask 1B／Task 3を実施


