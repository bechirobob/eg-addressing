# SDA Finding Resolution Matrix — NLI-WO-002 Review 06

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**SDA review:** `docs/sda/reviews/NLI-WO-002-review-06.md`  
**Reviewed implementation SHA:** `46371d41c64fb21c06e99fd120b19e55de11d571`  
**Current branch/PR:** `nli/wo-002-canonical-location-model`, PR #7, draft/open/unmerged  
**Prepared by:** implementation agent checkpoint after skill-pack merge from `origin/main` @ `0a60bbdadd81afab818bfdff3d3962f6b50b47eb`

> Complete one row per open finding. Do not edit reviewer-owned finding text or disposition.

## Resolution matrix

| Finding | Reviewer-required resolution | Root cause | Specific correction | Files/domains | Positive proof | Negative/regression proof | Fixing commit | RFI/risk | Agent status |
|---|---|---|---|---|---|---|---|---|---|
| F02 | Correct controlled maps; define exact source-to-target crosswalk joins; replace pseudo assertions with executable validation; execute grouped transforms. | Reviewed registry rows had row coverage but still used invalid controlled maps, generic crosswalk targets and pseudo-`ASSERT` strings. | Correct maps against observed values and target vocabularies; add explicit source entity/key, target entity/key, crosswalk lookup and target FK output; require executable SELECT/value/relationship assertions. | `docs/sda/data-model/transformation-registry-reviewed.json`, mapping docs, checker, convergence plan | Registry validates all 237 current fields and examples match target vocabularies. | Checker rejects pseudo-ASSERT, invalid controlled map, missing reference-crosswalk metadata and unknown current fields. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | Current values must remain source-backed; no hash-only no-loss claim. | READY FOR SDA REVIEW |
| F04 | Replace `standard-address`; enforce complete matrix for actual record types; test required/invalid/excess roles. | Role/cardinality matrix used a placeholder not present in the canonical `record_type` vocabulary and required-role enforcement was incomplete. | Key matrix by `address`, `building`, `entrance`, `landmark`, `non-building-object`, `service-location`, `unit`; enforce min/max/allowed subject types and required roles. | target model, draft SQL, fixtures, checker | Positive target-schema fixture coverage for all canonical record types. | Negative fixtures/checker reject `standard-address`, missing role, invalid subject/entity pair and excessive primary subject count. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | If SDA changes record-type vocabulary later, matrix must be updated first. | READY FOR SDA REVIEW |
| F05 | Apply no-self, reciprocal, same-owner and acyclic rules to aliases/geometry/every supersession relationship; catalogue temporal strategy. | Temporal checks improved for location versions but were incomplete for alias and geometry chains and broader mutable authoritative entities. | Add chain invariants and temporal catalogue; add alias/geometry no-self, reciprocal/same-owner and cycle checks where design SQL can express them. | target model, draft SQL, lifecycle/temporal docs, fixtures | Positive corrected/superseded and historical release fixtures validate retained old/new versions. | Negative fixtures reject self-cycle, reciprocal mismatch, cross-owner/cross-subject supersession and interval violations. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | Production enforcement still requires NLI-WO-002B. | READY FOR SDA REVIEW |
| F06 | Bind geometry promotion to authorized decision/evidence/authority/scope; enforce same-subject/role supersession; execute negative tests. | Geometry versions could become accepted with technical validity but without explicit authority decision/evidence chain. | Add `promotion_decision_event_id`, `promotion_evidence_object_id`, `promotion_authority_scope`; enforce compatible observation, quality, subject/role and supersession. | target model, draft SQL, geometry docs, scenario fixtures | Positive geometry promotion scenario with decision/evidence/scope passes. | Negative fixtures reject wrong subject type, wrong role/type, invalid geometry/SRID/3D, duplicate current, missing promotion evidence/decision and cross-subject supersession. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | Publication/official GIS authority remains unresolved; no official boundary claim. | READY FOR SDA REVIEW |
| F07 | Use executable transition-policy table/function for every bound lifecycle; test reachability, terminality, re-entry, orphan states and metadata. | Lifecycle metadata was richer but executable enforcement/checking covered only a subset and could not prove complete graph behavior. | Load lifecycle graphs into transition policy metadata; validate edge metadata, field bindings, reachability/terminality and transition positives/negatives. | lifecycle registry, target SQL, checker | Positive lifecycle transitions for bound families pass with permission/scope/evidence/audit metadata. | Negative transition tests reject forbidden edges and checker rejects missing metadata/unbound stateful fields. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | Runtime transition enforcement remains future implementation work. | READY FOR SDA REVIEW |
| F08 | Verify every expected route row against exact method/path/operation/handler/source/auth/roles; build field-complete dynamic response contracts. | Expected route/policy rows were manually/structurally present but contained wrong method/handler links and generic/empty dynamic contracts. | Maintain reviewed expected route policy keyed by method/path/operation/handler; compare to observed OpenAPI/AST; enumerate request/success/error fields and target projections/classifications. | OpenAPI inventory, route policy registries, projection contracts, API projection map, checker | All 105 OpenAPI operations have contract rows and policy comparison passes. | Checker rejects wrong method/handler/operation ID/source span/roles, empty 2xx dynamic contracts and generic target projections. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | No runtime API contract change authorized in PR #7. | READY FOR SDA REVIEW |
| F09 | Rebuild migration units after F02 closes; include executable transforms, dependency order, FK outputs, exception schema, cutover/abort gates, recovery. | Migration units inherited defective transformations and generic validation/control text. | Derive convergence units only from accepted transformation groups with exact source/target fields, FK outputs, dependency order and executable validation. | convergence plan, convergence units JSON, transformation registry | Convergence units align to reviewed transformation groups and dependency order. | Checker rejects pseudo-validation and generic reference-crosswalk behavior. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | Scale assumptions remain unapproved planning inputs. | READY FOR SDA REVIEW |
| F10 | Replace generic scenario shells with scenario-specific datasets and expected public/operator results. | Seven scenarios inserted many generic one-row-per-entity shells and did not prove national scenario-specific histories/projections. | Add scenario-specific builders/fixtures for urban, rural/landmark, multi-unit, no-formal-road, corrected/superseded, disputed geometry, administrative-boundary change; define expected operator/public outcomes. | representative records, fixtures JSON, target SQL validation, checker | Seven positive scenarios insert 324 target rows with scenario-specific relationships/history. | Seven negative semantic cases execute real SQL/policy failures; checker rejects simulated negative strings and scenario-output gaps. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | Expected outcomes must remain independent from observed generator logic. | READY FOR SDA REVIEW |
| F11 | Reconcile ADRs with named passing assertions; remove stale status/unsupported claims; keep open RFIs explicit. | ADRs were no longer generated but retained shared stale Review 05 language and claims not tied to passing assertions. | Update ADR-005 through ADR-009 individually as proposed Review 07 source docs; add assertion reconciliation and boundary notes; remove stale Review 05 claims. | ADR-005..ADR-009, checker | ADRs link to named design/checker/target validation evidence and remain proposed pending SDA. | Stale-status/unsupported-claim scan and checker guard prevent Review 05/unsupported acceptance drift. | `1cf7d555a08de750c580b87de14bc2020dc7a052` | SDA must accept or condition ADRs; implementation agent cannot accept them. | READY FOR SDA REVIEW |
| F12 | Extend semantic CI to detect every Review 06 defect class and avoid unchecked PASS claims. | CI checked counts/presence and allowed invalid semantics to pass. | Add named checks for controlled maps, pseudo assertions, record-type matrix, alias cycles, promotion authority, lifecycle graph behavior, route/policy contracts, dynamic responses, scenarios and catalog parity. | `design_consistency_check.py`, pipeline, reports, CI job | Local and exact-head CI report `Generated checks: 41`, `Errors: 0`, `Warnings: 0`. | Checker rejects the specific defect classes listed in Review 06 and fails deterministic diff on generated evidence. | `1cf7d555a08de750c580b87de14bc2020dc7a052`; generated evidence fix `2789194a1949ceccdd2c34210461f46ddf65dbb7` | Counts still must not be reported as semantic proof without named assertions. | READY FOR SDA REVIEW |
| F13 | Move migration-ledger race fix into separate maintenance PR under NLI-WO-001 controls; restore PR #7 design boundary. | Exact-head CI exposed a valid runtime migration-ledger race during design remediation, and the fix was initially included in PR #7. | Create branch from `main`, apply only `infra/scripts/migrate.py` advisory-lock/ledger fix and regression evidence; open PR #8; restore `infra/scripts/migrate.py` in PR #7. | PR #8, `infra/scripts/migrate.py` only in maintenance branch; PR #7 changed-path evidence | PR #8 exists open/draft with head `5650cd219156d23f10836ab7041b34693e9250b0`; PR #7 diff excludes `infra/scripts/migrate.py`. | Changed-path guard fails if PR #7 includes runtime/migration/app/data/env paths. | Maintenance PR #8 `5650cd219156d23f10836ab7041b34693e9250b0`; PR #7 restore/evidence heads through `2789194a1949ceccdd2c34210461f46ddf65dbb7` | PR #8 is a separate maintenance dependency; do not duplicate fix in PR #7. | READY FOR SDA REVIEW |

## Systemic causes

| Systemic cause | Findings affected | Control/skill change | Regression guard |
|---|---|---|---|
| Observed and expected evidence were too close or generated from the same logic | F02, F08, F10, F12 | S03/S05/S08/S11 require independent expected registries/fixtures | Checker rejects missing reviewed source metadata and mismatched route/contracts |
| Presence/count checks were treated as semantic proof | F02, F04-F12 | S11 requires claim-to-assertion matrix and executable positive/negative cases | `design_consistency_check.py` names defect-class checks; target SQL executes in disposable PostGIS |
| Design-only scope boundary was not protected when CI exposed runtime defect | F13 | S14 maintenance isolation now mandatory | Changed-path guard plus separate PR #8 |
| Generated artifacts were hand-edited instead of source generators | F12/evidence closeout | S11/S12 require deterministic regeneration | CI fails on regenerated diff; generator now emits controlled evidence |
| ADRs used shared boilerplate instead of decision-specific assertion links | F11 | S13/S16 stale-claim scan | ADR assertion reconciliation and stale-reference search |

## Accepted controls to preserve

- PR #7 remains draft, open, unmerged.
- NLI-WO-002B remains unauthorized.
- No executable migrations or runtime behavior changes in PR #7.
- NLI-WO-001 migration-only lifecycle controls remain preserved.
- Application startup must not create/alter schema or load fixtures in controlled environments.
- `registry-ready` remains distinct from official publication.
- PostgreSQL/PostGIS remains authoritative system of record.
- Public code grammar and official publication authority remain unresolved institutional decisions.
- Review 06 reviewer-owned sections remain immutable.

## Review-record protection

- Review outcome section changed: `NO`
- Finding observation/required-resolution text changed: `NO`
- Reviewer disposition table changed: `NO`
- Only designated resolution-log section changed: `YES` for prior remediation commit; this checkpoint must not change it unless new evidence requires a bounded update.
- Section-bounded updater test: required before any future Review 06 resolution-log modification.

## Exact-head remediation evidence

- Implementation SHA before skill-pack merge: `2789194a1949ceccdd2c34210461f46ddf65dbb7`
- Local branch SHA after merging skills `main`: `257318899a191c0fbca6953f97b1a6762b3086c3`
- Workflow runs for pre-merge Review 07 request head:
  - API CI `29337836769`: success
  - `migration-lifecycle` job `87101505912`: success
  - `api-tests` job `87101505942`: success
  - `api-image-runtime` job `87101505979`: success
  - `sda-design-model` job `87101506235`: success
  - Frontend CI `29337836804`: success
  - `frontend` job `87101506040`: success
- Changed-path proof after merge: no prohibited runtime path shown by `git diff --name-status origin/main...HEAD` beyond the already-scoped design/workflow evidence set; must be rechecked after checkpoint commit.
- Deterministic regeneration: local pipeline/checker must be rerun after the skill-pack merge before any new Review 07 request.
- Open findings after agent remediation: agent marks F02/F04-F13 `READY FOR SDA REVIEW`; SDA outcome remains `REWORK REQUIRED` until Review 07.

## Agent declaration

- [x] Every finding has a finding-specific correction and evidence.
- [x] No generic evidence list is accepted as the only proof; this matrix lists finding-specific root cause and assertion plan.
- [x] Agent status is `READY FOR SDA REVIEW`, not `SDA RESOLVED`.
- [x] Prior accepted controls are listed for preservation.
- [x] Out-of-scope defect was isolated under S14 as PR #8.
- [ ] Exact-head CI must complete again after the skill-pack merge/checkpoint commit before any renewed review request.
