# Energy Doctor｜設計課題ログ（Design Issue Log）

基準日：2026-09-01（初版登録）／2026-09-02更新（ED-DI-003〜005追加、Task2判定反映、Engine Patch 2 Accepted・ED-DI-002/004/005 Implementation Complete・ED-DI-003 Final Disposition Implemented・CLOSED反映）
管理範囲：**正本（V2.2 Design Ledger）自体の未整理事項**。Claude Codeの実装作業（Corrective Patch等）とは別枠で、S社側がDispositionするまでOPENのまま保持する。

## 運用ルール

- 本ログの項目（ED-DI-xxx）は、**Claude Codeを含む実装側が独自判断で解消してはならない**。
- 実装側（Claude Code）が正本内の矛盾・欠落に気づいた場合は、実装Issue（ISS-xx）とは別に、このログへの登録候補としてS社側へ報告する。
- Close条件が満たされ、S社側で正式決定した場合のみ、担当者がステータスをCLOSEDにし、決定内容とV2.2改訂履歴（`12_改訂履歴`）へのリンクを記載する。
- 関連：委任の役割分担は `Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`（Task1・Corrective Patch1の実施ルール）、`Energy_Doctor_ClaudeCode_Delegation_Plan_Rev0.3.docx`（Claude Codeへの委任区分）を参照。

---

## ED-DI-001｜Unknown表示文言の正本内不一致

**状態：** Final Disposition Approved / Implementation Pending（2026-09-02。顧客向け表示標準「分からない」で確定。V2.2/V2.3・Forms実装仕様・Adapter仕様への反映は残作業）
**発見経緯：** Task1 Corrective Patch検討時、ISS-02（Forms文言不一致）の裏取り調査で発見。
**関連実装Issue：** ISS-02（Corrective Patch 1でRESOLVED。暫定運用は本Final Dispositionの実装反映まで継続適用）

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

### 最終判断事項（Full Disposition時）→ 決定済み（下記Final Disposition参照）

顧客向け表示標準を「不明」とするか「分からない」とするかをS社側で決定し、決定後にV2.2の関連シート（02, 68, 76等）、Forms実装仕様、Engine Adapter仕様を同時改訂する。

### Final Disposition（2026-09-02承認）

1. 顧客向けUnknown表示標準は**「分からない」**とする。
   - 根拠：`02_回答選択肢`の標準選択肢マスタが既に「分からない」→内部値`UNKNOWN`で複数の選択肢IDにわたり一貫しており（本Issueの「事象」参照）、正本内での適用範囲が`68`より広い。また一般顧客向けの公開フォームとしても「不明」より柔らかく直感的な表現である。
2. 内部標準値は従来どおり**`UNKNOWN`**を維持する。
3. Forms Import Adapter / Normalizerは、後方互換のため**「分からない」「不明」「空欄」をすべて`UNKNOWN`として受理する**（Corrective Patch 1の実装をそのまま継続。表示文言の変更に伴うAdapter側の追加改修は不要）。
4. V2.2/V2.3の関連シート（`02_回答選択肢`、`68_公開フォーム最小質問セット`、`76_MicrosoftForms実装仕様`）、Microsoft Forms Implementation Spec、Adapter仕様・テストを同一改訂で整合させる。

Interim Operational Dispositionで採用していた「Formsは当面『不明』」という暫定運用は、本Final Dispositionの実装反映（Close条件②③）が完了次第、「分からない」へ切り替える。

### 変更禁止

上記Final Dispositionの範囲を超えて、正本の他の表示文言（例：他の選択肢マスタの表現、断定レベル等）に波及させない。ISS-04/07/08、ED-DI-002〜005の確定事項には触れない。

### Close条件（更新）

1. ~~正式表示文言の決定~~ → **Final Dispositionで決定済み（「分からない」）**
2. V2.2/V2.3正本内の表記統一（残作業＝S社側でExcel改訂。対象箇所はClaude Codeが実ファイル走査で特定済み。下記「(A)修正候補一覧」参照）
3. ~~Forms実装仕様（Microsoft Forms Implementation Spec）の更新~~ → **完了・改訂不要と確認済み（2026-09-02、Claude Codeが全6シートを実ファイル走査）。`01_Form_Settings`「分からない｜原則用意」、`02_Questions`のWQ-101〜405全16行、`03_Branching`・`06_GoLive_Checklist`のいずれにも「不明」の残存なし。`04_Engine_Mapping`の「不明は0点にしない」、`05_Acceptance_Test`のFT-02は内部表記でありS社の事前確認と完全一致。**
4. ~~Adapter受入値と内部標準値の仕様明文化~~ → **完了（2026-09-02）。`forms_adapter.py`のdocstringをFinal Disposition表記へ更新。受理ロジック（`_UNKNOWN_ALIASES`／`normalize_forms_response()`）自体は無変更であることをコード差分で確認済み。`ISSUES.md`のED-DI-001サマリ行も更新済み。**
5. ~~回帰試験（TC-A/B/C・Corrective Patch1/1.1・Engine Patch2・Task2・ED-DI-003 Final Pipeline Patch含む全既存テスト）PASS~~ → **完了（2026-09-02）。73テスト全PASS、Task2の5シナリオ再実行で`task2_results.json`差分ゼロ、正本ファイル（V2.2/V2.3・Forms実装仕様）はSHA256一致で無改変を確認済み。**

上記2（V2.2/V2.3の正本改訂）のみが残作業。それが完了した時点で、本Issueを完全Closeとする。それまでは**Final Disposition Approved / Implementation Pending**として保持する。

### (A) 修正候補一覧（2026-09-02、Claude Codeが実ファイル走査で特定・セル番地付き）

顧客が実際に選択する／読む表示文言としての「不明」。全12件、V2.3の80シートを走査して特定（`68`・`76`だけでなく、LP・Web/メール文面・フォーム項目初期値・エラー文・02の複合表示値にも残存が見つかった）。Excel自体は編集せず、箇所の特定のみ。

| # | シート | セル | 内容 |
|---|---|---|---|
| 1 | `68_公開フォーム最小質問セット` | E6:E21（16セル） | WQ-101〜WQ-405の選択肢末尾「／不明」 |
| 2 | `58_公開フォーム項目` | G13〜G16 | 質問群「初期値」列の`不明` |
| 3 | `58_公開フォーム項目` | L13 | エラー文言「不明も選択できます。」 |
| 4 | `76_MicrosoftForms実装仕様` | D6 | フォーム説明文（草案）「分からない項目は不明」 |
| 5 | `59_Web・メール文面` | D6 | 受付告知文面案「不明な項目は『不明』を選択できます。」 |
| 6 | `65_LPワイヤーフレーム` | A20 | 注記「分からない項目は『不明』を選択できます。」 |
| 7 | `66_LP掲載文章完成稿` | E18 | LP確定文言案（同旨） |
| 8 | `66_LP掲載文章完成稿` | E34 | FAQ確定文言案（同旨） |
| 9 | `57_LPページ仕様` | F8 | LP本文案「不明を選択できます。」 |
| 10 | `02_回答選択肢` | C20 | `点検未実施・不明`（ANS-FINDING4、内部値UNKNOWN） |
| 11 | `02_回答選択肢` | C24 | `対象・状況不明`（ANS-COMPLIANCE4、内部値UNKNOWN） |
| 12 | `02_回答選択肢` | C62 | `未管理・不明`（ANS-MAINT4、内部値UNKNOWN） |

**重要な訂正：** 本ログでは従来「`02_回答選択肢`は既に『分からない』で統一済み」としていたが、上記#10〜#12（3件）は「〜・不明」という複合表現のまま残っていることが実ファイル走査で判明した。他19件の同種選択肢（ANS-YESNOUNK、ANS-SEVERITY4等）は単独の「分からない」へ既に統一済み。**この3件は統一漏れの可能性があり、S社確認のうえ改訂要否を判断する。**

また、`68_公開フォーム最小質問セット`A24の「Version2.3 Governance Note」に、Interim時代の記述（「ED-DI-001 Interimにより公開FormsのUnknown表示は当面『不明』」）がそのまま残っていることも判明。これは(B)区分（内部ガバナンス注記）だが、内容が古くなっているため、S社改訂時にFinal Disposition内容へ更新することを推奨する。

**(B)修正してはいけない箇所：** `03_採点マトリクス`の「不明時処理」列、`04_Engine_Mapping`の内部ルール注記、各種試験名・テストケースの入力条件記述、内部フラグ列名等、多数（詳細はリポジトリの`engine/PATCH4_NOTES.md`参照）。いずれも顧客向け選択肢ではなく、内部処理・ルール名・試験名・過去経緯の記録であるため対象外と判断。

---

## ED-DI-002｜公開WQ-IDと正式Q-IDのTraceability不足

**状態：** Implementation Complete（2026-09-02。V2.3 `77_WQ-Q_Traceability`にてSource Authority確認完了・S社承認済み、Engine Patch 2で実装反映・Accepted）
**発見経緯：** Corrective Patch 1（ISS-03）検討時、`03_採点マトリクス`の質問別「不明時処理」を公開Web質問（WQ-ID）へ適用しようとして発見。
**関連実装Issue：** ISS-03（Corrective Patch 1でRESOLVED）、ISS-09（本Issueの実装側確認結果として統合管理・解消）

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

### Close確認（2026-09-02）

上記Close条件をすべて満たした。①V2.3 `77_WQ-Q_Traceability`に18問全てDirect/Aggregated/Partial/N/Aで確定登録（S社レビュー完了、WQ-404は`Q101/Q103/Q104/Q106/Q108/Q109/Q110/Q112/Q404/Q408`の閉じたリストへ確定）。②N/A判定（WQ-203, WQ-402等）および対応なし項目の扱いも77に明記。③Engine Patch 2で、77への参照コメントを追記（計算ロジック自体は変更せず、公開WQ回答から正式Qの個別回答値を自動生成・転記しない制約を維持）。④TC-A/B/C・Corrective Patch1/1.1・Task2の全回帰PASS済み（53件）。**本Issueは Implementation Complete としてClose扱いとする。**

### 関連実装確認（2026-09-02追記）

Corrective Patch 1でClaude Codeが本Issueの実装側裏取りを実施し、`ISSUES.md`のISS-09としてV2.2内にWQ-ID⇔Q-ID対応表が存在しないことを再確認した（名称類似のWQ-103↔Q109等は参考情報として記録のみ、実装には不採用）。**ISS-09はED-DI-002と別の独立Design Issueに昇格させず、本Issueの実装側確認結果（Status：OPEN / Blocked by ED-DI-002）として扱う。**

---

## ED-DI-003｜公開Web KPI／TOP5算定におけるUnknown時の集約・再正規化ルール

**状態：** CLOSED / Final Disposition Implemented（2026-09-02。粒度＝WQ単位、Threshold＝50%、TOP5非接続、顧客向け表示文言まで全Close条件①〜④完了）
**発見経緯：** Corrective Patch 1（ISS-03）のレビュー時に判明。Claude Codeが選定した「Unknown項目を除外し残りウェイトを再正規化する」実装が、正本に明記された唯一の解釈ではないことが分かった。
**関連実装Issue：** ISS-03（RESOLVED。Corrective Patch 1/1.1/Engine Patch 2で対応完了）

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

全項目Unknown時の挙動は、Corrective Patch 1.1で対応済みである。現在は`InsufficientDataError`（Pythonの例外）を送出せず、`diagnosis_status = INSUFFICIENT_DATA`として正常系の結果を返す実装になっている。この場合、Web_EDI/Web_DRIはnull相当、Guardrail／Issue_Candidate／TOP5は非表示（空）で返る。**ただし、これはCorrective Patch 1.1の暫定実装であり、「全項目Unknown時にKPI・Guardrail・TOP5をすべて非表示にする」という挙動自体が正式仕様として確定したわけではない**（本Issueの最終判断事項2〜3を参照）。

### 変更禁止

`weighted_score()`による再正規化方式を、S社Disposition前に「正式仕様」として文書化・恒久化しない。他の実装（例：ウェイトを再正規化しない方式）への変更も、S社側の決定を待たずに行わない。

### Approved Disposition（S社 Design Disposition Decision Record Rev0.1、2026-09-02承認）

1. Unknown項目のウェイト再正規化（`weighted_score()`）を正式仕様として採用する。
2. `Issue_Candidate`のU値には同ルールを適用しない。UnknownはU=0として扱い（他の重みは再正規化しない）、代わりにED-DI-005のreview_itemsで可視化する。
3. 全項目Unknown時は`diagnosis_status = INSUFFICIENT_DATA`の正常系として返す（例外にしない）。ただしGuardrail関連（guardrail_pending）とreview_itemsは、情報不足時でも非表示にしない（ED-DI-005と整合）。
4. KPIとは別に「情報充足率」を算出・管理し、最低情報充足率未満は`INSUFFICIENT_DATA`とする。

上記1〜4はEngine Patch 2で実装され、TC-A/B/C・Corrective Patch1/1.1回帰・Task2の5シナリオすべてでKPI/Guardrail/TOP5の既存挙動が変化しないことを確認済み（53テストPASS）。**本Issueの主要部分はAcceptedとして扱う。**

### 旧残論点（Final Disposition前の検討履歴）

Engine Patch 2のレビューにより、単なる「閾値0.5の正式値」だけでなく、**情報充足率の集計粒度**そのものが未決定であることが判明した。

- 現行実装：「回答済み有効ウェイト÷全対象ウェイト」を、**KPI算定式のトップレベル項（AVERAGEのブロック）単位**で計算している。例えばWeb_EDIの設備40%の項（WQ-101〜104のAVERAGE）は、4問中1問でも回答があれば「40%まるごと充足」として扱われる（Excelの`AVERAGE()`が空欄を無視する挙動と一貫）。
- この粒度では、「WQ-101のみ回答、102〜104はUnknown」のようなケースで情報充足率を実態より高く算定し得る。V2.3の「回答済み有効ウェイト÷全対象ウェイト」という文言を個別質問（WQ）単位で厳密に読んだ場合と数値が一致しない。
- S社としてはWQ単位を推奨（理由：情報充足率の目的は「KPI計算ができたか」ではなく「顧客がどれだけ情報を提供できたか」を表すことであり、項単位では情報不足を過小評価しやすいため）。ただし正式決定はPilot前に行う。

### 変更禁止

再正規化方式・情報充足率の算出構造（Engine Patch 2で実装済み）を、下記Close条件を満たす前に、粒度や閾値も含めて実装側の判断だけでさらに変更しない。

### 最終判断事項（すべて決定済み）

S社側で、Web_KPI（および必要であればTOP5_Calc）のUnknown時集約ルールについて、次を最終確定する。

1. ~~Unknown項目のウェイト再正規化を正式仕様とするか~~ → **Approved Dispositionで決定済み（上記）**
2. ~~`Issue_Candidate`のU値への適用可否~~ → **Approved Dispositionで決定済み（適用しない）**
3. ~~全項目Unknown時の挙動~~ → **Approved Dispositionで決定済み（正常系として返す。表示文言は下記Close条件④で確認）**
4. **情報充足率の集計粒度（項単位／WQ単位）とそれに対応する最低情報充足率Threshold** ← 残る論点

### Close条件（Pilot前）

Pilot開始前に、次を満たすこと。

1. information sufficiencyの集計粒度（項単位／WQ単位）をS社で正式決定
2. その粒度に対応する最低情報充足率Thresholdを正式決定（現状の`0.5`はあくまで仮値）
3. 決定値をEngineへ反映し、TC-A/B/C＋Task2 5シナリオを再Regression
4. `INSUFFICIENT_DATA`と顧客向け表示文言の整合を確認

上記4点は2026-09-02にすべて完了し、本Issueは**CLOSED**とする。

### WQ Sufficiency Validation（2026-09-02実施・PASS / Accepted for Design Evaluation）

Close条件①（粒度決定）②（Threshold決定）の判断材料として、WQ単位の情報充足率をトップレベル項単位と並行実装し、6パターンの境界ケース×40/50/60%の比較データを作成した（`engine/energy_doctor_engine/wq_sufficiency_validation.py`、`engine/WQ_SUFFICIENCY_VALIDATION_REPORT.md`）。本番`diagnosis_status`・`MIN_INFORMATION_SUFFICIENCY_THRESHOLD_TBC`とは構造的に非接続（AST検証済み）で、既存71テスト全PASS、Task2結果は不変、ISS-04（WQ-403二重加重）はHOLDのまま重複排除せず反映。**実装作業自体はPASS / Accepted for Design Evaluationとする。**

**①粒度の判断状況：** パターン2（回答率75%、全KPI OK）とパターン6（同じく回答率75%だがWeb_EPI重要WQにUnknownが集中、Web_EPIのみ40/50/60%すべてNG）の比較、およびパターン6における「WQ単位0.325」対「既存トップレベル項単位0.70（現行TBC閾値0.5でOK）」という乖離が実データで確認された。トップレベル項単位では「項内の1問回答で項全体を充足扱い」となり、特定KPIに重要な情報が欠けていても高い充足率が残り得ることが実証された。

**②Thresholdの判断状況：** 6パターンの実測表（EDI/DRI/EPI×40/50/60%、`WQ_SUFFICIENCY_VALIDATION_REPORT.md`§3参照）をS社でレビューした。

### Final Disposition（2026-09-02承認）

上記Validationの結果を踏まえ、S社は次のFinal Dispositionを承認した。

1. 情報充足率の正式集計粒度は**WQ単位**とする。
2. Web_EDI／Web_DRI／Web_EPIの最低情報充足率Thresholdは**50%**とする。判定は「`>= 0.50` → OK、`< 0.50` → INSUFFICIENT_DATA」とする。
   - 根拠：40%はPattern5（回答率43.75%、EDI充足率0.4333）でも全KPI OKとなり緩すぎる。60%はPattern3のDRI(0.5400)・Pattern4のDRI(0.5933)まで情報不足化させ、必要以上に診断を止める。50%は各パターンで不足しているKPIのみを選択的にNGにできる（Pattern3→EPIのみ、Pattern4→EDIのみ、Pattern5→EDIのみ、Pattern6→EPIのみ）。Pattern4のEPI=0.5000がちょうど境界でOKとなることも、ルールの定義しやすさを裏付ける。
3. 各WQの有効ウェイトは、現行Web KPI算定式のトップレベル項をWQへ均等展開して算出し、同一WQが複数項に登場する場合は寄与ウェイトを累積する（`wq_sufficiency_validation.py`の展開方法をそのまま正式仕様とする）。**ISS-04のWQ-403二重加重は、ISS-04がHOLDである限り現行式どおり維持する**（今回の正式化で重複排除・補正しない）。
4. Web_EPIのguardrail_urgencyは**virtual WQ-404**として有効ウェイト0.125を持ち、WQ-404がUnknownの場合はその0.125を未充足として扱う。
5. 3KPIのうち1つでも50%未満の場合、全体`diagnosis_status`は`INSUFFICIENT_DATA`とする。**ただし50%以上の個別KPI値は保持・表示可能とし、不足していないKPIまで無効化しない。**
6. **TOP5・Issue_Candidateの計算可否は、従来どおり`web_dri_top5_r`が計算可能かどうかにのみ依存させる。** 全体`diagnosis_status = INSUFFICIENT_DATA`、またはEDI/EPI側のWQ単位情報不足を理由に、TOP5を抑止・非表示にしない（例：Pattern6はEDI/DRI利用可・EPIのみINSUFFICIENT_DATA・全体INSUFFICIENT_DATAだが、TOP5は通常どおり表示する）。
7. Guardrail・guardrail_pending・review_itemsは、情報不足時にも従来ルールどおり保持する（非表示にしない）。

ED-DI-001、ISS-04/07/08は本Final Dispositionから分離したままとし、今回のPatchでは扱わない。

### Close条件（更新）

1. ~~information sufficiencyの集計粒度（項単位／WQ単位）をS社で正式決定~~ → **Final Dispositionで決定済み（WQ単位）**
2. ~~その粒度に対応する最低情報充足率Thresholdを正式決定~~ → **Final Dispositionで決定済み（50%）**
3. ~~決定値をEngineへ反映し、TC-A/B/C＋Corrective Patch1/1.1＋Engine Patch2＋Task2 5シナリオを再Regression~~ → **完了（2026-09-02、ED-DI-003 Final Pipeline Patch）。73テスト全PASS（既存71件中2件は定数リネームに伴う正当な期待値更新）。Task2の5シナリオは既存フィールド無変更・新フィールド追加のみ。EPIのみ情報不足でもTOP5が通常表示されることを専用テストで確認済み。**
4. ~~`INSUFFICIENT_DATA`と顧客向け表示文言の整合を確認~~ → **完了（2026-09-02、S社承認済み文言。詳細は下記「Close条件④：顧客向け表示文言」参照）**

上記4点は2026-09-02にすべて完了し、本Issueは**CLOSED**とする。

### Close条件④：顧客向け表示文言（2026-09-02 S社承認・確定）

内部の`diagnosis_status`はそのまま`INSUFFICIENT_DATA`を使い続け、顧客向け表示のみ次の案とする。

> 主表示：**判断に必要な情報が一部不足しています**
> 補足：回答済みの項目については参考値を表示しています。追加情報をご確認いただくことで、より確かな診断が可能です。

方針としては、「診断不能」「エラー」という否定的な印象を避けつつ、50%以上の個別KPI（Final Disposition point 4により保持・表示される）は参考値として見せ続ける、という今回の実装と整合させる。ED-DI-001（Unknown回答自体の表示文言「不明」/「分からない」）とは別問題であり、混在させない。

**S社承認済み（2026-09-02）。** これをもってClose条件④は満たされ、ED-DI-003のClose条件①〜④はすべて完了した。

---

## ED-DI-004｜Web_EDIの分野間集約方式と重大弱点の希釈

**状態：** Implementation Complete（2026-09-02。Approved Disposition：①40/20/20/20維持＋③分野別併記。Engine Patch 2で`domain_status.py`実装・Accepted）
**発見経緯：** Task2（模擬案件5パターンのEngine投入）で、SIM-01/03/04（テーマ分野は明確に悪いが他分野は良好、という混在プロファイル）のいずれもWeb_EDI総合点が「概ね良好」（67〜68）に着地する現象を確認。
**関連実装Issue：** Task2 TASK2_REPORT.md 提案-A（RESOLVED）

### 事象

Web_EDIは、`Web_KPI`シートの数式（`web_kpi.py`に再現済み・Excel原本と一致）で次の固定加重により算出される。

- 設備：40%
- エネルギー：20%
- 建屋：20%
- 管理：20%

（S社内レビューで「4分野均等25%」という表現が使われたが、正確には**設備を重視した40/20/20/20の固定加重**であり、均等ではない。）

この加重方式では、単一分野（特にウェイトの小さいエネルギー・建屋・管理）に深刻な課題があっても、他分野が良好であれば総合点が押し上げられ、Web_EDIの見出し値としては実態より楽観的に見える場合がある。TOP5の個別課題には正しく反映されているため実害は限定的だが、Web_EDIを見出し指標として顧客に見せる場面がある場合、実態と印象がずれる可能性がある。

これは数式上の不具合ではなく、正本が採用した設計（固定加重）の帰結であり、正本にもこの点についての明示的な設計意図（「そもそもEDIは何を表す指数か」）の記載はない。

### 変更禁止

Web_EDIの加重係数（40/20/20/20）または算定方式を、実装側の判断で変更しない。

### 最終判断事項

S社側で、Web_EDIの性格を次のいずれとするか決定する。

1. 現行の固定加重（40/20/20/20）を維持する（＝Web_EDIは「事業所全体の総合成熟度」を表す指数と割り切る）
2. 最低分野値によるペナルティ（Worst-domain penalty）等の補正を加える（＝Web_EDIに「重大な弱点の強い反映」という役割も持たせる）
3. その他の集約方式（例：分野別内訳を主指標側に併記する等）

### Approved Disposition（S社 Design Disposition Decision Record Rev0.1、2026-09-02承認）＝Close確認

**①＋③を採用。** Web_EDIは「事業所全体の総合状態を示す参考指数」と定義し、現行40/20/20/20固定加重を維持する（Worst-domain penaltyは導入しない）。一方、顧客表示ではWeb_EDI単独ではなく、設備・エネルギー・建屋・管理の分野別状態を併記し、重大弱点はGuardrailおよびTOP5・要確認事項（ED-DI-005）で表現する。

Engine Patch 2で`domain_status.py`を新設し、Web_EDIとは独立して分野別状態を出力する実装が完了。TC-A/B/C・Task2の全回帰でWeb_EDIの数値・順位に影響がないことを確認済み。**本Issueは Implementation Complete としてClose扱いとする。**

### Close条件

1. Web_EDIの性格・集約方式の正式決定
2. 決定内容のV2.2への反映（該当シートの改訂・設計意図の明記）
3. Engine実装への反映（現行維持の場合は「意図的にこの設計を採用した」旨の明記のみで可）
4. 回帰試験（TC-A/B/C含む）PASS

---

## ED-DI-005｜Unknown回答時のIssue Candidate可視化方針

**状態：** Implementation Complete（2026-09-02。Approved Disposition：②要確認事項レイヤー＋③Guardrail保留表示。Engine Patch 2で`review_items`/`guardrail_pending`実装・Accepted）
**発見経緯：** Task2で、SIM-01（IS-04：EOL・部品供給、MG-02：投資判断基準）・SIM-03（MG-02）において、Unknown回答によりその質問由来のIssue_Candidate自体が生成されず、TOP5はもちろん内部候補にも一切現れないことを確認。
**関連実装Issue：** Task2 TASK2_REPORT.md 提案-B（RESOLVED）、ED-DI-003（KPI集約ルール）と隣接するが、本Issueは**Issue Candidate生成ルール**の話であり別Issueとして管理する。

### 事象

現行の実装（Corrective Patch 1/1.1適用後）では、Unknown回答は該当Issue_Candidateを発火させない方向にのみ働く（実質的に「その課題を消す」）。Energy Doctorの基本思想は「不明＝0点ではなく情報不足として扱う」（V2.2 `03_採点マトリクス`）だが、現行実装では情報不足であること自体が顧客にもS社にも可視化されない。

老朽設備の交換部品供給が「分からない」といった回答は、事業所にとって重要な確認事項であり得るが、現状では「課題なし」と実質的に同じ扱いになり、直感に反する。

V2.2 `03_採点マトリクス`には質問ごとに異なる「不明時処理」（単純な除外だけでなく、Guardrail保留表示・L1扱い等）が定義されているが、公開WQ-IDとの対応（ED-DI-002）が未整理のため、現行の公開Engineでは一律「除外」的な挙動になっている。

### 変更禁止

Issue_Candidateの生成ロジック（Unknown時に課題を非表示にする現行動作）を、実装側の判断で変更しない。

### 最終判断事項

S社側で、Unknown回答時のIssue Candidate可視化方針を決定する。少なくとも次を含める。

1. 現行どおり「Unknownなら課題非表示」を維持するか
2. Unknownの多い質問を「情報不足・要確認事項」として別枠で提示するか
3. Guardrail対象の質問（安全・法令・BCP等に関わる質問）に限り、Unknownを保留表示扱いにするか
4. 上記とED-DI-002（WQ-ID⇔Q-ID対応表）、ED-DI-003（KPI集約ルール）との整合をどう取るか

### Approved Disposition（S社 Design Disposition Decision Record Rev0.1、2026-09-02承認）＝Close確認

**②＋③を採用。** Unknown回答は原則としてIssue Candidateの課題点数へ直接加算しない。ただし情報不足を不可視化せず、「要確認事項」として別枠で表示する。安全・法令・品質・BCP等のGuardrail対象質問（WQ-404、対応正式Q-IDはED-DI-002確定のとおり）がUnknownの場合は「Guardrail判定保留」として優先表示する。表示階層はGuardrail→要確認事項→TOP5。

Engine Patch 2で`review_items`（要確認事項）と`guardrail_pending`（Guardrail判定保留）を新設し、TOP5とは別レイヤーとして実装完了。Task2のSIM-01/03のUnknown事例で正しく`review_items`に出現することを確認済み。既存のTOP5順位ロジック・Issue_Candidateの通常スコアリングには影響なし。**本Issueは Implementation Complete としてClose扱いとする。**

### Close条件

1. 上記4項目の正式決定
2. V2.2への正式仕様の追記
3. Engine実装（Issue_Candidate生成ロジック）への反映
4. 回帰試験（TC-A/B/C含む）PASS

---

## Task 2 総合判定（2026-09-02）

| 項目 | 判定 |
|---|---|
| Task 2 シナリオ生成 | PASS |
| Engine計算 | PASS |
| Guardrail（5/5一致） | PASS |
| Unknown Adapter（実データでの正規化確認） | PASS |
| TOP-R03実運用確認（SIM-05で3件同点→2件への絞り込みを実データで確認） | PASS |
| SIM-01/03/04のREVIEW判定 | EngineバグではなくDesign Review Finding（ED-DI-004/005として登録） |
| **Task 2 総合** | **PASS with Design Review Findings** |

**UI/Report Review Finding（Design Issueとしては未登録）：** Guardrail課題本体（GR-01）よりも個別課題（例：SIM-03のBL-03）がTOP5で上位に来る場合があることを確認した（Task2 提案-C）。Guardrailは「最優先で確認すべき重大事項」、TOP5は「着手課題ランキング」であり役割が異なるため、ロジック上の不具合ではない。ただし顧客画面上でTOP5の1位表示がGuardrail本体より強く見える可能性があるため、**Task4（LP実画面QA）またはA3レポート実運用確認時に、表示階層（Guardrailと個別TOP5課題の見せ方）を確認する**こととし、現時点では新規Design Issueとして登録しない。

**Pilot受入基準としての記録：** SIM-05（比較的良好型）でTOP5が無理に5件出ず3件で止まったことは、Energy Doctorが営業都合で課題を捏造しない設計になっていることの実証である。Pilot前の受入基準の一つとして記録しておく価値がある。



## Engine Patch 2 総合判定（2026-09-02）

S社内レビューにより、Engine Patch 2（ED-DI-002〜005 Approved Dispositionの実装）は**Accepted**と判定した。確認事項は次の3点、いずれも問題なし。

1. 既存36件のうち変更された3箇所のテスト期待値は、いずれもED-DI-005「重大事項の未確認を非表示にしない」等の承認済み仕様変更に伴う正当な変更であり、回帰を隠すものではないことを確認（独自に該当コード・実行結果で裏取り済み）。
2. Issue_CandidateのU値の0代入は、Unknownの場合のみに限定され、既知回答の算定・TOP5順位ロジックには影響しないことを確認。
3. 情報充足率の「トップレベル項単位」の粒度は、V2.3の「回答済み有効ウェイト÷全対象ウェイト」という文言をWQ単位で厳密に読んだ場合と数値が一致しない場合があることが判明。これは実装の不備ではなくTBCの論点として、ED-DI-003のClose条件に追加した（後述）。

## 管理区分まとめ（2026-09-02更新／Engine Patch 2 Accepted反映）

| 区分 | 内容 |
|---|---|
| Corrective Patch 1（Claude Codeが実装・実装Issueとして解決） | ISS-02（**RESOLVED**）、ISS-06（**RESOLVED**） |
| Corrective Patch 1 / Engine Patch 2（実装Issue） | ISS-03（**RESOLVED**：Corrective Patch1/1.1＋Engine Patch2＋ED-DI-003 Final Pipeline Patchで対応完了） |
| 正本側 Design Issue（Implementation Complete） | ED-DI-002（**Implementation Complete**：77_WQ-Q_Traceability確定・Engine実装反映済み）、ED-DI-004（**Implementation Complete**：40/20/20/20維持＋domain_status実装）、ED-DI-005（**Implementation Complete**：review_items/guardrail_pending実装） |
| 正本側 Design Issue（CLOSED） | ED-DI-003（**CLOSED / Final Disposition Implemented**：粒度＝WQ単位、Threshold＝50%、TOP5非接続（`web_dri_top5_r`基準を維持）、顧客向け表示文言まで全Close条件完了。73テストPASS、Task2 5シナリオ再Regression確認済み） |
| Final Disposition Approved・実装反映待ち | ED-DI-001（**Final Disposition Approved / Implementation Pending**：顧客向け表示標準は「分からない」で確定。内部値`UNKNOWN`・Adapter互換は維持。V2.2/V2.3・Forms実装仕様への反映が残作業） |
| 設計判断待ち HOLD（実装側は変更不可） | ISS-04（WQ-403二重加重）、ISS-07（Guardrail複数該当時の正式表示順位）、ISS-08（WQ-301複数選択時60点固定） |
| Task 1 | Task 1A＝PASS維持／Task 1B＝PENDING維持 |
| Task 2 | PASS with Design Review Findings |
| Engine Patch 2 | **Accepted**（2026-09-02） |

### 今後の進め方（2026-09-02更新）

1. 済：ED-DI-001のInterim Operational DispositionをFormsチームへ通知
2. 済：Task 2（5模擬案件シナリオの作成・Engine投入）→ PASS with Design Review Findings、ED-DI-004/005を新規登録
3. 済：ED-DI-002〜005のS社 Design Disposition Decision Record Rev0.1承認、V2.3反映、Engine Patch 2実装・Accepted
4. 済：ED-DI-001のFull Disposition承認（顧客向け表示標準＝「分からない」）。残：正本・Forms実装仕様・Adapter仕様への反映、回帰試験
5. 済：ED-DI-003 Final Pipeline Patch反映、顧客向け表示文言承認、CLOSED
6. その後：実Forms出力でTask 1B／Task 3を実施
7. Task 4（LP実画面QA）またはA3レポート実運用確認時：Guardrail/TOP5の表示階層（UI/Report Review Finding、Task2 提案-C）を確認


