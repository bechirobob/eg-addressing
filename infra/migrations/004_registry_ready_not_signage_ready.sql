-- Correct pilot workflow terminology: internal approval is registry-ready.
-- Physical signage/publication comes only after full project or institutional approval.
UPDATE citizen_geotag_submissions
SET status = 'registry-ready',
    signage_batch = NULL,
    updated_at = NOW()
WHERE status = 'signage-ready';

UPDATE field_submissions
SET candidate_status = 'registry-ready',
    updated_at = NOW()
WHERE candidate_status = 'signage-ready';

UPDATE address_records
SET status = 'registry-ready',
    publication_state = 'internal-registry',
    record_bundle = jsonb_set(
      jsonb_set(
        jsonb_set(record_bundle, '{identity,status}', '"registry-ready"'::jsonb, true),
        '{identity,publication_state}', '"internal-registry"'::jsonb, true
      ),
      '{outputs,physical_rollout_status}', '"awaiting-full-project-approval"'::jsonb, true
    ),
    updated_at = NOW()
WHERE status = 'signage-ready';
