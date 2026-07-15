# NLI-WO-002 Pull Request Evidence — Review 10 Remediation / Review 11 Request

Draft PR #7 remains draft and unmerged. NLI-WO-002B remains unauthorized. PR #8 remains separate.

## Final submission head pending exact-head CI

- Final PR head is recorded in the PR body and Review 11 request after push.
- Final GitHub Actions workflow/job IDs are recorded in the PR body after exact-head CI completes.
- SDA Review 11 must not be requested until exact-head local/remote equality and CI are verified.

## Review 10 remediation commits

| Purpose | Commit |
|---|---|
| Review 10 task context and finding matrix | `32b9d18` |
| Remove validation-time authoring/repair | `e8064e9` |
| F02 independent observed target construction | `d4c85e3` |
| F04/F05/F06/F07 PostgreSQL execution suites | `91f294b` |
| F08 FastAPI/OpenAPI observed contract comparison | `be92706` |
| F10 fresh scenario source execution | `c645a21` |
| F12 mutation and F09/F11 convergence gates | `97c01ef` |

## Criterion-specific evidence matrix

| Criterion | Status | Assertion | Evidence | Remaining condition |
|---|---|---|---|---|
| AC-01 | READY FOR SDA REVIEW | pg_catalog inventory generated from disposable migrated PostGIS DB: 25 tables, 237 fields; reviewed current-field semantics added. | `current-pg-catalog.json`, `current-field-semantics-reviewed.json`, design report `Generated checks: 6284`, `Errors: 0`. | SDA acceptance pending |
| AC-02 | READY FOR SDA REVIEW | `location_record` remains canonical anchor; source identity/crosswalk assertions are named and checked. | F02 fixture report; target model. | SDA acceptance pending |
| AC-03 | READY FOR SDA REVIEW | administrative version/history scenario includes old/new versions and temporal assertions. | Review 09 F05/F10 temporal and scenario reports. | SDA acceptance pending |
| AC-04 | READY FOR SDA REVIEW | operational area remains separate from administrative units and convergence units preserve ownership boundary. | target model; convergence plan. | SDA acceptance pending |
| AC-05 | READY FOR SDA REVIEW | all canonical record types appear in positive inserted fixtures; multi-unit records are independent. | machine-readable fixtures; F04/F10 assertions. | SDA acceptance pending |
| AC-06 | READY FOR SDA REVIEW | internal IDs, public aliases, legacy crosswalks and unresolved references are separated; crosswalk-only final FK regressions fail. | F02 report; ADR-005 matrix row. | SDA acceptance pending |
| AC-07 | READY FOR SDA REVIEW | lifecycle policy table is populated and all 96 reviewed transitions execute positively. | `target-schema-catalog.json`; lifecycle transitions. | SDA acceptance pending |
| AC-08 | READY FOR SDA REVIEW | temporal/version scenarios prove corrected/superseded and administrative old/new history. | F05/F10 scenario assertions; mutation tests. | SDA acceptance pending |
| AC-09 | READY FOR SDA REVIEW | geometry promotion binds decision type/outcome, permission, institution/scope, observation, evidence and quality actor; four authority negatives reject. | physical SQL; target catalog; negative fixture report. | SDA acceptance pending |
| AC-10 | READY FOR SDA REVIEW | name records and subject integrity remain enforced; cardinality and scenario assertions cover subject links. | target schema/catalog. | SDA acceptance pending |
| AC-11 | READY FOR SDA REVIEW | governed archive/source/crosswalk joins are represented in executable F02 assertions and exception paths. | Review 09 source/expected/transform fixtures and transformation fixture report. | SDA acceptance pending |
| AC-12 | READY FOR SDA REVIEW | current/API classifications use reviewed sources; credential/header fields are non-business migration boundaries. | current semantics and API projection contracts. | SDA acceptance pending |
| AC-13 | READY FOR SDA REVIEW | lifecycle graphs are reviewed, loaded and positively exercised. | lifecycle assertion results. | SDA acceptance pending |
| AC-14 | READY FOR SDA REVIEW | target schema executes; 11 negative cases reject; mutation tests catch missing trigger/constraint regressions. | target schema validation; semantic mutation report. | SDA acceptance pending |
| AC-15 | READY FOR SDA REVIEW | 105 OpenAPI operations have independently reviewed route policies and 555 field projection assertions. | independent API expected contracts, observed response fixtures and projection assertions. | SDA acceptance pending |
| AC-16 | READY FOR SDA REVIEW | transformation registry covers 237 current fields with 90 fixtures and 1,370 named assertions. | Review 09 F02 independent transform report. | SDA acceptance pending |
| AC-17 | READY FOR SDA REVIEW | 90 convergence units are reviewed and tied to passing F02 assertions; no production migration authority claimed. | reviewed convergence units and plan. | SDA acceptance pending |
| AC-18 | READY FOR SDA REVIEW | seven scenario builders insert 342 target rows, execute 11 negative cases and expose 49 F04/F05/F10 assertions. | Review 09 independent scenario source/expected files and comparison report. | SDA acceptance pending |
| AC-19 | READY FOR SDA REVIEW | scale assumptions remain owner-pending and not production readiness evidence. | convergence units/plan. | SDA acceptance pending |
| AC-20 | READY FOR SDA REVIEW | disposable PostGIS target SQL executes; physical catalog parity is checked; semantic mutation probes pass. | target schema report; mutation report. | SDA acceptance pending |
| AC-21 | READY FOR SDA REVIEW | ADR-005..ADR-009 map acceptance claims to named assertions and visible unresolved conditions; ADRs remain proposed. | Review 09 F09/F11 reconciliation and ADR evidence matrix. | SDA acceptance pending |
| AC-22 | READY FOR SDA REVIEW | PR #7 excludes prohibited runtime paths; migration-ledger fix remains separate in PR #8. | changed-path proof and S16 audit. | SDA acceptance pending |

## Local verification before final push

- `review04_design_pipeline.py`: PASS against disposable PostGIS.
- `review09_semantic_mutation_tests.py`: PASS, 11/11 mutations caught.
- `design_consistency_check.py`: PASS, `Generated checks: 4371`, `Errors: 0`, `Warnings: 0`.
- `validate_skill_pack.py`: PASS, 31 skills, 50 Markdown files.
- `git diff --check`: PASS.
- Prohibited path guard: PASS; no changes under `services/api/**`, `infra/scripts/migrate.py`, `infra/migrations/**`, `apps/**`, `infra/docker/**`, `data/**`, or `.env*`.

## Changed-path proof

Scope guard before closeout found no changes under:

- `services/api/**`
- `infra/scripts/migrate.py`
- `infra/migrations/**`
- `apps/**`
- `infra/docker/**`
- `data/**`
- `.env*`

PR #7 remains a design/evidence PR. The migration-ledger advisory-lock fix is isolated in maintenance PR #8 under NLI-WO-001 database-lifecycle controls.
