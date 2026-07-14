# ADR-006 — Administrative identity, effective-dated code/name history and operational areas

## Status

Proposed for SDA Review 05. NLI-WO-002B remains unauthorized.

## Decision owner

System Design Authority; implementation agent may only encode and test the selected design boundary.

## Context

Review 04 rejected generated/template ADR rationale. This ADR is bound to explicit model identifiers and disposable-schema semantic tests.

## Model and constraint identifiers

administrative_unit.administrative_unit_id, administrative_code_history.official_code, name_record.subject_id, operational_area.lifecycle_state

## Decision

`administrative_unit` is identity only. Official codes are authoritative only in `administrative_code_history`; names are in `name_record`; mutable work-planning overlays are `operational_area` records linked by subject/geometry, not administrative identity.

## Alternatives considered

| Alternative | Benefit | Cost / rejection reason |
|---|---|---|
| Keep `stable_code` on administrative_unit | Simple lookup | Rejected by Review 04: creates duplicate code authority. |
| Use code as PK | Readable schema | Rejected: official codes can change and must be bitemporal. |
| Identity row plus code/name history | Reconstructable official state | Selected with exclusion constraints on effective/recorded intervals. |

## Implementation constraints

No `administrative_unit.stable_code`; code history one current per unit/scheme; admin version lifecycle uses `administrative_unit_lifecycle`; operational areas use separate lifecycle.

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

Overlapping code history aborts; missing current code leaves migration exception; retired unit cannot receive new public links without authority decision.

## Consequences

- The selected model is stricter than the current pilot schema and requires a controlled expand-migrate-contract phase.
- The stricter model prevents silent orphaning, duplicate authority, public leakage and impossible lifecycle states.

## Acceptance checks

Checker fails if `administrative_unit.stable_code` returns; target SQL executes admin code exclusion; fixtures include administrative-boundary-change scenario.
