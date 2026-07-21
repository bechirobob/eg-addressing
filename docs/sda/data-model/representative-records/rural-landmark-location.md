# Representative Record — Rural landmark location

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| location_record | lr-rural-001 | record_type=landmark | registry-ready | primary landmark + nearby locality |
| landmark | lm-rural-school-001 | landmark_type=landmark, name_record local/official | active | primary-subject |
| geometry_version | gv-rural-point-001 | geometry_role=landmark-point, Point | accepted-canonical | source observation from field device |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| field capture | 2026-07-14T10:00:00Z | 2026-07-14T10:02:00Z | field-captured | geometry_observation go-rural-001 |
| GIS validation | 2026-07-14T11:00:00Z | 2026-07-14T11:04:00Z | accepted-canonical | quality_assessment qa-rural-001 |
| internal registry | 2026-07-14T12:00:00Z | 2026-07-14T12:03:00Z | registry-ready | decision_event |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves no-formal-road rural addressability through landmark/locality without false road data.
