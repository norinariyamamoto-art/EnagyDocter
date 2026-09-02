# Energy Doctor｜ED-DI-001 Final Patch｜Claude Code実行指示

まず重要な前提：このPackageに同梱された `Energy_Doctor_Design_Issue_Log.md` の内容を正としてください。
リポジトリや過去のFile Library検索等で見つかるDesign_Issue_Log.mdが「ED-DI-001はInterim状態」
「ED-DI-003はTBC状態」に見える場合、それは古い版です。

このタスクを実行する前に、リポジトリ内の`Energy_Doctor_Design_Issue_Log.md`を
このPackage同梱版で上書きしてください。

現行状態：
- ED-DI-001 = Final Disposition Approved / Implementation Pending
- ED-DI-002/004/005 = Implementation Complete
- ED-DI-003 = CLOSED
- ISS-04/07/08 = HOLD

顧客向けUnknown表示標準を「分からない」に正式統一するED-DI-001実装Patchです。
ED-DI-002/004/005、ED-DI-003、ISS-04/07/08には一切触れないでください。

## 事前確認済みの事実

`03_Microsoft_Forms/Energy_Doctor_Microsoft_Forms_Implementation_Spec_v1.0.xlsx`
は既に顧客向け表示が「分からない」に統一されています。

- `01_Form_Settings`：「分からない｜原則用意。不明回答は悪評価せず情報不足として扱う」
- `02_Questions`：WQ-101〜WQ-405のUnknown選択肢はすべて「分からない」
  （WQ-202/203/204/302/402/403含む）
- `04_Engine_Mapping`の「不明は0点にしない」、`05_Acceptance_Test`のFT-02試験名
  「不明回答」は内部ルール・試験名であり(B)区分、修正対象外
- FT-02入力条件自体は既に「複数設問で『分からない』」

したがってForms Implementation Specは修正探索ではなく、
Final Dispositionとの整合確認として扱ってください。
主な修正候補はV2.3 Design Ledger側の
`68_公開フォーム最小質問セット`、`76_MicrosoftForms実装仕様`です。

## ED-DI-001 Final Disposition

1. 顧客向けUnknown表示標準＝「分からない」
2. 内部標準値＝`UNKNOWN`
3. Forms Import Adapter / Normalizerは後方互換のため
   「分からない」「不明」「空欄」→`UNKNOWN`を維持
4. V2.2/V2.3関連シート、Forms Implementation Spec、Adapter仕様・テストを整合

## 1. V2.3正本確認（改訂禁止）

対象：
`01_Core_Design/Energy_Doctor_LP_SelfDiagnosis_Design_V2_3_Traceability_Approved.xlsx`

必須確認：
- `68_公開フォーム最小質問セット`
- `76_MicrosoftForms実装仕様`
- その他のシートの顧客向け選択肢としての「不明」

区分：
(A) 修正候補：
顧客が実際に選択する回答選択肢表示としての「不明」

(B) 修正してはいけないもの：
- `03_採点マトリクス`の「不明時処理」
- 内部処理・ルール説明としての「不明」
- `04_Engine_Mapping`の「不明は0点にしない」
- 試験名「不明回答」
- 過去経緯説明としての「不明」

(A)/(B)を別々に、セル番地付きで提出。
(B)は修正対象外と判断した理由も記載。
Excel正本は直接編集しないこと。

## 2. Forms Implementation Spec再確認

上記事前確認済み内容を実ファイルで再確認。
相違があれば具体的に報告。
顧客向け選択肢として「不明」が残っていれば報告。
ファイル自体は編集しない。

## 3. コード側更新

`forms_adapter.py`等のdocstring/commentsで、
「Forms表示は当面『不明』」等のInterim Operational Disposition記述があれば、

「Final Disposition（2026-09-02）：顧客向け表示標準は『分からない』」

へ更新。

Adapterの受理ロジック
「不明」「分からない」「空欄」→UNKNOWN
は変更しない。

意味上残すべき「不明」まで機械置換しない。

## 4. Regression

- 既存73テストすべてPASS
- Task2の5シナリオ再実行
- 既存結果が変化しないことを確認

## 変更禁止

- Adapterの受理ロジック
- Web_EDI/DRI/EPI算定式
- TOP5順位ロジック
- ED-DI-002/004/005
- ED-DI-003
- ISS-04/07/08
- V2.2/V2.3 XLSX
- Forms Implementation Spec XLSX

## 完了報告必須項目

1. V2.3の(A)一覧：シート名・セル・現在文言
2. V2.3の(B)一覧：シート名・セル・現在文言・修正対象外理由
3. Forms Implementation Spec整合確認結果
4. Interim関連コメント更新箇所一覧
5. 73テスト全PASS
6. Task2 5シナリオ不変確認
7. 変更したコード・ドキュメント一覧

実在会社名・個人情報は使用しないこと。
正本Excel改訂はS社側作業。Claude Codeは改訂対象特定とコード参照更新のみ実施すること。
