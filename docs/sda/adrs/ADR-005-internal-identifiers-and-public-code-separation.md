# ADR-005 — Internal identifiers, public aliases and legacy crosswalk authority

## Status

Proposed for SDA Review 07. NLI-WO-002B remains unauthorized until SDA acceptance and a separate implementation work order.

## Decision owner

System Design Authority; implementation agent may only encode and test the selected design boundary.

## Context

Review 04 rejected generated/template ADR rationale. This ADR is bound to explicit model identifiers and disposable-schema semantic tests.

## Model and constraint identifiers

location_record.location_record_id, public_code_alias.public_code_alias_id, legacy_crosswalk.legacy_id, source_payload_archive.payload_uri

## Decision

Canonical identities use implementation-owned text identifiers; current operational IDs and public codes are never canonical identity. Legacy IDs are preserved only through `legacy_crosswalk`, and public codes live in `public_code_alias` with release-state prerequisites.

## Alternatives considered

| Alternative | Benefit | Cost / rejection reason |
|---|---|---|
| Reuse current operational IDs | Low migration effort | Rejected: conflates operational table keys with national canonical identity and blocks no-loss crosswalk proof. |
| Make public code the primary key | Human-readable joins | Rejected: public codes are mutable/releasable aliases, not permanent identity. |
| ULID-compatible text IDs plus crosswalk | Offline-friendly generation, stable joins, reversible migration | Selected with collision checks and crosswalk uniqueness. |

## Implementation constraints

`legacy_crosswalk` unique source keys; `public_code_alias` one active public alias per location; release item required before public projection.

## Security and privacy implications

- Restricted raw values remain in governed archives or evidence objects; hashes alone are not treated as archives.
- Public release requires publication authority and release-item prerequisites.
- Operator-only lineage, crosswalk and subject-link data is not projected publicly by default.

## Performance and operational trade-offs

- Write paths pay trigger/exclusion/index cost to prevent national-registry drift.
- Current reads use partial indexes and release snapshots.
- Bulk migration must batch by reviewed transformation unit and stop on exception thresholds.

## Migration consequences

- NLI-WO-002B remains unauthorized; this ADR defines acceptance gates for later executable work.
- Migration rows must use reviewed transformation decisions, crosswalk keys and source archives.
- Failed semantic checks create owned exceptions, not silent coercions.

## Failure modes

Duplicate crosswalk creates double canonical records; missing alias release leaks unapproved public code; ID collision aborts batch.

## Consequences

- The selected model is stricter than the current pilot schema and requires a controlled expand-migrate-contract phase.
- The stricter model prevents silent orphaning, duplicate authority, public leakage and impossible lifecycle states.

## Acceptance checks

CI compares crosswalk fields to pg_catalog inventory; semantic checks reject pseudo-assertions, invalid controlled maps, stale route contracts, alias-chain gaps and missing promotion authority; PR evidence records exact reviewed transformation rows.

## Evidence-linked conditions

- Condition: decision acceptance is limited to assertions executed by `review04_design_pipeline.py` and `design_consistency_check.py`.
- Evidence: target schema validation report, lifecycle binding registry, transformation registry, policy contracts and scenario validation report.
- Boundary: NLI-WO-002B remains unauthorized until SDA explicitly accepts the model.

## Unresolved RFIs

- No executable production migration authority is granted by this ADR.
- Institutional owner approval, operational rollout windows and production data retention rules remain future SDA/institution decisions.

## Acceptance tests

- CI must fail if the ADR claims a constraint absent from the model policy registry or target validation report.
- CI must fail if Review 06 resolution rows are updated outside the Review 06 resolution log.


## Review 07 assertion reconciliation

- Evidence source: `docs/sda/data-model/design-consistency-report.md` (`Generated checks: 41`, `Errors: 0`) and `docs/sda/data-model/target-schema-validation-report.md`.
- This ADR remains proposed until SDA Review 07 accepts the named assertions; it does not authorize NLI-WO-002B or production migration.
- Any claim about runtime behavior is out of scope for PR #7; the migration-ledger race fix is isolated in maintenance PR #8.
