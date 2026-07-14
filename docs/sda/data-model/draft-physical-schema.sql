-- NLI-WO-002 NON-EXECUTABLE DESIGN ARTIFACT
-- DO NOT APPLY. DO NOT COPY TO infra/migrations.
-- PostgreSQL/PostGIS typed physical proposal generated from target-model.json.

CREATE TABLE proposed_country (
  country_id text NOT NULL,
  iso2_code char(2) NOT NULL,
  official_name_es text NOT NULL,
  official_name_en text NOT NULL,
  lifecycle_state text NOT NULL DEFAULT 'active',
  source_authority_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_country_pk PRIMARY KEY (country_id),
  CONSTRAINT proposed_country_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_country_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_administrative_unit (
  administrative_unit_id text NOT NULL,
  country_id text NOT NULL,
  stable_code text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  retired_at timestamptz,
  CONSTRAINT proposed_administrative_unit_pk PRIMARY KEY (administrative_unit_id),
  CONSTRAINT proposed_administrative_unit_country_id_fk FOREIGN KEY (country_id) REFERENCES proposed_country(country_id)
);

CREATE TABLE proposed_administrative_unit_version (
  administrative_unit_version_id text NOT NULL,
  administrative_unit_id text NOT NULL,
  parent_administrative_unit_id text,
  admin_level text NOT NULL,
  lifecycle_state text NOT NULL DEFAULT 'active',
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  source_authority_id text NOT NULL,
  classification text NOT NULL DEFAULT 'public-after-release',
  CONSTRAINT proposed_administrative_unit_version_pk PRIMARY KEY (administrative_unit_version_id),
  CONSTRAINT proposed_administrative_unit_version_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id),
  CONSTRAINT proposed_administrative_unit_version_parent_administrative_unit_id_fk FOREIGN KEY (parent_administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id),
  CONSTRAINT proposed_administrative_unit_version_admin_level_vocab_ck CHECK (admin_level IN ('country', 'province', 'district', 'municipality', 'local_council')),
  CONSTRAINT proposed_administrative_unit_version_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_administrative_unit_version_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id),
  CONSTRAINT proposed_administrative_unit_version_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_name_record (
  name_record_id text NOT NULL,
  subject_entity text NOT NULL,
  subject_id text NOT NULL,
  language_code text NOT NULL,
  name_kind text NOT NULL,
  name_status text NOT NULL,
  name_text text NOT NULL,
  normalized_text text NOT NULL,
  source_record_id text,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_name_record_pk PRIMARY KEY (name_record_id),
  CONSTRAINT proposed_name_record_name_kind_vocab_ck CHECK (name_kind IN ('official-es', 'official-en', 'local', 'alternate', 'historical', 'normalized-search')),
  CONSTRAINT proposed_name_record_name_status_vocab_ck CHECK (name_status IN ('candidate', 'under-review', 'official-current', 'official-historical', 'alternate', 'retired', 'rejected', 'disputed')),
  CONSTRAINT proposed_name_record_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id)
);

CREATE TABLE proposed_operational_area (
  operational_area_id text NOT NULL,
  area_type text NOT NULL,
  name_record_id text,
  purpose text NOT NULL,
  lifecycle_state text NOT NULL,
  authority_owner text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  classification text NOT NULL DEFAULT 'government-internal',
  CONSTRAINT proposed_operational_area_pk PRIMARY KEY (operational_area_id),
  CONSTRAINT proposed_operational_area_area_type_vocab_ck CHECK (area_type IN ('campaign', 'routing', 'rollout', 'service', 'incident')),
  CONSTRAINT proposed_operational_area_name_record_id_fk FOREIGN KEY (name_record_id) REFERENCES proposed_name_record(name_record_id),
  CONSTRAINT proposed_operational_area_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_operational_area_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_operational_area_coverage (
  coverage_id text NOT NULL,
  operational_area_id text NOT NULL,
  administrative_unit_id text,
  geometry_version_id text,
  coverage_role text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_operational_area_coverage_pk PRIMARY KEY (coverage_id),
  CONSTRAINT proposed_operational_area_coverage_operational_area_id_fk FOREIGN KEY (operational_area_id) REFERENCES proposed_operational_area(operational_area_id),
  CONSTRAINT proposed_operational_area_coverage_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id),
  CONSTRAINT proposed_operational_area_coverage_geometry_version_id_fk FOREIGN KEY (geometry_version_id) REFERENCES proposed_geometry_version(geometry_version_id),
  CONSTRAINT proposed_operational_area_coverage_coverage_role_vocab_ck CHECK (coverage_role IN ('primary', 'partial', 'excluded', 'context'))
);

CREATE TABLE proposed_road (
  road_id text NOT NULL,
  road_class text NOT NULL DEFAULT 'unknown',
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_road_pk PRIMARY KEY (road_id),
  CONSTRAINT proposed_road_road_class_vocab_ck CHECK (road_class IN ('road', 'street', 'track', 'path', 'service-road', 'unknown')),
  CONSTRAINT proposed_road_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_road_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_road_segment (
  road_segment_id text NOT NULL,
  road_id text NOT NULL,
  sequence_number integer,
  measured_length_m numeric(12,2),
  lifecycle_state text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_road_segment_pk PRIMARY KEY (road_segment_id),
  CONSTRAINT proposed_road_segment_road_id_fk FOREIGN KEY (road_id) REFERENCES proposed_road(road_id),
  CONSTRAINT proposed_road_segment_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked'))
);

CREATE TABLE proposed_parcel_reference (
  parcel_reference_id text NOT NULL,
  external_parcel_id text NOT NULL,
  source_authority_id text NOT NULL,
  classification text NOT NULL DEFAULT 'restricted',
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_parcel_reference_pk PRIMARY KEY (parcel_reference_id),
  CONSTRAINT proposed_parcel_reference_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id),
  CONSTRAINT proposed_parcel_reference_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_building (
  building_id text NOT NULL,
  usage_class text,
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_building_pk PRIMARY KEY (building_id),
  CONSTRAINT proposed_building_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_building_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_entrance (
  entrance_id text NOT NULL,
  building_id text NOT NULL,
  entrance_role text NOT NULL DEFAULT 'access-point',
  lifecycle_state text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_entrance_pk PRIMARY KEY (entrance_id),
  CONSTRAINT proposed_entrance_building_id_fk FOREIGN KEY (building_id) REFERENCES proposed_building(building_id),
  CONSTRAINT proposed_entrance_entrance_role_vocab_ck CHECK (entrance_role IN ('primary-subject', 'access-point', 'context-road', 'context-locality', 'nearby-landmark', 'parent-building', 'external-parcel-reference')),
  CONSTRAINT proposed_entrance_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked'))
);

CREATE TABLE proposed_building_primary_entrance (
  building_primary_entrance_id text NOT NULL,
  building_id text NOT NULL,
  entrance_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_building_primary_entrance_pk PRIMARY KEY (building_primary_entrance_id),
  CONSTRAINT proposed_building_primary_entrance_building_id_fk FOREIGN KEY (building_id) REFERENCES proposed_building(building_id),
  CONSTRAINT proposed_building_primary_entrance_entrance_id_fk FOREIGN KEY (entrance_id) REFERENCES proposed_entrance(entrance_id)
);

CREATE TABLE proposed_unit (
  unit_id text NOT NULL,
  building_id text NOT NULL,
  parent_unit_id text,
  unit_label text NOT NULL,
  unit_type text NOT NULL DEFAULT 'unit',
  lifecycle_state text NOT NULL,
  classification text NOT NULL DEFAULT 'government-internal',
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_unit_pk PRIMARY KEY (unit_id),
  CONSTRAINT proposed_unit_building_id_fk FOREIGN KEY (building_id) REFERENCES proposed_building(building_id),
  CONSTRAINT proposed_unit_parent_unit_id_fk FOREIGN KEY (parent_unit_id) REFERENCES proposed_unit(unit_id),
  CONSTRAINT proposed_unit_unit_type_vocab_ck CHECK (unit_type IN ('address', 'building', 'unit', 'entrance', 'landmark', 'non-building-object', 'service-location')),
  CONSTRAINT proposed_unit_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_unit_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_landmark (
  landmark_id text NOT NULL,
  landmark_type text NOT NULL DEFAULT 'landmark',
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_landmark_pk PRIMARY KEY (landmark_id),
  CONSTRAINT proposed_landmark_landmark_type_vocab_ck CHECK (landmark_type IN ('address', 'building', 'unit', 'entrance', 'landmark', 'non-building-object', 'service-location')),
  CONSTRAINT proposed_landmark_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_landmark_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_locality (
  locality_id text NOT NULL,
  administrative_unit_id text NOT NULL,
  locality_type text NOT NULL,
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_locality_pk PRIMARY KEY (locality_id),
  CONSTRAINT proposed_locality_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id),
  CONSTRAINT proposed_locality_locality_type_vocab_ck CHECK (locality_type IN ('settlement', 'neighbourhood', 'village', 'quarter', 'informal_area')),
  CONSTRAINT proposed_locality_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_locality_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_non_building_object (
  object_id text NOT NULL,
  object_type text NOT NULL,
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_non_building_object_pk PRIMARY KEY (object_id),
  CONSTRAINT proposed_non_building_object_object_type_vocab_ck CHECK (object_type IN ('address', 'building', 'unit', 'entrance', 'landmark', 'non-building-object', 'service-location')),
  CONSTRAINT proposed_non_building_object_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_non_building_object_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_location_record (
  location_record_id text NOT NULL,
  record_type text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  retired_at timestamptz,
  classification text NOT NULL DEFAULT 'government-internal',
  CONSTRAINT proposed_location_record_pk PRIMARY KEY (location_record_id),
  CONSTRAINT proposed_location_record_record_type_vocab_ck CHECK (record_type IN ('address', 'building', 'unit', 'entrance', 'landmark', 'non-building-object', 'service-location')),
  CONSTRAINT proposed_location_record_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_location_record_version (
  location_record_version_id text NOT NULL,
  location_record_id text NOT NULL,
  version_number integer NOT NULL,
  lifecycle_state text NOT NULL,
  display_label_es text NOT NULL,
  display_label_en text,
  administrative_unit_version_id text NOT NULL,
  locality_id text,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  predecessor_version_id text,
  successor_version_id text,
  correction_case_id text,
  supersession_reason text,
  source_decision_event_id text NOT NULL,
  CONSTRAINT proposed_location_record_version_pk PRIMARY KEY (location_record_version_id),
  CONSTRAINT proposed_location_record_version_location_record_id_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id),
  CONSTRAINT proposed_location_record_version_lifecycle_state_vocab_ck CHECK (lifecycle_state IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked')),
  CONSTRAINT proposed_location_record_version_administrative_unit_version_id_fk FOREIGN KEY (administrative_unit_version_id) REFERENCES proposed_administrative_unit_version(administrative_unit_version_id),
  CONSTRAINT proposed_location_record_version_locality_id_fk FOREIGN KEY (locality_id) REFERENCES proposed_locality(locality_id),
  CONSTRAINT proposed_location_record_version_predecessor_version_id_fk FOREIGN KEY (predecessor_version_id) REFERENCES proposed_location_record_version(location_record_version_id),
  CONSTRAINT proposed_location_record_version_successor_version_id_fk FOREIGN KEY (successor_version_id) REFERENCES proposed_location_record_version(location_record_version_id),
  CONSTRAINT proposed_location_record_version_correction_case_id_fk FOREIGN KEY (correction_case_id) REFERENCES proposed_correction_case(correction_case_id),
  CONSTRAINT proposed_location_record_version_source_decision_event_id_fk FOREIGN KEY (source_decision_event_id) REFERENCES proposed_decision_event(decision_event_id)
);

CREATE TABLE proposed_location_record_object_link (
  link_id text NOT NULL,
  location_record_version_id text NOT NULL,
  object_entity text NOT NULL,
  object_id text NOT NULL,
  object_role text NOT NULL,
  cardinality_rank integer NOT NULL DEFAULT 1,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_location_record_object_link_pk PRIMARY KEY (link_id),
  CONSTRAINT proposed_location_record_object_link_location_record_version_id_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id),
  CONSTRAINT proposed_location_record_object_link_object_role_vocab_ck CHECK (object_role IN ('primary-subject', 'access-point', 'context-road', 'context-locality', 'nearby-landmark', 'parent-building', 'external-parcel-reference'))
);

CREATE TABLE proposed_location_record_relationship (
  relationship_id text NOT NULL,
  from_location_record_id text NOT NULL,
  to_location_record_id text NOT NULL,
  relationship_type text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  source_decision_event_id text NOT NULL,
  CONSTRAINT proposed_location_record_relationship_pk PRIMARY KEY (relationship_id),
  CONSTRAINT proposed_location_record_relationship_from_location_record_id_fk FOREIGN KEY (from_location_record_id) REFERENCES proposed_location_record(location_record_id),
  CONSTRAINT proposed_location_record_relationship_to_location_record_id_fk FOREIGN KEY (to_location_record_id) REFERENCES proposed_location_record(location_record_id),
  CONSTRAINT proposed_location_record_relationship_relationship_type_vocab_ck CHECK (relationship_type IN ('supersedes', 'corrects', 'duplicates', 'contains', 'served-by', 'near')),
  CONSTRAINT proposed_location_record_relationship_source_decision_event_id_fk FOREIGN KEY (source_decision_event_id) REFERENCES proposed_decision_event(decision_event_id)
);

CREATE TABLE proposed_public_code_alias (
  public_code_alias_id text NOT NULL,
  location_record_id text NOT NULL,
  public_code text NOT NULL,
  code_scheme text NOT NULL DEFAULT 'nli-reserved-v1',
  code_state text NOT NULL,
  reserved_at timestamptz NOT NULL,
  issued_at timestamptz,
  retired_at timestamptz,
  predecessor_alias_id text,
  successor_alias_id text,
  CONSTRAINT proposed_public_code_alias_pk PRIMARY KEY (public_code_alias_id),
  CONSTRAINT proposed_public_code_alias_location_record_id_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id),
  CONSTRAINT proposed_public_code_alias_code_state_vocab_ck CHECK (code_state IN ('reserved-internal', 'active-public', 'superseded', 'retired', 'revoked', 'blocked')),
  CONSTRAINT proposed_public_code_alias_predecessor_alias_id_fk FOREIGN KEY (predecessor_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id),
  CONSTRAINT proposed_public_code_alias_successor_alias_id_fk FOREIGN KEY (successor_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id)
);

CREATE TABLE proposed_geometry_observation (
  geometry_observation_id text NOT NULL,
  subject_hint_entity text,
  subject_hint_id text,
  observed_geom geometry(Geometry,4326) NOT NULL,
  geometry_role text NOT NULL,
  capture_method text NOT NULL,
  horizontal_accuracy_m numeric(10,2),
  source_record_id text NOT NULL,
  evidence_object_id text,
  licence_id text,
  observed_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  classification text NOT NULL DEFAULT 'restricted',
  CONSTRAINT proposed_geometry_observation_pk PRIMARY KEY (geometry_observation_id),
  CONSTRAINT proposed_geometry_observation_geometry_role_vocab_ck CHECK (geometry_role IN ('admin-boundary', 'operational-boundary', 'road-centerline', 'building-footprint', 'building-point', 'entrance-point', 'location-point', 'landmark-point', 'landmark-area', 'parcel-boundary')),
  CONSTRAINT proposed_geometry_observation_capture_method_vocab_ck CHECK (capture_method IN ('browser-gps', 'field-device-gps', 'manual-map-point', 'imported-geometry', 'derived-from-source', 'surveyed')),
  CONSTRAINT proposed_geometry_observation_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id),
  CONSTRAINT proposed_geometry_observation_evidence_object_id_fk FOREIGN KEY (evidence_object_id) REFERENCES proposed_evidence_object(evidence_object_id),
  CONSTRAINT proposed_geometry_observation_licence_id_fk FOREIGN KEY (licence_id) REFERENCES proposed_licence(licence_id),
  CONSTRAINT proposed_geometry_observation_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_geometry_version (
  geometry_version_id text NOT NULL,
  subject_entity text NOT NULL,
  subject_id text NOT NULL,
  geometry_role text NOT NULL,
  geom geometry(Geometry,4326) NOT NULL,
  source_observation_id text NOT NULL,
  transformation_id text,
  validation_method text NOT NULL,
  validated_by_actor_id text NOT NULL,
  quality_state text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  superseded_by_geometry_version_id text,
  dispute_case_id text,
  classification text NOT NULL DEFAULT 'restricted',
  CONSTRAINT proposed_geometry_version_pk PRIMARY KEY (geometry_version_id),
  CONSTRAINT proposed_geometry_version_geometry_role_vocab_ck CHECK (geometry_role IN ('admin-boundary', 'operational-boundary', 'road-centerline', 'building-footprint', 'building-point', 'entrance-point', 'location-point', 'landmark-point', 'landmark-area', 'parcel-boundary')),
  CONSTRAINT proposed_geometry_version_source_observation_id_fk FOREIGN KEY (source_observation_id) REFERENCES proposed_geometry_observation(geometry_observation_id),
  CONSTRAINT proposed_geometry_version_transformation_id_fk FOREIGN KEY (transformation_id) REFERENCES proposed_geometry_transformation(transformation_id),
  CONSTRAINT proposed_geometry_version_quality_state_vocab_ck CHECK (quality_state IN ('observed', 'quality-checked', 'reviewed', 'accepted-canonical', 'valid-with-warning', 'rejected', 'disputed', 'superseded')),
  CONSTRAINT proposed_geometry_version_superseded_by_geometry_version_id_fk FOREIGN KEY (superseded_by_geometry_version_id) REFERENCES proposed_geometry_version(geometry_version_id),
  CONSTRAINT proposed_geometry_version_dispute_case_id_fk FOREIGN KEY (dispute_case_id) REFERENCES proposed_dispute_case(dispute_case_id),
  CONSTRAINT proposed_geometry_version_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_geometry_transformation (
  transformation_id text NOT NULL,
  source_crs text NOT NULL,
  target_crs text NOT NULL,
  algorithm text NOT NULL,
  algorithm_version text NOT NULL,
  parameters_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  performed_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_geometry_transformation_pk PRIMARY KEY (transformation_id)
);

CREATE TABLE proposed_geometry_quality_assessment (
  quality_assessment_id text NOT NULL,
  geometry_version_id text NOT NULL,
  check_name text NOT NULL,
  check_result text NOT NULL,
  tolerance_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  measured_value_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  assessed_at timestamptz NOT NULL,
  assessed_by_actor_id text NOT NULL,
  CONSTRAINT proposed_geometry_quality_assessment_pk PRIMARY KEY (quality_assessment_id),
  CONSTRAINT proposed_geometry_quality_assessment_geometry_version_id_fk FOREIGN KEY (geometry_version_id) REFERENCES proposed_geometry_version(geometry_version_id),
  CONSTRAINT proposed_geometry_quality_assessment_check_result_vocab_ck CHECK (check_result IN ('observed', 'quality-checked', 'reviewed', 'accepted-canonical', 'valid-with-warning', 'rejected', 'disputed', 'superseded'))
);

CREATE TABLE proposed_licence (
  licence_id text NOT NULL,
  licence_name text NOT NULL,
  licence_uri text,
  usage_restriction text NOT NULL,
  classification text NOT NULL DEFAULT 'government-internal',
  CONSTRAINT proposed_licence_pk PRIMARY KEY (licence_id),
  CONSTRAINT proposed_licence_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_source_authority (
  source_authority_id text NOT NULL,
  authority_name text NOT NULL,
  authority_class text NOT NULL,
  legal_basis text,
  status text NOT NULL,
  CONSTRAINT proposed_source_authority_pk PRIMARY KEY (source_authority_id),
  CONSTRAINT proposed_source_authority_authority_class_vocab_ck CHECK (authority_class IN ('official-government', 'registry-authority', 'gis-data-authority', 'verified-field', 'unverified-field', 'citizen-submitted', 'imported-provisional', 'external-map-suggestion', 'derived-system', 'fixture-training')),
  CONSTRAINT proposed_source_authority_status_vocab_ck CHECK (status IN ('draft-candidate', 'registry-review', 'registry-ready', 'active', 'corrected', 'superseded', 'retired', 'disputed', 'revoked'))
);

CREATE TABLE proposed_source_package (
  source_package_id text NOT NULL,
  source_authority_id text NOT NULL,
  package_name text NOT NULL,
  package_checksum text NOT NULL,
  licence_id text,
  loaded_at timestamptz NOT NULL,
  load_context jsonb NOT NULL DEFAULT '{}'::jsonb,
  CONSTRAINT proposed_source_package_pk PRIMARY KEY (source_package_id),
  CONSTRAINT proposed_source_package_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id),
  CONSTRAINT proposed_source_package_licence_id_fk FOREIGN KEY (licence_id) REFERENCES proposed_licence(licence_id)
);

CREATE TABLE proposed_source_record (
  source_record_id text NOT NULL,
  source_package_id text NOT NULL,
  source_key text NOT NULL,
  raw_payload_hash text NOT NULL,
  raw_payload_classification text NOT NULL,
  recorded_at timestamptz NOT NULL,
  CONSTRAINT proposed_source_record_pk PRIMARY KEY (source_record_id),
  CONSTRAINT proposed_source_record_source_package_id_fk FOREIGN KEY (source_package_id) REFERENCES proposed_source_package(source_package_id),
  CONSTRAINT proposed_source_record_raw_payload_classification_vocab_ck CHECK (raw_payload_classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_evidence_object (
  evidence_object_id text NOT NULL,
  source_record_id text NOT NULL,
  storage_uri text NOT NULL,
  content_hash text NOT NULL,
  media_type text NOT NULL,
  classification text NOT NULL,
  captured_at timestamptz,
  retention_state text NOT NULL,
  CONSTRAINT proposed_evidence_object_pk PRIMARY KEY (evidence_object_id),
  CONSTRAINT proposed_evidence_object_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id),
  CONSTRAINT proposed_evidence_object_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal')),
  CONSTRAINT proposed_evidence_object_retention_state_vocab_ck CHECK (retention_state IN ('active', 'legal-hold', 'scheduled-disposal', 'disposed-metadata-retained'))
);

CREATE TABLE proposed_decision_event (
  decision_event_id text NOT NULL,
  decision_type text NOT NULL,
  actor_id text NOT NULL,
  authority_id text NOT NULL,
  reason_code text NOT NULL,
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  effective_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL,
  CONSTRAINT proposed_decision_event_pk PRIMARY KEY (decision_event_id),
  CONSTRAINT proposed_decision_event_decision_type_vocab_ck CHECK (decision_type IN ('promote-record', 'approve-geometry', 'correct-record', 'supersede-record', 'approve-publication', 'withdraw-publication', 'resolve-dispute')),
  CONSTRAINT proposed_decision_event_authority_id_fk FOREIGN KEY (authority_id) REFERENCES proposed_source_authority(source_authority_id)
);

CREATE TABLE proposed_location_record_assertion (
  assertion_id text NOT NULL,
  location_record_version_id text NOT NULL,
  target_entity text NOT NULL,
  target_field text NOT NULL,
  value_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_record_id text NOT NULL,
  evidence_object_id text,
  decision_event_id text NOT NULL,
  classification text NOT NULL,
  CONSTRAINT proposed_location_record_assertion_pk PRIMARY KEY (assertion_id),
  CONSTRAINT proposed_location_record_assertion_location_record_version_id_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id),
  CONSTRAINT proposed_location_record_assertion_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id),
  CONSTRAINT proposed_location_record_assertion_evidence_object_id_fk FOREIGN KEY (evidence_object_id) REFERENCES proposed_evidence_object(evidence_object_id),
  CONSTRAINT proposed_location_record_assertion_decision_event_id_fk FOREIGN KEY (decision_event_id) REFERENCES proposed_decision_event(decision_event_id),
  CONSTRAINT proposed_location_record_assertion_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_intake_case (
  intake_case_id text NOT NULL,
  source_record_id text NOT NULL,
  submitted_label text NOT NULL,
  intake_state text NOT NULL,
  provisional_code text,
  created_at timestamptz NOT NULL,
  closed_at timestamptz,
  CONSTRAINT proposed_intake_case_pk PRIMARY KEY (intake_case_id),
  CONSTRAINT proposed_intake_case_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id),
  CONSTRAINT proposed_intake_case_intake_state_vocab_ck CHECK (intake_state IN ('submitted', 'under-review', 'needs-field-check', 'duplicate-review', 'rejected', 'promoted-to-canonical', 'closed'))
);

CREATE TABLE proposed_field_assignment (
  assignment_id text NOT NULL,
  operational_area_id text NOT NULL,
  task_type text NOT NULL,
  team text NOT NULL,
  priority text NOT NULL,
  assignment_state text NOT NULL,
  created_at timestamptz NOT NULL,
  closed_at timestamptz,
  CONSTRAINT proposed_field_assignment_pk PRIMARY KEY (assignment_id),
  CONSTRAINT proposed_field_assignment_operational_area_id_fk FOREIGN KEY (operational_area_id) REFERENCES proposed_operational_area(operational_area_id),
  CONSTRAINT proposed_field_assignment_assignment_state_vocab_ck CHECK (assignment_state IN ('assigned', 'in-progress', 'field-captured', 'evidence-under-review', 'evidence-approved', 'evidence-rejected', 'needs-recapture', 'linked-to-canonical', 'cancelled'))
);

CREATE TABLE proposed_field_observation (
  field_observation_id text NOT NULL,
  intake_case_id text,
  assignment_id text,
  observation_type text NOT NULL,
  verification_state text NOT NULL,
  source_record_id text NOT NULL,
  geometry_observation_id text,
  notes_classification text NOT NULL,
  recorded_at timestamptz NOT NULL,
  CONSTRAINT proposed_field_observation_pk PRIMARY KEY (field_observation_id),
  CONSTRAINT proposed_field_observation_intake_case_id_fk FOREIGN KEY (intake_case_id) REFERENCES proposed_intake_case(intake_case_id),
  CONSTRAINT proposed_field_observation_assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES proposed_field_assignment(assignment_id),
  CONSTRAINT proposed_field_observation_verification_state_vocab_ck CHECK (verification_state IN ('assigned', 'in-progress', 'field-captured', 'evidence-under-review', 'evidence-approved', 'evidence-rejected', 'needs-recapture', 'linked-to-canonical', 'cancelled')),
  CONSTRAINT proposed_field_observation_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id),
  CONSTRAINT proposed_field_observation_geometry_observation_id_fk FOREIGN KEY (geometry_observation_id) REFERENCES proposed_geometry_observation(geometry_observation_id),
  CONSTRAINT proposed_field_observation_notes_classification_vocab_ck CHECK (notes_classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_correction_case (
  correction_case_id text NOT NULL,
  target_location_record_id text,
  target_public_code text,
  correction_type text NOT NULL,
  case_state text NOT NULL,
  submitted_at timestamptz NOT NULL,
  resolved_at timestamptz,
  resolution_event_id text,
  CONSTRAINT proposed_correction_case_pk PRIMARY KEY (correction_case_id),
  CONSTRAINT proposed_correction_case_target_location_record_id_fk FOREIGN KEY (target_location_record_id) REFERENCES proposed_location_record(location_record_id),
  CONSTRAINT proposed_correction_case_correction_type_vocab_ck CHECK (correction_type IN ('label', 'geometry', 'classification', 'duplicate', 'administrative-context')),
  CONSTRAINT proposed_correction_case_case_state_vocab_ck CHECK (case_state IN ('submitted', 'under-review', 'needs-evidence', 'approved', 'rejected', 'resolved', 'closed')),
  CONSTRAINT proposed_correction_case_resolution_event_id_fk FOREIGN KEY (resolution_event_id) REFERENCES proposed_decision_event(decision_event_id)
);

CREATE TABLE proposed_dispute_case (
  dispute_case_id text NOT NULL,
  target_entity text NOT NULL,
  target_id text NOT NULL,
  dispute_type text NOT NULL,
  case_state text NOT NULL,
  opened_at timestamptz NOT NULL,
  resolved_at timestamptz,
  resolution_event_id text,
  CONSTRAINT proposed_dispute_case_pk PRIMARY KEY (dispute_case_id),
  CONSTRAINT proposed_dispute_case_dispute_type_vocab_ck CHECK (dispute_type IN ('geometry', 'name', 'authority', 'publication', 'duplicate')),
  CONSTRAINT proposed_dispute_case_case_state_vocab_ck CHECK (case_state IN ('submitted', 'under-review', 'needs-evidence', 'approved', 'rejected', 'resolved', 'closed')),
  CONSTRAINT proposed_dispute_case_resolution_event_id_fk FOREIGN KEY (resolution_event_id) REFERENCES proposed_decision_event(decision_event_id)
);

CREATE TABLE proposed_publication_release (
  publication_release_id text NOT NULL,
  release_state text NOT NULL,
  authority_reference text NOT NULL,
  projection_type text NOT NULL,
  effective_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL,
  immutable_manifest_hash text NOT NULL,
  manifest_storage_uri text NOT NULL,
  created_by_actor_id text NOT NULL,
  CONSTRAINT proposed_publication_release_pk PRIMARY KEY (publication_release_id),
  CONSTRAINT proposed_publication_release_release_state_vocab_ck CHECK (release_state IN ('draft', 'approval-requested', 'approved', 'published', 'suspended', 'withdrawn')),
  CONSTRAINT proposed_publication_release_projection_type_vocab_ck CHECK (projection_type IN ('public-lookup', 'operator-case-file', 'partner-api', 'signage-export', 'statistics'))
);

CREATE TABLE proposed_publication_release_item (
  publication_release_item_id text NOT NULL,
  publication_release_id text NOT NULL,
  location_record_id text NOT NULL,
  location_record_version_id text NOT NULL,
  public_code_alias_id text NOT NULL,
  projection_payload_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  projection_payload_hash text NOT NULL,
  projection_state text NOT NULL,
  published_label text NOT NULL,
  published_geometry_policy text NOT NULL,
  CONSTRAINT proposed_publication_release_item_pk PRIMARY KEY (publication_release_item_id),
  CONSTRAINT proposed_publication_release_item_publication_release_id_fk FOREIGN KEY (publication_release_id) REFERENCES proposed_publication_release(publication_release_id),
  CONSTRAINT proposed_publication_release_item_location_record_id_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id),
  CONSTRAINT proposed_publication_release_item_location_record_version_id_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id),
  CONSTRAINT proposed_publication_release_item_public_code_alias_id_fk FOREIGN KEY (public_code_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id),
  CONSTRAINT proposed_publication_release_item_projection_state_vocab_ck CHECK (projection_state IN ('included', 'redacted', 'withdrawn', 'superseded'))
);

CREATE TABLE proposed_partner_projection (
  partner_projection_id text NOT NULL,
  publication_release_item_id text NOT NULL,
  partner_scope text NOT NULL,
  response_field_set jsonb NOT NULL DEFAULT '[]'::jsonb,
  classification text NOT NULL,
  expires_at timestamptz,
  CONSTRAINT proposed_partner_projection_pk PRIMARY KEY (partner_projection_id),
  CONSTRAINT proposed_partner_projection_publication_release_item_id_fk FOREIGN KEY (publication_release_item_id) REFERENCES proposed_publication_release_item(publication_release_item_id),
  CONSTRAINT proposed_partner_projection_classification_vocab_ck CHECK (classification IN ('public', 'public-after-release', 'government-internal', 'restricted', 'highly-restricted', 'security-internal'))
);

CREATE TABLE proposed_migration_exception (
  migration_exception_id text NOT NULL,
  batch_id text NOT NULL,
  source_table text NOT NULL,
  source_field text,
  source_key text NOT NULL,
  exception_type text NOT NULL,
  severity text NOT NULL,
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  owner text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz,
  CONSTRAINT proposed_migration_exception_pk PRIMARY KEY (migration_exception_id)
);

CREATE UNIQUE INDEX proposed_lrv_one_current_recorded ON proposed_location_record_version(location_record_id) WHERE recorded_to IS NULL;
CREATE UNIQUE INDEX proposed_admin_unit_version_one_current ON proposed_administrative_unit_version(administrative_unit_id) WHERE recorded_to IS NULL;
CREATE UNIQUE INDEX proposed_geometry_one_current_subject_role ON proposed_geometry_version(subject_entity, subject_id, geometry_role) WHERE recorded_to IS NULL;
CREATE UNIQUE INDEX proposed_public_code_unique ON proposed_public_code_alias(public_code);
CREATE INDEX proposed_geometry_observation_gist ON proposed_geometry_observation USING GIST (observed_geom);
CREATE INDEX proposed_geometry_version_gist ON proposed_geometry_version USING GIST (geom);
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_srid_ck CHECK (ST_SRID(observed_geom) = 4326);
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_srid_ck CHECK (ST_SRID(geom) = 4326);
-- WO-002B executable design must add triggers validating geometry role-to-subject/type rules from target-model.json.
-- WO-002B executable design must add exclusion constraints for non-overlapping effective intervals where range support is introduced.
