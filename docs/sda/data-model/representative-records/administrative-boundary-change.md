# Representative Record — Administrative boundary change

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| administrative_unit | au-malabo-001 | identity stable | active | two versions |
| administrative_unit_version | auv-malabo-v1/v2 | parent nullable for root; effective intervals non-overlap | v1 recorded_to set, v2 current | name/boundary versions |
| geometry_version | gv-admin-boundary-v2 | geometry_role=admin-boundary, MultiPolygon | accepted-canonical | subject administrative_unit_version |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| old boundary effective | 2020-01-01T00:00:00Z | 2026-07-01T10:00:00Z | active | source package |
| new boundary decision | 2026-07-14T00:00:00Z | 2026-07-14T09:00:00Z | active | decision_event |
| impact release | 2026-07-20T00:00:00Z | 2026-07-15T12:00:00Z | published | release manifest documents boundary context |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves administrative identity/version separation and boundary versioning.
