"""Export the 5 Task 2 scenarios' Forms_Response inputs as JSON and CSV test
data (the deliverable format requested), separate from the full engine
output dump (task2_results.json)."""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scenarios import SCENARIOS  # noqa: E402

WQ_COLUMNS = [
    "WQ-001",
    "WQ-101", "WQ-102", "WQ-103", "WQ-104",
    "WQ-201", "WQ-202", "WQ-203", "WQ-204",
    "WQ-301", "WQ-302", "WQ-303",
    "WQ-401", "WQ-402", "WQ-403", "WQ-404", "WQ-405",
    "WQ-501",
]

out_dir = Path(__file__).resolve().parent

# JSON
json_data = [
    {
        "case_id": s.case_id,
        "company": s.company,
        "site": s.site,
        "theme": s.theme,
        "profile": s.profile,
        "forms_response": s.forms_response,
    }
    for s in SCENARIOS
]
(out_dir / "forms_responses.json").write_text(
    json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8"
)

# CSV (wide: one row per case, one column per WQ)
with open(out_dir / "forms_responses.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["case_id", "company", "site", "theme"] + WQ_COLUMNS)
    for s in SCENARIOS:
        writer.writerow(
            [s.case_id, s.company, s.site, s.theme]
            + [s.forms_response.get(wq, "") for wq in WQ_COLUMNS]
        )

print("Wrote forms_responses.json and forms_responses.csv")
