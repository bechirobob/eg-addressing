# ADR-007 — Canonical record, object cardinality and subject registry

## Status

Proposed for SDA Review 04. NLI-WO-002B remains unauthorized.

## Context

Review 03 required a real domain decision, not generated generic rationale. The decision affects schema identity, migration reversibility, privacy boundaries, performance, operations and future implementation safety.

## Decision drivers

- Preserve official reconstruction without treating mutable codes or public aliases as identity.
- Protect restricted evidence and identity values.
- Keep target schema insertable and enforceable in PostgreSQL/PostGIS.
- Support national-scale lookup, correction, dispute and publication workflows.

## Decision

`location_record` remains sole canonical anchor; object roles are enforced by typed link/cardinality rules; polymorphic integrity uses `registry_subject`.

## Alternatives considered

| Alternative | Benefit | Cost / rejection reason |
|---|---|---|
| many nullable FKs | strong simple FKs | wide sparse tables and role explosion |
| opaque polymorphism | flexible | orphan risk |
| subject registry + typed cardinality | flexible and enforceable | selected |

## Security and privacy implications

- Restricted raw values are preserved in governed archives, never replaced by hashes alone.
- Public projections require release items; database presence is not public authority.
- Identity/crosswalk data is operator-only and auditable.

## Performance and operational trade-offs

- Additional crosswalk, interval and subject indexes are required.
- Writes pay validation cost; reads gain stable current indexes and release snapshots.
- Bulk migration must batch by owner and exception threshold.

## Migration consequences

- Existing ids are preserved as legacy crosswalks, not reused as canonical authority.
- Backfills are idempotent by legacy source key.
- Exceptions are first-class records with owner/SLA.

## Failure modes

- Missing crosswalk creates duplicate canonical entities.
- Weak subject validation creates orphan names/geometry/disputes.
- Missing release prerequisites exposes unapproved data.

## Consequences

- The selected model increases write-time validation and migration ceremony, but prevents silent identity, publication, geometry and evidence drift.
- Operators receive stable current projections while the database retains historical reconstruction and crosswalk evidence.
- WO-002B must implement the accepted constraints rather than inventing compatible-but-different semantics.

## Acceptance checks

- Disposable target schema executes in PostGIS.
- Machine-readable fixtures insert with FK/vocabulary/cardinality/geometry checks.
- Catalog comparison matches typed model.
- Review 04 semantic CI is green at the exact PR head.
