-- NLI-WO-002 NON-EXECUTABLE DESIGN ARTIFACT
-- DO NOT APPLY.
-- This file is intentionally under docs/sda/data-model/ and not infra/migrations/.
-- It proposes a future canonical data model for SDA review only.

-- Core reference geography
CREATE TABLE proposed_country (
  country_id TEXT PRIMARY KEY,
  iso2_code TEXT NOT NULL UNIQUE,
  official_name_es TEXT NOT NULL,
  official_name_en TEXT,
  status TEXT NOT NULL
);

CREATE TABLE proposed_administrative_unit (
  admin_unit_id TEXT PRIMARY KEY,
  country_id TEXT NOT NULL,
  parent_admin_unit_id TEXT,
  admin_level TEXT NOT NULL,
  official_code TEXT NOT NULL,
  status TEXT NOT NULL,
  effective_from DATE,
  effective_to DATE,
  source_authority TEXT NOT NULL,
  classification TEXT NOT NULL DEFAULT 'government-internal'
);

CREATE TABLE proposed_administrative_unit_name (
  admin_unit_name_id TEXT PRIMARY KEY,
  admin_unit_id TEXT NOT NULL,
  language_code TEXT NOT NULL,
  name_text TEXT NOT NULL,
  name_status TEXT NOT NULL,
  effective_from DATE,
  effective_to DATE
);

CREATE TABLE proposed_operational_area (
  operational_area_id TEXT PRIMARY KEY,
  area_type TEXT NOT NULL,
  purpose TEXT NOT NULL,
  status TEXT NOT NULL,
  classification TEXT NOT NULL DEFAULT 'government-internal'
);

-- Addressable objects
CREATE TABLE proposed_road (
  road_id TEXT PRIMARY KEY,
  lifecycle_state TEXT NOT NULL,
  source_authority TEXT NOT NULL
);

CREATE TABLE proposed_road_segment (
  road_segment_id TEXT PRIMARY KEY,
  road_id TEXT NOT NULL,
  segment_order INTEGER,
  lifecycle_state TEXT NOT NULL
);

CREATE TABLE proposed_road_name (
  road_name_id TEXT PRIMARY KEY,
  road_id TEXT NOT NULL,
  language_code TEXT NOT NULL,
  name_text TEXT NOT NULL,
  name_status TEXT NOT NULL,
  source_authority TEXT NOT NULL
);

CREATE TABLE proposed_building (
  building_id TEXT PRIMARY KEY,
  lifecycle_state TEXT NOT NULL,
  source_authority TEXT NOT NULL
);

CREATE TABLE proposed_entrance (
  entrance_id TEXT PRIMARY KEY,
  building_id TEXT,
  lifecycle_state TEXT NOT NULL
);

CREATE TABLE proposed_unit (
  unit_id TEXT PRIMARY KEY,
  building_id TEXT NOT NULL,
  unit_label TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  classification TEXT NOT NULL DEFAULT 'restricted'
);

CREATE TABLE proposed_landmark (
  landmark_id TEXT PRIMARY KEY,
  name_text TEXT NOT NULL,
  landmark_type TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL
);

CREATE TABLE proposed_parcel_reference (
  parcel_reference_id TEXT PRIMARY KEY,
  external_parcel_id TEXT,
  source_authority TEXT NOT NULL,
  classification TEXT NOT NULL DEFAULT 'restricted'
);

CREATE TABLE proposed_non_building_object (
  object_id TEXT PRIMARY KEY,
  object_type TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL
);

-- Sole canonical registry anchor
CREATE TABLE proposed_location_record (
  location_record_id TEXT PRIMARY KEY,
  current_version_id TEXT,
  lifecycle_state TEXT NOT NULL,
  publication_state TEXT NOT NULL DEFAULT 'not-public',
  classification TEXT NOT NULL DEFAULT 'government-internal',
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE proposed_location_record_version (
  location_record_version_id TEXT PRIMARY KEY,
  location_record_id TEXT NOT NULL,
  version_number INTEGER NOT NULL,
  is_current BOOLEAN NOT NULL DEFAULT FALSE,
  label_es TEXT NOT NULL,
  label_en TEXT,
  admin_unit_id TEXT,
  operational_area_id TEXT,
  road_segment_id TEXT,
  landmark_id TEXT,
  parcel_reference_id TEXT,
  building_id TEXT,
  entrance_id TEXT,
  unit_id TEXT,
  non_building_object_id TEXT,
  version_reason TEXT NOT NULL,
  source_authority TEXT NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL
);

CREATE UNIQUE INDEX proposed_location_record_one_current_version
  ON proposed_location_record_version(location_record_id)
  WHERE is_current = TRUE;

CREATE TABLE proposed_public_code_alias (
  public_code_alias_id TEXT PRIMARY KEY,
  location_record_id TEXT NOT NULL,
  public_code TEXT NOT NULL UNIQUE,
  code_state TEXT NOT NULL,
  is_current BOOLEAN NOT NULL DEFAULT TRUE,
  issued_at TIMESTAMPTZ,
  retired_at TIMESTAMPTZ
);

CREATE TABLE proposed_geometry_version (
  geometry_version_id TEXT PRIMARY KEY,
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  geometry_role TEXT NOT NULL,
  geometry_type TEXT NOT NULL,
  crs TEXT NOT NULL DEFAULT 'EPSG:4326',
  -- proposed future PostGIS field: geom GEOMETRY NOT NULL,
  accuracy_meters NUMERIC,
  capture_method TEXT NOT NULL,
  source_authority TEXT NOT NULL,
  quality_state TEXT NOT NULL,
  is_current BOOLEAN NOT NULL DEFAULT FALSE,
  classification TEXT NOT NULL DEFAULT 'restricted',
  captured_at TIMESTAMPTZ,
  recorded_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE proposed_location_record_event (
  location_record_event_id TEXT PRIMARY KEY,
  location_record_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  actor_id TEXT,
  source_record_id TEXT,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE proposed_source_package (
  source_package_id TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_authority TEXT NOT NULL,
  authority_status TEXT NOT NULL,
  package_checksum TEXT NOT NULL,
  loaded_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE proposed_source_record (
  source_record_id TEXT PRIMARY KEY,
  source_package_id TEXT,
  source_key TEXT NOT NULL,
  raw_payload_hash TEXT NOT NULL,
  classification TEXT NOT NULL
);

CREATE TABLE proposed_publication_release (
  publication_release_id TEXT PRIMARY KEY,
  release_state TEXT NOT NULL,
  authority_reference TEXT NOT NULL,
  effective_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE proposed_publication_release_item (
  publication_release_item_id TEXT PRIMARY KEY,
  publication_release_id TEXT NOT NULL,
  location_record_id TEXT NOT NULL,
  projection_type TEXT NOT NULL,
  projection_state TEXT NOT NULL
);
