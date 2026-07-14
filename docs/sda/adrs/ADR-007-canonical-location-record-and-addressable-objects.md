# ADR-007 — Subject registry enforcement for names, object links, disputes and geometry

## Status

Proposed for SDA Review 05. NLI-WO-002B remains unauthorized.

## Decision owner

System Design Authority; implementation agent may only encode and test the selected design boundary.

## Context

Review 04 rejected generated/template ADR rationale. This ADR is bound to explicit model identifiers and disposable-schema semantic tests.

## Model and constraint identifiers

registry_subject.subject_id, name_record.subject_id, location_record_object_link.subject_id, dispute_case.subject_id, geometry_version.subject_id, geometry_observation.subject_id

## Decision

Use `registry_subject.subject_id` as the shared referential target for names, object links, disputes, geometry observations and geometry versions. Do not use unconstrained entity-name plus opaque-ID pairs.

## Alternatives considered

| Alternative | Benefit | Cost / rejection reason |
|---|---|---|
| Opaque polymorphic pairs | Flexible and compact | Rejected: permits orphan names/geometry/disputes. |
| Typed link tables for every subject | Strongest native FK model | Deferred: high table count and migration complexity; acceptable future replacement if SDA chooses. |
| Shared subject registry | Single FK point with typed semantics | Selected with subject existence/delete/cardinality triggers. |

## Implementation constraints

Subject FK on all polymorphic surfaces; delete policy rejects hard delete with dependents; primary object cardinality trigger; current official Spanish name trigger.

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

Missing subject rejects write; duplicate primary object rejects write; hard delete with dependents rejects and requires retirement/merge.

## Consequences

- The selected model is stricter than the current pilot schema and requires a controlled expand-migrate-contract phase.
- The stricter model prevents silent orphaning, duplicate authority, public leakage and impossible lifecycle states.

## Acceptance checks

Negative fixtures reject missing subject and duplicate primary role; checker fails if opaque subject/entity fields return.
