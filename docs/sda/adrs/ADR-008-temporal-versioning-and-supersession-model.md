# ADR-008 — Bitemporal intervals, reciprocal chains and immutable release reconstruction

## Status

Proposed for SDA Review 05. NLI-WO-002B remains unauthorized.

## Decision owner

System Design Authority; implementation agent may only encode and test the selected design boundary.

## Context

Review 04 rejected generated/template ADR rationale. This ADR is bound to explicit model identifiers and disposable-schema semantic tests.

## Model and constraint identifiers

location_record_version.recorded_at/recorded_to, administrative_code_history.effective_from/effective_to, public_code_alias.predecessor_alias_id/successor_alias_id, publication_release_item.release_payload

## Decision

Bitemporal entities use effective and recorded intervals with exclusion constraints where PostgreSQL can enforce them, plus reciprocal/same-owner chain triggers for predecessor/successor and alias chains. Publication release items preserve immutable snapshots.

## Alternatives considered

| Alternative | Benefit | Cost / rejection reason |
|---|---|---|
| Boolean is_current flags | Simple current reads | Rejected: allows overlapping current facts. |
| Event stream only | Strong audit | Rejected for this phase: needs derived projections for every lookup. |
| Intervals plus chain triggers | Queryable reconstruction and DB-enforced safety | Selected. |

## Implementation constraints

Effective and recorded exclusion constraints; one current row indexes; predecessor/successor same-owner checks; object-link intervals must be valid and contained by owning version in implementation phase.

## Security and privacy implications

- Restricted raw values remain in governed archives or evidence objects; hashes alone are not treated as archives.
- Public release requires publication authority and release-item prerequisites.
- Operator-only lineage, crosswalk and subject-link data is not projected publicly by default.

## Performance and operational trade-offs

- Write paths pay trigger/exclusion/index cost to prevent national-registry drift.
- Current reads use partial indexes and release snapshots.
- Bulk migration must batch by reviewed transformation unit and stop on exception thresholds.

## Migration consequences

- NLI-WO-002B remains unauthorized; this ADR defines acceptance gates for later executable work.
- Migration rows must use reviewed transformation decisions, crosswalk keys and source archives.
- Failed semantic checks create owned exceptions, not silent coercions.

## Failure modes

Overlap aborts batch; self-cycle aborts; reciprocal mismatch becomes migration exception until repaired.

## Consequences

- The selected model is stricter than the current pilot schema and requires a controlled expand-migrate-contract phase.
- The stricter model prevents silent orphaning, duplicate authority, public leakage and impossible lifecycle states.

## Acceptance checks

Negative fixtures reject interval overlap and self chains; catalog report records exclusion constraints and current indexes.
