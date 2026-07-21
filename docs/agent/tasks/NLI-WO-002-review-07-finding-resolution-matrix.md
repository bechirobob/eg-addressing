# SDA Finding Resolution Matrix — NLI-WO-002 Review 07

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**SDA review:** `docs/sda/reviews/NLI-WO-002-review-07.md`  
**Reviewed implementation/checkpoint SHA:** `af7f296f5672bbb2b060b912607b965ac90d8fae`  
**Reviewer-owned Review 07 commit/head:** `ec3e88906cee173bac0f57c710398fe866e1e094`  
**Current synchronized local head before this checkpoint:** `c34b924017ce7571ba8e58b33062336dbc0c9fe4`  
**Current branch/PR:** `nli/wo-002-canonical-location-model`, PR #7 draft/open/unmerged  
**Prepared by:** Implementation Agent

> Complete one row per open finding. Do not edit reviewer-owned finding text, required resolution, disposition, or outcome. Agent status may become `READY FOR SDA REVIEW` only after finding-specific evidence exists.

## Resolution matrix

| Finding | Reviewer-required resolution | Root cause | Specific correction | Files/domains | Positive proof | Negative/regression proof | Fixing commit | RFI/risk | Agent status |
|---|---|---|---|---|---|---|---|---|---|
| F02 | Executable source-to-target transformation fixtures in disposable PostGIS; assert target values, row identity, reference crosswalk joins, archive/evidence references, exceptions, and no-loss reconciliation; prove final canonical FK targets. | Current mapping rows are exact by count but many transforms/no-loss statements are generic text or generated summaries rather than executed value/relationship reconciliation. | Add representative source fixture rows, transformation execution layer, reviewed transform expectations, FK/crosswalk/archive/evidence assertions, and fail-closed no-loss checks. | `transformation-registry*.json/md`, `current-to-target-mapping*`, pipeline/checker, reports | Representative current rows transform to exact target rows/fields/FKs and reconcile values/counts/relationships. | Unknown field, pseudo assertion, missing FK target, archive omission, relationship loss, and default classification fail. | Pending | Open RFIs remain authority blockers; do not publicize/implement beyond design. | PLANNED |
| F04 | Execute positive/negative datasets for every canonical record type: required/optional roles, min/max, subject types, missing role, excessive count, invalid pairing, retirement/merge effects, multilingual name history; complete multi-unit scenario or revise ADR-007. | Cardinality matrix exists but proof is partial and scenario-generated rather than exhaustive by canonical record type and lifecycle behavior. | Add record-type-specific positive/negative fixtures and scenario assertions for roles, names, retirement/merge, and multi-unit canonical units/projections. | `target-model.json`, fixtures, scenario docs, pipeline/checker, ADR-007 if needed | Every canonical record type has valid composition and expected projection assertions. | Missing role, excessive count, invalid subject pairing, retired/merged subject misuse, duplicate current official name fail. | Pending | ADR-007 remains proposed until proof passes. | PLANNED |
| F05 | Publish complete temporal-strategy register for every mutable authoritative entity; add chain rules to every correction/supersession relationship; execute historical reconstruction and negative cycle/mismatch/cross-owner/overlap/backdated/containment tests. | Some chains/triggers exist, but temporal authority is not classified and enforced consistently across all mutable authoritative entities and relationships. | Add temporal-strategy register, relationship-chain metadata, SQL/fixture assertions, and history reconstruction tests across entity families. | `lifecycle-state-machines.md`, `target-model.json`, SQL, pipeline/checker, reports | Historical reconstruction for versions, aliases, names, admin units, geometry, releases passes. | Two-node cycle, multi-node cycle, reciprocal mismatch, cross-owner supersession, overlap, invalid backdated correction, interval containment violation fail. | Pending | Official admin/publication authority remains RFI-gated. | PLANNED |
| F06 | Model and validate actor, institution, permission, territorial/data scope, decision type, source observation, evidence, and quality-assessment relationships; require role-matrix permission and subject scope; execute negative authority tests. | Geometry promotion stores authority-looking metadata but does not prove a permission-bearing institutional decision linked to evidence/observation/quality/scope. | Add promotion-authority model links and assertions tying actor/institution/permission/scope/decision/evidence/quality/observation to subject/role promotion. | geometry provenance docs, SQL, fixtures, pipeline/checker | Authorized actor/institution/scope can promote matching accepted observation with related evidence/quality. | wrong decision type, unauthorized actor, wrong institution/scope, unrelated evidence, unrelated assessment, cross-subject/role successor, and cycle fail. | Pending | Boundary/official authority RFIs remain open. | PLANNED |
| F07 | Populate disposable transition-policy table from independently reviewed lifecycle source; execute positive/negative transitions for every lifecycle family; validate graph reachability, terminal/re-entry, duplicates, bindings, permission/scope/evidence/audit/public effects. | Lifecycle table is created but not demonstrably populated; only invalid transition rejection is executed and would also pass on an empty table. | Populate transition policy from reviewed lifecycle registry; add graph completeness and transition execution assertions. | `lifecycle-transitions.json`, `lifecycle-state-machines.md`, SQL, pipeline/checker | Every lifecycle family has valid positive transitions with permission/evidence/audit/public-effect metadata. | Empty policy, orphan state, duplicate/conflicting edge, invalid transition, terminal re-entry, missing field binding fail. | Pending | No runtime workflow authority. | PLANNED |
| F08 | Maintain human-reviewed expected policy registry independent of AST generation; verify every row; define executable response-shape fixtures/Pydantic models for dynamic 2xx responses; map every request/success/error field to target/projection/classification/release/compatibility/adapter/test. | Expected policy/projection registries are still derived from observed AST or generic defaults; dynamic responses and field classifications are incomplete. | Split observed inventory from reviewed expectation source, add owner/status/sign-off fields, explicit dynamic response field fixtures, field-level classification/projection assertions. | OpenAPI inventories, route policies, projection contracts, pipeline/checker | Observed method/path/handler/roles match independent reviewed expectation and all fields map to exact projection/classification. | Generated-from-AST expected registry, unreviewed row, generic dynamic object, missing target projection/classification, keyword-only classification fail. | Pending | No API runtime changes. | PLANNED |
| F09 | After F02 closes, hand-review named migration units with executable transformation commands/tests, dependencies, crosswalk behavior, FK outputs, application-version matrix, ownership, exception SLA, idempotency, conflict precedence, validation SQL/tolerance, recovery, monitoring, cutover/abort, retirement proof. | Convergence units are generated summaries and inherit unaccepted transform/no-loss evidence. | Rebuild convergence units from executable F02 transform proof and hand-reviewed unit metadata; keep scale figures unapproved. | `schema-convergence-plan.md`, `schema-convergence-units.json`, reports | Units reference executable transform checks, dependencies, compatibility matrix, validation SQL, recovery/cutover gates. | Generic inherited controls, missing FK output, missing exception SLA, unapproved scale/readiness claim fail. | Pending | Depends on F02 closure; scale/owners remain unapproved where applicable. | PLANNED |
| F10 | Rewrite negative harness so invalid success fails outside exception handler; catch only expected DB/policy exceptions; assert expected class/message and unchanged state. Author seven independent scenario datasets/builders with scenario-specific assertions for cardinality, history, geometry, evidence, authority, releases, and public/operator projections. | `expect_sql_failure` catches its own `AssertionError`, so successful invalid actions are reported as rejected; positive scenarios are broad generated shells. | Fix harness control flow first; add regression proving false-pass bug; add expected exception/state assertions and scenario-specific builders/assertions. | `review04_design_pipeline.py`, fixtures, scenario docs, validation report, checker | Seven positive scenarios pass with expected relevant entities/projections and scenario-specific assertions. | A deliberately successful invalid action fails the suite; expected exception mismatch and state mutation fail. | Pending | First required follow-up sequence item. | PLANNED |
| F11 | Keep ADRs proposed; reconcile every decision constraint and acceptance statement to named passing assertions after F02/F04–F10/F12 close; record unresolved RFIs/unimplemented safeguards; remove aggregate PASS counts as primary decision evidence. | ADR source control improved but claims are ahead of executable evidence and use aggregate PASS counts. | Add ADR evidence matrix mapping constraints to named assertions and keep proposed/conditional status truthful until all defining evidence closes. | ADR-005–009, ADR/RFI coverage, checker/report | Each ADR claim references named assertion/evidence or explicit RFI/condition. | ADR accepted ahead of evidence, unresolved RFI hidden, aggregate-only PASS evidence fail. | Pending | Architecture acceptance blocked by open findings/RFIs. | PLANNED |
| F12 | Add named executable assertions for all remaining findings; generate check count from executed named assertions; report limitations; fail CI whenever an asserted safeguard is not exercised. | Semantic CI is deterministic but permits false positives and aggregate count claims without complete exercised safeguards. | Convert semantic checker to named assertion registry with limitations; fail on unexercised assertions and stale/generic evidence. | `design_consistency_check.py`, reports, CI evidence | Named assertions for F02/F04–F11 execute and report exact pass/fail/limitations. | Missing assertion, unexercised safeguard, stale generated count, false-pass negative harness fail CI. | Pending | Must be exact-head green before Review 08 request. | PLANNED |

## Systemic causes

| Systemic cause | Findings affected | Control/skill change | Regression guard |
|---|---|---|---|
| Self-referential/generated evidence compared to generated output | F02, F08, F09, F11, F12 | Maintain reviewed expected registries separate from observed generators | Checker fails when expected source declares/generated provenance or lacks review status/owner |
| Negative test harness catches its own failure | F10, F12 | Exception handling must catch only expected DB/policy exceptions and assert unchanged state | Deliberately successful invalid action must fail the suite |
| Aggregate counts used as semantic proof | F04, F07, F10, F11, F12 | Named assertions tied to specific claims/findings | Report count generated from assertion registry; unexercised assertion fails |
| Design claims exceed institutional authority | F05, F06, F09, F11 | RFIs remain explicit and ADRs stay proposed/conditional | Checker/report fails on public/implementation/readiness overclaim |
| Broad scenario shells instead of scenario-specific expected outcomes | F04, F10, F12 | Independent scenario builders/assertions per national scenario | Each scenario must assert only relevant entities and exact projections/history |

## Accepted controls to preserve

- PR #7 remains design-only, draft, unmerged, and free of runtime/API/frontend/backend/migration/container changes.
- PR #8 remains the separate maintenance path for migration-ledger race fix; no duplication in PR #7.
- Current PostGIS disposable design execution remains deterministic.
- `standard-address` remains removed from record cardinality as a non-vocabulary placeholder.
- Internal identifiers, public aliases, legacy/crosswalk references, and publication releases remain separated.
- Registry-ready remains distinct from published/public/signage/certificate release.
- Open RFIs remain visible and block reserved decisions.
- Review records remain protected except explicitly permitted resolution-log updates.

## Review-record protection

- Review outcome section changed: `NO`
- Finding observation/required-resolution text changed: `NO`
- Reviewer disposition table changed: `NO`
- Only designated resolution-log section changed: `NO` at checkpoint creation; may become `YES` after evidence exists.
- Section-bounded updater test: pending before resolution-log update.

## Exact-head remediation evidence

- Implementation SHA: pending after remediation commits.
- Workflow runs: pending.
- Job IDs: pending.
- Changed-path proof: current synchronized checkpoint shows no prohibited runtime paths.
- Deterministic regeneration: pending after remediation.
- Open findings after agent remediation: F02/F04/F05/F06/F07/F08/F09/F10/F11/F12 planned; F13 external maintenance condition remains.

## Agent declaration

- [x] Every finding has a finding-specific planned correction and evidence target.
- [x] No generic evidence list was copied across all findings.
- [x] Agent status is `PLANNED`, not `SDA RESOLVED`.
- [x] Prior accepted controls are listed for preservation.
- [x] Out-of-scope defects are isolated under S14.
- [ ] Exact-head CI completed before the Review 08 request.
