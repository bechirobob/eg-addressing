# Source, Evidence, Lineage, and Classification Model

## Lineage levels

- `source_authority`: institution/system/person class responsible for source legitimacy.
- `source_package`: imported or submitted package with checksum/license/load context.
- `source_record`: immutable source row/submission key and raw payload hash.
- `evidence_object`: files/media/field proof with content hash and retention state.
- `decision_event`: actor/authority/reason/effective/recorded time for promotion, correction, publication, dispute, or retirement.
- `location_record_assertion`: field-level assertion linking a target field to source/evidence/decision.

## Classification

Values are defined in `controlled-vocabularies.md`. Public projection is allowlisted by `publication_release_item`; database presence never implies publication.
