"""Run the 5 Task 2 scenarios through the existing engine (Corrective Patch
1.1 applied, unmodified) and dump full results as JSON for the evaluation
report. No engine logic is touched by this script."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from energy_doctor_engine import run_pipeline  # noqa: E402

from scenarios import SCENARIOS  # noqa: E402


def issue_to_dict(issue):
    return {
        "issue_id": issue.issue_id,
        "field": issue.field,
        "name": issue.name,
        "main_wq": issue.main_wq,
        "i": issue.i,
        "u": issue.u,
        "p": issue.p,
        "r": issue.r,
        "c": issue.c,
        "o": issue.o,
        "guard_add": issue.guard_add,
        "fire": issue.fire,
    }


def top5_calc_to_dict(row):
    return {
        "issue_id": row.issue_id,
        "field": row.field,
        "name": row.name,
        "top_base": row.top_base,
        "guard_add": row.guard_add,
        "top_score": row.top_score,
        "band": row.band,
        "fire": row.fire,
        "rank": row.rank,
        "is_top5": row.is_top5,
    }


def top5_final_to_dict(row):
    return {
        "candidate_id": row.candidate_id,
        "field": row.field,
        "name": row.name,
        "source_issues": row.source_issues,
        "score": row.score,
        "band": row.band,
        "field_rank": row.field_rank,
        "eligible": row.eligible,
        "final_rank": row.final_rank,
        "is_top5": row.is_top5,
        "tie_priority": row.tie_priority,
    }


def guardrail_to_dict(entry):
    return {
        "category": entry.category,
        "base_rank": entry.base_rank,
        "matched": entry.matched,
        "severity_add": entry.severity_add,
        "evidence_add": entry.evidence_add,
        "priority_score": entry.priority_score,
        "message": entry.message,
        "level": entry.level,
    }


def normalized_to_dict(norm):
    return {
        wq_id: {
            "raw": v.raw,
            "d": v.d,
            "e": v.e,
            "unknown": v.unknown,
            "evidence_c": v.evidence_c,
        }
        for wq_id, v in norm.items()
    }


results = []
for scenario in SCENARIOS:
    result = run_pipeline(scenario.forms_response)
    results.append(
        {
            "case_id": scenario.case_id,
            "company": scenario.company,
            "site": scenario.site,
            "theme": scenario.theme,
            "profile": scenario.profile,
            "forms_response": scenario.forms_response,
            "expected": {
                "guardrail": scenario.expected_guardrail,
                "top5_focus": scenario.expected_top5_focus,
                "edi_direction": scenario.expected_edi_direction,
                "dri_direction": scenario.expected_dri_direction,
                "epi_direction": scenario.expected_epi_direction,
            },
            "actual": {
                "diagnosis_status": result.diagnosis_status,
                "web_kpi": {
                    "web_edi": result.web_kpi.web_edi,
                    "web_edi_band": result.web_kpi.web_edi_band,
                    "web_dri": result.web_kpi.web_dri,
                    "web_dri_band": result.web_kpi.web_dri_band,
                    "web_dri_top5_r": result.web_kpi.web_dri_top5_r,
                    "web_epi": result.web_kpi.web_epi,
                    "web_epi_band": result.web_kpi.web_epi_band,
                },
                "guardrail_entries": [guardrail_to_dict(e) for e in result.guardrail_entries],
                "top_guardrail": guardrail_to_dict(result.top_guardrail) if result.top_guardrail else None,
                "normalized": normalized_to_dict(result.normalized),
                "issue_candidates": [issue_to_dict(i) for i in result.issue_candidates],
                "top5_calc": [top5_calc_to_dict(r) for r in result.top5_calc],
                "top5_final": [top5_final_to_dict(r) for r in result.top5_final],
                "top5": [top5_final_to_dict(r) for r in result.top5],
            },
        }
    )

out_path = Path(__file__).resolve().parent / "task2_results.json"
out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {out_path}")

for r in results:
    print(f"\n=== {r['case_id']} {r['company']} {r['site']} ({r['theme']}) ===")
    kpi = r["actual"]["web_kpi"]
    print(f"  status={r['actual']['diagnosis_status']}")
    print(f"  Web_EDI={kpi['web_edi']} ({kpi['web_edi_band']})  Web_DRI={kpi['web_dri']} ({kpi['web_dri_band']})  Web_EPI={kpi['web_epi']} ({kpi['web_epi_band']})")
    tg = r["actual"]["top_guardrail"]
    print(f"  Guardrail: {tg['category'] + ' ' + tg['level'] if tg else 'なし'}")
    print(f"  TOP5 ({len(r['actual']['top5'])}件):")
    for row in r["actual"]["top5"]:
        print(f"    #{row['final_rank']} {row['candidate_id']:8s} {row['name']} score={row['score']} band={row['band']}")
