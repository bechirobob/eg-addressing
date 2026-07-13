# Current-to-Target Mapping

**Status:** Draft for SDA review

## 1. Mapping disposition values

- `canonical-target`: becomes part of target canonical authority.
- `reference-target`: becomes governed reference data.
- `evidence-target`: preserved as source/evidence, not canonical.
- `operational-target`: retained as workflow/operations data.
- `compatibility`: retained temporarily for API/backward compatibility.
- `archive/deprecate`: retained historically or retired later.
- `outside-location-model`: not part of NLI-WO-002 data model.
- `RFI`: needs authority decision.

## 2. Table-level mapping

| Current table | Target entity/domain | Disposition | Notes |
|---|---|---|---|
| `provinces` | `administrative_unit` level `province` | reference-target | Preserve codes; add source/effective dates later. |
| `admin_units` | `administrative_unit` | reference-target | Normalize levels and parent hierarchy. |
| `territories` | `operational_area` | operational-target | Do not treat as legal geography. |
| `roads` | `road`, `road_segment`, `road_name` | canonical-target/evidence-target | Split geometry/name approval. |
| `buildings` | `building`, `entrance`, `addressable_object` | canonical-target/evidence-target | Keep relationship to road/segment/admin unit. |
| `addresses` | compatibility source to `location_record` | compatibility | Not second canonical authority. |
| `address_points` | `geometry_version` / legacy geometry observation | compatibility/evidence-target | Current active point becomes geometry observation/version. |
| `citizen_geotag_submissions` | `intake_case`, `geometry_observation`, candidate source | evidence-target | Candidate only until promotion. |
| `address_records` | `location_record` / current canonical anchor | canonical-target | Evolve as sole canonical authority. |
| `address_record_events` | `location_record_event` | canonical-target/audit | Preserve timeline. |
| `field_assignments` | `field_assignment` | operational-target | Workflow only. |
| `field_submissions` | `field_observation` | evidence-target | Evidence not canonical. |
| `address_corrections` | `correction_case` | operational/evidence-target | Link to canonical record/candidate. |
| `publication_packs` | `publication_release` | operational-target | Must target canonical records in future. |
| `publication_pack_addresses` | `publication_release_item` | compatibility -> target | Migrate from legacy addresses to canonical records. |
| `import_jobs` | `source_package`/ingestion job | evidence-target | Add checksum/source authority. |
| `import_rows` | `source_record` | evidence-target | Preserve raw lineage. |
| `audit_logs` | platform audit | outside-location-model/link | Link canonical events to audit IDs. |
| `users`, `auth_tokens` | identity/session | outside-location-model | Actor references only. |
| fixture/reference ledgers | load/fixture metadata | operational-target | Non-production fixture records never canonical. |

## 3. Critical field mappings

| Current field | Target | Disposition | Note |
|---|---|---|---|
| `addresses.public_code` | `public_code_alias.public_code` | compatibility | Future public code points to canonical record. |
| `addresses.publication_state` | `location_record.publication_state` or release item | compatibility | Must not be direct authority after convergence. |
| `addresses.verification_status` | validation/authority assertion | compatibility | Split from publication. |
| `citizen_geotag_submissions.grid_code` | candidate public-code reservation/source code | evidence-target | Not public authority until release. |
| `citizen_geotag_submissions.latitude/longitude` | `geometry_observation` | evidence-target | Candidate geometry. |
| `citizen_geotag_submissions.dip_last4` | restricted evidence/identity assertion | RFI/restricted | Avoid expanded identity storage. |
| `citizen_geotag_submissions.status` | candidate lifecycle | evidence-target | Map separately from canonical/publication status. |
| `citizen_geotag_submissions.field_status` | field verification lifecycle | evidence-target | Separate state machine. |
| `address_records.address_code` | public/internal code alias pending authority | canonical-target | Code grammar RFI remains. |
| `address_records.status` | canonical lifecycle | canonical-target | Do not overload publication. |
| `address_records.publication_state` | publication state | canonical-target | Values normalized. |
| `address_records.latitude/longitude/geom` | `geometry_version` current location point | canonical-target | Retain WGS84 compatibility during transition. |
| `address_records.record_bundle` | structured source/evidence/version data | compatibility -> normalized tables | Avoid permanent opaque authority. |
| `address_record_events.event_type` | `location_record_event.event_type` | canonical-target | Controlled event vocabulary. |
| `field_submissions.spatial_evidence` | `field_observation` + `evidence_object` | evidence-target | Preserve lineage/hash/object refs. |
| `publication_packs.status` | `publication_release.release_state` | operational-target | Requires publication authority. |
| `roads.spatial_evidence` | road geometry observations | evidence-target | Geometry not canonical without approval. |
| `buildings.spatial_evidence` | building/access geometry observations | evidence-target | Geometry not canonical without approval. |

## 4. Compatibility period

Future WO-002B should create compatibility reads/writes so existing public/operator workflows continue while canonical tables are expanded and backfilled. Contract phase can retire direct legacy reads only after parity checks pass.
