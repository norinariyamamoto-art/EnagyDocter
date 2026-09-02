# Energy Doctor Engine Patch 2 - Claude Code Instruction

このリポジトリに `Energy_Doctor_LP_SelfDiagnosis_Design_V2_3_Traceability_Approved.xlsx`
（V2.3確定版）を配置しました。特にシート77（WQ-Q_Traceability）、78（Web診断Disposition）、
13（算定式・順位ロジック）、12（改訂履歴 2.3〜2.3-R2）を読んでください。
あわせて `Energy_Doctor_Design_Issue_Log.md`（最新）も確認してください。

ED-DI-002〜005はS社で正式承認済みです（Design Disposition Decision Record Rev0.1、
WQ-Q Traceability確定）。今回はこの承認済み決定をEngineへ実装する
「Engine Patch 2」です。対象はCorrective Patch 1/1.1適用済みの現行Engine
（energy_doctor_engine）です。

## ED-DI-002（WQ-Q Traceability）の扱い

77_WQ-Q_Traceabilityが正式なマッピング正本になりましたが、「公開WQ回答から正式Qの
個別回答値は自動生成・転記しない」という制約は変わりません。したがって、このマッピングを
使ってEngineの計算ロジックを変更する必要はありません。コード側では、該当箇所の
docstring/コメントに「ED-DI-002 Approved: 77_WQ-Q_Traceability参照」という形で
参照を追記する程度で十分です。

唯一の例外は、WQ-404のGuardrail対象正式Q-IDが
`Q101 / Q103 / Q104 / Q106 / Q108 / Q109 / Q110 / Q112 / Q404 / Q408`
に閉じたことです。これはED-DI-005（後述）のGuardrail判定保留の対象範囲の根拠として
参照してください。Engineへの入力はWQ-404一問のみなので、実装上は「WQ-404がUnknownか
どうか」の分岐で十分です。

## ED-DI-003（Unknown時KPI集約）の実装

1. 残存ウェイト再正規化方式（weighted_score()）を正式仕様として確定してください。
   関連するdocstring等の「暫定実装」「S社Disposition待ち」という表現を
   「ED-DI-003 Approved Disposition」に更新してください。

2. 新規：情報充足率（information sufficiency rate）を、KPIごとに算出・公開してください。
   定義は「回答済み有効ウェイト ÷ 全対象ウェイト」です。Web_EDI/Web_DRI/Web_EPIそれぞれに
   ついて算出し、PipelineResult（またはWebKPI）へ新しいフィールドとして追加してください。

3. 最低情報充足率の具体的な閾値はまだ未確定です（78シートにも「Threshold TBC」と
   明記されています）。したがって、閾値は名前付き定数として1箇所に定義し、
   「これは仮値であり、S社がPilot前に正式決定する」という趣旨のコメントを必ず付けて
   ください。仮の数値自体はあなたの判断で構いませんが、その仮値を変えるだけで挙動が
   変わることを確認できるテストを含めてください。

4. 全項目Unknown時の`diagnosis_status = INSUFFICIENT_DATA`（Corrective Patch 1.1で実装済み）
   は維持してください。今回追加する情報充足率チェックと矛盾しないよう、情報充足率が
   最低閾値未満になった場合も同様に`INSUFFICIENT_DATA`として扱う、より一般化した条件に
   してください（全項目Unknownはこの条件の特殊ケースとして自然に含まれる形にする）。

5. Issue_CandidateのU値には重み再正規化を適用しないでください。Unknownはスコアに
   加算せず、代わりに下記のreview_items（要確認事項）として扱ってください。この決定は
   コード内コメントとPATCH2_NOTES.md相当の記録に明記してください。

## ED-DI-004（Web_EDI集約方式）の実装

- 加重係数（設備40%／エネルギー20%／建屋20%／管理20%）、算定式そのものは変更しないで
  ください。
- 新規：分野別状態（設備／エネルギー／建屋／管理それぞれの状態を表す値）を
  PipelineResultへ追加してください。既存のWQ_Normalizeの状態スコアから分野ごとに
  集約する形で構いません（Web_EDIの算定で使っている分野内訳の重み付き平均、または
  同等の集約方法）。Web_EDIとは独立して分野ごとの値を出力してください。
- Web_EDIの位置付け（「事業所全体の総合状態を示す参考指数」であり、単独では重大な
  単一分野弱点を表さない）をdocstringに明記してください。

## ED-DI-005（Unknown時Issue可視化）の実装

1. 新規：review_items（要確認事項）を追加してください。Unknown回答によりIssue_Candidateの
   通常条件を満たさなかった項目を、点数化・TOP5候補化せず、「情報不足のため要確認」の
   項目として一覧化してください。既存のissue_candidate.pyのロジックは壊さず、Unknownに
   よって発火しなかった項目を検出してreview_itemsとして別途出力する形にしてください。

2. 新規：Guardrail判定保留（guardrail_pending）を追加してください。WQ-404の回答が
   Unknown（Adapterで「不明」「分からない」「空欄」からUNKNOWNへ正規化されたもの）の
   場合、現行は単に「Guardrail発動なし」として処理されます。これを「発動なし」とは
   明確に区別される「判定保留」状態として返してください。

3. 表示階層はGuardrail → 要確認事項 → TOP5の順です。PipelineResultの構造またはその
   ドキュメントで、この順序が分かるようにしてください。

## 変更禁止

- Web_EDI/Web_DRI/Web_EPIの加重係数・算定式自体
- TOP-R03等、TOP5の既存順位ロジック
- ISS-04/07/08（引き続きHOLD）
- 正本ファイル（V2.2/V2.3のxlsx、Forms実装仕様）
- 公開WQ回答から正式Qの個別回答値を自動生成・転記するロジックの追加
  （ED-DI-002の制約を厳守してください）

## 完了条件

1. 情報充足率（Web_EDI/DRI/EPIごと）を計算・出力する実装
2. 情報充足率の最低閾値を仮値として定義し、閾値未満でINSUFFICIENT_DATAになることを
   テストで確認する（閾値はTBCである旨を明記）
3. 分野別状態（設備/エネルギー/建屋/管理）をWeb_EDIと独立して出力する実装とテスト
4. review_items（要確認事項）の実装とテスト
5. guardrail_pending（Guardrail判定保留）の実装とテスト
6. 既存の全テスト（Task1＋Corrective Patch1/1.1、計36件）が引き続きPASSすること
7. Task2の5シナリオを再実行し、新機能が違和感のない値になっているか確認すること
   （特にSIM-01/03のUnknown事例がreview_itemsに正しく出るか）
8. ED-DI-002〜005について、正本の制約（自動転記禁止、加重係数不変、TOP5ロジック不変）
   を破っていないことの確認
9. 変更したコード・テストの一覧、新規出力フィールドの仕様一覧をレポートとして提出

実在会社名・個人情報は使用しないでください。設計判断のうち未確定のもの（閾値の正式値、
顧客向け表示文言等）は、あなたが独自に「正式値」として確定させず、TBCとして明記して
ください。
