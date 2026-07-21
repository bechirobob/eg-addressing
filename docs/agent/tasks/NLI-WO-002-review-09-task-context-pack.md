# NLI-WO-002 Review 09 Task Context Pack

Date: 2026-07-14  
Branch: `nli/wo-002-canonical-location-model`  
Reviewed implementation/design head: `aa77f4b512b7389152239d3eaa27d4ab703c6ad2`  
Reviewer-owned Review 09 record/current PR head: `77ba5c68ba093a30d840d456ebef0c944a6c4f64`  
Outcome: `REWORK REQUIRED`

## Authority boundary

- PR #7 must remain open, draft, and unmerged.
- PR #8 remains separate.
- NLI-WO-002B remains unauthorized.
- No executable convergence, production deployment, official publication, public-code issuance, certificate/signage release, partner release, or real-data migration is authorized.
- PR #7 scope remains design/evidence only; do not copy PR #8 migration-runner maintenance work into PR #7.

## Active review source

- `docs/sda/reviews/NLI-WO-002-review-09.md`
- Review 09 explicitly rejects assertion-count evidence when expected and observed truth are produced by the same generator.
- The remediation goal is independent expected truth, domain-specific execution, observed-vs-expected comparison, full-pipeline mutation evidence, and exact-head Review 10 submission.

## Required repo-native skills invoked

Mandatory/cross-cutting:

- S01 authority, intake and scope
- S02 repository orientation and impact
- S03 acceptance planning and RFI
- S04 RFI and ADR management
- S05 authoritative current-state discovery
- S06 canonical data model and convergence
- S07 database/reference data
- S08 API, identity, security and privacy
- S09 GIS/evidence/publication
- S11 testing and semantic evidence
- S12 GitHub delivery/exact-head proof
- S13 SDA review remediation
- S14 maintenance isolation
- S16 self-audit and handoff

Domain/effect cards:

- S17 system architecture/domain boundaries
- S19 backend/domain logic
- S21 registry operations and case management
- S23 verification/quality/evidence review
- S24 publication/corrections/certificates/signage
- S26 import/export/worker/batch processing
- S28 infrastructure/environments/platform
- S29 performance/scalability/resilience
- S31 programme planning/roadmap/release management

## Affected modules / roles / environments

| Surface | Status |
|---|---|
| Data-model design artifacts | In scope |
| Disposable PostgreSQL/PostGIS validation | In scope |
| API contract evidence and controlled handler/response fixtures | In scope |
| Scenario source/expected-result evidence | In scope |
| Mutation harness and consistency checker | In scope |
| Convergence units and ADR evidence | In scope after lower findings pass |
| Runtime API/app/frontend implementation | Prohibited unless explicitly required for design-only test support; no runtime behavior change |
| Migration runner / PR #8 maintenance fix | Prohibited in PR #7 |
| Production/pilot data and secrets | Prohibited |

Roles/trust zones considered: SDA, implementation agent, registry operator, publication authority, geometry/field evidence authority, API consumer, public projection reader, institutional authority owner.

Environments: local disposable PostGIS validation, GitHub exact-head CI, PR #7 draft branch only.

## Review 09 remediation order

1. F02 — separate source fixtures, expected target fixtures, and transform implementation.
2. F08 — expected API contracts must be independently maintained and compared with observed handler/response fixtures.
3. F10 — independent minimal scenario source and expected-result files for all seven scenarios.
4. F12 — full-pipeline temp repository + disposable PostGIS mutation execution against authoritative sources.
5. F04–F07 — executed record-role, temporal, typed-authority and lifecycle graph tests.
6. F09/F11 — revalidate convergence and ADRs only after underlying evidence passes.
7. Review 10 closeout — S16, Review 09 resolution rows, PR body, push, exact-head CI, Review 10 request.

## Key Review 09 rejection themes

- F02 circular oracle: the same generic function calculated expected and actual outputs; synthetic FKs and duplicate rows were labelled idempotent.
- F08 circular contracts: observed OpenAPI/AST generated expected contracts and invented fallback fields.
- F10 self-referential scenarios: expected IDs/counts came from inserted fixture dictionaries, not independent expected results.
- F12 shallow mutation: generated reports were mutated, not authoritative source/generator/pipeline inputs.
- F04–F07 declared passes: integrity report contained prose/trigger-presence pass labels instead of executed matrix tests.
- F09/F11 inherited unresolved lower-level evidence.

## Initial implementation plan

### Lane F02

- Create reviewed source fixtures, reviewed expected target fixtures, and separate transform implementation artifacts.
- Ensure transform implementation cannot import/generate the expected fixture.
- Execute transforms into schema-compatible target tables with unique constraints.
- Create real target identities first, then crosswalks/FKs/relationships.
- Write governed archive and exception rows from transform behavior.
- Compare observed rows with independent expected target rows for exact values/types/translations/FKs/hashes/relationships/archive/exception/counts.
- Correct idempotency: second run creates zero additional rows and no unexpected row modifications.
- Add full-pipeline failure cases for wrong transform, wrong expected value, invalid translation, unresolved FK, missing identity/archive/exception, duplicate output, lost relationship and hash mismatch.

### Lane F08

- Maintain expected API contracts as reviewed source not written by the observed extractor.
- Use observed OpenAPI/AST/handler fixtures only as observed reality.
- Fail unresolved dynamic responses; no fallback `id`, `status`, copied path params or request fields.

### Lane F10

- Split all seven scenario sources and expected results into independent minimal files.
- Query disposable DB and compare exact presence and expected absence across state/projection/time axes.

### Lane F12

- Mutate authoritative sources/logic in temp repo workspaces.
- Create disposable PostGIS DB per run where needed.
- Run generator/pipeline/helpers/checker and require expected gate failure.

### Lane F04–F07

- Replace rollup declarations with executed tests and report only observed outcomes.

### Lane F09/F11 and closeout

- Revalidate only after lower evidence passes.
- Keep ADR-005..ADR-009 proposed and RFIs visible.
- Request Review 10 only after final exact-head CI proof.

## Verification checkpoints

- Local design pipeline must pass from source, not only checker.
- Helper scripts must regenerate deterministic artifacts.
- Mutations must fail for named expected reasons after full pipeline execution.
- `validate_skill_pack.py` must pass.
- `git diff --check` must pass.
- Prohibited runtime path guard must remain empty.
- PR #7 exact-head GitHub CI must be green before Review 10 request.
