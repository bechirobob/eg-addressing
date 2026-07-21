# Representative Record — Disputed geometry

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| geometry_version | gv-dispute-001 | quality_state=disputed, dispute_case_id set | disputed | old public release remains exact snapshot or suspended by authority |
| dispute_case | dc-geometry-001 | dispute_type=geometry, case_state=under-review | under-review | targets geometry_version |
| geometry_observation | go-dispute-new-001 | new observation captured | observed | candidate successor geometry |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| geometry released | 2026-07-10T00:00:00Z | 2026-07-09T14:00:00Z | accepted-canonical | release item |
| dispute opened | 2026-07-14T10:00:00Z | 2026-07-14T10:01:00Z | disputed | dispute_case |
| recapture | 2026-07-14T12:00:00Z | 2026-07-14T12:05:00Z | observed | new geometry_observation |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves geometry dispute behavior without overwriting approved/released geometry.
