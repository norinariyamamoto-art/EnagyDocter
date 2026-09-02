# Energy Doctor｜設計課題ログ（Design Issue Log）

基準日：2026-09-01（初版登録）／2026-09-02更新（ED-DI-002〜005
S社Approved Disposition反映、Task2判定反映） 管理範囲：**正本（V2.2
Design Ledger）自体の未整理事項**。Claude Codeの実装作業（Corrective
Patch等）とは別枠で、S社側がDispositionするまでOPENのまま保持する。

## 運用ルール

-   本ログの項目（ED-DI-xxx）は、**Claude
    Codeを含む実装側が独自判断で解消してはならない**。
-   実装側（Claude
    Code）が正本内の矛盾・欠落に気づいた場合は、実装Issue（ISS-xx）とは別に、このログへの登録候補としてS社側へ報告する。
-   Close条件が満たされ、S社側で正式決定した場合のみ、担当者がステータスをCLOSEDにし、決定内容とV2.2改訂履歴（`12_改訂履歴`）へのリンクを記載する。
-   関連：委任の役割分担は
    `Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md`（Task1・Corrective
    Patch1の実施ルール）、`Energy_Doctor_ClaudeCode_Delegation_Plan_Rev0.3.docx`（Claude
    Codeへの委任区分）を参照。

------------------------------------------------------------------------

## ED-DI-001｜Unknown表示文言の正本内不一致

**状態：** OPEN / Interim Operational Disposition Applied（2026-09-02）
**発見経緯：** Task1 Corrective
Patch検討時、ISS-02（Forms文言不一致）の裏取り調査で発見。
**関連実装Issue：** ISS-02（Corrective Patch
1でRESOLVED。暫定運用として継続適用）

### 事象

V2.2内でUnknown回答の表示文言が統一されていない。

-   `02_回答選択肢`：標準選択肢マスタでは表示値「分からない」／内部値
    `UNKNOWN`（例：ANS-SEVERITY4, ANS-YESNOUNK
    等、複数の選択肢IDで同様）
-   `68_公開フォーム最小質問セット`：公開Web質問（WQ-101〜WQ-403等）の選択肢は文言として「不明」

### Interim Operational Disposition（2026-09-02決定・暫定運用）

Microsoft Forms本体の作成をS社側で並行進行させる必要があるため、Full
Dispositionを待たず、次の暫定運用のみを決定した。

-   Microsoft
    Formsの公開画面におけるUnknown選択肢の表示文言は、当面、V2.2
    `68_公開フォーム最小質問セット` を優先し、**「不明」**で統一する。
-   Forms Import Adapter /
    Normalizerは、**「不明」「分からない」「空欄」**をすべて内部標準値
    `UNKNOWN` として受理する（Corrective Patch 1で実装済み・継続適用）。
-   本決定はForms作成を進めるための暫定運用上の決定であり、V2.2
    `02_回答選択肢` と `68_公開フォーム最小質問セット`
    の**正本内表記統一を意味しない**。
-   正本の恒久的な表示文言統一、関連シート・Forms実装仕様・Adapter仕様の同時改訂は、ED-DI-001
    **Full Disposition**時に実施する。

この暫定運用の適用により、本Issueは「未解決ではあるが、Forms作業・Task2の着手を止める理由ではない」ものとして扱う。

### 変更禁止

`02_回答選択肢` または `68_公開フォーム最小質問セット` を、Interim
Operational Dispositionの範囲を超えて一方に統一・書き換えしない（Full
Disposition時にまとめて改訂する）。

### 最終判断事項（Full Disposition時）

顧客向け表示標準を「不明」とするか「分からない」とするかをS社側で決定し、決定後にV2.2の関連シート（02,
68, 76等）、Forms実装仕様、Engine Adapter仕様を同時改訂する。

### Close条件（Full Disposition Close条件）

1.  正式表示文言の決定
2.  V2.2正本内の表記統一（該当シートの改訂）
3.  Forms実装仕様の更新
4.  Adapter受入値と内部標準値の仕様明文化
5.  回帰試験（TC-A/B/C含む）PASS

------------------------------------------------------------------------

## ED-DI-002｜公開WQ-IDと正式Q-IDのTraceability不足

**状態：** OPEN / Approved Disposition --- Implementation
Pending（2026-09-02）\
**発見経緯：** Corrective Patch
1（ISS-03）検討時、`03_採点マトリクス`の質問別「不明時処理」を公開Web質問（WQ-ID）へ適用しようとして発見。\
**関連実装Issue：** ISS-03（Corrective Patch 1で暫定対応中）

### 事象

V2.2内に、公開Web質問ID（WQ-101、WQ-202等）と、正式診断の質問ID（Q101、Q202等、`03_採点マトリクス`で使用）を結びつける対応表が存在しない。両方のID体系が同時に登場するシートはV2.2内に確認できなかった。

### 影響

`03_採点マトリクス`の「不明時処理」列（質問ごとに「スコア除外＋充足率減＋信頼度減」「Guardrail保留表示」「L1扱い」等、内容が異なる）を、公開18問（WQ-ID）のUnknown処理へ正式に適用することができない。類推・目視での対応付けは可能だが、正本による裏付けがない。

したがって、Corrective Patch
1では正式Q-ID側の質問別Unknown処理を公開WQへ推測で移植せず、**既存の公開18問Engine
v1.4で定義済みのUnknown処理を維持しながら、Unknown入力で計算エラーが発生しないことを優先する。**
正式Q-ID由来の質問別Unknown処理の全面反映は、本Issue
Close後の別Patchとする。

### 変更禁止

WQ-ID⇔Q-IDの対応関係を、実装側（Claude
Code含む）が推測で割り当てない。ISS-03の対応では、一意に対応を確認できる場合は根拠を示して報告し、確認できない質問はED-DI-002関連Issueとして残す。

### 最終判断事項

S社側で、WQ-ID⇔Q-IDの正式な対応表を作成し、V2.2内（例：新規シート、または`68_公開フォーム最小質問セット`への列追加）に登録する。あわせて、対応する質問がない場合（公開18問側で簡略化・省略された項目）のUnknown処理方針も定義する。

### S社 Approved Disposition（2026-09-02）

S社は `Energy Doctor｜S社 Design Disposition Decision Record Rev0.1`
を承認し、次を正式Dispositionとする。

-   V2.2へ公開WQ-ID⇔正式Q-IDのTraceability表を新設する。
-   対応関係は1対1を強制せず、`Direct / Aggregated / Partial / N/A`
    の4区分を使用する。
-   根拠を示せない対応は `N/A` とし、推測で紐付けない。
-   `N/A`
    または公開側で簡略化・省略された項目のUnknown処理は、Traceability表作成時に明示する。
-   V2.2への正式反映とEngine実装・回帰試験が完了するまで、本IssueはCloseせず実装待ちとして管理する。

### Close条件

1.  WQ-ID⇔Q-ID対応表の作成・V2.2への登録
2.  対応なし項目のUnknown処理方針の決定
3.  Engine実装（Web_KPI／WQ_Normalize等）への反映
4.  回帰試験（TC-A/B/C含む）PASS

### 関連実装確認（2026-09-02追記）

Corrective Patch 1でClaude
Codeが本Issueの実装側裏取りを実施し、`ISSUES.md`のISS-09としてV2.2内にWQ-ID⇔Q-ID対応表が存在しないことを再確認した（名称類似のWQ-103↔Q109等は参考情報として記録のみ、実装には不採用）。**ISS-09はED-DI-002と別の独立Design
Issueに昇格させず、本Issueの実装側確認結果（Status：OPEN / Blocked by
ED-DI-002）として扱う。**

------------------------------------------------------------------------

## ED-DI-003｜公開Web KPI／TOP5算定におけるUnknown時の集約・再正規化ルール

**状態：** OPEN / Approved Disposition --- Implementation
Pending（2026-09-02） **発見経緯：** Corrective Patch
1（ISS-03）のレビュー時に判明。Claude
Codeが選定した「Unknown項目を除外し残りウェイトを再正規化する」実装が、正本に明記された唯一の解釈ではないことが分かった。
**関連実装Issue：** ISS-03（Corrective Patch 1で暫定対応済み）

### 事象

Web_EDI/Web_DRI/Web_EPI（`Web_KPI`シート）の一部項目は、AVERAGEでラップされず単一セルを直接加重する数式になっている（例：Web_DRIの「0.20×D11」「0.10×D17」）。該当項目がUnknownの場合、Excel原本では#VALUE!になる（=想定外の入力であり、正本はこのケースの挙動を定義していない）。

Corrective Patch
1では、この場合に「Unknown項目を除外し、残りの項目でウェイトを100%に再正規化する」方式（`weighted_score()`）を実装した。この方式はAVERAGE内での欠損値の扱いと整合的で合理的だが、次のような他の設計も同様に成立し得るため、**正本が定めた唯一の正式仕様とは言えない**。

-   残り項目を100%へ再正規化する（Corrective Patch 1の暫定実装）
-   Unknown部分のみ除外し、元のウェイトのまま評価する（合計が1未満になる）
-   該当KPI自体を「情報不足」として算出しない
-   参考値は出しつつ、診断信頼度（confidence）を下げて表示する

また、`Issue_Candidate`のU列（TOP5_Calcの基礎スコア）についても同じ思想を適用してよいか、および全16問Unknownの場合にどう返すか（例外か、正常系のINSUFFICIENT_DATA状態か）も、本Issueに含めて整理する。

### 暫定実装方針（Corrective Patch 1に反映済み・仮運用）

`energy_doctor_engine/excel_compat.py`の`weighted_score()`により、Web_KPI・TOP5_CalcのUnknown項目を除外・残りウェイト再正規化する方式を暫定実装として採用している。ソースコードのdocstringにも「V2.2
`03_採点マトリクス`由来のルールではなく、汎用フォールバックである」旨を明記済み。

全項目Unknown時の挙動は、Corrective Patch
1.1で対応済みである。現在は`InsufficientDataError`（Pythonの例外）を送出せず、`diagnosis_status = INSUFFICIENT_DATA`として正常系の結果を返す実装になっている。この場合、Web_EDI/Web_DRIはnull相当、Guardrail／Issue_Candidate／TOP5は非表示（空）で返る。**ただし、これはCorrective
Patch
1.1の暫定実装であり、「全項目Unknown時にKPI・Guardrail・TOP5をすべて非表示にする」という挙動自体が正式仕様として確定したわけではない**（本Issueの最終判断事項2〜3を参照）。

### 変更禁止

`weighted_score()`による再正規化方式を、S社Disposition前に「正式仕様」として文書化・恒久化しない。他の実装（例：ウェイトを再正規化しない方式）への変更も、S社側の決定を待たずに行わない。

### 最終判断事項

S社側で、Web_KPI（および必要であればTOP5_Calc）のUnknown時集約ルールを正式決定する。決定事項には最低限、次を含める。

1.  Unknown項目のウェイト再正規化を正式仕様とするか、他方式にするか
2.  `Issue_Candidate`のU値（TOP5_Calcの基礎スコア）にも同じルールを適用するか
3.  全項目Unknown時の挙動（Corrective Patch
    1.1により実装上は例外ではなく`diagnosis_status = INSUFFICIENT_DATA`の正常系として返す形に統一済み。S社側で確認すべきは、この閾値・返却内容自体を正式仕様とするか、および顧客向け表示文言）
4.  KPIを算出・表示してよい最低回答数／最低情報充足率の設定要否

### S社 Approved Disposition（2026-09-02）

S社は `Energy Doctor｜S社 Design Disposition Decision Record Rev0.1`
を承認し、次を正式Dispositionとする。

-   Unknown項目をKPI算定対象から除外し、残存ウェイトを100%へ再正規化する現行方式を正式採用する。
-   KPIとは別に「情報充足率」を管理し、回答不足による過信を防止する。
-   最低情報充足率未満では `diagnosis_status = INSUFFICIENT_DATA`
    とする方向を正式採用する。
-   Corrective Patch 1.1の正常系返却（例外を送出しない）は維持する。
-   最低情報充足率の具体的閾値および顧客向け表示文言はPilot前に確定する。
-   `Issue_Candidate`
    のU値への適用範囲は、V2.2改訂時にED-DI-005との整合を確認して明文化する。
-   V2.2への正式反映、必要なEngine
    Patch、回帰試験完了までは本IssueをCloseしない。

### Close条件

1.  上記4項目の正式決定
2.  V2.2への正式仕様の追記（該当シートまたは新規シート）
3.  Engine実装への反映（暫定実装からの置き換え、または正式採用の明記）
4.  回帰試験（TC-A/B/C含む）PASS

------------------------------------------------------------------------

## ED-DI-004｜Web_EDIの分野間集約方式と重大弱点の希釈

**状態：** OPEN / Approved Disposition --- Implementation
Pending（2026-09-02） **発見経緯：**
Task2（模擬案件5パターンのEngine投入）で、SIM-01/03/04（テーマ分野は明確に悪いが他分野は良好、という混在プロファイル）のいずれもWeb_EDI総合点が「概ね良好」（67〜68）に着地する現象を確認。
**関連実装Issue：** Task2 TASK2_REPORT.md 提案-A

### 事象

Web_EDIは、`Web_KPI`シートの数式（`web_kpi.py`に再現済み・Excel原本と一致）で次の固定加重により算出される。

-   設備：40%
-   エネルギー：20%
-   建屋：20%
-   管理：20%

（S社内レビューで「4分野均等25%」という表現が使われたが、正確には**設備を重視した40/20/20/20の固定加重**であり、均等ではない。）

この加重方式では、単一分野（特にウェイトの小さいエネルギー・建屋・管理）に深刻な課題があっても、他分野が良好であれば総合点が押し上げられ、Web_EDIの見出し値としては実態より楽観的に見える場合がある。TOP5の個別課題には正しく反映されているため実害は限定的だが、Web_EDIを見出し指標として顧客に見せる場面がある場合、実態と印象がずれる可能性がある。

これは数式上の不具合ではなく、正本が採用した設計（固定加重）の帰結であり、正本にもこの点についての明示的な設計意図（「そもそもEDIは何を表す指数か」）の記載はない。

### 変更禁止

Web_EDIの加重係数（40/20/20/20）または算定方式を、実装側の判断で変更しない。

### 最終判断事項

S社側で、Web_EDIの性格を次のいずれとするか決定する。

1.  現行の固定加重（40/20/20/20）を維持する（＝Web_EDIは「事業所全体の総合成熟度」を表す指数と割り切る）
2.  最低分野値によるペナルティ（Worst-domain
    penalty）等の補正を加える（＝Web_EDIに「重大な弱点の強い反映」という役割も持たせる）
3.  その他の集約方式（例：分野別内訳を主指標側に併記する等）

### S社 Approved Disposition（2026-09-02）

S社は `Energy Doctor｜S社 Design Disposition Decision Record Rev0.1`
を承認し、次を正式Dispositionとする。

-   Web_EDIの固定加重は現行どおり
    **設備40%／エネルギー20%／建屋20%／管理20%** を維持する。
-   Web_EDIは「事業所全体の総合状態を示す参考指数」と定義する。
-   Worst-domain penaltyは導入しない。
-   顧客表示ではWeb_EDI単独ではなく、設備・エネルギー・建屋・管理の分野別状態を併記する方針とする。
-   重大弱点の表現はGuardrail・要確認事項・TOP5との役割分担で補完する。
-   V2.2への設計意図・表示方針の正式反映と回帰試験完了までは本IssueをCloseしない。

### Close条件

1.  Web_EDIの性格・集約方式の正式決定
2.  決定内容のV2.2への反映（該当シートの改訂・設計意図の明記）
3.  Engine実装への反映（現行維持の場合は「意図的にこの設計を採用した」旨の明記のみで可）
4.  回帰試験（TC-A/B/C含む）PASS

------------------------------------------------------------------------

## ED-DI-005｜Unknown回答時のIssue Candidate可視化方針

**状態：** OPEN / Approved Disposition --- Implementation
Pending（2026-09-02） **発見経緯：**
Task2で、SIM-01（IS-04：EOL・部品供給、MG-02：投資判断基準）・SIM-03（MG-02）において、Unknown回答によりその質問由来のIssue_Candidate自体が生成されず、TOP5はもちろん内部候補にも一切現れないことを確認。
**関連実装Issue：** Task2 TASK2_REPORT.md
提案-B、ED-DI-003（KPI集約ルール）と隣接するが、本Issueは**Issue
Candidate生成ルール**の話であり別Issueとして管理する。

### 事象

現行の実装（Corrective Patch
1/1.1適用後）では、Unknown回答は該当Issue_Candidateを発火させない方向にのみ働く（実質的に「その課題を消す」）。Energy
Doctorの基本思想は「不明＝0点ではなく情報不足として扱う」（V2.2
`03_採点マトリクス`）だが、現行実装では情報不足であること自体が顧客にもS社にも可視化されない。

老朽設備の交換部品供給が「分からない」といった回答は、事業所にとって重要な確認事項であり得るが、現状では「課題なし」と実質的に同じ扱いになり、直感に反する。

V2.2
`03_採点マトリクス`には質問ごとに異なる「不明時処理」（単純な除外だけでなく、Guardrail保留表示・L1扱い等）が定義されているが、公開WQ-IDとの対応（ED-DI-002）が未整理のため、現行の公開Engineでは一律「除外」的な挙動になっている。

### 変更禁止

Issue_Candidateの生成ロジック（Unknown時に課題を非表示にする現行動作）を、実装側の判断で変更しない。

### 最終判断事項

S社側で、Unknown回答時のIssue
Candidate可視化方針を決定する。少なくとも次を含める。

1.  現行どおり「Unknownなら課題非表示」を維持するか
2.  Unknownの多い質問を「情報不足・要確認事項」として別枠で提示するか
3.  Guardrail対象の質問（安全・法令・BCP等に関わる質問）に限り、Unknownを保留表示扱いにするか
4.  上記とED-DI-002（WQ-ID⇔Q-ID対応表）、ED-DI-003（KPI集約ルール）との整合をどう取るか

### S社 Approved Disposition（2026-09-02）

S社は `Energy Doctor｜S社 Design Disposition Decision Record Rev0.1`
を承認し、次を正式Dispositionとする。

-   Unknown回答をTOP5課題点数へ直接加算しない。
-   Unknownによる情報不足は「要確認事項」としてTOP5とは別レイヤーで可視化する。
-   安全・法令・品質・BCP等のGuardrail対象質問がUnknownの場合は「Guardrail判定保留」として優先表示する。
-   表示階層は原則として **Guardrail → 要確認事項 → TOP5** とする。
-   ED-DI-002のTraceabilityおよびED-DI-003の情報充足率と整合する形でV2.2へ仕様化する。
-   V2.2への正式反映、Engine実装、回帰試験完了までは本IssueをCloseしない。

### Close条件

1.  上記4項目の正式決定
2.  V2.2への正式仕様の追記
3.  Engine実装（Issue_Candidate生成ロジック）への反映
4.  回帰試験（TC-A/B/C含む）PASS

------------------------------------------------------------------------

## Task 2 総合判定（2026-09-02）

  -----------------------------------------------------------------------------------------------------------
  項目                                                                   判定
  ---------------------------------------------------------------------- ------------------------------------
  Task 2 シナリオ生成                                                    PASS

  Engine計算                                                             PASS

  Guardrail（5/5一致）                                                   PASS

  Unknown Adapter（実データでの正規化確認）                              PASS

  TOP-R03実運用確認（SIM-05で3件同点→2件への絞り込みを実データで確認）   PASS

  SIM-01/03/04のREVIEW判定                                               EngineバグではなくDesign Review
                                                                         Finding（ED-DI-004/005として登録）

  **Task 2 総合**                                                        **PASS with Design Review Findings**
  -----------------------------------------------------------------------------------------------------------

**UI/Report Review Finding（Design Issueとしては未登録）：**
Guardrail課題本体（GR-01）よりも個別課題（例：SIM-03のBL-03）がTOP5で上位に来る場合があることを確認した（Task2
提案-C）。Guardrailは「最優先で確認すべき重大事項」、TOP5は「着手課題ランキング」であり役割が異なるため、ロジック上の不具合ではない。ただし顧客画面上でTOP5の1位表示がGuardrail本体より強く見える可能性があるため、**Task4（LP実画面QA）またはA3レポート実運用確認時に、表示階層（Guardrailと個別TOP5課題の見せ方）を確認する**こととし、現時点では新規Design
Issueとして登録しない。

**Pilot受入基準としての記録：**
SIM-05（比較的良好型）でTOP5が無理に5件出ず3件で止まったことは、Energy
Doctorが営業都合で課題を捏造しない設計になっていることの実証である。Pilot前の受入基準の一つとして記録しておく価値がある。

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  区分                                          内容
  --------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Corrective Patch 1（Claude                    ISS-02（**RESOLVED**：Adapterで「不明」「分からない」「空欄」をUnknownとして受理、正本ファイル無改変）、ISS-06（**RESOLVED**：TOP-R03同一分野最大2件を同点時も含め徹底、Guardrail/BL-01/03特例は無変更）
  Codeが実装・実装Issueとして解決）             

  Corrective Patch                              ISS-03（**PARTIALLY RESOLVED / Design Disposition Required**：計算エラー防止・例外排除はCorrective Patch 1.1で達成。ウェイト再正規化方式の正式採否はED-DI-003へ切り出し）
  1（実装Issue・一部設計判断待ち）              

  正本側 Design                                 ED-DI-001（**OPEN / Interim Operational Disposition Applied**：Forms表示は当面「不明」、AdapterがUnknown表記を吸収。Forms作業のブロッカーではない）、ED-DI-002〜005（**OPEN / Approved Disposition ---
  Issue（S社がDisposition、実装側は変更不可）   Implementation Pending**。S社 Decision Record Rev0.1を2026-09-02承認。V2.2正式反映・Engine実装・回帰試験完了後にClose判定）

  設計判断待ち HOLD（実装側は変更不可）         ISS-04（WQ-403二重加重）、ISS-07（Guardrail複数該当時の正式表示順位）、ISS-08（WQ-301複数選択時60点固定）

  Task 1                                        Task 1A＝PASS維持／Task 1B＝PENDING維持

  Task 2                                        **PASS with Design Review Findings**（詳細は上記「Task 2 総合判定」）
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### 今後の進め方（2026-09-02更新）

1.  済：ED-DI-001のInterim Operational DispositionをFormsチームへ通知
2.  済：Task 2（5模擬案件シナリオの作成・Engine投入）→ PASS with Design
    Review Findings、ED-DI-004/005を新規登録
3.  済：ED-DI-002〜005のS社 Design Disposition承認（Decision Record
    Rev0.1、2026-09-02）
4.  次：承認DispositionをV2.2へ一括反映し、改訂正本を確定
5.  その後：改訂正本に基づくEngine PatchをClaude
    Codeへ指示し、TC-A/B/C＋Task2回帰を実施
6.  回帰PASS後：実Forms出力でTask 1B／Task 3を実施
7.  Task
    4（LP実画面QA）またはA3レポート実運用確認時：Guardrail/TOP5の表示階層（UI/Report
    Review Finding、Task2 提案-C）を確認
