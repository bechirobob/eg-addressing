-- 000_current_operational_schema.sql
-- Deterministic schema bootstrap for NLI-WO-001.
-- This migration is the executable replacement for the historical application
-- bootstrap DDL. It intentionally contains schema only: no reference data,
-- users, demonstration fixtures, or operational records.
-- Existing migrations 001-006 are preserved unchanged and run after this file.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS reference_data_loads (
    package_id TEXT PRIMARY KEY,
    package_version TEXT NOT NULL,
    source TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    package_checksum TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    execution_context TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS reference_data_load_history (
    id BIGSERIAL PRIMARY KEY,
    package_id TEXT NOT NULL,
    package_version TEXT NOT NULL,
    source TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    package_checksum TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    execution_context TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS development_fixture_batches (
    batch_id TEXT PRIMARY KEY,
    fixture_version TEXT NOT NULL,
    environment TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cleaned_at TIMESTAMPTZ,
    execution_context TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS development_fixture_records (
    batch_id TEXT NOT NULL REFERENCES development_fixture_batches(batch_id) ON DELETE CASCADE,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    created_by_batch BOOLEAN NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (batch_id, table_name, record_id)
);

CREATE TABLE IF NOT EXISTS provinces (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE TABLE IF NOT EXISTS admin_units (
            id TEXT PRIMARY KEY,
            level TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            parent_id TEXT REFERENCES admin_units(id),
            province_code TEXT REFERENCES provinces(code),
            name_es TEXT NOT NULL,
            name_en TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS province_code TEXT REFERENCES provinces(code);

ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active';

ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS sort_order INTEGER NOT NULL DEFAULT 0;

ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            revoked_at TIMESTAMPTZ,
            last_seen_at TIMESTAMPTZ
        );

ALTER TABLE auth_tokens ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE auth_tokens ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMPTZ;

ALTER TABLE auth_tokens ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS audit_logs (
            id BIGSERIAL PRIMARY KEY,
            actor_user_id TEXT,
            actor_username TEXT,
            actor_role TEXT,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE TABLE IF NOT EXISTS territories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            province_code TEXT NOT NULL REFERENCES provinces(code),
            admin_unit_id TEXT REFERENCES admin_units(id),
            type TEXT NOT NULL,
            readiness TEXT NOT NULL,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE territories ADD COLUMN IF NOT EXISTS admin_unit_id TEXT REFERENCES admin_units(id);

ALTER TABLE territories ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE territories ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS roads (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            status TEXT NOT NULL,
            length_km TEXT NOT NULL,
            spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE roads ADD COLUMN IF NOT EXISTS spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE roads ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE roads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL UNIQUE,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            road_id TEXT NOT NULL REFERENCES roads(id),
            status TEXT NOT NULL,
            usage TEXT NOT NULL,
            spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE buildings ADD COLUMN IF NOT EXISTS spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE buildings ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE buildings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS addresses (
            id TEXT PRIMARY KEY,
            formatted TEXT NOT NULL UNIQUE,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            road_id TEXT NOT NULL REFERENCES roads(id),
            building_id TEXT NOT NULL REFERENCES buildings(id),
            province_code TEXT NOT NULL REFERENCES provinces(code),
            public_code TEXT,
            issuance_method TEXT NOT NULL DEFAULT 'manual',
            source TEXT NOT NULL DEFAULT 'admin-portal',
            verification_status TEXT NOT NULL DEFAULT 'provisional',
            superseded_by_address_id TEXT REFERENCES addresses(id),
            status TEXT NOT NULL,
            publication_state TEXT NOT NULL DEFAULT 'draft',
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS public_code TEXT;

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS issuance_method TEXT NOT NULL DEFAULT 'manual';

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'admin-portal';

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS verification_status TEXT NOT NULL DEFAULT 'provisional';

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS superseded_by_address_id TEXT REFERENCES addresses(id);

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS publication_state TEXT NOT NULL DEFAULT 'draft';

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE addresses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE UNIQUE INDEX IF NOT EXISTS idx_addresses_public_code_unique ON addresses (public_code) WHERE public_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS address_points (
            id TEXT PRIMARY KEY,
            address_id TEXT NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            accuracy_meters DOUBLE PRECISION,
            source_method TEXT NOT NULL DEFAULT 'manual',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE INDEX IF NOT EXISTS idx_address_points_address_id_active ON address_points (address_id, is_active);

CREATE TABLE IF NOT EXISTS address_corrections (
            id TEXT PRIMARY KEY,
            address_id TEXT REFERENCES addresses(id),
            public_code TEXT,
            query TEXT NOT NULL,
            correction_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            reporter_name TEXT,
            reporter_contact TEXT,
            status TEXT NOT NULL DEFAULT 'submitted',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE address_corrections ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT '';

ALTER TABLE address_corrections ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_address_corrections_status_created_at ON address_corrections (status, created_at DESC);

CREATE TABLE IF NOT EXISTS citizen_geotag_submissions (
            id TEXT PRIMARY KEY,
            territory_id TEXT REFERENCES territories(id),
            address_label TEXT NOT NULL,
            citizen_name TEXT,
            citizen_contact TEXT,
            dip_last4 TEXT,
            identity_verification_status TEXT NOT NULL DEFAULT 'unverified',
            identity_document_verified BOOLEAN NOT NULL DEFAULT FALSE,
            identity_verified_at TIMESTAMPTZ,
            landmark TEXT NOT NULL DEFAULT '',
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            accuracy_meters DOUBLE PRECISION,
            capture_method TEXT NOT NULL DEFAULT 'browser-gps',
            grid_code TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'submitted',
            duplicate_hint TEXT NOT NULL DEFAULT 'none',
            reviewer_note TEXT NOT NULL DEFAULT '',
            suggested_road_name TEXT,
            suggested_local_area TEXT,
            suggested_place_name TEXT,
            map_display_name TEXT,
            road_suggestion_source TEXT,
            road_suggestion_attribution TEXT,
            road_suggestion_status TEXT NOT NULL DEFAULT 'not-suggested',
            reviewed_road_name TEXT,
            field_submission_id TEXT,
            field_status TEXT NOT NULL DEFAULT 'assigned',
            field_note TEXT NOT NULL DEFAULT '',
            field_verified_at TIMESTAMPTZ,
            signage_batch TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS citizen_name TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS citizen_contact TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS dip_last4 TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS identity_verification_status TEXT NOT NULL DEFAULT 'unverified';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS identity_document_verified BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS identity_verified_at TIMESTAMPTZ;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS landmark TEXT NOT NULL DEFAULT '';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS capture_method TEXT NOT NULL DEFAULT 'browser-gps';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS duplicate_hint TEXT NOT NULL DEFAULT 'none';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT '';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS suggested_road_name TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS suggested_local_area TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS suggested_place_name TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS map_display_name TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS road_suggestion_source TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS road_suggestion_attribution TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS road_suggestion_status TEXT NOT NULL DEFAULT 'not-suggested';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS reviewed_road_name TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_submission_id TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_status TEXT NOT NULL DEFAULT 'assigned';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_note TEXT NOT NULL DEFAULT '';

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_verified_at TIMESTAMPTZ;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS signage_batch TEXT;

ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_citizen_geotag_status_created_at ON citizen_geotag_submissions (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_citizen_geotag_grid_code ON citizen_geotag_submissions (grid_code);

CREATE TABLE IF NOT EXISTS address_records (
            id TEXT PRIMARY KEY,
            address_code TEXT NOT NULL UNIQUE,
            source_submission_id TEXT REFERENCES citizen_geotag_submissions(id),
            province_code TEXT REFERENCES provinces(code),
            territory_id TEXT REFERENCES territories(id),
            address_label TEXT NOT NULL,
            status TEXT NOT NULL,
            publication_state TEXT NOT NULL DEFAULT 'not-public',
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            accuracy_meters DOUBLE PRECISION,
            search_text TEXT NOT NULL DEFAULT '',
            record_bundle JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS source_submission_id TEXT REFERENCES citizen_geotag_submissions(id);

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS province_code TEXT REFERENCES provinces(code);

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS territory_id TEXT REFERENCES territories(id);

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS publication_state TEXT NOT NULL DEFAULT 'not-public';

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS accuracy_meters DOUBLE PRECISION;

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS search_text TEXT NOT NULL DEFAULT '';

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS record_bundle JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE address_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_address_records_code ON address_records (address_code);

CREATE INDEX IF NOT EXISTS idx_address_records_status_updated ON address_records (status, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_address_records_active_status_updated ON address_records (status, updated_at DESC) WHERE is_archived = FALSE;

CREATE INDEX IF NOT EXISTS idx_address_records_active_code ON address_records (address_code) WHERE is_archived = FALSE;

CREATE INDEX IF NOT EXISTS idx_address_records_province_status ON address_records (province_code, status);

CREATE INDEX IF NOT EXISTS idx_address_records_territory_status ON address_records (territory_id, status);

CREATE TABLE IF NOT EXISTS address_record_events (
            id TEXT PRIMARY KEY,
            address_record_id TEXT NOT NULL REFERENCES address_records(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            actor_id TEXT,
            actor_username TEXT,
            actor_role TEXT,
            details JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE INDEX IF NOT EXISTS idx_address_record_events_record_created ON address_record_events (address_record_id, created_at DESC);

CREATE TABLE IF NOT EXISTS field_assignments (
            assignment_id TEXT PRIMARY KEY,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            territory TEXT NOT NULL,
            task TEXT NOT NULL,
            team TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE TABLE IF NOT EXISTS field_submissions (
            id TEXT PRIMARY KEY,
            assignment_id TEXT REFERENCES field_assignments(assignment_id),
            territory_id TEXT NOT NULL REFERENCES territories(id),
            submission_type TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            candidate_status TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            submitted_by TEXT NOT NULL,
            review_status TEXT NOT NULL DEFAULT 'submitted',
            reviewer_note TEXT NOT NULL DEFAULT '',
            registry_entity_id TEXT,
            spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT '';

ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS registry_entity_id TEXT;

ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS import_jobs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            imported_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE import_jobs ADD COLUMN IF NOT EXISTS imported_count INTEGER NOT NULL DEFAULT 0;

ALTER TABLE import_jobs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS import_rows (
            job_id TEXT NOT NULL REFERENCES import_jobs(id) ON DELETE CASCADE,
            row_number INTEGER NOT NULL,
            submission_type TEXT NOT NULL,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            candidate_name TEXT NOT NULL,
            candidate_status TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            validation_status TEXT NOT NULL,
            validation_message TEXT NOT NULL,
            committed_submission_id TEXT,
            PRIMARY KEY (job_id, row_number)
        );

ALTER TABLE import_rows ADD COLUMN IF NOT EXISTS committed_submission_id TEXT;

CREATE TABLE IF NOT EXISTS publication_packs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            audience TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

ALTER TABLE publication_packs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS publication_pack_addresses (
            publication_pack_id TEXT NOT NULL REFERENCES publication_packs(id) ON DELETE CASCADE,
            address_id TEXT NOT NULL REFERENCES addresses(id),
            PRIMARY KEY (publication_pack_id, address_id)
        );
