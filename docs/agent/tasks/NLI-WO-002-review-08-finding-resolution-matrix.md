# NLI-WO-002 Review 08 Finding Resolution Matrix

Date: 2026-07-14  
Review: `docs/sda/reviews/NLI-WO-002-review-08.md`  
Starting head: `f7ab590753b9205b824fab988682be84b93d6fc7`

## Resolution matrix

| Finding | Review 08 problem | Required agent response | Primary artifacts | Required proof | Commit | Status |
|---|---|---|---|---|---|---|
| F02 | Transformation report records assertion-ID presence, not source-to-target execution. | Build disposable source schema/rows, target schema, executable design transforms, exact value/FK/archive/exception/count/hash/relationship/idempotency checks, and real failure cases. | transformation fixture source, transformation execution report, pipeline/checker scripts | Real DB/source-to-target execution; failure tests for wrong value, translation, FK, archive, exception, duplicate output, relationship loss, hash mismatch. | TBD | OPEN |
| F08 | API projections still use generic reviewed payload envelopes and pending owners. | Independently author exact method/path/operation/handler/auth/role/request/success/error field contracts, classifications, exact projections, prerequisites, compatibility/deprecation behavior and executable contract tests. | reviewed API policy/projection registries, contract fixtures, projection assertion report | Executable contract tests per operation; credentials/session material excluded from business migration. | TBD | OPEN |
| F10 | Positive scenario proof reads generated fixture dictionaries, not persisted state. | Replace broad shells with scenario-specific builders/files and post-insert DB queries for exact histories, authority, geometry, lifecycle, releases and public/operator projections. | scenario source files/builders, scenario query assertion report | Persisted DB queries and exact expected outputs for all seven scenarios. | TBD | OPEN |
| F12 | Mutation probes test custom local predicates, not the real pipeline/checker. | Copy design sources to temp workspace, apply one mutation, run actual generator/checker, require correct gate/reason failure. | Review 08 mutation runner/report | Actual pipeline/checker failures for all required mutation classes. | TBD | OPEN |
| F04 | Cardinality architecture exists but full matrix not exercised. | Add positive/negative DB tests for every canonical record type, missing roles, excessive counts, invalid role/entity pairs, retirement, merge and multilingual name history. | target schema/catalog/report, cardinality assertion report | Executed DB positive and negative outcomes per record type. | TBD | OPEN |
| F05 | Temporal constraints exist but complete reconstruction is not proved. | Add temporal-strategy register for every authoritative mutable entity plus as-of registry/effective/public reconstruction and chain/cycle/overlap/backdated tests. | temporal strategy register, target report | Executed reconstruction queries and negative temporal cases. | TBD | OPEN |
| F06 | Geometry authority is JSON/text metadata, not a typed institutional relationship; negative matrix incomplete. | Define typed authority relationship connecting decision, actor/service identity, institution, permission, territorial/data scope, observation, evidence and quality assessment; execute complete mismatch matrix. | target model/schema/report, geometry authority assertions | Positive and negative authority DB outcomes. | TBD | OPEN |
| F07 | Allowed lifecycle edges execute, but graph completeness and denial semantics remain unproved. | Add graph validator for initial states, reachability, terminality, re-entry, orphan/conflicting edges and denied transitions for permission/scope/evidence/audit/public-effect per family. | lifecycle registry/report/checker | Executed graph validation and denial cases per lifecycle family. | TBD | OPEN |
| F09 | Convergence units depend on non-executed F02 assertions. | Rebuild/revalidate every convergence unit after F02 real transformed target rows exist. | reviewed convergence units and plan | Each unit references exact transform command/test, final target rows/FKs, exceptions, tolerances and gates. | TBD | OPEN |
| F11 | ADR evidence depends on unresolved guarantees. | Keep ADRs proposed; after F02/F04-F10/F12 pass, reconcile every acceptance statement to named executable assertions and visible RFIs/conditions. | ADR evidence matrix and ADR files | No aggregate-only evidence; each guarantee points to passing executable assertion. | TBD | OPEN |
| F13 | Runtime maintenance remains correctly isolated. | Preserve PR #8 separation and PR #7 scope guard. | changed-path proof, PR metadata | No prohibited runtime paths; PR #7 draft/open/unmerged. | TBD | PRESERVE |

## Finding order

1. F02
2. F08
3. F10
4. F12
5. F04/F05/F06/F07
6. F09/F11
7. closeout for Review 09

## Evidence language

Use `READY FOR SDA REVIEW` only after implementation-agent evidence is complete. Do not mark `PASS` or `ACCEPTED` unless SDA records acceptance.
