-- Government-grade hardening indexes for high-traffic review and tracking paths.
-- Idempotent by design: safe to run repeatedly through the migration ledger.
CREATE INDEX IF NOT EXISTS idx_citizen_geotag_public_tracking
  ON citizen_geotag_submissions (id, status, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_citizen_geotag_signage_ready
  ON citizen_geotag_submissions (status, signage_batch, updated_at DESC)
  WHERE status = 'signage-ready';

CREATE INDEX IF NOT EXISTS idx_field_submissions_review_status_created
  ON field_submissions (review_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_address_corrections_status_updated
  ON address_corrections (status, updated_at DESC);
