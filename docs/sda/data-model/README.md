# NLI-WO-002 Data Model Design Pack

**Status:** READY FOR SDA REVIEW 03.  
**Boundary:** Design/documentation only; no runtime code, executable migration, API contract, infrastructure runtime, or production data change.

## Authoritative model sources

1. `target-model.json` — typed model metadata.
2. `target-entity-field-registry.md` — rendered authoritative field registry.
3. `current-to-target-mapping.json` — validated current-field map.
4. `design-consistency-report.md` — generated semantic check report.

## Acceptance-criterion evidence matrix

| Criterion | Agent status | Exact sections/artifacts | Validation assertion |
|---|---|---|---|
| AC-01 | READY FOR SDA REVIEW | `current-state-inventory.md` field table and `schema_migrations` control ledger | checker validates current-field map count and mapping coverage |
| AC-02 | READY FOR SDA REVIEW | `canonical-conceptual-model.md` and ADR-007 decide `location_record` as sole anchor | checker validates target registry and draft SQL have one location_record authority |
| AC-03 | READY FOR SDA REVIEW | `administrative_unit` + `administrative_unit_version` fields; ADR-006 | nullable root parent and one-current recorded interval validated |
| AC-04 | READY FOR SDA REVIEW | `operational_area` and `operational_area_coverage` | separate owner/vocabulary/geometry role validated |
| AC-05 | READY FOR SDA REVIEW | addressable object entities and cardinality matrix | representative records validate urban/rural/unit/no-road cases |
| AC-06 | READY FOR SDA REVIEW | ADR-005 and `public_code_alias` | public code and internal ID fields validated separate |
| AC-07 | READY FOR SDA REVIEW | `controlled-vocabularies.md`, `lifecycle-state-machines.md` | controlled fields and transitions validated |
| AC-08 | READY FOR SDA REVIEW | ADR-008 and version/release fields | single current mechanism and optional links validated |
| AC-09 | READY FOR SDA REVIEW | geometry entities and ADR-009 | role/type/SRID/quality/source/licence rules validated |
| AC-10 | READY FOR SDA REVIEW | `name_record` reusable naming model | dictionary validates semantic fields |
| AC-11 | READY FOR SDA REVIEW | source/evidence/assertion/decision chain | FK and classification completeness validated |
| AC-12 | READY FOR SDA REVIEW | field-level classification in target registry | checker validates every field classification exists |
| AC-13 | READY FOR SDA REVIEW | field-to-vocabulary registry | checker validates every controlled field vocabulary assignment |
| AC-14 | READY FOR SDA REVIEW | draft SQL constraints/indexes and target constraints | SQL parse/checks validate FKs, optionality, current rules |
| AC-15 | READY FOR SDA REVIEW | OpenAPI operation/projection matrix | route inventory and projection coverage validated |
| AC-16 | READY FOR SDA REVIEW | `current-to-target-mapping.json/md` | mapping targets validated against target registry |
| AC-17 | READY FOR SDA REVIEW | convergence plan batches B0-B9 | batch ownership/validation/recovery/cutover matrix present |
| AC-18 | READY FOR SDA REVIEW | seven distinct representative records | scenario records validated for required entities/states/projections |
| AC-19 | READY FOR SDA REVIEW | national-scale assumptions/index plan | scale rows and index rationale present |
| AC-20 | READY FOR SDA REVIEW | non-executable draft SQL generated from typed metadata | SQL parser/checks pass |
| AC-21 | READY FOR SDA REVIEW | ADRs/RFIs and reserved-question matrix | coverage matrix validates all 12 questions |
| AC-22 | READY FOR SDA REVIEW | changed-path proof; PR remains draft | GitHub final-head CI and forbidden-path check |
