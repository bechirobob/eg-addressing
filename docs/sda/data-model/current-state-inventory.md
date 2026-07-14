# Current-State Inventory — pg_catalog Derived

Generated from a disposable PostgreSQL/PostGIS database after applying accepted migrations. This replaces migration-text parsing. It includes migration-ledger and operational-control fields.

## Migration ledger and extensions

| Version | Filename | Checksum | Applied at | Execution context |
|---|---|---|---|---|
| 000 | 000_current_operational_schema.sql | 3374f474f1796bf4753172da706f1a8df3f3e83ca707b866d35ab2f320386a73 | <disposable-db-apply-time> | <review04-design-pipeline> |
| 001 | 001_schema_migration_baseline.sql | cca14e756c74f4820634cfc3a8c0c2de09b3645cfcd79822bcfe111635dfd2bb | <disposable-db-apply-time> | <review04-design-pipeline> |
| 002 | 002_government_grade_indexes_and_guards.sql | 591f96fb3a0f723a9c5858cd390dd1994d9aa7815f43ac0942d689786684d919 | <disposable-db-apply-time> | <review04-design-pipeline> |
| 003 | 003_canonical_address_records.sql | 26cf76bfdf1ba634579e55f924d5e978606e195cd6a33bd65f1a1f284621f215 | <disposable-db-apply-time> | <review04-design-pipeline> |
| 004 | 004_registry_ready_not_signage_ready.sql | 1d6c30eedcb6111703a62d2595aa4700cdb8bb8d79f2a3eb307ad1f5b5cb8e39 | <disposable-db-apply-time> | <review04-design-pipeline> |
| 005 | 005_address_record_postgis_geometry.sql | b97febc89d5bc94b3dd5d0d1a0f77f03395aee5616eeae755f3ad30872d003c5 | <disposable-db-apply-time> | <review04-design-pipeline> |
| 006 | 006_address_record_retirement_policy.sql | e6c0f3dd0508ff32ae5f12e52bfa6f68b065e356424c335e440bcd96b3161408 | <disposable-db-apply-time> | <review04-design-pipeline> |
| 007 | 007_lifecycle_metadata_hardening.sql | bcd606a1239ee343086b36be276540b6866d03287f7afe0621cc4d8225142d8d | <disposable-db-apply-time> | <review04-design-pipeline> |

## Installed extensions

| Extension | Version |
|---|---|
| fuzzystrmatch | 1.2 |
| plpgsql | 1.0 |
| postgis | 3.4.3 |
| postgis_tiger_geocoder | 3.4.3 |
| postgis_topology | 3.4.3 |

## Tables

| Table | Fields | Constraints | Indexes | Geometry | Disposition |
|---|---|---|---|---|---|
| `address_corrections` | 13 | 2 | 3 | — | operational/current-state |
| `address_points` | 9 | 2 | 2 | — | operational/current-state |
| `address_record_events` | 8 | 2 | 2 | — | operational/current-state |
| `address_records` | 17 | 7 | 10 | — | operational/current-state |
| `addresses` | 16 | 7 | 3 | — | operational/current-state |
| `admin_units` | 11 | 4 | 2 | — | operational/current-state |
| `audit_logs` | 9 | 1 | 1 | — | operational/current-state |
| `auth_tokens` | 6 | 2 | 1 | — | operational/current-state |
| `buildings` | 10 | 4 | 2 | — | operational/current-state |
| `citizen_geotag_submissions` | 33 | 2 | 5 | — | operational/current-state |
| `development_fixture_batches` | 6 | 1 | 1 | — | operational/current-state |
| `development_fixture_records` | 5 | 2 | 1 | — | operational/current-state |
| `field_assignments` | 7 | 2 | 1 | — | operational/current-state |
| `field_submissions` | 14 | 3 | 2 | — | operational/current-state |
| `import_jobs` | 7 | 1 | 1 | — | operational/current-state |
| `import_rows` | 10 | 3 | 1 | — | operational/current-state |
| `provinces` | 3 | 1 | 1 | — | operational/current-state |
| `publication_pack_addresses` | 2 | 3 | 1 | — | operational/current-state |
| `publication_packs` | 6 | 1 | 1 | — | operational/current-state |
| `reference_data_load_history` | 8 | 1 | 1 | — | operational/current-state |
| `reference_data_loads` | 7 | 1 | 1 | — | operational/current-state |
| `roads` | 9 | 3 | 2 | — | operational/current-state |
| `schema_migrations` | 5 | 1 | 1 | — | migration-ledger/control |
| `territories` | 9 | 4 | 2 | — | operational/current-state |
| `users` | 7 | 2 | 2 | — | operational/current-state |

## One row per current field

| Table | Field | Data type | UDT | Nullable | Default | Constraints | Indexes | Geometry | Classification | Lifecycle meaning |
|---|---|---|---|---|---|---|---|---|---|---|
| `address_corrections` | `id` | text | text | NO | — | address_corrections_address_id_fkey; address_corrections_pkey | address_corrections_pkey; idx_address_corrections_status_created_at; idx_address_corrections_status_updated | — | government-internal | identity/reference key |
| `address_corrections` | `address_id` | text | text | YES | — | address_corrections_address_id_fkey | — | — | government-internal | identity/reference key |
| `address_corrections` | `public_code` | text | text | YES | — | — | — | — | public | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `query` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `correction_type` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `reason` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `note` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `reporter_name` | text | text | YES | — | — | — | — | restricted | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `reporter_contact` | text | text | YES | — | — | — | — | restricted | descriptive, measurement, payload, geometry, or relationship value |
| `address_corrections` | `status` | text | text | NO | 'submitted'::text | — | idx_address_corrections_status_created_at; idx_address_corrections_status_updated | — | government-internal | controlled lifecycle/status value |
| `address_corrections` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_address_corrections_status_created_at | — | government-internal | recorded/effective timestamp |
| `address_corrections` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_address_corrections_status_updated | — | government-internal | recorded/effective timestamp |
| `address_corrections` | `reviewer_note` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_points` | `id` | text | text | NO | — | address_points_address_id_fkey; address_points_pkey | address_points_pkey; idx_address_points_address_id_active | — | government-internal | identity/reference key |
| `address_points` | `address_id` | text | text | NO | — | address_points_address_id_fkey | idx_address_points_address_id_active | — | government-internal | identity/reference key |
| `address_points` | `latitude` | double precision | float8 | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_points` | `longitude` | double precision | float8 | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_points` | `accuracy_meters` | double precision | float8 | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_points` | `source_method` | text | text | NO | 'manual'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_points` | `is_active` | boolean | bool | NO | true | — | idx_address_points_address_id_active | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_points` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `address_points` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `address_record_events` | `id` | text | text | NO | — | address_record_events_address_record_id_fkey; address_record_events_pkey | address_record_events_pkey; idx_address_record_events_record_created | — | government-internal | identity/reference key |
| `address_record_events` | `address_record_id` | text | text | NO | — | address_record_events_address_record_id_fkey | idx_address_record_events_record_created | — | government-internal | identity/reference key |
| `address_record_events` | `event_type` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_record_events` | `actor_id` | text | text | YES | — | — | — | — | government-internal | identity/reference key |
| `address_record_events` | `actor_username` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_record_events` | `actor_role` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_record_events` | `details` | jsonb | jsonb | NO | '{}'::jsonb | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_record_events` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_address_record_events_record_created | — | government-internal | recorded/effective timestamp |
| `address_records` | `id` | text | text | NO | — | address_records_pkey; address_records_source_submission_id_fkey; address_records_territory_id_fkey | address_records_pkey; idx_address_records_active_code; idx_address_records_active_status_updated; idx_address_records_code; idx_address_records_geom; idx_address_records_province_status; idx_address_records_search_text; idx_address_records_status_updated; idx_address_records_territory_status | — | government-internal | identity/reference key |
| `address_records` | `address_code` | text | text | NO | — | address_records_address_code_key | address_records_address_code_key; idx_address_records_active_code; idx_address_records_code | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `source_submission_id` | text | text | YES | — | address_records_source_submission_id_fkey | — | — | government-internal | identity/reference key |
| `address_records` | `province_code` | text | text | YES | — | address_records_province_code_fkey | idx_address_records_province_status | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `territory_id` | text | text | YES | — | address_records_territory_id_fkey | idx_address_records_territory_status | — | government-internal | identity/reference key |
| `address_records` | `address_label` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `status` | text | text | NO | — | — | idx_address_records_active_status_updated; idx_address_records_province_status; idx_address_records_status_updated; idx_address_records_territory_status | — | government-internal | controlled lifecycle/status value |
| `address_records` | `publication_state` | text | text | NO | 'not-public'::text | — | — | — | government-internal | controlled lifecycle/status value |
| `address_records` | `latitude` | double precision | float8 | NO | — | address_records_latitude_valid | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `longitude` | double precision | float8 | NO | — | address_records_longitude_valid | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `accuracy_meters` | double precision | float8 | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `search_text` | text | text | NO | ''::text | — | idx_address_records_search_text | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `record_bundle` | jsonb | jsonb | NO | '{}'::jsonb | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `is_archived` | boolean | bool | NO | false | — | idx_address_records_active_code; idx_address_records_active_status_updated | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `address_records` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `address_records` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_address_records_active_status_updated; idx_address_records_status_updated | — | government-internal | recorded/effective timestamp |
| `address_records` | `geom` | USER-DEFINED | geography | YES | — | — | idx_address_records_geom | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `id` | text | text | NO | — | addresses_building_id_fkey; addresses_pkey; addresses_road_id_fkey; addresses_superseded_by_address_id_fkey; addresses_territory_id_fkey | addresses_pkey; idx_addresses_public_code_unique | — | government-internal | identity/reference key |
| `addresses` | `formatted` | text | text | NO | — | addresses_formatted_key | addresses_formatted_key | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `territory_id` | text | text | NO | — | addresses_territory_id_fkey | — | — | government-internal | identity/reference key |
| `addresses` | `road_id` | text | text | NO | — | addresses_road_id_fkey | — | — | government-internal | identity/reference key |
| `addresses` | `building_id` | text | text | NO | — | addresses_building_id_fkey | — | — | government-internal | identity/reference key |
| `addresses` | `province_code` | text | text | NO | — | addresses_province_code_fkey | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `public_code` | text | text | YES | — | — | idx_addresses_public_code_unique | — | public | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `issuance_method` | text | text | NO | 'manual'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `source` | text | text | NO | 'admin-portal'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `verification_status` | text | text | NO | 'provisional'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `superseded_by_address_id` | text | text | YES | — | addresses_superseded_by_address_id_fkey | — | — | government-internal | identity/reference key |
| `addresses` | `status` | text | text | NO | — | — | — | — | government-internal | controlled lifecycle/status value |
| `addresses` | `publication_state` | text | text | NO | 'draft'::text | — | — | — | government-internal | controlled lifecycle/status value |
| `addresses` | `is_archived` | boolean | bool | NO | false | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `addresses` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `addresses` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `admin_units` | `id` | text | text | NO | — | admin_units_parent_id_fkey; admin_units_pkey | admin_units_pkey | — | government-internal | identity/reference key |
| `admin_units` | `level` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `admin_units` | `code` | text | text | NO | — | admin_units_code_key; admin_units_province_code_fkey | admin_units_code_key | — | public | descriptive, measurement, payload, geometry, or relationship value |
| `admin_units` | `parent_id` | text | text | YES | — | admin_units_parent_id_fkey | — | — | government-internal | identity/reference key |
| `admin_units` | `province_code` | text | text | YES | — | admin_units_province_code_fkey | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `admin_units` | `name_es` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `admin_units` | `name_en` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `admin_units` | `status` | text | text | NO | 'active'::text | — | — | — | government-internal | controlled lifecycle/status value |
| `admin_units` | `sort_order` | integer | int4 | NO | 0 | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `admin_units` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `admin_units` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `audit_logs` | `id` | bigint | int8 | NO | nextval('audit_logs_id_seq'::regclass) | audit_logs_pkey | audit_logs_pkey | — | government-internal | identity/reference key |
| `audit_logs` | `actor_user_id` | text | text | YES | — | — | — | — | government-internal | identity/reference key |
| `audit_logs` | `actor_username` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `audit_logs` | `actor_role` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `audit_logs` | `action` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `audit_logs` | `entity_type` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `audit_logs` | `entity_id` | text | text | NO | — | — | — | — | government-internal | identity/reference key |
| `audit_logs` | `details` | text | text | NO | '{}'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `audit_logs` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `auth_tokens` | `token` | text | text | NO | — | auth_tokens_pkey | auth_tokens_pkey | — | security-internal | descriptive, measurement, payload, geometry, or relationship value |
| `auth_tokens` | `user_id` | text | text | NO | — | auth_tokens_user_id_fkey | — | — | security-internal | identity/reference key |
| `auth_tokens` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | security-internal | recorded/effective timestamp |
| `auth_tokens` | `expires_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | security-internal | recorded/effective timestamp |
| `auth_tokens` | `revoked_at` | timestamp with time zone | timestamptz | YES | — | — | — | — | security-internal | recorded/effective timestamp |
| `auth_tokens` | `last_seen_at` | timestamp with time zone | timestamptz | YES | — | — | — | — | security-internal | recorded/effective timestamp |
| `buildings` | `id` | text | text | NO | — | buildings_pkey; buildings_road_id_fkey; buildings_territory_id_fkey | buildings_pkey | — | government-internal | identity/reference key |
| `buildings` | `label` | text | text | NO | — | buildings_label_key | buildings_label_key | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `buildings` | `territory_id` | text | text | NO | — | buildings_territory_id_fkey | — | — | government-internal | identity/reference key |
| `buildings` | `road_id` | text | text | NO | — | buildings_road_id_fkey | — | — | government-internal | identity/reference key |
| `buildings` | `status` | text | text | NO | — | — | — | — | government-internal | controlled lifecycle/status value |
| `buildings` | `usage` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `buildings` | `spatial_evidence` | jsonb | jsonb | NO | '{}'::jsonb | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `buildings` | `is_archived` | boolean | bool | NO | false | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `buildings` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `buildings` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `citizen_geotag_submissions` | `id` | text | text | NO | — | citizen_geotag_submissions_pkey; citizen_geotag_submissions_territory_id_fkey | citizen_geotag_submissions_pkey; idx_citizen_geotag_grid_code; idx_citizen_geotag_public_tracking; idx_citizen_geotag_signage_ready; idx_citizen_geotag_status_created_at | — | government-internal | identity/reference key |
| `citizen_geotag_submissions` | `territory_id` | text | text | YES | — | citizen_geotag_submissions_territory_id_fkey | — | — | government-internal | identity/reference key |
| `citizen_geotag_submissions` | `address_label` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `citizen_name` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `citizen_contact` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `dip_last4` | text | text | YES | — | — | — | — | restricted | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `identity_verification_status` | text | text | NO | 'unverified'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `identity_document_verified` | boolean | bool | NO | false | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `identity_verified_at` | timestamp with time zone | timestamptz | YES | — | — | — | — | government-internal | recorded/effective timestamp |
| `citizen_geotag_submissions` | `landmark` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `latitude` | double precision | float8 | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `longitude` | double precision | float8 | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `accuracy_meters` | double precision | float8 | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `capture_method` | text | text | NO | 'browser-gps'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `grid_code` | text | text | NO | — | — | idx_citizen_geotag_grid_code | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `status` | text | text | NO | 'submitted'::text | — | idx_citizen_geotag_public_tracking; idx_citizen_geotag_signage_ready; idx_citizen_geotag_status_created_at | — | government-internal | controlled lifecycle/status value |
| `citizen_geotag_submissions` | `duplicate_hint` | text | text | NO | 'none'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `reviewer_note` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `suggested_road_name` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `suggested_local_area` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `suggested_place_name` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `map_display_name` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `road_suggestion_source` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `road_suggestion_attribution` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `road_suggestion_status` | text | text | NO | 'not-suggested'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `reviewed_road_name` | text | text | YES | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `field_submission_id` | text | text | YES | — | — | — | — | government-internal | identity/reference key |
| `citizen_geotag_submissions` | `field_status` | text | text | NO | 'assigned'::text | — | — | — | government-internal | controlled lifecycle/status value |
| `citizen_geotag_submissions` | `field_note` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `field_verified_at` | timestamp with time zone | timestamptz | YES | — | — | — | — | government-internal | recorded/effective timestamp |
| `citizen_geotag_submissions` | `signage_batch` | text | text | YES | — | — | idx_citizen_geotag_signage_ready | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `citizen_geotag_submissions` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_citizen_geotag_status_created_at | — | government-internal | recorded/effective timestamp |
| `citizen_geotag_submissions` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_citizen_geotag_public_tracking; idx_citizen_geotag_signage_ready | — | government-internal | recorded/effective timestamp |
| `development_fixture_batches` | `batch_id` | text | text | NO | — | development_fixture_batches_pkey | development_fixture_batches_pkey | — | government-internal | identity/reference key |
| `development_fixture_batches` | `fixture_version` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `development_fixture_batches` | `environment` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `development_fixture_batches` | `loaded_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `development_fixture_batches` | `cleaned_at` | timestamp with time zone | timestamptz | YES | — | — | — | — | government-internal | recorded/effective timestamp |
| `development_fixture_batches` | `execution_context` | text | text | NO | '{}'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `development_fixture_records` | `batch_id` | text | text | NO | — | development_fixture_records_batch_id_fkey; development_fixture_records_pkey | development_fixture_records_pkey | — | government-internal | identity/reference key |
| `development_fixture_records` | `table_name` | text | text | NO | — | development_fixture_records_pkey | development_fixture_records_pkey | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `development_fixture_records` | `record_id` | text | text | NO | — | development_fixture_records_pkey | development_fixture_records_pkey | — | government-internal | identity/reference key |
| `development_fixture_records` | `created_by_batch` | boolean | bool | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `development_fixture_records` | `recorded_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `field_assignments` | `assignment_id` | text | text | NO | — | field_assignments_pkey | field_assignments_pkey | — | government-internal | identity/reference key |
| `field_assignments` | `territory_id` | text | text | NO | — | field_assignments_territory_id_fkey | — | — | government-internal | identity/reference key |
| `field_assignments` | `territory` | text | text | NO | — | field_assignments_territory_id_fkey | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_assignments` | `task` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_assignments` | `team` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_assignments` | `priority` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_assignments` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `field_submissions` | `id` | text | text | NO | — | field_submissions_assignment_id_fkey; field_submissions_pkey; field_submissions_territory_id_fkey | field_submissions_pkey; idx_field_submissions_review_status_created | — | government-internal | identity/reference key |
| `field_submissions` | `assignment_id` | text | text | YES | — | field_submissions_assignment_id_fkey | — | — | government-internal | identity/reference key |
| `field_submissions` | `territory_id` | text | text | NO | — | field_submissions_territory_id_fkey | — | — | government-internal | identity/reference key |
| `field_submissions` | `submission_type` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `candidate_name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `candidate_status` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `notes` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `submitted_by` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `review_status` | text | text | NO | 'submitted'::text | — | idx_field_submissions_review_status_created | — | government-internal | controlled lifecycle/status value |
| `field_submissions` | `reviewer_note` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `registry_entity_id` | text | text | YES | — | — | — | — | government-internal | identity/reference key |
| `field_submissions` | `spatial_evidence` | jsonb | jsonb | NO | '{}'::jsonb | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `field_submissions` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | idx_field_submissions_review_status_created | — | government-internal | recorded/effective timestamp |
| `field_submissions` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `import_jobs` | `id` | text | text | NO | — | import_jobs_pkey | import_jobs_pkey | — | government-internal | identity/reference key |
| `import_jobs` | `name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_jobs` | `source_name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_jobs` | `status` | text | text | NO | 'draft'::text | — | — | — | government-internal | controlled lifecycle/status value |
| `import_jobs` | `imported_count` | integer | int4 | NO | 0 | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_jobs` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `import_jobs` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `import_rows` | `job_id` | text | text | NO | — | import_rows_job_id_fkey; import_rows_pkey | import_rows_pkey | — | government-internal | identity/reference key |
| `import_rows` | `row_number` | integer | int4 | NO | — | import_rows_pkey | import_rows_pkey | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_rows` | `submission_type` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_rows` | `territory_id` | text | text | NO | — | import_rows_territory_id_fkey | — | — | government-internal | identity/reference key |
| `import_rows` | `candidate_name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_rows` | `candidate_status` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_rows` | `notes` | text | text | NO | ''::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_rows` | `validation_status` | text | text | NO | — | — | — | — | government-internal | controlled lifecycle/status value |
| `import_rows` | `validation_message` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `import_rows` | `committed_submission_id` | text | text | YES | — | — | — | — | government-internal | identity/reference key |
| `provinces` | `code` | text | text | NO | — | provinces_pkey | provinces_pkey | — | public | descriptive, measurement, payload, geometry, or relationship value |
| `provinces` | `name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `provinces` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `publication_pack_addresses` | `publication_pack_id` | text | text | NO | — | publication_pack_addresses_pkey; publication_pack_addresses_publication_pack_id_fkey | publication_pack_addresses_pkey | — | government-internal | identity/reference key |
| `publication_pack_addresses` | `address_id` | text | text | NO | — | publication_pack_addresses_address_id_fkey; publication_pack_addresses_pkey | publication_pack_addresses_pkey | — | government-internal | identity/reference key |
| `publication_packs` | `id` | text | text | NO | — | publication_packs_pkey | publication_packs_pkey | — | government-internal | identity/reference key |
| `publication_packs` | `name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `publication_packs` | `status` | text | text | NO | — | — | — | — | government-internal | controlled lifecycle/status value |
| `publication_packs` | `audience` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `publication_packs` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `publication_packs` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `reference_data_load_history` | `id` | bigint | int8 | NO | nextval('reference_data_load_history_id_seq'::regclass) | reference_data_load_history_pkey | reference_data_load_history_pkey | — | government-internal | identity/reference key |
| `reference_data_load_history` | `package_id` | text | text | NO | — | — | — | — | government-internal | identity/reference key |
| `reference_data_load_history` | `package_version` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_load_history` | `source` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_load_history` | `authority_status` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_load_history` | `package_checksum` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_load_history` | `loaded_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `reference_data_load_history` | `execution_context` | text | text | NO | '{}'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_loads` | `package_id` | text | text | NO | — | reference_data_loads_pkey | reference_data_loads_pkey | — | government-internal | identity/reference key |
| `reference_data_loads` | `package_version` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_loads` | `source` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_loads` | `authority_status` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_loads` | `package_checksum` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `reference_data_loads` | `loaded_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `reference_data_loads` | `execution_context` | text | text | NO | '{}'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `roads` | `id` | text | text | NO | — | roads_pkey; roads_territory_id_fkey | roads_pkey | — | government-internal | identity/reference key |
| `roads` | `name` | text | text | NO | — | roads_name_key | roads_name_key | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `roads` | `territory_id` | text | text | NO | — | roads_territory_id_fkey | — | — | government-internal | identity/reference key |
| `roads` | `status` | text | text | NO | — | — | — | — | government-internal | controlled lifecycle/status value |
| `roads` | `length_km` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `roads` | `spatial_evidence` | jsonb | jsonb | NO | '{}'::jsonb | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `roads` | `is_archived` | boolean | bool | NO | false | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `roads` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `roads` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `schema_migrations` | `version` | text | text | NO | — | schema_migrations_pkey | schema_migrations_pkey | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `schema_migrations` | `filename` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `schema_migrations` | `checksum` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `schema_migrations` | `applied_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `schema_migrations` | `execution_context` | text | text | NO | '{}'::text | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `territories` | `id` | text | text | NO | — | territories_admin_unit_id_fkey; territories_pkey | territories_pkey | — | government-internal | identity/reference key |
| `territories` | `name` | text | text | NO | — | territories_name_key | territories_name_key | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `territories` | `province_code` | text | text | NO | — | territories_province_code_fkey | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `territories` | `admin_unit_id` | text | text | YES | — | territories_admin_unit_id_fkey | — | — | government-internal | identity/reference key |
| `territories` | `type` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `territories` | `readiness` | text | text | NO | — | — | — | — | government-internal | controlled lifecycle/status value |
| `territories` | `is_archived` | boolean | bool | NO | false | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `territories` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `territories` | `updated_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
| `users` | `id` | text | text | NO | — | users_pkey | users_pkey | — | government-internal | identity/reference key |
| `users` | `username` | text | text | NO | — | users_username_key | users_username_key | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `users` | `full_name` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `users` | `role` | text | text | NO | — | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `users` | `password_hash` | text | text | NO | — | — | — | — | security-internal | descriptive, measurement, payload, geometry, or relationship value |
| `users` | `is_active` | boolean | bool | NO | true | — | — | — | government-internal | descriptive, measurement, payload, geometry, or relationship value |
| `users` | `created_at` | timestamp with time zone | timestamptz | NO | now() | — | — | — | government-internal | recorded/effective timestamp |
