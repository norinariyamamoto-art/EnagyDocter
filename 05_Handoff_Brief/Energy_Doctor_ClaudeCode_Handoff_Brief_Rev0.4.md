# Energy Doctor — Claude Code 作業ブリーフ（Rev0.4 / 基準日 2026-09-01）

> **Rev0.2での変更点**：Task 1における「正式KPI」と「公開18問の参考値」の混同を防ぐための記述を追加し、Task 1をTC-A/B/C全PASSまでの単独Gateとして明記した（詳細は本文中の「重要：KPIの優先関係」を参照）。
>
> **Rev0.3での変更点**：①冒頭「プロジェクト概要」の記述をWeb_EDI/Web_DRI/Web_EPIと正式KPIの区別が伝わる表現に修正、②`06_GoLive_Checklist`の項目数を実物（12項目）に修正、③Task 1のGate適用範囲を「Engineに依存する作業」に限定し、LP機械QA・Git化・Cloudflare Pages（closed）準備・Forms GUI作成（人による作業）はTask 1と並行してよいことを明記。
>
> **Rev0.4での変更点**：Task 1完了後のレビューで判明した実装Issue（ISS-01〜08）を「Corrective Patch 1（実装修正）」「正本側Design Issue（S社Disposition待ち）」「HOLD（設計判断待ち）」の3区分に整理。正本側Design Issueは別紙 `Energy_Doctor_Design_Issue_Log.md`（ED-DI-001, ED-DI-002）として独立管理することを明記した。あわせて、①ISS-02のForms表示変更はS社側、Claude CodeはAdapter/Normalizer側対応と役割分離、②ISS-03はED-DI-002 Close前に正式Q-ID側の質問別Unknown処理を公開WQへ推測移植しない、③Task 1完了条件をTask 1A/1Bへ明確化、④Task 7のUnknown表現を中立化した。

このファイルは、Energy Doctorプロジェクトの「模擬運用フェーズ」のうち、Claude Codeに委任するタスクをまとめたものです。
Claude Codeとの作業セッションの冒頭でこのファイルと該当のソースファイルを渡してください。

## プロジェクト概要

- 運営主体：澤電気機械株式会社（Corporate Brand）／サービス名：Energy Doctor（Service Brand）
- 内容：工場・事務棟等の事業所向けに公開診断18問（Microsoft Forms）に回答してもらい、診断Engine（現状はExcel）で公開18問用の `Web_EDI` / `Web_DRI` / `Web_EPI`（参考値）・Decision Guardrail・TOP5課題を算出し、A3サイズの投資診断レポートを返す、リード獲得用フロント商材。`Web_EDI`等は正式診断側のEDI／DRI／EPI（Frozen KPI）とは区別される。
- 現状：ブランド、LP（Cloudflare Pages向け静的サイト）、公開診断18問、診断Engine v1.4、A3レポート、Microsoft Forms実装仕様までがMaster Packageとして揃っている。
- 次工程：資料作成ではなく、実装・模擬運用・公開判断のフェーズ。

## 参照ファイル（正本）

| ファイル | 内容 |
|---|---|
| `02_Core_Design/Energy_Doctor_LP_SelfDiagnosis_Design_V2.2.xlsx` | 包括設計Ledger（正本）。特にシート「13_算定式・順位ロジック」「04_Guardrail判定」「11_テストケース」「68_公開フォーム最小質問セット」「76_MicrosoftForms実装仕様」「09_断定レベル・文章統制」 |
| `03_Diagnosis_A3/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx` | 現行の診断Engine。シート `Forms_Response`（入力）→ `WQ_Normalize` → `Issue_Candidate` → `Guardrail` → `TOP5_Calc` → `TOP5_Final`（重複統合・分野偏重抑制ルール）→ `A3_Output` / `A3_Report_P1` / `A3_Report_P2`。`Mock_Test_Cases`にTC-A/B/Cの期待値あり。 |
| `05_Microsoft_Forms/Energy_Doctor_Microsoft_Forms_Implementation_Spec_v1.0.xlsx` | Forms実装仕様。`02_Questions`（18問＋連絡先7項目）、`04_Engine_Mapping`（Forms列⇔Engine列の対応）、`06_GoLive_Checklist`（公開前必須12項目） |
| `04_LP_Web/Cloudflare_Pages_V1.0/` | LP実装一式。`index.html` / `styles.css` / `config.js`（receptionStatus: closed/test/open, フォームURL等） / `script.js` / `assets/` |
| `Energy_Doctor_Design_Issue_Log.md` | 正本(V2.2)側の未整理事項を管理するログ。ED-DI-001, ED-DI-002を登録済み。実装側はここに登録された項目を独自判断で解消しない。 |

**重要：Excel（上記の正本）に書かれているロジック・数値・文言が正である。** コード化する際に解釈が分かれる場合は、独自にロジックを変えず、Excelの計算式・期待値と一致することを優先する。一致しない場合はコード側のバグとして扱い、修正する。ロジック自体を変えたほうが良いと思われる場合は、変更せずに指摘だけ行う。

### 重要：KPIの優先関係（Rev0.2で追記）

- **V2.2＝正式設計の正本（Formal Design Authority）**。正式なEDI／DRI／EPI（Frozen KPI）はV2.2シート「13_算定式・順位ロジック」で定義されている。
- **Engine v1.4＝公開18問フローの実行リファレンス（Executable Reference）**。Engine v1.4の `Web_KPI` シートには次のとおり明記されている：「Web簡易KPI｜参考値（正式EDI・DRI・EPIを置換しない）」「公開18問では詳細診断の全構成質問を満たさないため、Web簡易参考値として算出。正式値はV2.2シート13の算定式を正とする」。
- つまりEngine v1.4が実際に算出しているのは **`Web_EDI` / `Web_DRI` / `Web_EPI`**（18問による参考値・Proxy）であり、V2.2の正式Frozen KPIとは別物である。
- **Claude Codeへの指示：** Task 1でコード化・再現するのは `Web_EDI` / `Web_DRI` / `Web_EPI`（Engine v1.4のWeb_KPIシートの計算）である。これを正式EDI／DRI／EPIと呼び替えたり、V2.2の正式KPIをこの18問から再実装したりしないこと。V2.2とEngine v1.4の間で矛盾に気づいた場合は、自己判断で調整せず、Issueとして報告する。

## Task 1 完了状況とCorrective Patch 1（Rev0.4で追記）

Task 1（Engineロジックのコード化＋TC-A/B/C自動テスト）は、ロジック再現部分をTask 1AとしてPASSした。一方、実Forms回答を用いた回帰確認はTask 1BとしてPENDINGで管理する。

- **Task 1A（ロジック再現）：PASS。** TC-A/B/Cとも、Excel期待値（Web_EDI/Web_DRI/Web_EPI・Guardrail・TOP5順位）と一致。
- **Task 1B（実Forms回帰）：PENDING。** TC-B/Cは`Mock_Test_Cases`シートに実測入力データが存在せず、目標出力を満たす入力をClaude Code側で構成して検証したもの。Forms実装後、実際の回答でTC-B/Cを再試験するまでCloseしない。

Task 1完了時にClaude Codeから報告されたIssue（ISS-01〜ISS-08）は、次の3区分で管理する。

| 区分 | 対象 | 実施者・対応 |
|---|---|---|
| **Corrective Patch 1**（実装修正、Claude Codeが実施） | ISS-02（Forms表記とEngine内部値の整合）、ISS-03（Unknown入力時の計算エラー防止と既定公開Engine動作の維持）、ISS-06（TOP-R03同一分野最大2件の徹底） | Claude Codeが修正・再テストを実施。詳細は下記「Corrective Patch 1 指示」を参照。 |
| **正本側 Design Issue**（S社がDisposition、実装側は変更不可） | ED-DI-001（Unknown表示文言の正本内不一致）、ED-DI-002（公開WQ-ID⇔正式Q-IDのTraceability不足） | 別紙 `Energy_Doctor_Design_Issue_Log.md` で独立管理。S社側の決定まで正本（V2.2）を書き換えない。 |
| **HOLD**（設計判断待ち、実装側は変更不可） | ISS-04（WQ-403二重加重）、ISS-07（Guardrail複数該当時の正式表示順位）、ISS-08（WQ-301複数選択時60点固定） | S社側で設計意図を確認してから対応方針を決定する。 |

### Corrective Patch 1 指示（Claude Codeへそのまま渡せる）

> Task 1Aで確認されたISS-02、ISS-03、ISS-06のみを修正してください。ISS-04、ISS-07、ISS-08はHOLDのままとし、変更しないでください。
>
> **ISS-02：Forms表記とEngine内部値の整合**
>
> S社側のForms実装方針として、公開Formsの表示はV2.2 `68_公開フォーム最小質問セット` を優先し、該当するUnknown選択肢は「不明」とします。Microsoft Forms本体のGUI変更はClaude Codeの作業範囲外です。
>
> Claude CodeはAdapter / Normalizer側で、少なくとも「不明」「分からない」「空欄」をすべてUnknownとして受理し、内部標準値 `UNKNOWN` へ正規化してください。
>
> V2.2 `02_回答選択肢` では表示値「分からない」→内部値 `UNKNOWN` の定義も存在するため、この正本内の表示定義差はED-DI-001として記録済みです。どちらか一方へ正本全体を勝手に書き換えないでください。
>
> **ISS-03：Unknown処理**
>
> Unknownを一律に0点として扱わず、既存の公開18問Engine v1.4で定義済みのUnknown処理を維持しつつ、Unknown入力によって `#VALUE!` 等の計算エラーが発生しないよう修正してください。
>
> V2.2 `03_採点マトリクス` には正式Q-IDごとに異なる「不明時処理」が定義されていますが、公開WQ-ID⇔正式Q-IDの正式対応表は存在しません（ED-DI-002）。
>
> したがって、**正式Q-ID側の質問別Unknown処理を公開WQへ推測で移植してはいけません。**
>
> 一意に対応を確認できるものがあれば根拠を示して報告し、確認できないものはED-DI-002関連Issueとして残してください。
>
> Corrective Patch 1では最低限、「不明」「分からない」「空欄」のいずれでも計算エラーを発生させず、既存Web_KPI・Guardrail・TOP5の既定動作を壊さないことを確認してください。
>
> 正式Q-ID由来の質問別Unknown処理の全面反映は、ED-DI-002 Close後の別Patchとします。
>
> **ISS-06：TOP-R03**
>
> 「同一分野最大2件」の既定ルールを、同点時でも確実に満たすよう修正してください。既存のGuardrail優先、TOP_SCORE、TiePriority等の順位ロジックは変更せず、同一分野で3件以上が同点となった場合でも最終選択は最大2件に制限してください。安全・法令等の既定例外がある場合は正本の既定ルールを優先してください。
>
> **変更禁止：** ISS-04（WQ-403二重加重）、ISS-07（Guardrail複数該当時の正式表示順位）、ISS-08（WQ-301複数選択時60点固定）は設計判断待ちのため変更しないでください。
>
> **完了条件：**
> 1. ISS-02/03/06の修正内容を一覧化
> 2. TC-A/B/Cを再実行し既存期待値・順位が維持される
> 3. 「不明」「分からない」「空欄」のUnknown入力テストを追加
> 4. Web_KPIで計算エラーが発生しない
> 5. TOP-R03同点ケースで同一分野最大2件を確認
> 6. 公開WQ-ID⇔正式Q-ID対応に不明点があればIssueとして報告
> 7. ISS-04/07/08を変更していないことを明記

### Task 1（最優先・単独Gate）: 診断Engineロジックのコード化とTC-A/B/C自動テスト

**目的：** Excelを毎回手作業で確認する運用をやめ、回帰テストを自動化する。

**Gate運用（Rev0.3で範囲を限定）：** Task 1のGateが止めるのは「Engineに依存する作業」に限る。

- **Task 1A完了（ロジック再現PASS）を待つもの：**
  - Task 2：模擬案件データをEngineへ投入して評価すること
  - Task 3：Forms→Engine接続の最終検証
  - A3出力とのロジック整合確認
- **Task 1Aと並行して進めてよいもの：**
  - S社側のMicrosoft Forms GUI作成（人による作業）
  - Task 4：LPのHTML/CSS/JS機械QA
  - Task 5：Gitリポジトリ化、Cloudflare Pages（closed状態）でのデプロイ準備
  - Task 6：Go-Live Checklistの進捗管理表のコード化（項目自体はまだ「未」のままでよい）

Engineに依存しない作業まで止める必要はない。

**やること：**
1. `Forms_Response` 形式（WQ-001, WQ-101〜104, WQ-201〜204, WQ-301〜303, WQ-401〜405, WQ-501）の回答を入力として受け取る。
2. `WQ_Normalize` → `Issue_Candidate` → `Guardrail` → `TOP5_Calc` → `TOP5_Final`（重複統合ルールTOP-R02、同一分野最大2件ルールTOP-R03、安全・法令は例外）の順にロジックを実装する（言語はPython推奨。Claude Codeの判断でJS可）。
3. `Web_EDI` ／ `Web_DRI` ／ `Web_EPI`（Engine v1.4の`Web_KPI`シートの参考値算定式）をそのまま再現する。**V2.2シート13の正式EDI／DRI／EPI算定式をここで実装しない**（上記「重要：KPIの優先関係」を参照）。
4. `Mock_Test_Cases` シートの3ケースを自動テストとして再現する（数値はいずれも `Web_EDI` / `Web_DRI` / `Web_EPI` の値）：
   - **TC-A（製造工場・混在リスク型）**：Guardrail「BCP・供給継続 L2」が発動し、Web_EDI43／Web_DRI36／Web_EPI80近辺、TOP5がGuardrail課題→EOL・復旧→建屋影響の順に上位に来ること。重大課題が平均点に埋没しないことを確認する。
   - **TC-B（研究所＋事務棟・管理良好型）**：Guardrailなし、Web_EDI100／Web_DRI100／Web_EPI18近辺、B評価以上が少ない場合に無理に5件のTOP課題を表示しない（0件でよい）ことを確認する。
   - **TC-C（物流センター・重大Guardrail型）**：「安全・法令」Guardrailが同点条件下でも最優先に来ること、Web_EDI27／Web_DRI22／Web_EPI91近辺になることを確認する。
5. 3ケースのロジック再現PASSをもってTask 1A完了とする。**Task 1Bは実Forms回帰完了までPENDINGとし、Forms実装後にTC-B/Cを実回答で再試験してCloseする。**

**完了条件（DoD）：** Task 1Aは、上記3ケースの自動テストがリポジトリに存在し、実行して全てPASSし、Excel側の数値・順位と照合済みであることをコメント等に明記した時点で完了とする。Task 1Bは、実Forms回答を用いた回帰試験が完了し、TC-B/Cを含む期待結果との一致を確認した時点でCloseする。

### Task 2: 模擬案件データの生成（3〜5件）

**やること：** 次の5パターンについて、18問分のダミー回答データ（架空の会社名・数値）をJSONまたはExcel形式で作成する。
- 老朽設備型
- 省エネ型
- 建屋課題型
- BCP型
- 比較的良好型

Task 1Aのエンジンに投入して、A3出力・TOP5・Guardrailが各パターンの想定と矛盾しない結果になることを確認する（例：老朽設備型なら設備関連課題が上位に出る、など）。

**注意：** 実在する会社名・数値・個人情報は一切使用しないこと。

### Task 3: Forms出力 ⇔ Engineマッピングの整合性チェック

`04_Engine_Mapping` シートの対応表（WQ_ID／Forms出力／Engine列／正規化ルール等）をコード化し、Forms（またはその想定エクスポートファイル）の列名・選択肢の表記と仕様書がずれていないかを自動検証するスクリプトを作成する。Forms未実装の間は、仕様書どおりの想定ヘッダーでダミー検証しておき、実データ入手後に差し替えられる構成にする。最終検証はTask 1A PASS後かつ実Forms出力取得後に実施する。

### Task 4: LPコードの機械的QA

対象：`04_LP_Web/Cloudflare_Pages_V1.0/index.html`, `styles.css`, `script.js`, `config.js`

- レスポンシブ崩れ（主要ブレークポイントでのレイアウト確認）
- リンク切れ、コンソールエラー、alt属性の欠落などのアクセシビリティ・チェック
- `config.js` の `receptionStatus`（closed/test/open）切替が想定どおりCTA・フォーム遷移の表示に反映されるかのロジック確認
- 見つかった問題は修正する（軽微な修正はそのまま実施してよい）

**対象外（人が行う）：** 実機・実ブラウザでの目視での第一印象、文字量の感じ方、ロゴの見え方などの感性評価。

### Task 5: Cloudflare Pagesデプロイ準備

- `04_LP_Web/Cloudflare_Pages_V1.0/` をGitリポジトリ化する（未整備の場合）
- 静的サイトとしてCloudflare Pagesにそのままdeployできる状態を確認する
- 受付状態は `closed` のまま維持する（openへは切り替えない）

### Task 6: Go-Live Checklist / 進捗管理のコード化

`06_GoLive_Checklist` の12項目を、Markdown表またはJSONで進捗管理できる形にし、更新のたびに履歴が残る形式（例：チェック日・担当・状態）にする。

### Task 7（公開後・データが貯まってから着手）: 集計・分析スクリプトの雛形

10件ごとに以下を集計する雛形コードを用意する（実データが集まるまでは動作確認用のダミーデータで良い）：
- 離脱質問（どの質問で回答をやめたか）
- **Unknown回答（「不明」等）が多い質問**
- TOP5の違和感（同じ課題が出続けていないか等）
- A3で修正が多かった文章
- 実案件化率

## Claude Codeに任せないこと（人が対応）

- Microsoft Forms本体の作成・質問登録・URL発行（GUI操作。組織のAPI権限が必要なため自動化はスコープ外）
- 実機・実ブラウザでのスマートフォン目視確認、文章量やロゴの感性評価
- 個人情報・営業秘密の保存先運用ルールの決定
- 正式受付開始（open切替）の可否判断
- A3レポートの文章が「顧客に誤解を与えないか」「断定しすぎていないか」の最終レビュー（`09_断定レベル・文章統制` に沿った機械チェックまではAIで一次スクリーニング可能だが、最終判断は人が行う）

## 共通の注意事項

- 実案件の個人情報・営業秘密は絶対にClaude Codeに投入しない。模擬データは常に架空のものを使う。
- 診断ロジック・文言のルールを変更する必要があると気づいた場合は、勝手に変更せず、その旨をまとめて報告する。
- 作業単位ごとに、何を正本（Excelのどのシート）と突合したかを明記する。

## 最初にClaude Codeへ渡す指示（例）

**Task 1（初回）を実施させる場合：**

> `Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md` を最初に読み、Task 1のみ実施してください。  
> Engine v1.4の公開18問ロジックと `Web_EDI` / `Web_DRI` / `Web_EPI`、Guardrail、TOP5を再現し、TC-A/B/CをExcel期待値と照合してください。  
> V2.2の正式EDI/DRI/EPIを18問から再実装しないでください。  
> 不整合・解釈差は修正せずIssueとして報告してください。

**Corrective Patch 1（Task 1A完了後）を実施させる場合：**

> `Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.4.md` を最初に読み、「Corrective Patch 1 指示」に記載されたISS-02、ISS-03、ISS-06のみを修正してください。  
> ED-DI-001、ED-DI-002は正本側Design IssueとしてOPENのまま扱い、実装側で独自解消しないでください。  
> ISS-04、ISS-07、ISS-08はHOLDのため変更しないでください。  
> 修正後、Unknown 3表記テスト、TOP-R03同点ケース、TC-A/B/C回帰テストを実行し、変更内容・テスト結果・未解決Issueを報告してください。

この間、S社側ではMicrosoft Formsの作成、LPの機械的QAやCloudflare Pages（closed状態）のデプロイ準備を並行して進めてよい。次の本質的なGateは、Claude Codeから返るCorrective Patch 1の結果（Unknown 3表記の正規化、Unknown入力時の既定公開Engine動作維持、TOP-R03同点ケース、TC-A/B/C回帰結果、未解決Issue）のレビューである。
