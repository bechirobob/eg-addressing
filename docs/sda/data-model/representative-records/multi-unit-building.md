# Representative Record — Multi-Unit Building

## IDs and entities

| Entity | ID | State/classification | Relationships |
|---|---|---|---|
| `source_authority` | `sa-eg-registry-001` | official-government / government-internal | source owner |
| `source_package` | `sp-multi-unit-building-001` | checksum recorded | contains source record |
| `source_record` | `sr-multi-unit-building-001` | restricted where citizen/evidence exists | supports intake/assertions |
| `evidence_object` | `ev-multi-unit-building-photo-001` | restricted | linked by content hash |
| `location_record` | `lr-multi-unit-building-001` | active / government-internal | sole canonical anchor |
| `location_record_version` | `lrv-multi-unit-building-001` | current, effective `2026-07-13T10:00:00Z` | exact target for publication |
| `public_code_alias` | `pca-multi-unit-building-001` | active-public | released alias `EG-NLI-MUL-0001` |
| `geometry_observation` | `go-multi-unit-building-001` | restricted, EPSG:4326 | raw evidence geometry |
| `geometry_version` | `gv-multi-unit-building-001` | valid, current | approved geometry for record/object |
| `publication_release` | `rel-multi-unit-building-001` | publicly-released | immutable manifest |
| `publication_release_item` | `reli-multi-unit-building-001` | released | snapshots `lrv-multi-unit-building-001` and `pca-multi-unit-building-001` |

## Object relationships

| Link | Role | Object | Cardinality note |
|---|---|---|---|
| `lrv-multi-unit-building-001 -> object` | primary-subject | scenario-specific road/building/unit/landmark/admin object | Multiple object links allowed by `location_record_object_link`. |
| `lrv-multi-unit-building-001 -> administrative_unit` | located-in | province/district/municipality/locality context | Admin context uses effective version. |

## State and event timeline

| Event | State | Effective at | Recorded at | Actor/authority | Evidence |
|---|---|---|---|---|---|
| intake submitted | submitted | 2026-07-13T09:00:00Z | 2026-07-13T09:00:05Z | citizen/operator | source_record + evidence_object |
| registry approved | registry-ready | 2026-07-13T10:00:00Z | 2026-07-13T10:03:00Z | registry-authority | decision_event |
| publication released | publicly-released | 2026-07-14T00:00:00Z | 2026-07-13T15:00:00Z | publication-authority | release manifest |


## Geometry and quality

| Geometry | Type/SRID | Source | Quality | Constraint |
|---|---|---|---|---|
| `go-multi-unit-building-001` | `geometry(Point,4326)` or role-specific geometry | source/evidence | unvalidated observation | never published directly |
| `gv-multi-unit-building-001` | approved `geometry(Geometry,4326)` | validated from observation | valid/current | one current per subject/role |

## Classification and projections

| Projection | Expected fields | Forbidden fields |
|---|---|---|
| Operator | lifecycle, source/evidence metadata, geometry quality, event timeline | secrets/credentials |
| Public | released public code, released label, approved public geometry policy, public status | citizen contact, DIP, raw evidence, internal notes |
| Partner/export | release-scoped fields from `publication_release_item` | unrelated case-file details |

## Scenario-specific validation

This worked record exercises `Multi-Unit Building` while preserving the same canonical pattern: source/evidence -> decision -> immutable version -> public alias -> publication snapshot. Corrections, disputes, units, locality, and boundary changes use new versions/events rather than overwriting history.
