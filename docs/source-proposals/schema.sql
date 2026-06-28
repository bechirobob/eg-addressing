-- National Digital Addressing Platform
-- Core PostgreSQL + PostGIS schema for pilot MVP

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$ BEGIN
    CREATE TYPE user_status AS ENUM ('active', 'suspended', 'invited', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE rollout_status AS ENUM ('planned', 'active', 'paused', 'completed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE naming_status AS ENUM ('proposed', 'under_review', 'approved', 'retired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE address_status AS ENUM ('draft', 'submitted', 'under_review', 'approved', 'published', 'disputed', 'corrected', 'retired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE assignment_status AS ENUM ('assigned', 'active', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE sync_status AS ENUM ('local_only', 'synced', 'failed', 'conflicted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE review_status AS ENUM ('draft', 'submitted', 'accepted', 'rejected', 'needs_correction');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE verification_outcome AS ENUM ('passed', 'failed', 'disputed', 'escalated');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE correction_status AS ENUM ('submitted', 'under_review', 'approved', 'rejected', 'resolved');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE install_status AS ENUM ('planned', 'fabricated', 'installed', 'damaged', 'replaced');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE client_status AS ENUM ('active', 'paused', 'revoked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
    CREATE TYPE credential_status AS ENUM ('active', 'rotated', 'revoked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS countries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS provinces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS districts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    province_id UUID NOT NULL REFERENCES provinces(id) ON DELETE RESTRICT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS municipalities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id UUID NOT NULL REFERENCES districts(id) ON DELETE RESTRICT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID NOT NULL REFERENCES municipalities(id) ON DELETE RESTRICT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    zone_type TEXT NOT NULL,
    rollout_status rollout_status NOT NULL DEFAULT 'planned',
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    password_hash TEXT NOT NULL,
    status user_status NOT NULL DEFAULT 'invited',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS user_role_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    scope_type TEXT,
    scope_id UUID,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE (user_id, role_id, scope_type, scope_id)
);

CREATE TABLE IF NOT EXISTS roads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    road_code TEXT NOT NULL UNIQUE,
    official_name TEXT,
    provisional_name TEXT,
    road_type TEXT NOT NULL,
    naming_status naming_status NOT NULL DEFAULT 'proposed',
    geom geometry(MultiLineString, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    landmark_type TEXT NOT NULL,
    geom geometry(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS parcels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    parcel_ref TEXT,
    ownership_status TEXT,
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS buildings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    parcel_id UUID REFERENCES parcels(id) ON DELETE SET NULL,
    primary_road_id UUID REFERENCES roads(id) ON DELETE SET NULL,
    building_type TEXT NOT NULL,
    building_name TEXT,
    floor_count INTEGER,
    occupancy_status TEXT,
    geom geometry(Geometry, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS building_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    building_id UUID NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    unit_code TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    floor_label TEXT,
    status address_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (building_id, unit_code)
);

CREATE TABLE IF NOT EXISTS addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    building_id UUID REFERENCES buildings(id) ON DELETE SET NULL,
    building_unit_id UUID REFERENCES building_units(id) ON DELETE SET NULL,
    road_id UUID REFERENCES roads(id) ON DELETE SET NULL,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    address_code TEXT NOT NULL UNIQUE,
    address_line_1 TEXT NOT NULL,
    address_line_2 TEXT,
    numbering_value TEXT NOT NULL,
    postal_code TEXT,
    status address_status NOT NULL DEFAULT 'draft',
    is_official BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (building_id IS NOT NULL OR building_unit_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS address_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address_id UUID NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
    version_no INTEGER NOT NULL,
    snapshot_json JSONB NOT NULL,
    change_reason TEXT,
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (address_id, version_no)
);

CREATE TABLE IF NOT EXISTS address_status_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address_id UUID NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
    from_status address_status,
    to_status address_status NOT NULL,
    note TEXT,
    acted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    acted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS field_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    assigned_user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assignment_type TEXT NOT NULL,
    status assignment_status NOT NULL DEFAULT 'assigned',
    starts_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS field_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES field_assignments(id) ON DELETE CASCADE,
    submitted_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    building_id UUID REFERENCES buildings(id) ON DELETE SET NULL,
    road_id UUID REFERENCES roads(id) ON DELETE SET NULL,
    payload_json JSONB NOT NULL,
    gps_geom geometry(Point, 4326),
    sync_status sync_status NOT NULL DEFAULT 'local_only',
    review_status review_status NOT NULL DEFAULT 'draft',
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS submission_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_submission_id UUID NOT NULL REFERENCES field_submissions(id) ON DELETE CASCADE,
    storage_key TEXT NOT NULL,
    photo_type TEXT NOT NULL,
    captured_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS verification_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address_id UUID REFERENCES addresses(id) ON DELETE SET NULL,
    field_submission_id UUID REFERENCES field_submissions(id) ON DELETE SET NULL,
    verification_type TEXT NOT NULL,
    outcome verification_outcome NOT NULL,
    note TEXT,
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS correction_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address_id UUID NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
    requester_type TEXT NOT NULL,
    requester_name TEXT,
    requester_contact TEXT,
    issue_type TEXT NOT NULL,
    description TEXT NOT NULL,
    status correction_status NOT NULL DEFAULT 'submitted',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS signage_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE RESTRICT,
    road_id UUID REFERENCES roads(id) ON DELETE SET NULL,
    address_id UUID REFERENCES addresses(id) ON DELETE SET NULL,
    asset_type TEXT NOT NULL,
    asset_code TEXT NOT NULL UNIQUE,
    install_status install_status NOT NULL DEFAULT 'planned',
    storage_or_vendor_ref TEXT,
    geom geometry(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agency_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    agency_type TEXT NOT NULL,
    status client_status NOT NULL DEFAULT 'active',
    contact_name TEXT,
    contact_email TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS api_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_client_id UUID NOT NULL REFERENCES agency_clients(id) ON DELETE CASCADE,
    credential_hash TEXT NOT NULL,
    scope_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status credential_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_client_id UUID REFERENCES agency_clients(id) ON DELETE SET NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    action TEXT NOT NULL,
    before_json JSONB,
    after_json JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_provinces_geom ON provinces USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_districts_geom ON districts USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_municipalities_geom ON municipalities USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_zones_geom ON zones USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_roads_zone_id ON roads(zone_id);
CREATE INDEX IF NOT EXISTS idx_roads_geom ON roads USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_buildings_zone_id ON buildings(zone_id);
CREATE INDEX IF NOT EXISTS idx_buildings_geom ON buildings USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_addresses_zone_id ON addresses(zone_id);
CREATE INDEX IF NOT EXISTS idx_addresses_status ON addresses(status);
CREATE INDEX IF NOT EXISTS idx_addresses_official ON addresses(is_official);
CREATE INDEX IF NOT EXISTS idx_field_submissions_assignment_id ON field_submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_field_submissions_sync_status ON field_submissions(sync_status);
CREATE INDEX IF NOT EXISTS idx_field_submissions_review_status ON field_submissions(review_status);
CREATE INDEX IF NOT EXISTS idx_field_submissions_geom ON field_submissions USING GIST (gps_geom);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_correction_requests_status ON correction_requests(status);

INSERT INTO roles (code, name, description)
VALUES
    ('super_admin', 'Platform Super Administrator', 'Technical and emergency platform authority'),
    ('national_registry_admin', 'National Registry Administrator', 'Owns official publication workflows'),
    ('ministry_reviewer', 'Ministry Reviewer', 'Ministry-level review and approval role'),
    ('municipal_validator', 'Municipal Validator', 'Local territorial validation role'),
    ('field_supervisor', 'Field Supervisor', 'Oversees enumerator operations'),
    ('enumerator', 'Field Enumerator', 'Captures field records and evidence'),
    ('helpdesk_agent', 'Helpdesk Agent', 'Handles correction requests and support'),
    ('agency_readonly', 'Agency Read-Only User', 'Searches approved records only'),
    ('auditor', 'Auditor', 'Reviews logs and compliance activity')
ON CONFLICT (code) DO NOTHING;
