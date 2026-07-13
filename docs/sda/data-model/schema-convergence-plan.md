# Expand–Migrate–Contract Convergence Plan

**Status:** Draft proposal for later NLI-WO-002B authorization

## 1. Non-authorizing note

This plan is not a deployment authorization. It describes the likely safe path after SDA accepts the design model.

## 2. Expand phase

- Add target canonical/reference/evidence/publication tables via reviewed executable migrations.
- Add compatibility columns/views where needed.
- Keep current writes unchanged until new write adapters are ready.
- Add state/vocabulary reference tables or check constraints only after mapping is complete.
- Add source authority and geometry version tables before backfill.
- Add spatial indexes after PostGIS restore/readiness proof.

## 3. Migrate phase

- Backfill administrative units from `provinces` and `admin_units` with source/effective metadata.
- Backfill operational areas from `territories`.
- Backfill canonical records from `address_records` first, because it is current canonical case-file layer.
- Link legacy `addresses` as compatibility/source records, not as a second authority.
- Convert `citizen_geotag_submissions` into intake/evidence cases.
- Convert `field_submissions.spatial_evidence` into field observations/evidence metadata.
- Convert publication packs into publication releases and release items.
- Compute before/after counts, checksums, relationship checks, geometry validity counts, and publication safety checks.

## 4. Dual-read / adapter phase

- Public lookup reads canonical projection first.
- Operator search reads canonical records with fallback only where mapped.
- Publication/export/signage use publication release items.
- Legacy endpoints keep response shape unless a later API work order authorizes contract changes.

## 5. Cutover phase

- Freeze legacy write paths or route them through canonical services.
- Enforce canonical invariants.
- Monitor audit, counts, query parity, public safety, and geometry parity.

## 6. Contract phase

- Remove unused fallback reads after evidence window.
- Deprecate legacy columns/tables only through explicit migration work order.
- Preserve audit/history and public-code redirect/supersession behavior.

## 7. Validation gates

| Gate | Required evidence |
|---|---|
| Schema gate | migration dry run, empty DB, upgrade DB, rollback/forward recovery. |
| Count gate | source/target row counts per mapped entity. |
| Relationship gate | FK and relationship parity. |
| Geometry gate | valid geometry counts, null geometry exceptions, SRID check. |
| Publication gate | no internal registry rows in public projections. |
| API parity gate | current API responses match expected compatibility projections. |
| Audit gate | creation/update/publication events have actor/source/time. |
| Restore gate | backup/restore retains counts, hashes, relationships, geometry. |

## 8. Performance/index assumptions

High-growth tables: source records, intake cases, geometry versions, events, evidence objects, public lookup aliases. Expected indexes: public code unique current, canonical state/update, admin hierarchy, source package, geometry GiST, event record/time, release item record/release, correction/dispute target/status.
