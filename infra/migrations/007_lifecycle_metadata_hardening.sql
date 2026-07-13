-- 007_lifecycle_metadata_hardening.sql
-- Explicit lifecycle metadata hardening and legacy auth-token expiry backfill.
-- This migration intentionally isolates the only data repair formerly embedded
-- in the 000 schema bridge.

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

UPDATE auth_tokens
SET expires_at = COALESCE(expires_at, created_at + INTERVAL '12 hours')
WHERE expires_at IS NULL OR expires_at <= created_at;
