# Field-Level Data Dictionary

Generated from the authoritative target registry; no field-name suffix inference.

| Field | Semantic meaning | Type | Nullability | Default | Owner | Classification | Projection | Temporal behavior | Constraints |
|---|---|---|---|---|---|---|---|---|---|
| `administrative_code_history.admin_code_history_id` | Stable history row id. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | PRIMARY KEY |
| `administrative_code_history.administrative_unit_id` | Administrative identity. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_code_history.code_scheme` | Code scheme/version. | text | no | 'national-admin-code' | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_code_history.official_code` | Official code value effective for interval. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | not identity |
| `administrative_code_history.effective_from` | Effective start. | timestamptz | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_code_history.effective_to` | Effective end. | timestamptz | yes | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_code_history.recorded_from` | Recorded start. | timestamptz | no | now() | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_code_history.recorded_to` | Recorded end. | timestamptz | yes | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_code_history.source_id` | Source authority. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `administrative_unit.administrative_unit_id` | Stable opaque internal ID for an administrative unit. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit.country_id` | Owning country. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit.stable_code` | Stable official or provisional administrative code. | text | no | — | Registry Authority | government-internal | "operator" | current fact | UNIQUE within country and authority package |
| `administrative_unit.created_at` | Recorded identity creation time. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `administrative_unit.retired_at` | Recorded retirement time for the identity; historical versions remain queryable. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `administrative_unit_version.administrative_unit_version_id` | Version identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit_version.administrative_unit_id` | Administrative identity being versioned. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit_version.parent_administrative_unit_id` | Parent administrative unit; NULL for root country/province rows where permitted. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit_version.admin_level` | Administrative hierarchy level. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit_version.lifecycle_state` | Version lifecycle state. | text | no | 'active' | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit_version.effective_from` | Time this version became legally/effectively valid. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `administrative_unit_version.effective_to` | Exclusive end of legal/effective interval. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `administrative_unit_version.recorded_at` | When the system recorded this version. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `administrative_unit_version.recorded_to` | When this recorded version was closed; NULL is the sole authoritative current-version mechanism. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | one recorded_to IS NULL version per administrative_unit_id |
| `administrative_unit_version.source_authority_id` | Authority for this hierarchy/status version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `administrative_unit_version.classification` | Visibility classification for this version. | text | no | 'public-after-release' | Registry Authority | government-internal | "operator" | current fact | — |
| `building.building_id` | Building identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building.usage_class` | Building usage class where known. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building.lifecycle_state` | Building lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building.source_authority_id` | Building source/authority. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building.effective_from` | Building effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `building.effective_to` | Building effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `building_primary_entrance.building_primary_entrance_id` | Assignment identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building_primary_entrance.building_id` | Building. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building_primary_entrance.entrance_id` | Primary entrance. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `building_primary_entrance.effective_from` | Primary assignment start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `building_primary_entrance.effective_to` | Primary assignment end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `correction_case.correction_case_id` | Correction case identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `correction_case.target_location_record_id` | Target record, if resolved. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `correction_case.target_public_code` | Submitted/target public code, if applicable. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `correction_case.correction_type` | Correction type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `correction_case.case_state` | Correction case state. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `correction_case.submitted_at` | Submission time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `correction_case.resolved_at` | Resolution time. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `correction_case.resolution_event_id` | Decision resolving case. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `country.country_id` | Stable internal country identifier. | text | no | — | Registry Authority | government-internal | "operator" | current fact | ULID-compatible text or reserved country key |
| `country.iso2_code` | ISO-3166 alpha-2 country code. | char(2) | no | — | Registry Authority | government-internal | "operator" | current fact | UNIQUE; CHECK iso2_code = upper(iso2_code) |
| `country.official_name_es` | Official Spanish country name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `country.official_name_en` | Approved English presentation name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `country.lifecycle_state` | Reference lifecycle state. | text | no | 'active' | Registry Authority | government-internal | "operator" | current fact | — |
| `country.source_authority_id` | Authority that issued this country reference. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `country.created_at` | Recorded creation time. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `decision_event.decision_event_id` | Decision event identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `decision_event.decision_type` | Decision type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `decision_event.actor_id` | Actor/system making decision. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `decision_event.authority_id` | Responsible authority. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `decision_event.reason_code` | Controlled or authority reason code. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `decision_event.details_json` | Supplemental non-authoritative details. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `decision_event.effective_at` | Decision effective time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `decision_event.recorded_at` | Decision recorded time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `dispute_case.dispute_case_id` | Dispute identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `dispute_case.target_entity` | Target entity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `dispute_case.target_id` | Target ID. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `dispute_case.dispute_type` | Dispute type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `dispute_case.case_state` | Dispute state. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `dispute_case.opened_at` | Opened time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `dispute_case.resolved_at` | Resolved time. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `dispute_case.resolution_event_id` | Resolution decision. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `entrance.entrance_id` | Entrance identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `entrance.building_id` | Building served by entrance. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `entrance.entrance_role` | Entrance/access role. Review 03 correction: uses entity-specific vocabulary. | text | no | 'access-point' | Registry Authority | government-internal | "operator" | current fact | — |
| `entrance.lifecycle_state` | Entrance lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `entrance.effective_from` | Entrance effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `entrance.effective_to` | Entrance effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `evidence_object.evidence_object_id` | Evidence identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `evidence_object.source_record_id` | Source record for evidence. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `evidence_object.storage_uri` | Object-storage URI/key/version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `evidence_object.content_hash` | Content hash. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `evidence_object.media_type` | MIME/media type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `evidence_object.classification` | Evidence classification. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `evidence_object.captured_at` | Capture time where known. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | observed time | — |
| `evidence_object.retention_state` | Retention/legal-hold state. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.assignment_id` | Assignment identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.operational_area_id` | Operational area for assignment. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.task_type` | Task type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.team` | Team label or ID. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.priority` | Priority. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.assignment_state` | Assignment/verification state. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_assignment.created_at` | Assignment creation. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `field_assignment.closed_at` | Assignment closure. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `field_observation.field_observation_id` | Observation identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.intake_case_id` | Related intake case. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.assignment_id` | Related assignment. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.observation_type` | Observed thing/type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.verification_state` | Verification lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.source_record_id` | Source record for observation. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.geometry_observation_id` | Captured geometry observation. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.notes_classification` | Classification of notes/details. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `field_observation.recorded_at` | Recorded time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `geometry_observation.geometry_observation_id` | Observation identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.subject_hint_entity` | Optional intended subject entity before approval. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.subject_hint_id` | Optional intended subject ID before approval. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.observed_geom` | Observed source geometry in EPSG:4326. | geometry(Geometry,4326) | no | — | Registry Authority | government-internal | "operator" | current fact | CHECK ST_SRID(observed_geom)=4326; CHECK ST_IsValid(observed_geom) |
| `geometry_observation.geometry_role` | Intended role of geometry. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.capture_method` | Capture/source method. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.horizontal_accuracy_m` | Horizontal accuracy/uncertainty in meters. | numeric(10,2) | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.source_record_id` | Source record carrying the observation. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.evidence_object_id` | Supporting evidence object. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.licence_id` | Licence governing the source geometry. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_observation.observed_at` | Capture/observation time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | observed time | — |
| `geometry_observation.recorded_at` | Recorded time. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `geometry_observation.classification` | Observation classification. | text | no | 'restricted' | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.quality_assessment_id` | Assessment identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.geometry_version_id` | Assessed geometry version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.check_name` | Quality check name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.check_result` | Result value. Review 03 correction: uses entity-specific vocabulary. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.tolerance_json` | Tolerance/config used. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.measured_value_json` | Measured results. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_quality_assessment.assessed_at` | Assessment time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `geometry_quality_assessment.assessed_by_actor_id` | Actor/system running assessment. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.transformation_id` | Transformation identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.source_crs` | Original CRS. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.target_crs` | Target CRS; normally EPSG:4326. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.algorithm` | Transformation algorithm/library. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.algorithm_version` | Algorithm/library version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.parameters_json` | Transformation parameters. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_transformation.performed_at` | Transformation time. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `geometry_version.geometry_version_id` | Approved geometry version identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.subject_entity` | Approved subject table. | text | no | — | Registry Authority | government-internal | "operator" | current fact | CHECK subject_entity allowed for geometry_role |
| `geometry_version.subject_id` | Approved subject ID validated by subject_entity rule. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.geometry_role` | Geometry role. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.geom` | Approved geometry. | geometry(Geometry,4326) | no | — | Registry Authority | government-internal | "operator" | current fact | CHECK ST_SRID(geom)=4326; CHECK ST_IsValid(geom); CHECK GeometryType(geom) allowed for geometry_role |
| `geometry_version.source_observation_id` | Source observation promoted to approved geometry. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.transformation_id` | Transformation lineage, if geometry was transformed/derived. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.validation_method` | Validation method or rule set. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.validated_by_actor_id` | Actor/system approving geometry. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.quality_state` | Geometry quality/lifecycle state. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.effective_from` | Geometry effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `geometry_version.effective_to` | Geometry effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `geometry_version.recorded_at` | Recorded approval time. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `geometry_version.recorded_to` | Recorded closure time; NULL means current approved version for subject/role. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | one recorded_to IS NULL per subject_entity, subject_id, geometry_role |
| `geometry_version.superseded_by_geometry_version_id` | Later geometry version that supersedes this one. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.dispute_case_id` | Active/resolved dispute case if applicable. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `geometry_version.classification` | Geometry classification. | text | no | 'restricted' | Registry Authority | government-internal | "operator" | current fact | — |
| `intake_case.intake_case_id` | Intake case identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `intake_case.source_record_id` | Source submission/import record. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `intake_case.submitted_label` | Submitted address/location label. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `intake_case.intake_state` | Intake lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `intake_case.provisional_code` | Offline/grid/provisional code, not canonical public code. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `intake_case.created_at` | Case creation time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `intake_case.closed_at` | Case closure time. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `landmark.landmark_id` | Landmark identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `landmark.landmark_type` | Landmark type. Review 03 correction: uses entity-specific vocabulary. | text | no | 'landmark' | Registry Authority | government-internal | "operator" | current fact | — |
| `landmark.lifecycle_state` | Landmark lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `landmark.source_authority_id` | Landmark source. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `landmark.effective_from` | Landmark effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `landmark.effective_to` | Landmark effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `legacy_crosswalk.legacy_crosswalk_id` | Stable crosswalk row id. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | PRIMARY KEY |
| `legacy_crosswalk.source_table` | Current source table name. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `legacy_crosswalk.source_field` | Current source field name. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `legacy_crosswalk.legacy_id` | Current source primary or natural key value. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `legacy_crosswalk.target_entity` | Target entity name. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `legacy_crosswalk.target_id` | Target row identifier. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `legacy_crosswalk.created_at` | Crosswalk creation time. | timestamptz | no | now() | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `licence.licence_id` | Licence identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `licence.licence_name` | Licence name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `licence.licence_uri` | Licence URL/reference. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `licence.usage_restriction` | Usage/publication restrictions. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `licence.classification` | Licence metadata classification. | text | no | 'government-internal' | Registry Authority | government-internal | "operator" | current fact | — |
| `locality.locality_id` | Locality identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `locality.administrative_unit_id` | Containing or governing administrative unit. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `locality.locality_type` | Locality type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `locality.lifecycle_state` | Locality lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `locality.source_authority_id` | Locality source/authority. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `locality.effective_from` | Locality effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `locality.effective_to` | Locality effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record.location_record_id` | Canonical record identity; never reused. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record.record_type` | Record type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record.created_at` | Record creation time. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `location_record.retired_at` | Record retirement time, if identity retired. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `location_record.classification` | Maximum classification for the record identity. | text | no | 'government-internal' | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.assertion_id` | Assertion identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.location_record_version_id` | Version containing asserted fact. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.target_entity` | Target entity for asserted field. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.target_field` | Target field name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.value_json` | Typed value snapshot or redacted marker. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.source_record_id` | Source record supporting assertion. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.evidence_object_id` | Evidence object supporting assertion. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.decision_event_id` | Decision authorizing assertion. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_assertion.classification` | Assertion classification. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_object_link.link_id` | Object link identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_object_link.location_record_version_id` | Version that owns the link. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_object_link.object_entity` | Linked object table. | text | no | — | Registry Authority | government-internal | "operator" | current fact | CHECK object_entity in allowed object subjects |
| `location_record_object_link.object_id` | Linked object ID; checked by object-role validation. | text | no | — | Registry Authority | government-internal | "operator" | current fact | validated by object_entity-specific rule |
| `location_record_object_link.object_role` | Role of object for this record version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_object_link.cardinality_rank` | Rank/order where multiple links have same role. | integer | no | 1 | Registry Authority | government-internal | "operator" | current fact | UNIQUE(location_record_version_id, object_role, cardinality_rank) |
| `location_record_object_link.effective_from` | Link effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record_object_link.effective_to` | Link effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record_relationship.relationship_id` | Relationship identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_relationship.from_location_record_id` | Source record. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_relationship.to_location_record_id` | Target record. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_relationship.relationship_type` | Relationship type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_relationship.effective_from` | Relationship effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record_relationship.effective_to` | Relationship effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record_relationship.source_decision_event_id` | Decision event authorizing relationship. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.location_record_version_id` | Version identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.location_record_id` | Canonical record being versioned. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.version_number` | Monotonic per-record version number. | integer | no | — | Registry Authority | government-internal | "operator" | current fact | UNIQUE(location_record_id, version_number) |
| `location_record_version.lifecycle_state` | Registry lifecycle state for this version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.display_label_es` | Spanish display label for this version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.display_label_en` | English display label where approved. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.administrative_unit_version_id` | Effective administrative context version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.locality_id` | Optional locality context. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.effective_from` | Official effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record_version.effective_to` | Official effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `location_record_version.recorded_at` | Recorded transaction start. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `location_record_version.recorded_to` | Recorded transaction end; NULL is the single current-version mechanism. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | one recorded_to IS NULL per location_record_id |
| `location_record_version.predecessor_version_id` | Optional prior version in correction/supersession chain. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.successor_version_id` | Optional later version once superseded/corrected. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.correction_case_id` | Correction case that produced this version, if applicable. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.supersession_reason` | Reason for supersession/correction/retirement. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `location_record_version.source_decision_event_id` | Decision event authorizing this version. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.migration_exception_id` | Exception identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.batch_id` | Migration/backfill batch. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.source_table` | Source table. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.source_field` | Source field. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.source_key` | Source record key. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.exception_type` | Exception type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.severity` | Severity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.details_json` | Details. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.owner` | Responsible owner. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.created_at` | Exception creation. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | current fact | — |
| `migration_exception.resolved_at` | Resolution time. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.name_record_id` | Name row identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.subject_entity` | Named entity table. | text | no | — | Registry Authority | government-internal | "operator" | current fact | CHECK subject_entity in configured named subjects |
| `name_record.subject_id` | Named entity ID; validated by subject registry/checks in WO-002B. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.language_code` | BCP-47 language code, e.g. es-GQ or en. | text | no | — | Registry Authority | government-internal | "operator" | current fact | CHECK language_code <> '' |
| `name_record.name_kind` | Kind of name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.name_status` | Name lifecycle status. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.name_text` | Authoritative or candidate written name preserving accents/spelling. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.normalized_text` | Search-only normalized form; never replaces name_text. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.source_record_id` | Source/evidence for the name. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `name_record.effective_from` | Name effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `name_record.effective_to` | Name effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `non_building_object.object_id` | Object identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `non_building_object.object_type` | Object type. Review 03 correction: uses entity-specific vocabulary. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `non_building_object.lifecycle_state` | Object lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `non_building_object.source_authority_id` | Object source. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `non_building_object.effective_from` | Object effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `non_building_object.effective_to` | Object effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `operational_area.operational_area_id` | Operational area identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area.area_type` | Purpose class. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area.name_record_id` | Optional display name. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area.purpose` | Operational purpose statement. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area.lifecycle_state` | Operational area lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area.authority_owner` | Named operational owner. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area.effective_from` | Operational effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `operational_area.effective_to` | Operational effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `operational_area.classification` | Area visibility classification. | text | no | 'government-internal' | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area_coverage.coverage_id` | Coverage row identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area_coverage.operational_area_id` | Operational area. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area_coverage.administrative_unit_id` | Administrative unit covered, if applicable. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area_coverage.geometry_version_id` | Operational boundary geometry, if applicable. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area_coverage.coverage_role` | Coverage role. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `operational_area_coverage.effective_from` | Coverage start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `operational_area_coverage.effective_to` | Coverage end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `parcel_reference.parcel_reference_id` | Parcel reference identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `parcel_reference.external_parcel_id` | External source parcel identifier. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `parcel_reference.source_authority_id` | External parcel authority/source. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `parcel_reference.classification` | Parcel reference classification. | text | no | 'restricted' | Registry Authority | government-internal | "operator" | current fact | — |
| `parcel_reference.effective_from` | Reference effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `parcel_reference.effective_to` | Reference effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `partner_projection.partner_projection_id` | Projection identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `partner_projection.publication_release_item_id` | Release item being projected. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `partner_projection.partner_scope` | Partner/institution/use-case scope. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `partner_projection.response_field_set` | Allowlisted response fields. | jsonb | no | '[]'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `partner_projection.classification` | Projection classification. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `partner_projection.expires_at` | Projection expiry. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `public_code_alias.public_code_alias_id` | Alias identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `public_code_alias.location_record_id` | Record owning the alias. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `public_code_alias.public_code` | Human public code. Grammar remains RFI-controlled. | text | no | — | Registry Authority | government-internal | "operator" | current fact | UNIQUE; not reused for another location_record_id |
| `public_code_alias.code_scheme` | Code scheme/version. | text | no | 'nli-reserved-v1' | Registry Authority | government-internal | "operator" | current fact | — |
| `public_code_alias.code_state` | Alias lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `public_code_alias.reserved_at` | Reservation time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `public_code_alias.issued_at` | Public issue time. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `public_code_alias.retired_at` | Retirement time. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `public_code_alias.predecessor_alias_id` | Prior alias if superseded. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `public_code_alias.successor_alias_id` | Successor alias after supersession. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.publication_release_id` | Release identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.release_state` | Release lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.authority_reference` | Named approval/authority reference. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.projection_type` | Projection audience/type. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.effective_at` | Release effective time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `publication_release.recorded_at` | Release recorded time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `publication_release.immutable_manifest_hash` | Hash of full release manifest. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.manifest_storage_uri` | Durable complete projection/manifest artifact reference. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release.created_by_actor_id` | Actor/system creating release. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.publication_release_item_id` | Release item identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.publication_release_id` | Release header. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.location_record_id` | Canonical record identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.location_record_version_id` | Exact version released. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.public_code_alias_id` | Exact alias released. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.projection_payload_json` | Complete immutable public/partner/export payload snapshot. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.projection_payload_hash` | Hash of immutable payload. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.projection_state` | Release item state. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.published_label` | Exact label released. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `publication_release_item.published_geometry_policy` | Geometry precision/generalization policy for release. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `registry_subject.subject_id` | Stable ULID-compatible subject identifier. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | PRIMARY KEY; ULID-compatible |
| `registry_subject.subject_entity` | Allowed target entity name. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | CHECK subject_entity in allowed subject set |
| `registry_subject.subject_native_id` | ID in the subject entity table. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | validated by subject trigger |
| `registry_subject.created_at` | Recorded creation time. | timestamptz | no | now() | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `road.road_id` | Road identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road.road_class` | Road class. | text | no | 'unknown' | Registry Authority | government-internal | "operator" | current fact | — |
| `road.lifecycle_state` | Road lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road.source_authority_id` | Road authority/source. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road.created_at` | Recorded creation. | timestamptz | no | now() | Registry Authority | government-internal | "operator" | recorded time | — |
| `road_segment.road_segment_id` | Segment identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road_segment.road_id` | Owning road. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road_segment.sequence_number` | Optional ordering within road. | integer | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road_segment.measured_length_m` | Measured length in meters; NULL until geometry validated. | numeric(12,2) | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road_segment.lifecycle_state` | Segment lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `road_segment.effective_from` | Segment effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `road_segment.effective_to` | Segment effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
| `source_authority.source_authority_id` | Authority identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_authority.authority_name` | Authority name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_authority.authority_class` | Authority class. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_authority.legal_basis` | Legal/institutional basis if known. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_authority.status` | Authority lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_package.source_package_id` | Package identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_package.source_authority_id` | Package authority. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_package.package_name` | Package name. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_package.package_checksum` | Package checksum. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_package.licence_id` | Licence for package. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_package.loaded_at` | Load time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `source_package.load_context` | Controlled load context. | jsonb | no | '{}'::jsonb | Registry Authority | government-internal | "operator" | current fact | — |
| `source_payload_archive.archive_id` | Archive object id. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | PRIMARY KEY |
| `source_payload_archive.source_record_id` | Source record. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `source_payload_archive.payload_uri` | Controlled encrypted object/storage URI. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `source_payload_archive.payload_hash_sha256` | Integrity hash for archived payload. | text | no | — | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `source_payload_archive.classification` | Payload classification. | text | no | 'restricted' | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `source_payload_archive.retention_state` | Retention state. | text | no | 'active' | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `source_payload_archive.created_at` | Archive creation time. | timestamptz | no | now() | SDA/Registry Authority | government-internal | {"operator": "allowed by role", "public": "never unless released"} | recorded-time governed | — |
| `source_record.source_record_id` | Source record identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_record.source_package_id` | Owning package. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_record.source_key` | Source system key. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_record.raw_payload_hash` | Hash of raw source payload. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_record.raw_payload_classification` | Raw source classification. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `source_record.recorded_at` | Recorded time. | timestamptz | no | — | Registry Authority | government-internal | "operator" | recorded time | — |
| `unit.unit_id` | Unit identity. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.building_id` | Parent building. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.parent_unit_id` | Optional parent unit for nested units. | text | yes | — | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.unit_label` | Human-readable unit label. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.unit_type` | Unit type. Review 03 correction: uses entity-specific vocabulary. | text | no | 'unit' | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.lifecycle_state` | Unit lifecycle. | text | no | — | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.classification` | Unit visibility classification. | text | no | 'government-internal' | Registry Authority | government-internal | "operator" | current fact | — |
| `unit.effective_from` | Unit effective start. | timestamptz | no | — | Registry Authority | government-internal | "operator" | effective time | — |
| `unit.effective_to` | Unit effective end. | timestamptz | yes | — | Registry Authority | government-internal | "operator" | effective time | — |
