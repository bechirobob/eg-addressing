# Canonical Conceptual Model

## Architecture decisions

- **single_current_version_mechanism:** Open recorded interval: recorded_to IS NULL is the only authoritative current-version marker. Pointers and booleans are derived views only and not stored in the target model.
- **root_admin_insertability:** administrative_unit_version.parent_administrative_unit_id is nullable; root and first versions are insertable.
- **creation_safe_objects:** building does not require primary entrance; building_primary_entrance assigns it after entrance exists. unit.parent_unit_id is nullable for root units.
- **publication_snapshots:** publication_release_item stores complete immutable projection payload JSON, payload hash, manifest URI, exact location_record_version_id, and exact public_code_alias_id.
- **geometry_subject_integrity:** geometry_version subject_entity/subject_id is constrained by role-to-subject registry and validated by WO-002B triggers; role-to-type rules are explicit in target-model.json.
- **field_mapping_policy:** Every current field maps to an existing target field, a structured multi-target transformation, archive/compatibility disposition, RFI/exception, or accepted-loss request. This pack uses no accepted-loss requests.

## Domains and entities

| Domain | Entity | Owner | Meaning |
|---|---|---|---|
| Administrative Geography | `country` | GIS/Data Authority | Country identity row for Equatorial Guinea and future scoped reference datasets. |
| Administrative Geography | `administrative_unit` | GIS/Data Authority | Stable administrative identity independent of mutable names, hierarchy, and boundaries. |
| Administrative Geography | `administrative_unit_version` | GIS/Data Authority | Effective-dated administrative hierarchy/name/status version. |
| Names | `name_record` | Registry/GIS Authority | Reusable multilingual, alternate, historical, and normalized names for named target entities. |
| Operational Geography | `operational_area` | Operations Authority | Campaign/routing/rollout/service/incident area distinct from legal administration. |
| Operational Geography | `operational_area_coverage` | Operations Authority | Relationship between operational areas and administrative units/boundaries. |
| Addressable Objects | `road` | Registry Authority | Named access corridor identity independent of geometry segmentation. |
| Addressable Objects | `road_segment` | Registry Authority | Geometry/routing segment of a road. |
| Addressable Objects | `parcel_reference` | GIS/Data Authority | Optional external parcel/cadastre reference without ownership/title claim. |
| Addressable Objects | `building` | Registry Authority | Building object; entrances/units can be added after building creation. |
| Addressable Objects | `entrance` | Registry Authority | Access point to a building; creation-safe because building does not require primary entrance. |
| Addressable Objects | `building_primary_entrance` | Registry Authority | Optional effective-dated primary entrance assignment avoiding building/entrance circular inserts. |
| Addressable Objects | `unit` | Registry Authority | Unit/sub-address object within a building; parent unit is optional for root units. |
| Addressable Objects | `landmark` | Registry Authority | Landmark object used as addressable subject or contextual reference. |
| Administrative Geography | `locality` | GIS/Data Authority | Named locality/settlement/neighbourhood context below or beside formal admin hierarchy. |
| Addressable Objects | `non_building_object` | Registry Authority | Non-building addressable object such as kiosk, site, utility point, or compound feature. |
| Location Registry | `location_record` | Registry Authority | Sole canonical registry anchor for addressable records. |
| Location Registry | `location_record_version` | Registry Authority | Immutable bitemporal version of canonical record attributes. |
| Location Registry | `location_record_object_link` | Registry Authority | Typed relationship between a record version and one or more addressable/context objects. |
| Location Registry | `location_record_relationship` | Registry Authority | Relationship between canonical records, e.g. supersession/duplicate/contains. |
| Identifiers | `public_code_alias` | Registry Authority | Public code alias independent of internal IDs and exact release state. |
| Geometry | `geometry_observation` | GIS/Data Authority | Raw or candidate spatial evidence, never automatically official geometry. |
| Geometry | `geometry_version` | GIS/Data Authority | Approved geometry version for a typed subject and role. |
| Geometry | `geometry_transformation` | GIS/Data Authority | Reproducible transformation from one geometry/source to another. |
| Geometry | `geometry_quality_assessment` | GIS/Data Authority | Automated or human quality assessment for approved geometry. |
| Source and Evidence | `licence` | Legal/Privacy Authority | Licence/usage terms for external data or evidence. |
| Source and Evidence | `source_authority` | SDA | Institution/system/source authority class. |
| Source and Evidence | `source_package` | Data Authority | Import/submission/reference package with checksum and licence. |
| Source and Evidence | `source_record` | Data Authority | Immutable source row/submission key and raw payload hash. |
| Source and Evidence | `evidence_object` | Legal/Privacy Authority | Classified evidence object metadata; binary object remains in object storage. |
| Source and Evidence | `decision_event` | SDA/Registry Authority | Authority decision/audit event that promotes or changes model state. |
| Source and Evidence | `location_record_assertion` | Registry Authority | Field-level assertion linking target facts to source/evidence/decision. |
| Field Operations | `intake_case` | Registry Authority | Candidate/evidence intake case from citizen/import/operator source. |
| Field Operations | `field_assignment` | Field Operations Authority | Field work assignment. |
| Field Operations | `field_observation` | Field Operations Authority | Field observation and verification result. |
| Corrections and Publication | `correction_case` | Registry Authority | Correction request/case targeting a canonical record or public code. |
| Corrections and Publication | `dispute_case` | Registry Authority | Dispute case targeting a record, object, geometry, name, or release item. |
| Corrections and Publication | `publication_release` | Publication Authority | Immutable release manifest header for public/partner/export projections. |
| Corrections and Publication | `publication_release_item` | Publication Authority | Immutable release item snapshot targeting exact version and alias. |
| Agency Integration | `partner_projection` | Publication Authority | Partner-scoped projection authorization for release items. |
| Convergence | `migration_exception` | Operations Authority | Structured exception record for future WO-002B migration/backfill issues. |

## Record type / object role cardinality

| Record type | Required roles | Optional roles | Max per role | Independent-addressability criterion |
|---|---|---|---|---|
| `address` | `primary-subject` | `context-road`, `access-point`, `nearby-landmark`, `external-parcel-reference`, `context-locality` | {"access-point": 1, "primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
| `building` | `primary-subject` | `context-road`, `access-point`, `external-parcel-reference` | {"primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
| `unit` | `primary-subject`, `parent-building` | `access-point`, `context-road` | {"parent-building": 1, "primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
| `entrance` | `primary-subject` | `parent-building`, `context-road` | {"primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
| `landmark` | `primary-subject` | `context-locality`, `context-road` | {"primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
| `non-building-object` | `primary-subject` | `context-road`, `context-locality` | {"primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
| `service-location` | `primary-subject` | `nearby-landmark`, `context-road`, `context-locality` | {"primary-subject": 1} | Independently addressable when it requires its own public/protected lookup, correction/dispute history, release snapshot, or agency/field workflow. |
