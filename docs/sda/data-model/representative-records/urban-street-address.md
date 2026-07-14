# Representative Record — Urban street address

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| location_record | lr-urban-001 | record_type=address, classification=government-internal | active via current version | version links building, entrance, road_segment |
| road + road_segment | road-malabo-independencia / seg-001 | road_class=street, geometry_role=road-centerline | active | context-road object link |
| building + entrance | bldg-urban-001 / ent-urban-main | building first, primary entrance assigned later | active | creation-safe primary entrance |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| intake | 2026-07-14T08:00:00Z | 2026-07-14T08:01:00Z | submitted | source_record sr-urban-001 |
| registry approval | 2026-07-14T09:00:00Z | 2026-07-14T09:05:00Z | active | decision_event promote-record |
| release | 2026-07-15T00:00:00Z | 2026-07-14T16:00:00Z | published | publication_release_item exact lrv+pca |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves ordinary street/building/entrance/public-code flow.
