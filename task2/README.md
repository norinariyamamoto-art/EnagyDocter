# Task 2｜模擬案件データ5パターン

Handoff Brief Rev0.4 Task 2の成果物。当初はCorrective Patch 1.1適用済みのEngineで実施し、
その後Engine Patch 2（ED-DI-002〜005実装）適用後に再実行した（`TASK2_REPORT.md`末尾の
「追記（2026-09-02）」参照）。5ケースのProfile・Forms_Response自体はいずれの実行でも
変更していない。

## ファイル構成

| ファイル | 内容 |
|---|---|
| `scenarios.py` | 5ケースの事業所Profile定義と、そこから導出したForms_Response（18問回答） |
| `run_scenarios.py` | `scenarios.py`をEngineへ投入し、`task2_results.json`（生出力全件）を生成するスクリプト |
| `export_test_data.py` | `forms_responses.json`/`.csv`（入力データのみの整形版）を生成するスクリプト |
| `forms_responses.json` / `forms_responses.csv` | 5ケース分のForms_Response入力データ（テストデータ本体） |
| `task2_results.json` | 5ケースそれぞれの正規化結果・Issue_Candidate・TOP5_Calc・TOP5_Final・Guardrail・Web_KPIの全件生出力（再現用エビデンス） |
| `TASK2_REPORT.md` | 評価レポート本体（Profile・期待挙動・実測結果・PASS/REVIEW判定・違和感の3分類報告） |

## 再実行方法

```bash
cd task2
python3 run_scenarios.py       # task2_results.json を再生成
python3 export_test_data.py    # forms_responses.json/.csv を再生成
```

`sys.path`で`../engine`を参照しているため、`engine/energy_doctor_engine`パッケージが
存在するリポジトリ構成のまま実行すること。
