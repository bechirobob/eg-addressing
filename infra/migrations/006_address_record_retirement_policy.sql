-- 006_address_record_retirement_policy.sql
-- Adds FK-safe retirement support for canonical address_records.

ALTER TABLE address_records
  ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_address_records_active_status_updated
  ON address_records (status, updated_at DESC)
  WHERE is_archived = FALSE;

CREATE INDEX IF NOT EXISTS idx_address_records_active_code
  ON address_records (address_code)
  WHERE is_archived = FALSE;
