-- Canonical address record case-file layer.
-- Keeps indexed government registry anchors separate from flexible JSONB evidence bundles.
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
ALTER TABLE address_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_address_records_code ON address_records (address_code);
CREATE INDEX IF NOT EXISTS idx_address_records_status_updated ON address_records (status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_address_records_province_status ON address_records (province_code, status);
CREATE INDEX IF NOT EXISTS idx_address_records_territory_status ON address_records (territory_id, status);
CREATE INDEX IF NOT EXISTS idx_address_records_search_text ON address_records USING gin (to_tsvector('simple', search_text));

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
