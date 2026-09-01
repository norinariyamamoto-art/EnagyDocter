# Energy Doctor - Claude Code Handoff Brief Rev0.2
Baseline: 2026-09-01

## 1. Objective
Implement and mechanically verify the Energy Doctor public 18-question diagnostic flow without changing approved diagnostic policy. The next phase is implementation, regression testing, pilot preparation, LP QA, and deployment preparation.

## 2. Source files and authority
1. `01_Core_Design/Energy_Doctor_LP_SelfDiagnosis_Design_V2.2.xlsx`
   - Formal design ledger / frozen design rules.
   - Use for design principles, formal formulas, Guardrail/TOP5 rules, wording-control rules, and traceability.
2. `02_Diagnosis_Engine/Energy_Doctor_Public_Diagnosis_Engine_v1.4_Customer_A3.xlsx`
   - CURRENT executable reference for the PUBLIC 18-question flow.
   - Input path: Forms_Response -> WQ_Normalize -> Issue_Candidate -> Guardrail -> TOP5_Calc -> TOP5_Final -> A3 outputs.
   - Mock_Test_Cases contains TC-A/B/C regression references.
3. `03_Microsoft_Forms/Energy_Doctor_Microsoft_Forms_Implementation_Spec_v1.0.xlsx`
   - Current Forms question/branch/mapping/Go-Live specification.
4. `04_LP_Web/`
   - Current Cloudflare Pages static LP implementation.

## 3. Critical KPI clarification
Do NOT calculate the formal frozen EDI/DRI/EPI from the 18-question public form unless the formal input requirements are actually present.
For the current public flow, reproduce `Web_EDI`, `Web_DRI`, and `Web_EPI` as REFERENCE / PROXY values exactly as implemented in Engine v1.4.
Do not rename these proxy values as formal EDI/DRI/EPI and do not overwrite the V2.2 formal KPI baseline.

If V2.2 and Engine v1.4 appear inconsistent, stop that item and create an issue for human disposition. Do not silently reconcile or invent a rule.

## 4. Task 1 - first and highest priority
Code the CURRENT public Engine v1.4 logic and create automated regression tests for TC-A/B/C.

Required pipeline:
`Forms_Response -> WQ_Normalize -> Issue_Candidate -> Guardrail -> TOP5_Calc -> TOP5_Final`

Requirements:
- Preserve UNKNOWN / `分からない` handling. Do not convert it to zero unless an explicit approved rule requires it.
- Keep Decision Guardrail independent from aggregate KPI scoring.
- Preserve TOP5 duplicate merge, same-field maximum rule, and Guardrail tie priority.
- Do not change approved issue names, scoring weights, thresholds, or wording policy.
- If code and Excel disagree, investigate the code first. If the Excel sources themselves conflict, report the conflict.

Regression expectations:
- TC-A: Web_EDI about 43, Web_DRI about 36, Web_EPI about 80; BCP/supply-continuity Guardrail; Guardrail issue ranks first.
- TC-B: Web_EDI 100, Web_DRI 100, Web_EPI about 18; no Guardrail; do not fabricate five TOP issues when meaningful issues are absent.
- TC-C: Web_EDI about 27, Web_DRI about 22, Web_EPI about 91; safety/legal Guardrail ranks first even under a same-score tie.

Definition of Done:
- automated tests exist in repository;
- TC-A/B/C all PASS;
- comparison output documents Excel expected result vs code result;
- ambiguity/issues list is produced;
- no approved Excel logic was silently changed.

## 5. Tasks after Task 1
Task 2: generate five fictional pilot datasets: aging equipment, energy saving, building/environment, BCP, well-managed.
Task 3: create Forms-export-to-Engine mapping validator. Until real Forms export exists, use expected headers; later replace with actual export.
Task 4: mechanically QA LP HTML/CSS/JS/config: responsive structure, broken links, console errors, alt/ARIA, closed/test/open behavior.
Task 5: prepare Cloudflare Pages/Git deployment while keeping `receptionStatus = closed`.
Task 6: convert Go-Live checklist to version-controlled Markdown/JSON status tracking.
Task 7: only after real operational data exists, prepare aggregate-analysis scripts.

## 6. Out of scope / human approval required
- Creating/configuring Microsoft Forms GUI and issuing its public URL.
- Final customer-facing judgment of A3 wording and whether it could mislead.
- Personal-information / confidential-data policy decisions.
- Final Go-Live approval and switching receptionStatus to `open`.
- Human visual/brand impression review on real devices.
- Any change to diagnostic policy, scoring rules, thresholds, Guardrail policy, TOP5 policy, or approved wording rules.

## 7. Data restrictions
Use fictional test data only. Do not put real customer personal information, confidential information, drawings, or trade secrets into the coding/test environment unless separately approved by the human owner.

## 8. Change control
For every task, state:
- source workbook and sheet(s) used;
- code/files changed;
- test result;
- unresolved issues;
- whether any source ambiguity was found.

Do not proceed from a source ambiguity by assumption.
