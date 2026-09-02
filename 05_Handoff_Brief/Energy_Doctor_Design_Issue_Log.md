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
2. 内部標準値は従来どおり**`UNKNOWN`**を維持する。
3. Forms Import Adapter / Normalizerは、後方互換のため**「分からない」「不明」「空欄」をすべて`UNKNOWN`として受理する**。
4. V2.2/V2.3の関連シート（`02_回答選択肢`、`68_公開フォーム最小質問セット`、`76_MicrosoftForms実装仕様`）、Microsoft Forms Implementation Spec、Adapter仕様・テストを同一改訂で整合させる。

### Close条件（更新）

1. ~~正式表示文言の決定~~ → **Final Dispositionで決定済み（「分からない」）**
2. V2.2/V2.3正本内の表記統一（主に`68_公開フォーム最小質問セット`・`76_MicrosoftForms実装仕様`が対象。`02_回答選択肢`は既に「分からない」で整合済みのため対象外の見込み）（残作業＝S社側でExcel改訂）
3. ~~Forms実装仕様（Microsoft Forms Implementation Spec）の更新~~ → **更新ではなく整合確認で足りることが判明。`01_Form_Settings`「分からない｜原則用意」、`02_Questions`のWQ-101〜405のUnknown選択肢、いずれも既に「分からない」で統一済みを確認済み。Claude Codeによる実ファイル走査での最終確認のみ残作業。**
4. Adapter受入値と内部標準値の仕様明文化（Interim時代のコメントをFinal Dispositionへ更新）（残作業）
5. 回帰試験（TC-A/B/C・Corrective Patch1/1.1・Engine Patch2・Task2・ED-DI-003 Final Pipeline Patch含む全既存テスト）PASS（残作業）

上記2・4・5（および3の最終確認）が完了し、S社側で正本Excel（主に68・76）を改訂した後、本Issueを完全Closeとする。それまでは**Final Disposition Approved / Implementation Pending**として保持する。

---

## ED-DI-002｜公開WQ-IDと正式Q-IDのTraceability不足
**状態：** Implementation Complete（2026-09-02。V2.3 `77_WQ-Q_Traceability`にてSource Authority確認完了・S社承認済み、Engine Patch 2で実装反映・Accepted）

---

## ED-DI-003｜公開Web KPI／TOP5算定におけるUnknown時の集約・再正規化ルール
**状態：** CLOSED / Final Disposition Implemented（2026-09-02。粒度＝WQ単位、Threshold＝50%、TOP5非接続、顧客向け表示文言まで全Close条件①〜④完了）

Final Disposition：
- 情報充足率の正式集計粒度＝WQ単位
- Web_EDI／Web_DRI／Web_EPI最低情報充足率Threshold＝50%
- Web_EPI guardrail_urgency＝virtual WQ-404、有効ウェイト0.125
- 全体INSUFFICIENT_DATAでも、50%以上の個別KPI値は保持・表示可能
- TOP5可否は`web_dri_top5_r`のみで判断し、EDI/EPIの不足を理由に抑止しない
- Guardrail・guardrail_pending・review_itemsは情報不足時にも保持
- 顧客向け主表示：「判断に必要な情報が一部不足しています」
- 補足：「回答済みの項目については参考値を表示しています。追加情報をご確認いただくことで、より確かな診断が可能です。」
- 73テストPASS、Task2 5シナリオ再Regression確認済み

---

## ED-DI-004｜Web_EDIの分野間集約方式と重大弱点の希釈
**状態：** Implementation Complete（2026-09-02。Approved Disposition：40/20/20/20維持＋分野別併記。Engine Patch 2で`domain_status.py`実装・Accepted）

---

## ED-DI-005｜Unknown回答時のIssue Candidate可視化方針
**状態：** Implementation Complete（2026-09-02。Approved Disposition：要確認事項レイヤー＋Guardrail保留表示。Engine Patch 2で`review_items`/`guardrail_pending`実装・Accepted）

---

## Task 2 総合判定（2026-09-02）
**PASS with Design Review Findings**

- Guardrail：5/5一致
- Unknown Adapter：実データで正規化確認済み
- TOP-R03：SIM-05で実運用確認済み
- SIM-05：TOP5を無理に5件出さず3件で停止。Pilot受入基準として記録
- Guardrail/TOP5表示階層はTask4またはA3レポート実運用確認でUI Review

---

## 管理区分まとめ（2026-09-02）

- ED-DI-001：**Final Disposition Approved / Implementation Pending**
- ED-DI-002：**Implementation Complete**
- ED-DI-003：**CLOSED / Final Disposition Implemented**
- ED-DI-004：**Implementation Complete**
- ED-DI-005：**Implementation Complete**
- ISS-04：**HOLD**
- ISS-07：**HOLD**
- ISS-08：**HOLD**
- Task 1A：PASS
- Task 1B：PENDING
- Task 2：PASS with Design Review Findings
- Engine Patch 2：Accepted
