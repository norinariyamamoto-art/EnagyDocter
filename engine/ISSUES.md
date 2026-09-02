# Task 1 Issue一覧

Energy_Doctor_ClaudeCode_Handoff_Brief_Rev0.3 の指示に基づき、ロジック・しきい値・文言は
一切変更せず、Excelの数式どおりに実装した。以下は実装中に判断に迷った点、Excel内で
矛盾または未定義に見えた点の一覧。**すべて報告のみで、コード側で独自に解釈・修正はしていない。**

正本突合の範囲：`02_Diagnosis_Engine/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx`
のシート `Forms_Response` / `WQ_Normalize` / `Issue_Candidate` / `Guardrail` / `Web_KPI` /
`TOP5_Calc` / `TOP5_Final` / `Mock_Test_Cases`（数式・値とも `data_only=False/True` 両方で確認）。
参考として `01_Core_Design/...V2.2.xlsx` のシート `04_Guardrail判定` `68_公開フォーム最小質問セット`、
および `03_Microsoft_Forms/...Implementation_Spec_v1.0.xlsx` のシート `02_Questions` `04_Engine_Mapping`
も確認した（Task1で再実装はしていない）。

## 現在の状況（2026-09-02 / Engine Patch 2 反映後）

Handoff Brief Rev0.4は、Task1完了後のレビューで確認された本ドキュメントのISS-01〜08を
3区分に整理した。Corrective Patch 1/1.1でISS-02・ISS-06をRESOLVED、ISS-03を
PARTIALLY RESOLVEDとした。その後、Task2（模擬案件5パターン）のレビューで新規に
ED-DI-004（Web_EDI分野間集約の希釈）・ED-DI-005（Unknown時Issue可視化）が登録され、
ED-DI-002〜005はいずれもS社承認済み（Decision Record Rev0.1）となった。**Engine Patch 2**
（本パッケージの最新変更）は、この承認済み決定のうちEngineへの実装が必要な部分
（情報充足率・分野別状態・要確認事項・Guardrail判定保留、およびED-DI-003の正式仕様化）を
実装したもの。詳細な修正内容・完了条件チェックリストは `PATCH2_NOTES.md` を参照
（Corrective Patch 1/1.1の詳細は引き続き `PATCH1_NOTES.md` を参照）。

| Issue | 区分 | 状況 |
|---|---|---|
| ISS-01 | （Task1B、実Forms回帰待ち） | OPEN（未対応、Forms実装後に再検証） |
| ISS-02 | Corrective Patch 1（実装修正） | **RESOLVED**（`forms_adapter.py`。詳細は本ファイルのISS-02節） |
| ISS-03 | Corrective Patch 1 / Engine Patch 2（実装修正） | **RESOLVED**（Engine Patch 2でED-DI-003が正式Approved Dispositionとなり、`weighted_score()`のdocstringも「正式仕様」表記に更新。情報充足率の追加・全項目Unknown時のstatus一般化も完了。詳細は本ファイルのISS-03節） |
| ISS-04 | HOLD（設計判断待ち） | 変更なし |
| ISS-05 | （参考記録、対応区分未指定） | 変更なし |
| ISS-06 | Corrective Patch 1（実装修正） | **RESOLVED**（`_enforce_field_cap()`。詳細は本ファイルのISS-06節） |
| ISS-07 | HOLD（設計判断待ち） | 変更なし |
| ISS-08 | HOLD（設計判断待ち） | 変更なし |
| ISS-09 | ED-DI-002の実装側確認結果として統合管理（独立Design Issueではない） | OPEN / Blocked by ED-DI-002 |
| ED-DI-001 | 正本側Design Issue（S社Disposition待ち） | OPEN / Interim Operational Disposition Applied。実装側では解消しない |
| ED-DI-002 | 正本側Design Issue（S社Approved・Implementation Pending→**実装済み**） | V2.3シート77（WQ-Q Traceability）確定。Engine側は参照コメント追記のみ（計算ロジック変更なし）。V2.2/V2.3への正式反映自体はS社側の管理事項として残る |
| ED-DI-003 | 正本側Design Issue（S社Approved・Implementation Pending→**実装済み**） | 残存ウェイト再正規化を正式仕様化、情報充足率を追加。閾値・Issue_CandidateのU値への適用範囲は引き続きTBC（`PATCH2_NOTES.md`参照） |
| ED-DI-004（Task2発） | 正本側Design Issue（S社Approved・Implementation Pending→**実装済み**） | Web_EDI加重係数は現行維持、分野別状態(`domain_status`)を独立出力として追加 |
| ED-DI-005（Task2発） | 正本側Design Issue（S社Approved・Implementation Pending→**実装済み**） | `review_items`・`guardrail_pending`を追加。表示階層（Guardrail→要確認事項→TOP5）をpipeline.pyに反映 |

---

## ISS-01（重要）TC-B / TC-Cの入力データがExcel内に存在しない

`Mock_Test_Cases` シートA7に明記されている：

> 注：TC-B/Cは次の実入力試験用シナリオ。現時点ではロジックレビュー条件として固定し、
> Microsoft Forms実装後に実測回答を流す。

`Forms_Response` シートにはTC-A（Case_ID=TC-WEB-A）の回答行しか存在せず、TC-B/Cは
「主要回答条件」欄の文章記述（例：「法令または安全の未解決／代替なし／管理基準なし／
中期計画なし／3か月以内」）のみで、Web_EDI/DRI/EPIの目標値（列I）もExcelの数式が
実際に計算した結果ではなく、人手で記入された目標値と判断した。

**対応：** TC-B/Cについては、文章条件を満たしTask1の実装ロジック（Excel数式の忠実再現）
に通したときに目標値（TC-B: EDI100/DRI100/EPI18、TC-C: EDI27/DRI22/EPI91）と一致する
回答セットを探索的に構築し、`tests/fixtures.py` に明記した（TC-Cは約18万通りの組み合わせを
総当たりして目標値と完全一致する組を採用）。TC-Aのみが実際にExcelが計算した値との
1:1照合であり、TC-B/Cは「文章条件+目標KPIを満たす一例」であって、正本が定めた
唯一の入力ではない。**Microsoft Forms実装後、実測回答が得られ次第、
`tests/fixtures.py` のTC-B/C部分を実測値に置き換えて再検証することを推奨する。**

---

## ISS-02（重要・RESOLVED）Microsoft Forms実装仕様の選択肢文言がEngine v1.4の数式と一致しない

`03_Microsoft_Forms/Energy_Doctor_Microsoft_Forms_Implementation_Spec_v1.0.xlsx`
シート`02_Questions`の選択肢文言は、Engine v1.4の`WQ_Normalize`シートが厳密一致（IF文）
で判定している文字列と、複数のWQで異なっている：

| WQ | Engine v1.4 `WQ_Normalize`が期待する文字列 | `03_Microsoft_Forms`の選択肢文言 |
|---|---|---|
| WQ-202 | `詳細に把握` | `設備・工程別まで詳細に把握` |
| WQ-203 | `迅速に確認` `時間をかければ確認` `困難` | `迅速に確認できる` `時間をかければ確認できる` `確認が困難` |
| WQ-204 | `複数実施` | `複数実施し効果確認済み` |
| WQ-302 | `問題時のみ` | `問題発生時のみ` |
| WQ-402 | `慣例で判断` | `慣例・経験で判断` |
| WQ-403 | `計画のみ` `案件ごと` | `計画あり・予算未確定` `案件ごとに検討` |
| 全WQ共通 | 不明扱いの文字列は `不明` | `分からない` |

一方、`01_Core_Design/...V2.2.xlsx` シート`68_公開フォーム最小質問セット`の選択肢文言は
Engine v1.4の数式が期待する文字列と完全に一致しており（`不明`表記も含む）、
Engine v1.4は`68_公開フォーム最小質問セット`を正本として作られていると判断した。

`04_Engine_Mapping`シート（Forms→Engineマッピング）には「正規化」列があるが、
実際の文言変換テーブルは記載されておらず、シート名`WQ_Normalize`を指しているのみで
具体的な変換規則は定義されていない。

**Task1への影響：** 本実装（TC-A/B/C）ではEngine自身の`Forms_Response`シートの語彙
（=`68_公開フォーム最小質問セット`の語彙）を入力形式として採用した。これはBrief記載の
「Forms_Response形式の回答を入力として受け取る」の指示にも合致する。

**Task3への申し送り：** 実際にMicrosoft Formsを`03_Microsoft_Forms`仕様どおりに構築した
場合、上記の文言差異により多くの回答がEngineのIF判定に一致せず、状態Score（D列）が
空欄になる（ISS-03参照）。Forms実装前に、Forms仕様の選択肢文言をEngine/V2.2シート68に
合わせて修正するか、Engine側の正規化ステップで文言マッピングを追加するかの判断が必要。

### Corrective Patch 1での対応（Rev0.4）

裏取り調査の過程で、V2.2内にもUnknown表示文言の不一致があることが判明した
（`02_回答選択肢`は表示値「分からない」・内部値`UNKNOWN`、`68_公開フォーム最小質問セット`
は表示文言「不明」）。これは正本(V2.2)自体の未整理事項のため、`ED-DI-001`として
`Energy_Doctor_Design_Issue_Log.md`へ独立登録し、実装側では解消していない。

S社の暫定運用方針（Rev0.4）：公開Forms表示は`68_公開フォーム最小質問セット`（「不明」）を
優先し、Microsoft Forms本体のGUI変更は対象外（人が行う）。Claude Codeの対応範囲は
Adapter/Normalizer層のみ：新規モジュール`energy_doctor_engine/forms_adapter.py`
（`normalize_forms_response()`）を追加し、`Forms_Response`の各WQ回答のうち
「不明」「分からない」「空欄（空文字列・空白のみ）」をすべて内部標準値`"UNKNOWN"`へ
正規化した上で`WQ_Normalize`以降へ渡すようにした。`wq_normalize.py`の
`UNKNOWN_VALUES`にも`"UNKNOWN"`を追加し、直接呼び出された場合でも同様に扱われるようにした。
`02_回答選択肢`・`68_公開フォーム最小質問セット`・Forms実装仕様のいずれも書き換えていない
（`tests/test_corrective_patch1.py::test_adapter_does_not_rewrite_v22_or_forms_spec_files`
でSHA256突合により確認）。

---

## ISS-03（PARTIALLY RESOLVED / Design Disposition Required — `ED-DI-003`）状態Score（D列）が空欄になった場合、Web_DRI/Web_EPI/TOP5_Calcの一部項目がExcel上で#VALUE!になりうる

`WQ_Normalize`の状態Score（D列）・緊急Score（E列）は、選択肢が想定外（例：ISS-02の文言不一致や、
本来存在しない自由入力）の場合、IFチェーンの最終分岐で空欄（Excel上は空文字列）になる。

- `AVERAGE()`を使っている項目（Web_EDIの大半、Web_DRIの一部）は空欄を無視して平均するため
  問題ない。
- しかし `Web_KPI!B6`（Web_DRI）の `0.20*WQ_Normalize!D11` と `0.10*WQ_Normalize!D17` のように
  **単一セルを直接係数倍する項目**は、D11またはD17が空欄だとExcelでは`#VALUE!`エラーになる
  （数値×文字列はエラー）。
- **Corrective Patch 1の調査で追加判明：** `Issue_Candidate`の16課題すべてのU列（緊急度）が
  `=WQ_Normalize!E19`（WQ-405の緊急Score）を直接参照しており、これも同じ単独セル直接参照の
  パターンである。したがってWQ-405が想定外回答で空欄になった場合、Web_KPIだけでなく
  **TOP5_Calcの全16行の計算が同時に失敗しうる**（Task1A時点のコードでは
  `TypeError: unsupported operand type(s) for *: 'float' and 'NoneType'`として実際に検出）。

今回TC-A/B/CではすべてWeb_KPI/Issue_Candidateが認識可能な選択肢を用いたため発生しなかったが、
実運用でISS-02のような文言不一致や想定外回答が入ると、Web_DRI/Web_EPI/TOP5_Calc全体の
算出が失敗しうる状態だった。

### Corrective Patch 1での対応（Rev0.4）

指示どおり、Unknownを一律0点として扱わず、既存の「不明」時の挙動（0点にしない・全体の
評価を歪めない）を踏襲しつつ計算エラーを防ぐ方針で対応した。V2.2 `03_採点マトリクス`の
Q-ID別「不明時処理」（列挙形式が質問ごとに異なる。「不明＝スコア除外＋充足率減＋信頼度減」
「不明＝Guardrail保留表示」「不明＝L1」等）は、公開WQ-IDとの正式な対応表が存在しないため
（`ED-DI-002`）、**移植・流用は一切行っていない。**

代わりに、既にこの数式群の中でExcel自身が採用している「AVERAGE()は空欄を無視して残りの
メンバーで平均する」という原則を、単独セル直接参照の項目（Web_DRIの`D11`・`D17`単独項、
Web_EPIの`E19`単独項、Issue_CandidateのU列＝`E19`）にも一貫して適用する
`energy_doctor_engine/excel_compat.py`の`weighted_score()`を新設した。これは特定の質問の
Unknown処理ルールを規定するものではなく、「空欄の項をその場で除外し、残りのウェイトを
合計1になるよう再正規化する」という既存のAVERAGE挙動をそのまま拡張した、質問非依存の
汎用フォールバックである。

修正済みファイル：`excel_compat.py`（`weighted_score`/`avg_or_none`/`InsufficientDataError`新設）、
`web_kpi.py`（Web_DRI/Web_EPIの該当項をすべて`weighted_score`経由に変更）、
`top5_calc.py`（TOP_BASE計算を`weighted_score`経由に変更）。テストは
`tests/test_corrective_patch1.py`を参照。

### `ED-DI-003`｜ウェイト再正規化方式はS社Disposition待ちの暫定実装（Corrective Patch 1レビューで判明）

Corrective Patch 1のレビューで、上記の「Unknown項目を除外し残りウェイトを再正規化する」
方式（`weighted_score()`）は、V2.2が明示的に定めた唯一の仕様ではなく、他にも同様に成立し
得る設計（①ウェイトを再正規化せず、残った合計が1未満のまま評価する、②該当KPI自体を
「情報不足」として算出しない、③参考値は出しつつ診断信頼度を下げて表示する、等）がある
ことが指摘された。これを`Energy_Doctor_Design_Issue_Log.md`の**`ED-DI-003`（新規）**として
正本側Design Issueに切り出した。**再正規化方式自体（重みの配分ロジック）の是非は、
引き続きS社Dispositionを待つ事項であり、実装側では決定・変更していない。**

`ED-DI-003`は次の4点の正式決定を求めている（詳細はログ本体を参照）：
1. Unknown項目のウェイト再正規化を正式仕様とするか、他方式にするか
2. `Issue_Candidate`のU値にも同じルールを適用するか
3. 全項目Unknown時の挙動（例外か、正常系のINSUFFICIENT_DATA状態か。顧客表示文言含む）
4. KPIを算出・表示してよい最低回答数／最低情報充足率の設定要否

### Corrective Patch 1.1での対応（`ED-DI-003`のうち実装側で対応可能な2点のみ）

`ED-DI-003`の4項目のうち、上記3.（全項目Unknown時の挙動）については、S社Dispositionを
待たずに実装側だけで是正できる問題（Pythonの未捕捉例外がどこにもキャッチされず異常終了に
見えていた点）があったため、Corrective Patch 1.1として次の2点のみを修正した。1./2./4.
（再正規化方式そのものの採否、Issue_CandidateのU値への適用可否、最低情報充足率の要否）は
一切決定・変更していない。

1. **全項目Unknown時を例外ではなく正常な業務状態として返す：** `weighted_score()`が
   全項目Unknown（ウェイト合計0）の場合に送出していた`InsufficientDataError`を、例外throwから
   `None`を返す方式に変更した。呼び出し元（`web_kpi.py`）はこれを受けて該当KPI（Web_EDI/
   Web_DRI）を`None`として扱い、パイプライン全体としては`pipeline.py`が新設した
   `PipelineResult.diagnosis_status`（`"OK"`または`"INSUFFICIENT_DATA"`）で、Web_EDIまたは
   Web_DRIが算出不能だったことを呼び出し側が判定できるようにした。この場合、Guardrail・
   Issue_Candidate・TOP5はいずれも算出せず空リスト/`None`で返す（Guardrail/TOP5非表示）。
   `InsufficientDataError`クラス自体は削除せず残している（将来、厳格な例外送出を望む
   呼び出し側が明示的に使う余地を残すため）。
2. **暫定実装であることの明記：** `weighted_score()`のdocstringに、この再正規化方式が
   「Corrective Patch 1の暫定実装であり、V2.2が定めた唯一の仕様ではない」旨と、代替案・
   `ED-DI-003`への参照を追記した。本ファイル（本節）と`PATCH1_NOTES.md`にも同様に
   `ED-DI-003`への参照を追記した。

修正済みファイル：`excel_compat.py`（`weighted_score()`のdocstring更新・`None`返却化、
`InsufficientDataError`のdocstring更新）、`web_kpi.py`（`WebKPI`の全フィールドをOptional化、
`_round_or_none()`新設）、`pipeline.py`（`diagnosis_status`・`DIAGNOSIS_STATUS_OK`/
`DIAGNOSIS_STATUS_INSUFFICIENT_DATA`新設、`INSUFFICIENT_DATA`時にGuardrail/TOP5をスキップ）。
テストは`tests/test_corrective_patch1.py`の
`test_all_wq_unknown_returns_insufficient_data_status_not_an_exception`等を参照。

`Issue_Candidate`のU列への同ルール適用可否（`ED-DI-003`の決定事項2.）は、今回一切変更・
拡張していない（`top5_calc.py`はCorrective Patch 1時点のまま）。

---

## ISS-04（HOLD・変更禁止）Web_DRI算定式でWQ-403（中期計画）が二重に加重されている

`Web_KPI!B6`（Web_DRI）の数式：

```
0.30*AVERAGE(D4:D5,D8:D9,D13) + 0.25*AVERAGE(D6:D7,D10) + 0.20*D11
  + 0.15*AVERAGE(D15:D17) + 0.10*D17
```

`D17`（WQ-403「中期計画」）が `0.15*AVERAGE(D15:D17)` の一部としても、
`0.10*D17` として単独でも二重に計上されている（WQ-401「管理体制」・WQ-402「判断基準」は
1回ずつしか計上されない）。ウェイト合計は0.30+0.25+0.20+0.15+0.10=1.00で数式自体は
矛盾なく成立するが、意図的にWQ-403を重く見る設計なのか、他のWQ（例:WQ-402）の
書き間違いなのか、Excelのコメント等からは判別できなかった。ロジックは変更せず
数式どおりに実装した。**Rev0.4でHOLD（設計判断待ち）に指定されたため、Corrective
Patch 1でも変更していない**（回帰テスト`tests/test_corrective_patch1.py::test_iss_04_07_08_are_unchanged`
でTC-AのWeb_DRIが36のまま変わらないことを確認済み）。

---

## ISS-05 TOP-R02（重複統合ルール）の実装方法がIssueペアごとに異なる

`TOP5_Final`シートの重複統合は、対象によって実装方法が異なる：

- IS-03（代替手段）とIS-04（EOL・部品供給）→ **構造的に1行へ統合**（`EQ-03`、
  `MAX(スコア3,スコア4)`）。
- BL-01（建屋・環境課題）とBL-03（建屋環境による品質・操業影響）→ **BL-01側に
  条件付き抑制**（`TOP5_Final!H11`: BL-03のスコアが35以上なら常にBL-01を除外）。
  BL-03自体が最終的にTOP5対象か否か（分野上限等で落ちるか）に関わらず、
  BL-03スコア>=35であればBL-01は無条件で候補から除外される。

後者の設計だと、例えば建屋分野で他の2件（BL-02, BL-03）がすでに分野上限2件を
埋めていて、かつBL-03自体がGuardrail等より順位が低くTOP5に入らない場合でも、
BL-01は復活せず候補にすらならない。これが意図どおりか（BL-01は常にBL-03の
下位互換として扱ってよいか）は正本のコメントからは読み取れなかった。
ロジックは変更せず数式どおりに実装した。

---

## ISS-06（RESOLVED）TOP-R03（同一分野最大2件ルール）が同点(タイ)時に3件以上通過しうる

`TOP5_Final!G`列（分野内順位）は `COUNTIFS(同一分野, スコア>自分)+1` で計算されるため、
2位が同点で複数件ある場合、全員が「分野内順位2位」となり、`<=2`判定を全員が
通過してしまう（3件以上が同一分野で候補(H=1)になりうる）。

TC-Aでは「設備」分野でEQ-01/EQ-02が同点51.8で分野内順位2位タイとなり、
EQ-03（74.3, 分野内順位1位）と合わせて3件とも候補（H=1）になっていた
（Task1A時点の`tests/test_tc_a.py`の実行結果でも確認済み）。当時はEQ-01/EQ-02の
最終順位が9位・10位のため最終TOP5には影響しなかったが、スコアの並びによっては
「同一分野最大2件」という設計意図（`TOP5_Final!A2`）に反し、最終TOP5に
同一分野が3件以上含まれる可能性が理論上あった。

### Corrective Patch 1での対応（Rev0.4）

指示どおり、既存のGuardrail優先・TOP_SCORE・TiePriorityの順位ロジック自体は変更せず、
`top5_final.py`に`_enforce_field_cap()`を追加した。これは既存の分野内順位（G列）計算・
既定の候補判定（H列）計算の**後**に適用される後処理で、非Guardrail分野において候補
（`eligible=True`）が2件を超える場合にのみ、スコア降順→TiePriority昇順→シート記載順
（＝既存のFinal Rank計算がすでに使っているタイブレークと同一の優先順位）で上位2件のみを
残し、残りを`eligible=False`に降格する。Guardrail分野（安全・法令の例外）、およびBL-01が
BL-03により無条件抑制される既存ルール（ISS-05）には一切作用しない。

**設計上の注意点（検証済み）：** 単純に「同一分野内でスコア降順・シート順にソートして
一意な順位を振り直す」方式では、BL-01/BL-02のように元々COUNTIFSで正しく区別されていた
（同点でない）ペアまで巻き込んで誤って順位を変えてしまう副作用があることを検証中に発見した
（BL-01がBL-03と同スコアでタイになる場合、ソートによる仮の順位付けがBL-01をBL-02より
先に並べてしまい、本来BL-02が持つべき「分野内順位2位」をBL-01に奪われる）。そのため、
既存のG列・H列の計算はそのまま残し、**候補が2件を超えたときにのみ**上位2件へ絞り込む
後処理として実装した。

回帰確認：TC-Aの「設備」分野（EQ-01/EQ-02/EQ-03）でEQ-02が候補から外れることを確認したが、
EQ-01/EQ-02はもともと最終TOP5に入っていなかったため、TC-AのTOP5自体（順位・課題名・
スコア）はPatch適用前後で完全に一致する（`tests/test_corrective_patch1.py::test_top5_regression_tc_a_unchanged_after_patch`）。
3件が完全に同点となる新規テストケース（`FIELD_CAP_TIE_FORMS_RESPONSE`、管理分野の
MG-01/02/03を意図的に同スコアへ構成）で、候補が正しく2件に制限されることを確認した
（`tests/test_corrective_patch1.py::test_three_way_tie_is_capped_at_two_per_field`）。

---

## ISS-07（HOLD・変更禁止）Guardrailシートは複数カテゴリ同時該当時の「表示優先」を数式で定義していない

`Guardrail`シートは「安全・法令」「品質・顧客要求」「BCP・供給継続」の3行が
独立して算出されるのみで、複数該当時にどれを表示するかを決める数式（例:
MAXやIF）がシート上に存在しない。列構成（基礎順位600/550/500、該当時は一律+50+15）
から、Priority Score（F列）が最大のものを採用するのが自然と判断し、
`energy_doctor_engine/guardrail.py`の`top_guardrail()`でその解釈を実装した。
この解釈がA3レポート側の実際の採用方法と一致しているかは、`A3_Output`等の
別シートでの実際の参照方法を含めて確認を推奨する。**Rev0.4でHOLD（設計判断待ち）に
指定されたため、Corrective Patch 1でも変更していない**（回帰テストでTC-Aの
Guardrail採用結果がBCP・供給継続のまま変わらないことを確認済み）。

---

## ISS-08（軽微・HOLD・変更禁止）WQ-301（建屋環境）は複数選択でも一律60点

`WQ_Normalize!D12`は「特になし」以外の回答なら（「結露」単独でも「結露、暑熱、粉じん」
のような複数選択でも）一律60点になる。深刻な複合環境課題と軽微な単一課題を
区別しない設計だが、これが意図どおりかは正本からは読み取れなかった。
ロジックは変更せず数式どおりに実装した。**Rev0.4でHOLD（設計判断待ち）に指定されたため、
Corrective Patch 1でも変更していない**（回帰テスト`tests/test_corrective_patch1.py::test_iss_04_07_08_are_unchanged`
で単一選択と複数選択のWeb_EDIが一致することを確認済み）。

---

## ISS-09（`ED-DI-002`の実装側確認結果／独立Design Issueではない）公開WQ-ID⇔正式Q-IDの一意対応は確認できなかった

**状態：** OPEN / Blocked by `ED-DI-002`。`Energy_Doctor_Design_Issue_Log.md`の
`ED-DI-002`「関連実装確認（2026-09-02追記）」に記載のとおり、本項目は独立のDesign Issueへ
昇格させず、`ED-DI-002`の実装側裏取り結果として同Issue配下で管理する（本ファイルでは
参照の便宜上、他のISS番号と並べて記載している）。

Corrective Patch 1のISS-03対応にあたり、V2.2 `03_採点マトリクス`（正式Q-ID Q101〜、
「不明時処理」列に質問別の扱いが定義されている）を、公開WQ-ID（WQ-101〜）へ適用できないか
調査した。

**確認結果：** V2.2内に、WQ-IDとQ-IDを同一シート上で対応付けている箇所は見つからなかった
（`03_採点マトリクス`はQ-ID列のみ、`68_公開フォーム最小質問セット`はWQ-ID列のみで、
両者を結ぶ列・シートが存在しない）。これは`Energy_Doctor_Design_Issue_Log.md`の
`ED-DI-002`として既にS社側で認識・登録済みの事項と一致する。

**類推による示唆（実装には一切使用していない）：** 質問テーマの文言を突き合わせると、
`WQ-103（代替手段）`と`Q109（代替手段）`、`WQ-204（省エネ改善）`と`Q224（省エネ改善）`は
テーマ名が完全一致しており、`WQ-101（設備年式把握）`と`Q201（設備年齢）`、
`WQ-102（故障履歴）`と`Q203（故障傾向）`も類似している。ただし、これらは名称の類似から
気づいた**参考情報**に過ぎず、V2.2内のどのシートにもこの対応関係を正式に定義した記載は
ない。Brief Rev0.4の指示（「一意に対応を確認できるものがあれば根拠を示して報告し、
確認できないものはED-DI-002関連Issueとして残す」）に従い、上記はいずれも「一意に確認
できたもの」とは判断せず、正式Q-ID側のUnknown処理をこれらのWQへ移植することはしていない。

**Close条件：** 独立のClose条件は設定しない。`ED-DI-002`本体がClose（WQ-ID⇔Q-ID対応表の
V2.2への登録、対応なし項目の方針決定、Engine実装への反映、回帰試験PASS）した時点で、
本項目も合わせて解消したものとして扱う。

---

## 確認できた一致点（矛盾ではないが記録）

- `01_Core_Design/...V2.2.xlsx`シート`68_公開フォーム最小質問セット`の質問文・選択肢は
  Engine v1.4の`WQ_Normalize`の判定文字列と完全一致していた（`不明`表記含む）。
  Engine v1.4はV2.2シート68を正本として作られていると判断できる根拠になった。
- Web_KPIシートのヘッダーコメント（`Web簡易KPI｜参考値（正式EDI・DRI・EPIを置換しない）`）
  どおり、V2.2シート13の正式KPI算定式とは明確に分離されており、本実装でも
  V2.2シート13は一切参照・再実装していない。
