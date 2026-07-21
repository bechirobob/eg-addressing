# NLI-WO-002 Authoritative Assurance Harness — Review 11 Checkpoint

## 0. Checkpoint boundary

This document is the F14 architecture checkpoint requested by SDA Review 11. It is **not** a remediation implementation.

At this stage:

- Do **not** mark F02-F12 or F14 resolved.
- Do **not** request SDA Review 12.
- Do **not** add another review-numbered shadow framework such as `r11_*` tables, reports, policies or scripts.
- Do **not** modify runtime application code, frontend code, executable migrations, migration runner, Docker runtime configuration, production/pilot data, `.env*`, secrets, or PR #8 changes.
- Do **not** copy PR #8's runtime fix into PR #7.
- Implementation of this harness requires SDA assessment and the next controlled instruction.

## 1. Design objective

SDA Review 11 rejected the evidence architecture because Review 04-10 validation increasingly proved parallel shadow models instead of the proposed target design. The replacement assurance harness must have **one executable source of target truth**:

1. Accepted current migrations create the current/source side.
2. `docs/sda/data-model/draft-physical-schema.sql` creates the canonical target side.
3. Separately reviewed fixtures and expected outputs live in control tables/files and are never generated, repaired or derived from observed output by validation.
4. Every F02-F12 claim is observed from the same current-source, canonical-target and control execution path.

The harness is a design-validation jutsu, not NLI-WO-002B runtime implementation.

## 2. Proposed database/schema topology

The authoritative harness uses one disposable PostgreSQL/PostGIS database per local/CI run, with three isolated schemas. Mutation tests create a fresh database or fresh isolated schema set per mutation case.

| Schema/database role | Name | Built from | Purpose | May contain |
|---|---|---|---|---|
| Current source | `current_source` | Accepted migrations via `infra/scripts/migrate.py apply` against an empty disposable database, then schema moved/set/search-pathed or applied into an isolated database used as source authority | Catalog-derived current records, complete source rows, current API data setup where needed | Current application tables, migration ledger, reference data, controlled source fixtures |
| Canonical target | `canonical_target` | `docs/sda/data-model/draft-physical-schema.sql` from empty | The only executable target truth for WO-002 design validation | Proposed target tables, constraints, functions, triggers, indexes, vocabularies, target fixtures produced by transforms |
| Test control | `test_control` | Harness control DDL generated from reviewed source registries, not review-numbered shadow domain tables | Run metadata, immutable expected truth, source/target fixture manifests, comparison results, mutation control, evidence hashes | Expected source records, expected target records, expected API contracts, expected scenario outputs, run IDs, assertion rows |

### 2.1 Topology rules

- `current_source` must be built from accepted migrations, not regex-parsed SQL or generated catalog JSON alone.
- `canonical_target` must be built from `docs/sda/data-model/draft-physical-schema.sql` exactly as checked in for PR #7.
- `test_control` is not a parallel business model. It stores harness metadata and independently reviewed expected truth only.
- No `r11_*` policy/schema. Existing `r10_*` shadows are not carried forward.
- Target assertions must query `canonical_target` tables, constraints, functions, triggers and FKs.
- Control assertions may store expected values and comparison results, but cannot decide policy independently when the target schema should decide.

## 3. Authoritative test paths

The single harness will execute the following paths through one database topology.

| Review area | Authoritative execution path |
|---|---|
| Complete current source records | Load complete records into `current_source` using accepted migration tables, reference data and harness source fixture manifests. Source records are keyed by actual source primary/natural keys, not one row per field. |
| Grouped source-to-target transformations | Run grouped transform implementations that consume complete source records and produce one or more intended target rows. Transform groups define source keys, target entities, child rows, ID/crosswalk algorithms, archive/exception behavior and idempotency key. |
| Actual target entity inserts | Insert into `canonical_target` target tables created by `draft-physical-schema.sql`, not generic text staging. |
| Actual target foreign keys | Validate FKs by querying actual `canonical_target` primary keys and relationship tables. Final canonical FKs must reference real target rows. |
| Actual target constraints and triggers | Positive and negative cases execute transactions against target constraints/functions/triggers. Broad catch-all failures are not accepted; expected error message/reason must match. |
| Record-role cardinality | Insert target records, versions and object links into `canonical_target`; test required/optional absence, min/max, invalid role/entity, retired/deleted/merged successor repointing and bilingual name history using target queries. |
| Temporal reconstruction | Load reviewed histories into target temporal tables; execute registry-as-recorded, effective-as-of and public-release queries at named dates; execute invalid cycles, overlap, reciprocal mismatch, cross-owner and dependent-interval operations against target constraints/functions. |
| Geometry authority | Exercise target geometry observation/version/evidence/decision/quality tables and typed authority assertion references. Promotion must fail without permitted actor/institution/scope/evidence/quality/decision. |
| Lifecycle contextual policy | Load reviewed lifecycle metadata for initial/terminal states, re-entry, forbidden transitions, permission keys, institution/scope, evidence, audit and public-effect prerequisites; execute target transition policy for every edge or coverage-complete partition. |
| Seven national scenarios | Load complete hand-authored scenario source records into `current_source`, run transforms into `canonical_target`, then query named-time canonical/effective/recorded/public/operator projections and expected absences. |
| API response observations | Use FastAPI `TestClient` or deterministic handler/service fixtures against controlled data to capture real request, success and error shapes, authentication mode, roles/scopes and unexpected fields. OpenAPI remains an inventory input, not the sole observer. |
| Convergence validation | Generate convergence evidence from authoritative target rows, relationships, exceptions, archives, crosswalks, idempotent rerun and recovery/cutover metadata. |
| Mutation testing | For each mutation, create complete checkout/database isolation, mutate authoritative source/model/policy/fixture/API/scenario inputs, run exact CI path, and require the named gate/reason. |

## 4. Fixture authority

Validation must never create, repair, or derive expected truth from observed output.

| Fixture class | Authority and maintenance rule | Forbidden validation behavior |
|---|---|---|
| Complete source records | Hand-authored under reviewed fixture directories; each fixture references actual current-source table/key/field groups and source package metadata. | Creating missing source fixtures from current catalogs or observed target output. |
| Expected target records | Hand-authored expected target entities/relationships with real target table names, typed values, expected target keys/FKs and allowed absences. | Deriving expected rows from transform output, target inserts or generated reports. |
| Transform implementation | Separate reviewed implementation spec or executable script mapping complete source records to target rows. | Reading expected target rows to decide target entity, field, identity, relationship, archive, exception or FK. |
| Expected API contracts | Reviewed operation contracts with method/path/operation/handler/auth/roles/scopes, exact request fields, success fields, error fields, classification and target projection/non-migrated decision. | Repairing contracts from OpenAPI, observed responses or previous report rows. |
| Expected scenario outputs | Hand-authored expected canonical/effective/recorded/public/operator outputs and expected absences for each named date. | Copying expected outputs from observed scenario reports. |
| Expected mutation failures | Reviewed mutation manifest naming source mutation, expected failing gate, expected reason and unrelated setup failures that do not count. | Editing detector/test code to raise the expected reason or pre-seeding passing results. |

## 5. API execution design

OpenAPI-only observation is insufficient for dynamic responses. The harness will use a two-level approach.

### 5.1 Static inventory

- Generate current OpenAPI from `services/api/app/main.py`.
- Inventory method, path, operation ID, parameters, declared schemas and response status codes.
- Use OpenAPI to detect declared compatibility drift, not as proof of dynamic response shape.

### 5.2 Runtime observation

For each operation in scope:

1. Create controlled source/current data using accepted migrations and fixture setup.
2. Use FastAPI `TestClient(app)` when route dependencies can be satisfied in-process.
3. Use deterministic handler/service fixture execution only when full HTTP setup would require unrelated infrastructure; record the reason and exact callable.
4. Execute:
   - unauthenticated request where relevant;
   - authenticated allowed role/scope request;
   - wrong role;
   - wrong territorial/data scope where implemented;
   - invalid record state where implemented;
   - validation-error request.
5. Capture recursively:
   - request shape actually accepted;
   - success response shape and values/classes;
   - error response shape;
   - status code;
   - authentication mode;
   - roles and scopes required/observed;
   - unexpected fields.
6. Compare against immutable expected contracts.

### 5.3 API failure rules

- Unexpected success fields fail unless an expected contract explicitly reviews/classifies them.
- Missing expected fields fail.
- Broad `response.body: object` is allowed only when paired with a reviewed explicit non-migrated decision and a reason why nested fields are not part of the contract.
- Route auth/roles/scopes must be compared, not just recorded.
- Sensitive field projection changes require explicit review.

## 6. Existing script disposition

| Script | Current role | Disposition | Reason / target harness role |
|---|---|---|---|
| `review04_design_pipeline.py` | Generates current inventory, target model artifacts, draft schema reports and evidence. | Refactor into authoritative harness entrypoint modules. | Retain catalog/OpenAPI generation concepts; remove evidence aggregation that accepts shadow-suite counts as authoritative. |
| `design_consistency_check.py` | Consistency gate across generated reports and review artifacts. | Refactor. | It should read authoritative harness run results and generated artifact parity, not bless parallel reports. |
| `review07_semantic_mutation_tests.py` | Older mutation checks. | Retire after authoritative F12 replacement is accepted. | Superseded by source-mutation manifest and fresh DB/repo isolation. |
| `review08_semantic_mutation_tests.py` | Review 08 mutation checks. | Retire after authoritative F12 replacement is accepted. | Superseded by authoritative mutation runner. |
| `review08_f04_f07_integrity_report.py` | Review 08 integrity report. | Retire after authoritative F04-F07 target-schema tests exist. | Metadata/report presence cannot be target truth. |
| `review08_f09_f11_reconciliation.py` | Older convergence/ADR reconciliation. | Retire after authoritative F09/F11 exists. | Superseded by target-row convergence evidence. |
| `review08_api_projection_contracts.py` | Earlier API projection generation. | Refactor or retire. | Keep only any useful static inventory logic; dynamic runtime contract comparison moves to harness. |
| `review09_f02_independent_transform.py` | F02 field-level transform runner using generic staging. | Refactor into complete-record transform harness. | Preserve no-bootstrap, strict expected-error and idempotency discipline; replace per-field generic tables with target inserts. |
| `review09_api_contract_comparison.py` | F08 OpenAPI expected-vs-observed comparison. | Refactor into runtime API contract harness. | Preserve immutable expected contract principle; add TestClient/handler execution and unexpected-field failures. |
| `review09_scenario_comparison.py` | F10 generic scenario table comparison. | Replace. | Scenario execution must load actual target schema and complete domain records; `r10_scenario_entity` retires. |
| `review09_f04_f07_executed_tests.py` | F04-F07 PostgreSQL tests using `r10_*` shadow tables and Python policies. | Replace/refactor by extracting case inventory only. | The execution target becomes `canonical_target`; shadow policy tables retire. |
| `review09_semantic_mutation_tests.py` | F12 temp-workspace mutation runner. | Replace. | Must use full repo checkout, fresh DB/schema per case, no seeded pass report, authoritative-source mutations only. |
| `review09_f09_f11_reconciliation.py` | F09/F11 reconciliation using suite labels/reports. | Refactor. | Must reconcile target rows/FKs/exceptions/archives/API/scenario evidence from authoritative harness. |

### 6.1 `r10_*` shadow tables and policies to retire

The following are test-only parallel schema objects and must not continue as the authoritative evidence path once equivalent target-schema checks exist:

- `r10_role_rule`
- `r10_subject`
- `r10_location_record`
- `r10_location_record_version`
- `r10_location_record_object_link`
- `r10_name_record`
- `r10_temporal_strategy`
- `r10_temporal_history`
- `r10_temporal_link`
- `r10_actor`
- `r10_service`
- `r10_institution`
- `r10_membership`
- `r10_permission`
- `r10_territorial_scope`
- `r10_data_scope`
- `r10_authority_assertion`
- `r10_decision_event`
- `r10_observation`
- `r10_evidence`
- `r10_quality_assessment`
- `r10_geometry_promotion`
- `r10_scenario_entity`

The business rules currently implemented in Python helpers such as `assert_role_valid()`, `assert_required_roles()`, `assert_promotion()` and lifecycle context lambdas must move to target-schema functions/constraints or to harness code that only invokes target functions and compares results.

## 7. Mutation isolation design

Each mutation case must be isolated.

| Step | Required behavior |
|---|---|
| Complete checkout | Use a complete repository checkout/worktree including `docs/`, `services/`, `infra/`, workflows and any scripts required by CI. Partial copies are prohibited. |
| Fresh database/schema | Create a new disposable database or unique schema set for the mutation case. Do not reuse the base run database. |
| Current migrations | Apply accepted current migrations from empty using the controlled migration path. |
| Target design | Apply `docs/sda/data-model/draft-physical-schema.sql` from empty into `canonical_target`. |
| Mutation target | Mutate authoritative sources: current source fixture, expected target fixture, transform implementation, target model/schema source, role/cardinality source, temporal policy source, geometry authority source, lifecycle metadata, expected API contract or runtime response fixture, scenario source/expected/query logic. |
| Prohibited mutation target | Do not mutate detector/test code to raise expected text. Do not pre-seed passing reports. |
| Exact CI path | Run the same design-harness command chain used by CI. |
| Failure requirement | The mutation must fail at the named gate for the named reason. Setup/dependency errors do not count. |
| Cleanup | Drop mutation database/schema and remove temp checkout/worktree. Record cleanup result. |

## 8. Proposed exact CI command chain

The future authoritative `sda-design-model` path should replace the current Review 04-10 sequence with a single harness chain. Names are proposed and require SDA acceptance before implementation.

```bash
python -m pip install -r services/api/requirements.txt
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py discover-current
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py apply-target
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py run-transforms
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py run-domain-suites
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py run-scenarios
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py observe-api
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py reconcile
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py mutate
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL \
  python docs/sda/data-model/scripts/authoritative_harness.py check
python docs/agent/scripts/validate_skill_pack.py
```

Compatibility during migration may temporarily run old and new evidence in parallel, but the old shadow reports must be clearly labelled as legacy guardrails and not used to claim F02-F12 closure.

## 9. Bounded implementation sequence after SDA approval

No implementation begins until SDA assesses this checkpoint.

| Commit group | Scope | Tests moved | Reports retired/compatibility |
|---|---|---|---|
| 1 — Harness skeleton and topology | Add non-runtime harness script/control DDL; create `current_source`, `canonical_target`, `test_control`; apply accepted migrations and draft schema from empty. | Discovery/current schema and draft target schema execution. | Keep old Review 04-10 reports as compatibility guardrails. |
| 2 — Fixture authority | Add complete source records, expected target records, transform specs, API expected contracts and scenario expected outputs as reviewed sources. | Validate fixture completeness and no-bootstrap guards. | Mark old generated expected/observed files legacy where replaced. |
| 3 — F02 target transforms | Move grouped transforms into actual `canonical_target` tables with real types/FKs/idempotency. | F02 entity-level no-loss, FK, archive, exception, relationship and idempotency tests. | Retire generic transform staging after parity. |
| 4 — F04-F07 target domain suites | Execute record-role, temporal, geometry authority and lifecycle context through target constraints/functions. | F04-F07 positive/negative target-schema suites. | Retire `r10_*` shadow tables/policies after equivalent coverage passes. |
| 5 — F08 runtime API contracts | Add FastAPI TestClient/handler observations and exact field comparison. | Request/success/error/auth/roles/scopes/unexpected-field tests. | OpenAPI-only observer becomes static inventory support. |
| 6 — F10 target scenarios | Load seven complete scenarios into actual target schema and compare named outputs/absences. | Scenario canonical/effective/recorded/public/operator queries. | Retire `r10_scenario_entity`. |
| 7 — F12 authoritative mutations | Replace mutation runner with full checkout/fresh DB/source mutation path. | Named mutations against authoritative sources. | Retire older mutation scripts. |
| 8 — F09/F11 reconciliation | Generate convergence/ADR evidence from authoritative harness outputs. | Convergence units and ADR evidence matrix. | Retire label/report-based reconciliation. |
| 9 — Final cleanup and exact-head gates | Remove or archive legacy reports from acceptance path; update PR evidence and S16. | Full CI, clean regeneration, changed-path guard, exact-head proof. | Request SDA Review 12 only after green exact-head evidence. |

## 10. Compatibility while replacing old suites

To avoid temporarily losing safeguards:

- Existing Review 04-10 scripts remain runnable until their authoritative equivalents pass.
- New harness reports must state which old report each section replaces.
- During overlap, failures in either old or new guardrails block closeout unless explicitly classified as legacy false-positive by SDA-approved transition note.
- Final cleanup must remove old shadow reports from acceptance evidence and leave only historical references.
- The PR body must distinguish: legacy guardrail, authoritative harness evidence, and SDA-accepted evidence.

## 11. Open architecture decisions and RFIs

| RFI | Decision required | Why it matters |
|---|---|---|
| R11-RFI-001 | Whether actor/service/institution/membership/permission/scope/authority assertion are canonical NLI entities or typed references to an Identity and Trust domain. | Determines F06 target schema design and whether geometry promotion FKs point to owned tables or external reference contracts. |
| R11-RFI-002 | Reviewed lifecycle metadata source for initial/terminal states, re-entry, forbidden transitions, permission keys, scope, evidence, audit and public-effect prerequisites. | Required before F07 can be authoritative rather than inferred. |
| R11-RFI-003 | Which endpoints require full FastAPI HTTP TestClient versus deterministic handler/service fixtures. | Required to bound F08 runtime execution without adding unrelated infrastructure. |
| R11-RFI-004 | Future CI command naming and whether `authoritative_harness.py` should replace or wrap `review04_design_pipeline.py`. | Required for stable exact-head evidence and generated artifact policy. |
| R11-RFI-005 | Which expected target/scenario/API fixtures require SDA or institutional sign-off before being considered independent expected truth. | Required to prevent the harness from becoming another self-authored expected source. |
| R11-RFI-006 | Publication/public-code/certificate/signage authority remains outside this checkpoint unless SDA explicitly authorizes controlled simulation. | Prevents F10/F24-style public projection tests from implying publication approval. |

## 12. Scope and prohibited-path result for this checkpoint

This checkpoint is expected to touch only:

- `docs/sda/reviews/NLI-WO-002-review-11.md`
- `docs/agent/tasks/NLI-WO-002-review-11-task-context-pack.md`
- `docs/agent/tasks/NLI-WO-002-review-11-finding-resolution-matrix.md`
- `docs/sda/data-model/authoritative-assurance-harness.md`

Prohibited for this checkpoint:

- `services/api/**`
- `apps/**`
- `frontend/**`
- `infra/migrations/**`
- `infra/scripts/migrate.py`
- `infra/docker/**`
- `data/**`
- `.env*`
- PR #8 runtime fix paths

## 13. Checkpoint exit criteria

This checkpoint is complete only when:

- Review 11 is read and preserved.
- The task context pack exists.
- The finding-resolution matrix exists.
- This authoritative harness design exists.
- The repository skill pack validates.
- Changed-path guard shows only allowed docs paths.
- The branch is pushed and local/remote heads match.
- No SDA Review 12 request is made.

Next instruction required from SDA: **YES — before implementing the harness**.
