# Implementation Plan — NLI-WO-002 Review 01 Remediation

## Scope

Resolve findings F01-F12 on PR #7 while keeping the branch documentation-only and draft. NLI-WO-002B remains unauthorized.

## Finding map

| Finding | Resolution artifact |
|---|---|
| F01 | Rebuilt AC/evidence matrix in `README.md`, PR evidence, review log. |
| F02 | Catalog-derived `current-state-inventory.md` and one-row-per-field `current-to-target-mapping.md`. |
| F03 | `target-model.json`, target registry, reconciled ERD/dictionary/SQL. |
| F04 | Rewritten ADR-006/007 and target object link model. |
| F05 | Rewritten ADR-008, lifecycle, publication snapshot model, SQL fields. |
| F06 | Rewritten geometry model and ADR-009 with observation/version split. |
| F07 | Authoritative `controlled-vocabularies.md`. |
| F08 | Complete target dictionary and API projection map. |
| F09 | Expanded convergence plan. |
| F10 | Worked representative records. |
| F11 | Rewritten ADRs/RFIs; RFI-001 withdrawn; added RFI-006. |
| F12 | `design_consistency_check.py` and generated report. |

## No-change confirmation

No runtime code, executable migration, API contract, infrastructure, or production data will be changed.
