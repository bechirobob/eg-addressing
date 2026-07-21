# NLI-WO-002 Review 08 Task Context Pack

Date: 2026-07-14  
Branch: `nli/wo-002-canonical-location-model`  
Review-record/current PR head: `f7ab590753b9205b824fab988682be84b93d6fc7`  
Reviewed implementation/design head: `c94ececed0d7ac15281624b4825082bc547185cf`  
Outcome to remediate: `REWORK REQUIRED`

## Authority header

| Field | Value |
|---|---|
| Programme | EG National Location Infrastructure / NLI design-authority work |
| Active work order | `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md` |
| Active review | `docs/sda/reviews/NLI-WO-002-review-08.md` |
| PR | #7 — draft/open/unmerged |
| Maintenance dependency | PR #8 remains separate; do not duplicate its migration-runner fix |
| NLI-WO-002B | Unauthorized |
| Change class | Design/evidence remediation only; no runtime implementation or executable migration |

## Required skills invoked

Repository-native skills invoked for this remediation lane:

- S01 authority intake and scope
- S02 repository orientation and impact
- S03 acceptance planning and RFI
- S05 authoritative current-state discovery
- S06 canonical data model and convergence
- S08 API, identity, security and privacy
- S09 GIS, evidence and publication
- S11 testing and semantic evidence
- S12 GitHub delivery and exact-head proof
- S13 SDA review remediation
- S14 maintenance fix isolation
- S16 self-audit and context handoff
- S17 system architecture and domain boundaries
- S19 backend services and domain logic
- S20 citizen portal and public services
- S21 registry operations and case management
- S22 field operations, mobile and offline sync
- S23 verification, quality and evidence review
- S24 publication, corrections, certificates and signage
- S25 agency integrations, notifications and interoperability
- S26 import/export, worker and batch processing
- S27 reporting, analytics and national data products
- S31 programme planning, roadmap and release management

Hermes execution skills also loaded: delivery discipline, minimal-change engineering, systematic debugging, evidence collection, reality checking, SDA remediation references, generated-artifact closeout and generated evidence metric readback.

## In scope

- Replace F02 metadata/assertion-ID presence with real disposable source-to-target transformation execution.
- Replace F08 generic API envelopes with exact independently reviewed request/success/error field contracts and executable contract tests.
- Replace F10 in-memory fixture assertions with post-insert database queries and exact public/operator/historical outputs for the seven required scenarios.
- Replace F12 local predicate mutation probes with temporary-workspace real pipeline/checker mutation executions.
- Complete F04/F05/F06/F07 evidence gaps after the blocker layers are corrected.
- Revalidate F09 convergence units only after executable F02 transformation results exist.
- Keep ADRs proposed and reconcile F11 only after defining guarantees point to named executable assertions.
- Update S16, Review 08 resolution rows, controlled evidence and PR body at final head.

## Supporting evidence files likely touched

- `docs/sda/data-model/scripts/review04_design_pipeline.py`
- `docs/sda/data-model/scripts/design_consistency_check.py`
- `docs/sda/data-model/scripts/review07_semantic_mutation_tests.py` or replacement Review 08 mutation runner
- `docs/sda/data-model/transformation-fixtures-reviewed.json`
- generated transformation/source-to-target execution reports
- `docs/sda/data-model/openapi-reviewed-route-policies.json`
- `docs/sda/data-model/openapi-reviewed-projection-contracts.json`
- generated API projection assertion artifacts
- scenario fixture source files under `docs/sda/data-model/representative-records/`
- target schema/catalog/report artifacts
- convergence-unit and ADR evidence artifacts after lower layers pass
- Review 08 resolution log and S16 self-audit files

## Prohibited

- Do not merge PR #7.
- Do not implement or authorize NLI-WO-002B.
- Do not duplicate PR #8's migration-runner maintenance fix.
- Do not change runtime application/API behavior under `services/api/**`.
- Do not add executable migrations under `infra/migrations/**`.
- Do not change app routes/components under `apps/**`.
- Do not change Docker runtime configuration, production/pilot data, `.env*`, or secret-bearing paths.

## Readiness boundary

Successful agent remediation may claim `READY FOR SDA REVIEW 09` only after exact-head local and GitHub CI evidence is green and PR #7 remains draft/open/unmerged. It must not claim SDA acceptance, implementation authorization, production readiness, public-code issuance, official publication or real migration readiness.

## Review 08 root-cause summary

Review 08 rejects the current pack because several high-count evidence reports still prove metadata presence rather than behavior:

- F02 transformation report marks expected assertion IDs as passed without executing transformations or target row comparison.
- F08 uses generic `response.body.reviewed_payload` envelopes for dynamic successful API responses.
- F10 positive scenario proof is derived from in-memory fixture dictionaries instead of persisted target database state and exact outputs.
- F12 mutation tests mutate local objects and check custom predicates instead of running the real generator/checker against mutated sources.
- F04/F05/F06/F07 have partial executable controls but incomplete positive/negative matrices.
- F09/F11 inherit unresolved guarantees from F02/F04-F10/F12.

## Execution order

1. F02 blocker: real disposable transformation execution and failure tests.
2. F08 blocker: exact API field contracts and executable contract tests.
3. F10 blocker: persisted scenario query assertions and exact projections.
4. F12 blocker: actual pipeline/checker mutation executions.
5. F04/F05/F06/F07 completion.
6. F09/F11 revalidation.
7. S16/Review 08/evidence/PR/CI closeout and Review 09 request.

## Stop conditions / RFIs

- Stop if a required institutional owner/authority is missing and cannot be modeled as an explicit unresolved RFI.
- Stop if exact response field ownership cannot be derived from handlers/tests and would require inventing API behavior.
- Stop if F02 would require changing runtime code or migrations rather than docs-only executable design evidence.
- Stop if local/remote PR state diverges or PR #7 stops being draft/open/unmerged.
