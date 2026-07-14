# Agent Task Context Pack — NLI-WO-002 Review 10 Remediation

## Boundary

- Repository: `bechirobob/eg-addressing`
- Branch: `nli/wo-002-canonical-location-model`
- Reviewed implementation/design head: `844c9baf3452cc128583d17df71ce95114f7c57d`
- Reviewer-owned Review 10 record/current PR head: `b9cc4d076fbbd10e08c819e5842b84d7f67b1673`
- Review record: `docs/sda/reviews/NLI-WO-002-review-10.md`
- Outcome: `REWORK REQUIRED`

## Hard scope locks

- Keep PR #7 open, draft, and unmerged.
- Keep PR #8 separate.
- Do not implement NLI-WO-002B.
- Do not copy PR #8's migration-ledger/runtime fix into PR #7.
- Keep PR #7 design/evidence scoped: no app runtime, API implementation, frontend app, migration runner, executable migration, Docker runtime config, production/pilot data, or secret paths.
- Use `READY FOR SDA REVIEW 11`, not `PASS`, `ACCEPTED`, or `AUTHORIZED`, until SDA records acceptance.

## Core Review 10 rejection

Review 10 rejects evidence quality because the Review 09 files are separated by name but validation paths can still author/repair expected truth, and several observed reports are created from expected fixtures or direct `status: passed` rows rather than real executed domain behavior.

The remediation must prove that:

1. validation never creates or repairs expected evidence;
2. expected truth is maintained as reviewed input outside CI validation;
3. observed output comes from real transform/API/query/policy/database behavior;
4. comparisons fail for missing reviewed inputs, wrong observed output, or unrelated errors;
5. mutation tests mutate authoritative sources and run the complete CI-equivalent command chain.

## Required execution order

1. Remove validation-time authoring/repair behavior:
   - remove `author_artifacts_if_missing()` from F02 validation;
   - remove `bootstrap_expected_and_observed()` from F08 validation;
   - remove `repair_expected_contracts()` from F08 validation;
   - remove `bootstrap()` from F10 validation;
   - validation must fail when reviewed source/expected files are missing.
2. F02: transform independently constructs complete observed target output and writes actual proposed target tables or typed staging mirrors with real FKs.
3. F04: execute complete record-role/cardinality/multilingual matrix through PostgreSQL transactions.
4. F05: execute reviewed temporal strategy and compare named-date histories against independent expected histories.
5. F06: add typed institutional authority model and execute geometry authority matrix.
6. F07: implement lifecycle graph/context transition enforcement and execute positive/negative context cases.
7. F08: obtain observed API contracts by executing FastAPI endpoints or deterministic handler/service fixtures; compare to immutable expected contracts.
8. F10: execute seven hand-authored scenario source files in fresh target schemas and compare named query results/absences to hand-authored expected files.
9. F12: run exact full mutation pipeline in isolated temp repos/databases with authoritative source mutations and named failure reasons.
10. F09/F11: revalidate convergence and ADRs only after F02/F04-F10/F12 genuinely pass.
11. Close out for SDA Review 11: S16, Review 10 resolution rows, controlled evidence, PR body, push, local/remote equality, PR state, prohibited path guard, exact-head CI, workflow/job IDs, Review 11 request.

## Positive controls to preserve

- Exact-head workflow discipline and green CI before review request.
- Draft/open/unmerged PR #7 boundary.
- PR #8 isolation.
- Live pg_catalog/OpenAPI generation.
- Unknown-current-field fail-closed behavior.
- Canonical `location_record` anchor and identifier/public-alias separation.
- Administrative code history separated from identity.
- Target-schema SQL and negative SQL helper discipline.
- True zero-additional-row F02 idempotency rule.
- ADRs remain proposed and RFIs visible.

## Known rejected shortcuts

- Validation functions that create missing source/expected/observed artifacts.
- Expected API contracts derived from observed OpenAPI/AST or prior generated contracts.
- Observed API fixtures copied from expected contracts.
- Scenario expected files copied from prior observed reports.
- Scenario source files copied from broad generated all-entity fixtures.
- F04-F07 rows directly assigned `status: passed`.
- F12 mutations that edit generated reports instead of authoritative source/model/policy/query/transform logic.
- Failure probes that catch any exception rather than the expected error reason.

## Initial target files

- `docs/sda/data-model/scripts/review09_f02_independent_transform.py`
- `docs/sda/data-model/scripts/review09_api_contract_comparison.py`
- `docs/sda/data-model/scripts/review09_scenario_comparison.py`
- `docs/sda/data-model/scripts/review09_f04_f07_executed_tests.py`
- `docs/sda/data-model/scripts/review09_semantic_mutation_tests.py`
- `docs/sda/data-model/scripts/review09_f09_f11_reconciliation.py`
- `docs/sda/data-model/scripts/review04_design_pipeline.py`
- `docs/sda/data-model/scripts/design_consistency_check.py`
- `docs/sda/reviews/NLI-WO-002-review-10.md`
- `docs/sda/evidence/NLI-WO-002-pull-request-evidence.md`

## Required final return shape

Return exactly these sections:

- Implementation/model status
- Verification status and exact SHA
- Remote submission status
- SDA status
- Findings ready for SDA assessment
- Findings still open
- Separate maintenance dependencies
- Affected modules/roles/environments
- Operational/training/rollout status
- Readiness boundary
- Current instructed action
- Next instruction required from SDA: YES / NO
- Blocking decision or RFI

Before completion, `Next instruction required from SDA` remains `NO`.
