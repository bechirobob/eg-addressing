# Representative Record — No formal road location

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| location_record | lr-no-road-001 | record_type=service-location | registry-ready | primary non_building_object, nearby-landmark, context-locality |
| non_building_object | obj-waterpoint-001 | object_type=service-location | active | primary-subject |
| location_record_object_link | link-no-road-ctx | no context-road role required | valid | locality/landmark only |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| submission | 2026-07-14T07:00:00Z | 2026-07-14T07:02:00Z | submitted | intake_case |
| field verification | 2026-07-14T13:00:00Z | 2026-07-14T13:10:00Z | linked-to-canonical | field_observation |
| internal approval | 2026-07-14T15:00:00Z | 2026-07-14T15:01:00Z | registry-ready | decision_event |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves the model does not force false road/building data.
