# NLI-WO-002 Pull Request Evidence — Review 07

Draft PR #7 remains draft and unmerged. NLI-WO-002B remains unauthorized.

## Exact implementation head validated before evidence closeout

- Implementation/stamp head validated by GitHub Actions: `f36cda7d68a6131ffdd1c11b86d2569860686788`
- API CI run `29337375340`: **success**
  - `migration-lifecycle` job `87099934845`: success
  - `api-image-runtime` job `87099934865`: success
  - `sda-design-model` job `87099934876`: success
  - `api-tests` job `87099934897`: success
- Frontend CI run `29337375180`: **success**
  - `frontend` job `87099934523`: success

Final PR-head CI after this evidence closeout is recorded in the SDA Review 07 request comment.

## Review 06 remediation commits

| Purpose | Commit |
|---|---|
| Review 06 semantic remediation | `1cf7d555a08de750c580b87de14bc2020dc7a052` |
| Review 06 resolution evidence stamp | `f36cda7d68a6131ffdd1c11b86d2569860686788` |
| Migration-ledger runtime fix split out | Maintenance PR #8, not PR #7 |

## Criterion-specific evidence matrix

| Criterion | Status | Assertion | Evidence | Remaining condition |
|---|---|---|---|---|
| AC-01 | READY FOR SDA REVIEW | pg_catalog inventory generated from disposable migrated PostGIS DB: 25 tables, 237 fields, ledger included. | Review 07 semantic-design CI exact-head run; design report Generated checks: 41, Errors: 0. | SDA acceptance pending |
| AC-02 | READY FOR SDA REVIEW | location_record remains sole canonical anchor; subject registry/crosswalks prevent second address authority. | Target model, subject registry checks, reviewed transformation registry. | SDA acceptance pending |
| AC-03 | READY FOR SDA REVIEW | administrative code history and name history are separated from identity. | Target registry and target schema validation. | SDA acceptance pending |
| AC-04 | READY FOR SDA REVIEW | operational area lifecycle remains separate from administrative units. | Controlled vocabulary/lifecycle registry. | SDA acceptance pending |
| AC-05 | READY FOR SDA REVIEW | record/object matrix is keyed by actual canonical record_type values, not standard-address. | Executed target schema and semantic checker. | SDA acceptance pending |
| AC-06 | READY FOR SDA REVIEW | internal IDs, public aliases and legacy crosswalks are separated with exact reference-crosswalk joins. | Reviewed transformation rows and ADR-005. | SDA acceptance pending |
| AC-07 | READY FOR SDA REVIEW | lifecycle graphs load into executable transition policy and are checked for field bindings/edge metadata. | Lifecycle registry and target helper table catalog. | SDA acceptance pending |
| AC-08 | READY FOR SDA REVIEW | version, alias and geometry supersession rules include no-self/reciprocal/same-owner/acyclic checks. | Target SQL triggers and negative execution. | SDA acceptance pending |
| AC-09 | READY FOR SDA REVIEW | geometry promotion requires authorized decision, evidence object, authority scope, accepted quality and same-subject/role supersession. | Target model, target SQL trigger and scenario fixtures. | SDA acceptance pending |
| AC-10 | READY FOR SDA REVIEW | name records and subject integrity are enforced through registry-subject FK and current-name rule. | Target schema validation. | SDA acceptance pending |
| AC-11 | READY FOR SDA REVIEW | governed archive and source/crosswalk joins preserve original facts and exception paths. | Reviewed transformation registry. | SDA acceptance pending |
| AC-12 | READY FOR SDA REVIEW | classifications are explicit in current/target mapping and API contracts. | API projection contracts and field registry. | SDA acceptance pending |
| AC-13 | READY FOR SDA REVIEW | field-to-vocabulary registry and transition graphs are validated. | Controlled vocabularies and lifecycle transitions. | SDA acceptance pending |
| AC-14 | READY FOR SDA REVIEW | target schema executed; constraints, indexes, triggers and helper policy tables cataloged. | Target schema validation report. | SDA acceptance pending |
| AC-15 | READY FOR SDA REVIEW | 105 OpenAPI operations have exact method/path/handler/auth/roles and concrete projection contracts. | Route policy and projection contract registries. | SDA acceptance pending |
| AC-16 | READY FOR SDA REVIEW | transformation registry covers 237 current fields with executable SELECT no-loss assertions and reference joins. | Transformation registry and semantic checker. | SDA acceptance pending |
| AC-17 | READY FOR SDA REVIEW | convergence plan is rebuilt after accepted transformation rows and no longer uses pseudo-ASSERT validation. | Schema convergence plan. | SDA acceptance pending |
| AC-18 | READY FOR SDA REVIEW | seven scenario builders insert 342 target rows and execute seven negative cases. | Machine-readable fixtures and target report. | SDA acceptance pending |
| AC-19 | READY FOR SDA REVIEW | scale assumptions remain explicitly review inputs, not implementation authorization. | Convergence plan and Review 06 resolution log. | SDA acceptance pending |
| AC-20 | READY FOR SDA REVIEW | dependency-safe target SQL executes in disposable PostGIS and catalog parity is checked. | sda-design-model job evidence; final PR-head job IDs are in the Review 07 request comment. | SDA acceptance pending |
| AC-21 | READY FOR SDA REVIEW | ADRs 005-009 are hand-maintained source docs with Review 07 assertion reconciliation. | ADRs 005-009. | SDA acceptance pending |
| AC-22 | READY FOR SDA REVIEW | PR #7 excludes runtime code, executable migrations, app code, production data and env files; migration-ledger fix is split to PR #8. | Changed-path proof and PR state. | SDA acceptance pending |

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
