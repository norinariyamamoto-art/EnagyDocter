# ED-DI-001｜V2.3 正本改訂後 Verification｜Claude Code実行指示

S社側でV2.3正本Excel（`Energy_Doctor_LP_SelfDiagnosis_Design_V2_3_Traceability_Approved.xlsx`）を、
別紙 `ED-DI-001_V2.3_Revision_Table.md` のとおり改訂しました。
今回は改訂結果を確認する**検証タスク**です。コード変更は想定していません。

## 重要なSource確認結果

当初指示ではGovernance Noteを `76_MicrosoftForms実装仕様!A24` としていましたが、
改訂前V2.3正本を直接確認した結果、同セルは空欄であり、実際のInterim Governance Noteは
`68_公開フォーム最小質問セット!A24` に存在しました。

本パッケージのAfter正本は、実在する `68_公開フォーム最小質問セット!A24` をFinal Dispositionへ更新しています。
したがって今回の正しい差分期待値は、

**30セル＋`68_公開フォーム最小質問セット!A24`＝計31セル**

です。`76_MicrosoftForms実装仕様!A24`を新規作成・変更してはいけません。

## 1. 正本差分確認

同梱の以下2ファイルを直接比較してください。

- BEFORE：`Energy_Doctor_LP_SelfDiagnosis_Design_V2_3_Traceability_Approved_BEFORE_ED_DI_001.xlsx`
- AFTER：`Energy_Doctor_LP_SelfDiagnosis_Design_V2_3_Traceability_Approved.xlsx`

変更セルが別紙記載の31セルだけであることを確認してください。
それ以外のセル差分があれば、正本を修正せずIssueとして一覧報告してください。

## 2. 顧客向けUnknown表示確認

以下を確認してください。

- `68_公開フォーム最小質問セット` E6:E21
- `58_公開フォーム項目` G13:G16・L13
- `76_MicrosoftForms実装仕様` D6
- `59_Web・メール文面` D6
- `65_LPワイヤーフレーム` A20
- `66_LP掲載文章完成稿` E18・E34
- `57_LPページ仕様` F8
- `02_回答選択肢` C20・C24・C62

顧客向けUnknown表示はすべて「分からない」であること。
C20/C24/C62は**単独の「分からない」**であること。

## 3. Governance Note確認

`68_公開フォーム最小質問セット!A24` が次のFinal Disposition内容であることを確認してください。

> ED-DI-001 Final Disposition（2026-09-02）により、公開FormsのUnknown顧客向け表示標準は「分からない」とする。内部標準値はUNKNOWNを維持し、「分からない」「不明」「空欄」は後方互換のためUNKNOWNとして受理する。

また、`76_MicrosoftForms実装仕様!A24` は改訂対象ではないことを確認してください。

## 4. 内部表記・ロジック不変確認

次が変更されていないことを確認してください。

- `UNKNOWN`等の内部値
- `ANS-FINDING4`、`ANS-COMPLIANCE4`、`ANS-MAINT4`等の選択肢ID
- `03_採点マトリクス`の「不明時処理」列名・内容
- `04_Engine_Mapping`の「不明は0点にしない」等の内部ルール表記
- Guardrail・TOP5・採点ロジックに関わる数式・重み・判定基準

## 5. Regression

- 既存73テスト：全PASS
- Task2 5シナリオ：`task2_results.json`が変更前と完全一致（zero diff）

## 変更禁止

- BEFORE/AFTER正本XLSXの編集
- Forms実装仕様XLSXの編集
- Engineコード
- Adapterロジック
- ISS-04/07/08
- ED-DI-002〜005確定仕様

## 完了条件

1. workbook logical-cell diff = 別紙31セルのみ
2. 顧客向けUnknown = 「分からない」
3. Governance Note = `68_公開フォーム最小質問セット!A24` Final Disposition
4. 内部表記・ロジック不変
5. 73 tests PASS
6. Task2 5 scenarios zero diff
7. 問題があれば修正せずIssue報告

実在会社名・個人情報は使用しないでください。
