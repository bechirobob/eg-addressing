# NLI-WO-002 Review 09 Finding Resolution Matrix

Date: 2026-07-14  
Review: `docs/sda/reviews/NLI-WO-002-review-09.md`  
Reviewed implementation/design head: `aa77f4b512b7389152239d3eaa27d4ab703c6ad2`  
Reviewer-owned record/current PR head: `77ba5c68ba093a30d840d456ebef0c944a6c4f64`

## Resolution matrix

| Finding | Review 09 issue | Required remediation | Primary evidence artifact(s) | Status |
|---|---|---|---|---|
| F02 | Circular source/expected/actual transform oracle; synthetic FKs; duplicate rows labelled idempotent | Maintain independent source fixtures, independent expected target fixtures and separate transform implementation per group; run transform into schema-compatible target tables; compare exact observed vs expected; enforce real idempotency and full-pipeline failure cases | `review09-source-fixtures-reviewed.json`; `review09-expected-target-fixtures-reviewed.json`; `review09-transform-implementation-reviewed.json`; `review09-transformation-execution-report.json` | Pending |
| F08 | Expected contracts generated from observed OpenAPI/AST; fallback invented fields; heuristic classifications/targets | Maintain independently reviewed expected API contract source; execute/collect observed handler response fixtures; compare exact request/success/error fields, roles/scopes, targets, classifications, owners and release/deprecation/test metadata; unresolved dynamic responses fail | `openapi-expected-contracts-reviewed.json`; `openapi-observed-response-shapes.json`; `openapi-contract-comparison-report.json` | Pending |
| F10 | Scenario query assertions compare against same fixture IDs/counts and presence booleans | Create minimal independent source and expected-result files for seven scenarios; query target DB and compare exact presence/absence across canonical state, relationships, geometry, evidence, lifecycle, publication, operator/public projections and named-date histories | `review09/scenarios/*/source.json`; `review09/scenarios/*/expected.json`; `review09-scenario-comparison-report.json` | Pending |
| F12 | Mutations tamper with generated reports and run checker only | Mutate authoritative source/expected fixture/transform/API/scenario/lifecycle/model inputs in temp repo + disposable PostGIS; run generator/pipeline/helpers/checker; require expected gate failure | `review09-full-pipeline-mutation-report.json` | Pending |
| F04 | Declared record-role/cardinality/name passes | Execute positive/negative record-type-role matrix: required/optional roles, missing required role, invalid role/entity, maxima, retired/deleted/merged subjects, merge/successor and ES/EN current/history names | `review09-f04-record-role-execution-report.json` | Pending |
| F05 | Temporal register/reconstruction descriptive, not complete as-of execution | Reviewed temporal-strategy registry for every mutable authoritative entity; execute registry/effective/public named-date reconstruction and chain/cycle/cross-owner/overlap/backdated/dependent-interval cases | `review09-f05-temporal-execution-report.json` | Pending |
| F06 | Geometry authority still text/JSON claims; incomplete negative matrix | Model typed actor/service identity, institution membership, permission, territorial/data scope, decision authority, observation, evidence and quality assessment; execute full positive/negative authority matrix | `review09-f06-typed-geometry-authority-report.json` | Pending |
| F07 | Lifecycle graph pass statuses hard-coded; transition validator lacks context prerequisites | Build graph validator for each field-bound lifecycle; enforce actor/permission/scope/evidence/audit/public-effect context; execute positive and negative cases per lifecycle family | `review09-f07-lifecycle-graph-report.json` | Pending |
| F09 | Convergence units inherit circular F02 evidence | Revalidate every unit only after independent F02 suite passes; bind unit to exact source fixture, transform command, expected fixture, observed rows/FKs/archive/exception/idempotency and cutover/recovery evidence | `review09-f09-convergence-revalidation-report.json` | Pending |
| F11 | ADR matrix ahead of executable guarantees | Keep ADRs proposed; bind each decision statement to specific independently executable assertions only after lower findings pass; preserve RFIs/conditions | `review09-f11-adr-evidence-report.json`; `adr-005-009-evidence-matrix.md` | Pending |
| F13 | PR #8 separate maintenance dependency | Preserve isolation; do not copy migration-runner fix into PR #7 | changed-path guard | Resolved for PR #7 / external maintenance open |

## Closeout requirements for Review 10

- Every finding gets its own correcting commit and exact evidence.
- S16 self-audit completed at final implementation head.
- Review 09 resolution rows updated individually.
- PR body updated from Review 09 to Review 10 framing.
- Stale/exaggerated evidence claims removed.
- Push and confirm local/remote head equality.
- Confirm PR #7 remains draft/open/unmerged.
- Confirm prohibited runtime paths absent.
- Exact-head GitHub CI green for agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend.
- Record workflow and job IDs.
- Request SDA Review 10 against exact implementation head.
