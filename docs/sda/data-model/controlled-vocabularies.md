# Controlled Vocabulary Registry

One authoritative field-to-vocabulary registry. Review 05 separates canonical records, reference objects, operational areas, source authorities, names, cases, geometry, and publication lifecycles.

## Field-to-vocabulary registry

| Target field | Vocabulary | Owner | Allowed values |
|---|---|---|---|
| `administrative_unit_version.admin_level` | `admin_level` | GIS/Data Authority | country, district, local_council, municipality, province |
| `administrative_unit_version.lifecycle_state` | `administrative_unit_lifecycle` | GIS/Data Authority | proposed, official, historical, retired, revoked |
| `administrative_unit_version.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `building.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `correction_case.correction_type` | `correction_type` | Registry Authority | administrative-context, classification, duplicate, geometry, label |
| `correction_case.case_state` | `case_state` | Registry Authority | approved, closed, needs-evidence, rejected, resolved, submitted, under-review |
| `country.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `decision_event.decision_type` | `decision_type` | SDA/Registry Authority | approve-geometry, approve-publication, correct-record, promote-record, resolve-dispute, supersede-record, withdraw-publication |
| `dispute_case.dispute_type` | `dispute_type` | Registry Authority | authority, duplicate, geometry, name, publication |
| `dispute_case.case_state` | `case_state` | Registry Authority | approved, closed, needs-evidence, rejected, resolved, submitted, under-review |
| `entrance.entrance_role` | `entrance_role` | Registry Authority | main, secondary, service, emergency, gate |
| `entrance.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `evidence_object.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `evidence_object.retention_state` | `retention_state` | Legal/Privacy Authority | active, disposed-metadata-retained, legal-hold, scheduled-disposal |
| `field_assignment.assignment_state` | `field_verification_state` | Field Operations Authority | assigned, cancelled, evidence-approved, evidence-rejected, evidence-under-review, field-captured, in-progress, linked-to-canonical, needs-recapture |
| `field_observation.verification_state` | `field_verification_state` | Field Operations Authority | assigned, cancelled, evidence-approved, evidence-rejected, evidence-under-review, field-captured, in-progress, linked-to-canonical, needs-recapture |
| `field_observation.notes_classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `geometry_observation.geometry_role` | `geometry_role` | GIS/Data Authority | admin-boundary, building-footprint, building-point, entrance-point, landmark-area, landmark-point, location-point, operational-boundary, parcel-boundary, road-centerline |
| `geometry_observation.capture_method` | `capture_method` | GIS/Data Authority | browser-gps, derived-from-source, field-device-gps, imported-geometry, manual-map-point, surveyed |
| `geometry_observation.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `geometry_quality_assessment.check_result` | `quality_check_result` | GIS/Data Authority | passed, passed-with-warning, failed, not-applicable |
| `geometry_version.geometry_role` | `geometry_role` | GIS/Data Authority | admin-boundary, building-footprint, building-point, entrance-point, landmark-area, landmark-point, location-point, operational-boundary, parcel-boundary, road-centerline |
| `geometry_version.quality_state` | `geometry_quality_state` | GIS/Data Authority | accepted-canonical, disputed, observed, quality-checked, rejected, reviewed, superseded, valid-with-warning |
| `geometry_version.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `intake_case.intake_state` | `intake_state` | Registry Authority | closed, duplicate-review, needs-field-check, promoted-to-canonical, rejected, submitted, under-review |
| `landmark.landmark_type` | `landmark_type` | Registry/GIS Authority | school, clinic, market, religious-site, public-office, natural-feature, other |
| `landmark.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `licence.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `locality.locality_type` | `locality_type` | GIS/Data Authority | informal_area, neighbourhood, quarter, settlement, village |
| `locality.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `location_record.record_type` | `record_type` | Registry Authority | address, building, entrance, landmark, non-building-object, service-location, unit |
| `location_record.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `location_record_assertion.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `location_record_object_link.object_role` | `object_role` | Registry Authority | access-point, context-locality, context-road, external-parcel-reference, nearby-landmark, parent-building, primary-subject |
| `location_record_relationship.relationship_type` | `relationship_type` | Registry Authority | contains, corrects, duplicates, near, served-by, supersedes |
| `location_record_version.lifecycle_state` | `canonical_record_lifecycle` | Registry Authority | candidate, under-review, active, corrected, superseded, disputed, retired, revoked |
| `name_record.name_kind` | `name_kind` | Registry/GIS Authority | alternate, historical, local, normalized-search, official-en, official-es |
| `name_record.name_status` | `name_status` | Registry/GIS Authority | alternate, candidate, disputed, official-current, official-historical, rejected, retired, under-review |
| `non_building_object.object_type` | `non_building_object_type` | Registry Authority | utility-asset, public-space, delivery-point, infrastructure-node, other |
| `non_building_object.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `operational_area.area_type` | `operational_area_type` | Operations Authority | campaign, incident, rollout, routing, service |
| `operational_area.lifecycle_state` | `operational_area_lifecycle` | Operations Authority | planned, active, suspended, closed, archived |
| `operational_area.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `operational_area_coverage.coverage_role` | `coverage_role` | Operations Authority | context, excluded, partial, primary |
| `parcel_reference.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `partner_projection.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `public_code_alias.code_state` | `public_code_state` | Programme Owner / Registry Authority | active-public, blocked, reserved-internal, retired, revoked, superseded |
| `publication_release.release_state` | `publication_release_state` | Publication Authority | approval-requested, approved, draft, published, suspended, withdrawn |
| `publication_release.projection_type` | `projection_type` | Publication Authority | operator-case-file, partner-api, public-lookup, signage-export, statistics |
| `publication_release_item.projection_state` | `publication_item_state` | Publication Authority | included, redacted, superseded, withdrawn |
| `registry_subject.subject_state` | `subject_lifecycle` | Registry Authority | active, retired, merged, deleted-prohibited |
| `registry_subject.delete_policy` | `delete_policy` | Registry Authority | retire-only, cascade-prohibited, merge-required |
| `road.road_class` | `road_class` | Registry/GIS Authority | path, road, service-road, street, track, unknown |
| `road.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `road_segment.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `source_authority.authority_class` | `source_authority_class` | SDA | citizen-submitted, derived-system, external-map-suggestion, fixture-training, gis-data-authority, imported-provisional, official-government, registry-authority, unverified-field, verified-field |
| `source_authority.status` | `lifecycle_state` | Registry Authority | active, corrected, disputed, draft-candidate, registry-ready, registry-review, retired, revoked, superseded |
| `source_payload_archive.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `source_payload_archive.retention_state` | `retention_state` | Legal/Privacy Authority | active, disposed-metadata-retained, legal-hold, scheduled-disposal |
| `source_record.raw_payload_classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |
| `unit.unit_type` | `unit_type` | Registry Authority | apartment, office-suite, room, shop-unit, compound-unit |
| `unit.lifecycle_state` | `reference_object_lifecycle` | Registry/GIS Authority | candidate, active, corrected, superseded, retired, revoked |
| `unit.classification` | `classification` | Legal/Privacy Authority | government-internal, highly-restricted, public, public-after-release, restricted, security-internal |

## `admin_level`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| country | Sovereign country row. |
| district | District-level administrative unit. |
| local_council | Recognized lower level when authorized. |
| municipality | Municipality-level administrative unit. |
| province | First-level administrative unit. |

## `administrative_unit_lifecycle`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| proposed | Proposed administrative version. |
| official | Official active version. |
| historical | Historical official version. |
| retired | Retired version. |
| revoked | Revoked version. |

## `building_lifecycle`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate building. |
| active | Active building. |
| demolished | Demolished building. |
| retired | Retired building. |
| revoked | Revoked building. |

## `canonical_record_lifecycle`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate record. |
| under-review | Registry review. |
| active | Current approved canonical state. |
| corrected | Corrected by later version. |
| superseded | Superseded. |
| disputed | Active dispute. |
| retired | Retired. |
| revoked | Revoked. |

## `capture_method`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| browser-gps | Browser GPS coordinate. |
| derived-from-source | Derived from source geometry. |
| field-device-gps | Field device GPS. |
| imported-geometry | Imported geometry. |
| manual-map-point | Manual map correction. |
| surveyed | Surveyed/authoritative capture. |

## `case_lifecycle`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| submitted | Submitted. |
| under-review | Under review. |
| needs-evidence | Needs evidence. |
| approved | Approved. |
| rejected | Rejected. |
| resolved | Resolved. |
| closed | Closed. |

## `case_state`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| approved | Approved. |
| closed | Closed. |
| needs-evidence | More evidence required. |
| rejected | Rejected. |
| resolved | Resolved. |
| submitted | Case submitted. |
| under-review | Under review. |

## `classification`

Owner: **Legal/Privacy Authority**

| Value | Meaning |
|---|---|
| government-internal | Internal government/operator use. |
| highly-restricted | Identity/security-sensitive data. |
| public | Approved public data. |
| public-after-release | Internal until published through release. |
| restricted | Sensitive operational/evidence/location data. |
| security-internal | Security/session credential data. |

## `correction_type`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| administrative-context | Admin/locality context correction. |
| classification | Classification/visibility correction. |
| duplicate | Duplicate/merge correction. |
| geometry | Geometry correction. |
| label | Label/name correction. |

## `coverage_role`

Owner: **Operations Authority**

| Value | Meaning |
|---|---|
| context | Context only. |
| excluded | Explicitly excluded area. |
| partial | Partially covered unit. |
| primary | Primary covered unit. |

## `decision_type`

Owner: **SDA/Registry Authority**

| Value | Meaning |
|---|---|
| approve-geometry | Approve geometry version. |
| approve-publication | Approve release. |
| correct-record | Apply correction. |
| promote-record | Promote candidate to canonical. |
| resolve-dispute | Resolve dispute. |
| supersede-record | Supersede record/version. |
| withdraw-publication | Withdraw release. |

## `delete_policy`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| retire-only | Do not hard delete; retire and preserve links. |
| cascade-prohibited | Reject delete while dependent links exist. |
| merge-required | Merge/supersession required before retirement. |

## `dispute_type`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| authority | Authority/source dispute. |
| duplicate | Duplicate/supersession dispute. |
| geometry | Geometry dispute. |
| name | Name/label dispute. |
| publication | Publication/projection dispute. |

## `entrance_role`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| main | Main entrance. |
| secondary | Secondary entrance. |
| service | Service entrance. |
| emergency | Emergency entrance. |
| gate | Compound/gate access. |

## `field_verification_state`

Owner: **Field Operations Authority**

| Value | Meaning |
|---|---|
| assigned | Assigned to field team. |
| cancelled | Cancelled. |
| evidence-approved | Approved as evidence. |
| evidence-rejected | Rejected evidence. |
| evidence-under-review | Supervisor review. |
| field-captured | Evidence captured. |
| in-progress | Capture in progress. |
| linked-to-canonical | Linked to canonical record. |
| needs-recapture | Recapture required. |

## `geometry_quality_state`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| accepted-canonical | Approved canonical geometry. |
| disputed | Dispute unresolved. |
| observed | Raw observation captured. |
| quality-checked | Automated checks passed or recorded. |
| rejected | Rejected for canonical use. |
| reviewed | Human/system authority reviewed. |
| superseded | Replaced by newer geometry version. |
| valid-with-warning | Approved with documented warning. |

## `geometry_role`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| admin-boundary | Administrative polygon/multipolygon. |
| building-footprint | Building polygon/multipolygon. |
| building-point | Building representative point. |
| entrance-point | Entrance/access point. |
| landmark-area | Landmark polygon/multipolygon. |
| landmark-point | Landmark point. |
| location-point | Address/location point. |
| operational-boundary | Operational area polygon/multipolygon. |
| parcel-boundary | External parcel polygon when authorized. |
| road-centerline | Road or segment line/multiline. |

## `intake_state`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| closed | Closed without promotion. |
| duplicate-review | Possible duplicate. |
| needs-field-check | Needs field verification. |
| promoted-to-canonical | Promoted to canonical record. |
| rejected | Rejected. |
| submitted | Submitted by citizen/operator/import. |
| under-review | Under review. |

## `landmark_type`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| school | School. |
| clinic | Clinic/health point. |
| market | Market. |
| religious-site | Religious site. |
| public-office | Public office. |
| natural-feature | Natural feature. |
| other | Other approved landmark. |

## `lifecycle_state`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| active | Current active canonical state. |
| corrected | Corrected by later version. |
| disputed | Subject to unresolved dispute. |
| draft-candidate | Candidate not yet under authority review. |
| registry-ready | Approved for internal registry use only. |
| registry-review | Under registry review. |
| retired | No longer valid for current use. |
| revoked | Invalidated by authority. |
| superseded | Replaced by successor record or version. |

## `locality_lifecycle`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate locality. |
| official | Official locality. |
| renamed | Renamed locality. |
| retired | Retired locality. |

## `locality_type`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| informal_area | Recognized operational/local context pending authority. |
| neighbourhood | Neighbourhood not necessarily legal hierarchy. |
| quarter | Urban quarter/barrio. |
| settlement | Settlement/locality context. |
| village | Village/local reference. |

## `name_kind`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| alternate | Alternate known spelling/name. |
| historical | Former name retained for history. |
| local | Local/community name. |
| normalized-search | Search-only normalized value, not authoritative display. |
| official-en | Approved English presentation. |
| official-es | Official Spanish written form. |

## `name_lifecycle`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate. |
| official-current | Current official. |
| official-historical | Historical official. |
| alternate | Alternate. |
| disputed | Disputed. |
| retired | Retired. |
| rejected | Rejected. |

## `name_status`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| alternate | Allowed alternate display/search name. |
| candidate | Suggested name. |
| disputed | Name dispute unresolved. |
| official-current | Current approved name. |
| official-historical | Previously approved name. |
| rejected | Rejected candidate. |
| retired | No longer used. |
| under-review | Name under review. |

## `non_building_object_type`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| utility-asset | Utility asset. |
| public-space | Public space. |
| delivery-point | Delivery point. |
| infrastructure-node | Infrastructure node. |
| other | Other approved object. |

## `object_role`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| access-point | Access/entrance object. |
| context-locality | Locality context. |
| context-road | Road/segment context. |
| external-parcel-reference | Optional external parcel context. |
| nearby-landmark | Landmark used for description. |
| parent-building | Parent building for unit. |
| primary-subject | Main object represented by the record version. |

## `operational_area_lifecycle`

Owner: **Operations Authority**

| Value | Meaning |
|---|---|
| planned | Planned. |
| active | Active. |
| suspended | Suspended. |
| closed | Closed. |
| archived | Archived. |

## `operational_area_type`

Owner: **Operations Authority**

| Value | Meaning |
|---|---|
| campaign | Field campaign area. |
| incident | Temporary incident/project zone. |
| rollout | Rollout sequence area. |
| routing | Intake routing area. |
| service | Service coverage area. |

## `projection_type`

Owner: **Publication Authority**

| Value | Meaning |
|---|---|
| operator-case-file | Protected operator case file. |
| partner-api | Partner-scoped API projection. |
| public-lookup | Public lookup/proof. |
| signage-export | Signage/export projection. |
| statistics | Aggregated/statistical projection. |

## `public_code_state`

Owner: **Programme Owner / Registry Authority**

| Value | Meaning |
|---|---|
| active-public | Currently released public code. |
| blocked | Reserved to prevent future use. |
| reserved-internal | Reserved but not public. |
| retired | No longer assigned to current records. |
| revoked | Invalidated by authority. |
| superseded | Replaced by a successor alias. |

## `publication_item_state`

Owner: **Publication Authority**

| Value | Meaning |
|---|---|
| included | Included in release manifest. |
| redacted | Included with redaction. |
| superseded | Replaced by later release item. |
| withdrawn | Removed from public/partner projection. |

## `publication_lifecycle`

Owner: **Publication Authority**

| Value | Meaning |
|---|---|
| approval-requested | Submitted for authority approval. |
| approved | Approved for release but not yet published. |
| draft | Release being prepared. |
| published | Published to named audience. |
| suspended | Temporarily hidden or restricted. |
| withdrawn | Release withdrawn by authority. |

## `publication_release_state`

Owner: **Publication Authority**

| Value | Meaning |
|---|---|
| approval-requested | Submitted for authority approval. |
| approved | Approved for release but not yet published. |
| draft | Release being prepared. |
| published | Published to named audience. |
| suspended | Temporarily hidden or restricted. |
| withdrawn | Release withdrawn by authority. |

## `quality_check_result`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| passed | Check passed. |
| passed-with-warning | Check passed with warning. |
| failed | Check failed. |
| not-applicable | Check not applicable. |

## `record_type`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| address | Address/location record with public/protected lookup purpose. |
| building | Building-level canonical location. |
| entrance | Separately addressable entrance/access point. |
| landmark | Landmark-based location. |
| non-building-object | Other authorized addressable object. |
| service-location | Service/delivery location not tied to building. |
| unit | Separately addressable unit/sub-address. |

## `reference_object_lifecycle`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate reference object. |
| active | Active object. |
| corrected | Corrected by later object version. |
| superseded | Superseded. |
| retired | Retired. |
| revoked | Revoked. |

## `relationship_type`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| contains | Container relationship. |
| corrects | Record/version corrects another. |
| duplicates | Potential/confirmed duplicate. |
| near | Nearby/context relationship. |
| served-by | Service/access relationship. |
| supersedes | Record replaces another. |

## `retention_state`

Owner: **Legal/Privacy Authority**

| Value | Meaning |
|---|---|
| active | Retained for active use. |
| disposed-metadata-retained | Object disposed, metadata retained. |
| legal-hold | Held by legal/audit requirement. |
| scheduled-disposal | Scheduled for disposal after approval. |

## `road_class`

Owner: **Registry/GIS Authority**

| Value | Meaning |
|---|---|
| path | Pedestrian or local path. |
| road | General road. |
| service-road | Service/access road. |
| street | Urban street. |
| track | Track/unpaved access. |
| unknown | Unknown class pending validation. |

## `road_lifecycle`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate road. |
| field-verified | Field verified road. |
| official | Official road. |
| superseded | Superseded road. |
| retired | Retired road. |

## `road_segment_lifecycle`

Owner: **GIS/Data Authority**

| Value | Meaning |
|---|---|
| draft | Draft segment. |
| active | Active segment. |
| realigned | Realigned segment. |
| retired | Retired segment. |

## `source_authority_class`

Owner: **SDA**

| Value | Meaning |
|---|---|
| citizen-submitted | Citizen submission. |
| derived-system | System-derived value. |
| external-map-suggestion | External map/geocoder suggestion. |
| fixture-training | Fixture/training data. |
| gis-data-authority | GIS/data steward. |
| imported-provisional | Imported provisional source. |
| official-government | Official government source. |
| registry-authority | Registry decision. |
| unverified-field | Unverified field observation. |
| verified-field | Verified field observation. |

## `source_authority_lifecycle`

Owner: **SDA**

| Value | Meaning |
|---|---|
| candidate | Candidate source. |
| trusted | Trusted source. |
| deprecated | Deprecated source. |
| revoked | Revoked source. |

## `subject_lifecycle`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| active | Subject can receive links. |
| retired | Subject retained but not assignable. |
| merged | Subject merged into successor. |
| deleted-prohibited | Delete attempted but policy requires retirement. |

## `unit_lifecycle`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| candidate | Candidate unit. |
| active | Active unit. |
| merged | Merged unit. |
| split | Split unit. |
| retired | Retired unit. |

## `unit_type`

Owner: **Registry Authority**

| Value | Meaning |
|---|---|
| apartment | Apartment/flat. |
| office-suite | Office suite. |
| room | Room-level unit. |
| shop-unit | Shop/commercial unit. |
| compound-unit | Compound/yard unit. |
