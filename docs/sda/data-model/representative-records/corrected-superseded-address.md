# Representative Record — Corrected and superseded address

## Entity instances

| Entity | ID | Required target fields instantiated | Classification/state | Relationships |
|---|---|---|---|---|
| location_record_version | lrv-corrected-001-v1 | recorded_to set when corrected | corrected | successor_version_id=lrv-corrected-001-v2 |
| location_record_version | lrv-corrected-001-v2 | predecessor_version_id=v1, correction_case_id set | active | current by recorded_to IS NULL |
| publication_release_item | pri-corrected-v1 | old release snapshot remains immutable | superseded | new release item targets v2 |

## Timeline

| Event | Effective time | Recorded time | State/value | Source/evidence/decision |
|---|---|---|---|---|
| old release | 2026-07-10T00:00:00Z | 2026-07-09T14:00:00Z | published | release item v1 |
| correction approved | 2026-07-12T00:00:00Z | 2026-07-14T09:00:00Z | corrected | correction_case |
| new release | 2026-07-15T00:00:00Z | 2026-07-14T16:00:00Z | published | release item v2 |

## Geometry, evidence, aliases, and projections

- Geometry uses valid `geometry_observation` and approved `geometry_version` fields from `target-model.json`.
- Each scenario is evaluated against a `location_record` or explicitly documented source/control record so canonical authority remains clear.
- Public alias/release uses `public_code_alias`, `publication_release`, and `publication_release_item` exact version/alias snapshots.
- Operator projection includes source/evidence/quality/case fields according to classification.
- Public projection includes only the immutable release item payload.

**Scenario validation:** Proves backdated correction, recorded time, predecessor/successor, and immutable publication history.
