# Expand–Migrate–Contract Convergence Plan

## Authority boundary

NLI-WO-002B remains unauthorized. This plan is implementation-authority detail for future scoping only.

## Migration batches and dependencies

| Batch | Dependency | Action | Owner | Idempotency/exception handling | Validation/tolerance |
|---|---|---|---|---|---|
| B0 backup/readiness | accepted WO-002B | backup, restore drill, migration-state proof | Ops/SDA | abort if backup/restore not proven | zero unresolved readiness errors |
| B1 reference/source foundations | B0 | create source_authority/package/record/evidence, vocab tables | backend/data | upsert by authority/package checksum | counts match source ledgers |
| B2 geography/operations | B1 | admin units, names, boundaries, locality, operational areas/coverage | GIS/data | upsert by official/source code | hierarchy no cycles, active parent exists |
| B3 objects/geometry observations | B1/B2 | roads/segments/names/buildings/entrances/units/landmarks/non-building objects; raw geometry observations | registry/GIS | deterministic source keys; exceptions queue | geometry valid or exceptioned |
| B4 canonical records/versions | B2/B3 | backfill address_records first, then legacy addresses as compatibility source | registry | natural key = current address_records.id/address_code | source/target counts/checksums match |
| B5 assertions/events/cases | B4 | normalize record_bundle, events, corrections, disputes, field observations | registry | event idempotency by source+type+time hash | every canonical fact has source/decision |
| B6 publication aliases/releases | B4/B5 | create public_code_alias, release snapshots, partner/export projections | publication authority | alias non-reuse checks | no internal-only record in public release |
| B7 dual read/write | B6 | adapters: canonical write with legacy compatibility projection | backend | retriable writes by idempotency key | API parity suite green |
| B8 cutover | monitoring window | canonical-first reads, freeze legacy direct writes | SDA/Ops | forward-only unless gate fails | parity, latency, error budget within tolerance |
| B9 contract/deprecate | B8 acceptance | retire fallback reads and legacy mutable paths | SDA | archive before drop | deprecation evidence accepted |

## Precedence and conflict behavior

1. Existing `address_records` wins over legacy `addresses` for canonical registry facts.
2. `citizen_geotag_submissions` remains evidence/candidate unless already promoted to address_records.
3. Field/GIS validated geometry wins over citizen/browser geometry; weaker geometry remains observation.
4. Publication release snapshots win over mutable current record for historical public proof.
5. Conflicts go to exception queues, not silent overwrite.

## Dual-read/write behavior

During compatibility, writes go to canonical target and project to legacy response shapes. Reads use canonical target first with explicit fallback only for unmigrated rows. Public endpoints read only release items. Operator endpoints may show migration exceptions.

## Validation SQL examples

- `SELECT COUNT(*) FROM address_records` equals canonical backfill count excluding archived/exceptioned rows.
- `SELECT public_code, COUNT(*) FROM proposed_public_code_alias GROUP BY public_code HAVING COUNT(*) > 1` returns 0.
- `SELECT location_record_id, COUNT(*) FROM proposed_location_record_version WHERE is_current GROUP BY 1 HAVING COUNT(*) <> 1` returns 0.
- `SELECT COUNT(*) FROM proposed_geometry_version WHERE ST_SRID(geom) <> 4326 OR NOT ST_IsValid(geom)` returns 0 except approved exceptions.
- Public release check: no `publication_release_item` targets a version whose record publication state is below release-approved.

## Monitoring, rollback, and forward recovery

Before cutover, rollback is database restore plus app rollback. After dual-write begins, prefer forward recovery: pause writes, reconcile idempotency keys, replay source records/events, regenerate projections, and verify parity. Contract phase requires a recorded monitoring window with no unresolved exceptions.

## National-scale assumptions

Initial pilot scale: thousands of records. National scale: millions of location records, geometry observations, events, and source records. Index priorities: public code unique lookup, canonical lifecycle/publication filters, source package/record joins, event timeline, PostGIS GiST geometry, admin hierarchy, publication release items. Partition candidates after national rollout: events, source_records, geometry_observations, evidence_objects by time/source package; publication release items by release/projection type.
