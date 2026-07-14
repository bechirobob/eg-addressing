# Representative Record — Multi-unit building

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| building | bldg-multi-001 | building can exist before entrance/unit | active | parent building |
| unit | unit-multi-apt-2a | parent_unit_id=NULL, unit_label=2A | active | unit has own location_record only because independently addressable |
| location_record | lr-unit-2a | record_type=unit | active | object links primary unit + parent-building + access-point |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| building approved | 2026-07-14T09:00:00Z | 2026-07-14T09:05:00Z | active | decision_event |
| unit created | 2026-07-14T09:30:00Z | 2026-07-14T09:31:00Z | active | field_observation + decision_event |
| unit release | 2026-07-15T00:00:00Z | 2026-07-14T17:00:00Z | published | release item snapshots unit version and alias |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves unit/sub-address semantics and creation-safe building/entrance/unit relationships.
