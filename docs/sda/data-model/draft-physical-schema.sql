-- NLI-WO-002 NON-EXECUTABLE DESIGN ARTIFACT
-- DO NOT APPLY. DO NOT COPY TO infra/migrations.
-- PostgreSQL/PostGIS design proposal only.

CREATE TABLE proposed_country (
  country_id TEXT NOT NULL,
  iso2_code TEXT,
  official_name_es TEXT,
  official_name_en TEXT,
  lifecycle_state TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  created_at TIMESTAMPTZ,
  CONSTRAINT proposed_country_pk PRIMARY KEY (country_id)
);

CREATE TABLE proposed_administrative_unit (
  administrative_unit_id TEXT NOT NULL,
  country_id TEXT NOT NULL,
  parent_administrative_unit_id TEXT NOT NULL,
  admin_level TEXT,
  official_code TEXT,
  lifecycle_state TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  recorded_from TIMESTAMPTZ,
  recorded_to TIMESTAMPTZ,
  source_authority_id TEXT NOT NULL,
  classification TEXT NOT NULL,
  CONSTRAINT proposed_administrative_unit_pk PRIMARY KEY (administrative_unit_id)
);

CREATE TABLE proposed_administrative_unit_name (
  administrative_unit_name_id TEXT NOT NULL,
  administrative_unit_id TEXT NOT NULL,
  language_code TEXT,
  name_text TEXT,
  name_kind TEXT,
  name_status TEXT,
  normalized_text TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  source_record_id TEXT NOT NULL,
  CONSTRAINT proposed_administrative_unit_name_pk PRIMARY KEY (administrative_unit_name_id)
);

CREATE TABLE proposed_administrative_boundary_version (
  boundary_version_id TEXT NOT NULL,
  administrative_unit_id TEXT NOT NULL,
  geom GEOMETRY(Geometry,4326),
  srid TEXT,
  quality_state TEXT,
  source_record_id TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  recorded_at TIMESTAMPTZ NOT NULL,
  is_current BOOLEAN,
  CONSTRAINT proposed_administrative_boundary_version_pk PRIMARY KEY (boundary_version_id)
);

CREATE TABLE proposed_locality (
  locality_id TEXT NOT NULL,
  administrative_unit_id TEXT NOT NULL,
  locality_type TEXT,
  name_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_locality_pk PRIMARY KEY (locality_id)
);

CREATE TABLE proposed_operational_area (
  operational_area_id TEXT NOT NULL,
  area_type TEXT,
  purpose TEXT,
  lifecycle_state TEXT NOT NULL,
  authority_owner TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  classification TEXT NOT NULL,
  CONSTRAINT proposed_operational_area_pk PRIMARY KEY (operational_area_id)
);

CREATE TABLE proposed_operational_area_coverage (
  coverage_id TEXT NOT NULL,
  operational_area_id TEXT NOT NULL,
  administrative_unit_id TEXT NOT NULL,
  boundary_version_id TEXT NOT NULL,
  coverage_role TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_operational_area_coverage_pk PRIMARY KEY (coverage_id)
);

CREATE TABLE proposed_road (
  road_id TEXT NOT NULL,
  road_class TEXT,
  lifecycle_state TEXT NOT NULL,
  primary_name_id TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  created_at TIMESTAMPTZ,
  CONSTRAINT proposed_road_pk PRIMARY KEY (road_id)
);

CREATE TABLE proposed_road_segment (
  road_segment_id TEXT NOT NULL,
  road_id TEXT NOT NULL,
  from_node_ref TEXT,
  to_node_ref TEXT,
  measured_length_m TEXT,
  lifecycle_state TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_road_segment_pk PRIMARY KEY (road_segment_id)
);

CREATE TABLE proposed_road_name (
  road_name_id TEXT NOT NULL,
  road_id TEXT NOT NULL,
  road_segment_id TEXT NOT NULL,
  language_code TEXT,
  name_text TEXT,
  name_status TEXT,
  normalized_text TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  source_record_id TEXT NOT NULL,
  CONSTRAINT proposed_road_name_pk PRIMARY KEY (road_name_id)
);

CREATE TABLE proposed_parcel_reference (
  parcel_reference_id TEXT NOT NULL,
  external_parcel_id TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  classification TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_parcel_reference_pk PRIMARY KEY (parcel_reference_id)
);

CREATE TABLE proposed_building (
  building_id TEXT NOT NULL,
  primary_entrance_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  usage_class TEXT,
  source_authority_id TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_building_pk PRIMARY KEY (building_id)
);

CREATE TABLE proposed_entrance (
  entrance_id TEXT NOT NULL,
  building_id TEXT NOT NULL,
  entrance_role TEXT,
  access_point_geometry_version_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_entrance_pk PRIMARY KEY (entrance_id)
);

CREATE TABLE proposed_unit (
  unit_id TEXT NOT NULL,
  building_id TEXT NOT NULL,
  unit_label TEXT,
  unit_type TEXT,
  parent_unit_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  classification TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_unit_pk PRIMARY KEY (unit_id)
);

CREATE TABLE proposed_landmark (
  landmark_id TEXT NOT NULL,
  landmark_type TEXT,
  primary_name_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_landmark_pk PRIMARY KEY (landmark_id)
);

CREATE TABLE proposed_non_building_object (
  object_id TEXT NOT NULL,
  object_type TEXT,
  primary_name_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_non_building_object_pk PRIMARY KEY (object_id)
);

CREATE TABLE proposed_location_record (
  location_record_id TEXT NOT NULL,
  record_type TEXT,
  current_version_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  publication_state TEXT,
  classification TEXT NOT NULL,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  CONSTRAINT proposed_location_record_pk PRIMARY KEY (location_record_id)
);

CREATE TABLE proposed_location_record_version (
  location_record_version_id TEXT NOT NULL,
  location_record_id TEXT NOT NULL,
  version_number INTEGER,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  recorded_from TIMESTAMPTZ,
  recorded_to TIMESTAMPTZ,
  predecessor_version_id TEXT NOT NULL,
  successor_version_id TEXT NOT NULL,
  correction_case_id TEXT NOT NULL,
  supersession_reason TEXT,
  is_current BOOLEAN,
  display_label_es TEXT,
  display_label_en TEXT,
  administrative_unit_id TEXT NOT NULL,
  locality_id TEXT NOT NULL,
  source_decision_id TEXT NOT NULL,
  CONSTRAINT proposed_location_record_version_pk PRIMARY KEY (location_record_version_id)
);

CREATE TABLE proposed_location_record_object_link (
  link_id TEXT NOT NULL,
  location_record_version_id TEXT NOT NULL,
  object_type TEXT,
  object_id TEXT NOT NULL,
  object_role TEXT,
  cardinality_rank INTEGER,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  CONSTRAINT proposed_location_record_object_link_pk PRIMARY KEY (link_id)
);

CREATE TABLE proposed_location_record_relationship (
  relationship_id TEXT NOT NULL,
  from_location_record_id TEXT NOT NULL,
  to_location_record_id TEXT NOT NULL,
  relationship_type TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  source_decision_id TEXT NOT NULL,
  CONSTRAINT proposed_location_record_relationship_pk PRIMARY KEY (relationship_id)
);

CREATE TABLE proposed_public_code_alias (
  public_code_alias_id TEXT NOT NULL,
  location_record_id TEXT NOT NULL,
  public_code TEXT,
  code_scheme TEXT,
  code_state TEXT,
  reserved_at TIMESTAMPTZ,
  issued_at TIMESTAMPTZ,
  retired_at TIMESTAMPTZ,
  predecessor_alias_id TEXT NOT NULL,
  successor_alias_id TEXT NOT NULL,
  CONSTRAINT proposed_public_code_alias_pk PRIMARY KEY (public_code_alias_id)
);

CREATE TABLE proposed_geometry_observation (
  geometry_observation_id TEXT NOT NULL,
  subject_hint_type TEXT,
  observed_geom GEOMETRY(Geometry,4326),
  srid TEXT,
  geometry_role TEXT,
  capture_method TEXT,
  accuracy_meters TEXT,
  source_record_id TEXT NOT NULL,
  evidence_object_id TEXT NOT NULL,
  license_id TEXT NOT NULL,
  observed_at TIMESTAMPTZ,
  recorded_at TIMESTAMPTZ NOT NULL,
  classification TEXT NOT NULL,
  CONSTRAINT proposed_geometry_observation_pk PRIMARY KEY (geometry_observation_id)
);

CREATE TABLE proposed_geometry_version (
  geometry_version_id TEXT NOT NULL,
  subject_table TEXT,
  subject_id TEXT NOT NULL,
  geometry_role TEXT,
  geom GEOMETRY(Geometry,4326),
  srid TEXT,
  source_observation_id TEXT NOT NULL,
  validation_method TEXT,
  validated_by_actor_id TEXT NOT NULL,
  quality_state TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  recorded_at TIMESTAMPTZ NOT NULL,
  superseded_by_geometry_version_id TEXT NOT NULL,
  is_current BOOLEAN,
  classification TEXT NOT NULL,
  CONSTRAINT proposed_geometry_version_pk PRIMARY KEY (geometry_version_id)
);

CREATE TABLE proposed_geometry_quality_assessment (
  quality_assessment_id TEXT NOT NULL,
  geometry_version_id TEXT NOT NULL,
  check_name TEXT,
  check_result TEXT,
  tolerance TEXT,
  measured_value TEXT,
  assessed_at TIMESTAMPTZ,
  assessed_by_actor_id TEXT NOT NULL,
  CONSTRAINT proposed_geometry_quality_assessment_pk PRIMARY KEY (quality_assessment_id)
);

CREATE TABLE proposed_source_authority (
  source_authority_id TEXT NOT NULL,
  authority_name TEXT,
  authority_class TEXT,
  legal_basis TEXT,
  contact_reference TEXT,
  status TEXT,
  CONSTRAINT proposed_source_authority_pk PRIMARY KEY (source_authority_id)
);

CREATE TABLE proposed_source_package (
  source_package_id TEXT NOT NULL,
  source_authority_id TEXT NOT NULL,
  package_name TEXT,
  package_checksum TEXT,
  license_id TEXT NOT NULL,
  loaded_at TIMESTAMPTZ,
  load_context TEXT,
  CONSTRAINT proposed_source_package_pk PRIMARY KEY (source_package_id)
);

CREATE TABLE proposed_source_record (
  source_record_id TEXT NOT NULL,
  source_package_id TEXT NOT NULL,
  source_key TEXT,
  raw_payload_hash TEXT,
  raw_payload_classification TEXT,
  recorded_at TIMESTAMPTZ NOT NULL,
  CONSTRAINT proposed_source_record_pk PRIMARY KEY (source_record_id)
);

CREATE TABLE proposed_evidence_object (
  evidence_object_id TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  storage_uri TEXT,
  content_hash TEXT,
  media_type TEXT,
  classification TEXT NOT NULL,
  captured_at TIMESTAMPTZ,
  retention_state TEXT,
  CONSTRAINT proposed_evidence_object_pk PRIMARY KEY (evidence_object_id)
);

CREATE TABLE proposed_decision_event (
  decision_event_id TEXT NOT NULL,
  decision_type TEXT,
  actor_id TEXT NOT NULL,
  authority_id TEXT NOT NULL,
  reason_code TEXT,
  details_json TEXT,
  effective_at TIMESTAMPTZ,
  recorded_at TIMESTAMPTZ NOT NULL,
  CONSTRAINT proposed_decision_event_pk PRIMARY KEY (decision_event_id)
);

CREATE TABLE proposed_location_record_assertion (
  assertion_id TEXT NOT NULL,
  location_record_version_id TEXT NOT NULL,
  field_name TEXT,
  field_value_hash TEXT,
  source_record_id TEXT NOT NULL,
  evidence_object_id TEXT NOT NULL,
  decision_event_id TEXT NOT NULL,
  classification TEXT NOT NULL,
  CONSTRAINT proposed_location_record_assertion_pk PRIMARY KEY (assertion_id)
);

CREATE TABLE proposed_intake_case (
  intake_case_id TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  submitted_label TEXT,
  intake_state TEXT,
  provisional_code TEXT,
  created_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ,
  CONSTRAINT proposed_intake_case_pk PRIMARY KEY (intake_case_id)
);

CREATE TABLE proposed_field_observation (
  field_observation_id TEXT NOT NULL,
  intake_case_id TEXT NOT NULL,
  assignment_id TEXT NOT NULL,
  observation_type TEXT,
  verification_state TEXT,
  source_record_id TEXT NOT NULL,
  geometry_observation_id TEXT NOT NULL,
  notes_classification TEXT,
  recorded_at TIMESTAMPTZ NOT NULL,
  CONSTRAINT proposed_field_observation_pk PRIMARY KEY (field_observation_id)
);

CREATE TABLE proposed_field_assignment (
  assignment_id TEXT NOT NULL,
  operational_area_id TEXT NOT NULL,
  task_type TEXT,
  team TEXT,
  priority TEXT,
  assignment_state TEXT,
  created_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ,
  CONSTRAINT proposed_field_assignment_pk PRIMARY KEY (assignment_id)
);

CREATE TABLE proposed_correction_case (
  correction_case_id TEXT NOT NULL,
  target_location_record_id TEXT NOT NULL,
  target_public_code TEXT,
  correction_type TEXT,
  case_state TEXT,
  submitted_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  resolution_event_id TEXT NOT NULL,
  CONSTRAINT proposed_correction_case_pk PRIMARY KEY (correction_case_id)
);

CREATE TABLE proposed_dispute_case (
  dispute_case_id TEXT NOT NULL,
  target_subject_type TEXT,
  target_subject_id TEXT NOT NULL,
  dispute_type TEXT,
  case_state TEXT,
  opened_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  resolution_event_id TEXT NOT NULL,
  CONSTRAINT proposed_dispute_case_pk PRIMARY KEY (dispute_case_id)
);

CREATE TABLE proposed_publication_release (
  publication_release_id TEXT NOT NULL,
  release_state TEXT,
  authority_reference TEXT,
  projection_type TEXT,
  effective_at TIMESTAMPTZ,
  recorded_at TIMESTAMPTZ NOT NULL,
  immutable_manifest_hash TEXT,
  created_by_actor_id TEXT NOT NULL,
  CONSTRAINT proposed_publication_release_pk PRIMARY KEY (publication_release_id)
);

CREATE TABLE proposed_publication_release_item (
  publication_release_item_id TEXT NOT NULL,
  publication_release_id TEXT NOT NULL,
  location_record_id TEXT NOT NULL,
  location_record_version_id TEXT NOT NULL,
  public_code_alias_id TEXT NOT NULL,
  projection_payload_hash TEXT,
  projection_state TEXT,
  published_label TEXT,
  published_geom_policy TEXT,
  CONSTRAINT proposed_publication_release_item_pk PRIMARY KEY (publication_release_item_id)
);

CREATE TABLE proposed_partner_projection (
  partner_projection_id TEXT NOT NULL,
  publication_release_item_id TEXT NOT NULL,
  partner_scope TEXT,
  response_field_set TEXT,
  classification TEXT NOT NULL,
  expires_at TIMESTAMPTZ,
  CONSTRAINT proposed_partner_projection_pk PRIMARY KEY (partner_projection_id)
);


-- Referential/integrity intent examples for WO-002B executable migration design.
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_lrv_record_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id);
ALTER TABLE proposed_public_code_alias ADD CONSTRAINT proposed_public_code_record_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id);
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_pri_version_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id);
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_pri_alias_fk FOREIGN KEY (public_code_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id);
CREATE UNIQUE INDEX proposed_location_record_one_current_version ON proposed_location_record_version(location_record_id) WHERE is_current = TRUE;
CREATE UNIQUE INDEX proposed_public_code_alias_unique_code ON proposed_public_code_alias(public_code);
CREATE UNIQUE INDEX proposed_public_code_alias_one_current ON proposed_public_code_alias(location_record_id) WHERE code_state = 'active-public';
CREATE UNIQUE INDEX proposed_geometry_one_current_per_subject_role ON proposed_geometry_version(subject_table, subject_id, geometry_role) WHERE is_current = TRUE;
CREATE INDEX proposed_geometry_version_geom_gist ON proposed_geometry_version USING GIST (geom);
CREATE INDEX proposed_geometry_observation_geom_gist ON proposed_geometry_observation USING GIST (observed_geom);
CREATE INDEX proposed_location_record_state_idx ON proposed_location_record(lifecycle_state, publication_state);
-- Future trigger required: validate geometry_version.subject_table/subject_id against allowed target table.
-- Future exclusion constraint required: prevent overlapping effective intervals per location_record when is_current/effective intervals conflict.
