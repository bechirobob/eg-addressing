# ADR-009 — Geometry observations, approved versions and subject-bound spatial integrity

## Status

Proposed for SDA Review 05. NLI-WO-002B remains unauthorized.

## Decision owner

System Design Authority; implementation agent may only encode and test the selected design boundary.

## Context

Review 04 rejected generated/template ADR rationale. This ADR is bound to explicit model identifiers and disposable-schema semantic tests.

## Model and constraint identifiers

geometry_observation.observed_geom, geometry_version.geom, geometry_version.geometry_role, geometry_version.subject_id, geometry_quality_assessment.check_result

## Decision

Raw spatial captures are `geometry_observation`; approved operational geometry is `geometry_version`. Both link to `registry_subject`; role/type/SRID/dimensionality/current/supersession rules are enforced in disposable target SQL and tested by scenario fixtures.

## Alternatives considered

| Alternative | Benefit | Cost / rejection reason |
|---|---|---|
| Single geometry column per object | Fast reads | Rejected: loses observations, licence, transformations and quality evidence. |
| External GIS-only authority | Central GIS control | Rejected: app cannot enforce publication/registry constraints. |
| Observation plus approved version | Lineage and enforceable current geometry | Selected with GiST indexes and role/type triggers. |

## Implementation constraints

SRID 4326, 2D validity, role-to-type matrix, subject FK, one current geometry per subject/role, no self supersession.

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

Wrong geometry type rejects; missing subject rejects; self supersession rejects; overlapping current geometry rejects.

## Consequences

- The selected model is stricter than the current pilot schema and requires a controlled expand-migrate-contract phase.
- The stricter model prevents silent orphaning, duplicate authority, public leakage and impossible lifecycle states.

## Acceptance checks

Positive fixtures cover admin boundary, operational boundary, road, building, entrance, location and landmark roles; negative geometry fixtures reject wrong type and self-supersession.

## Evidence-linked conditions

- Condition: decision acceptance is limited to assertions executed by `review04_design_pipeline.py` and `design_consistency_check.py`.
- Evidence: target schema validation report, lifecycle binding registry, transformation registry, policy contracts and scenario validation report.
- Boundary: NLI-WO-002B remains unauthorized until SDA explicitly accepts the model.

## Unresolved RFIs

- No executable production migration authority is granted by this ADR.
- Institutional owner approval, operational rollout windows and production data retention rules remain future SDA/institution decisions.

## Acceptance tests

- CI must fail if the ADR claims a constraint absent from the model policy registry or target validation report.
- CI must fail if Review 05 resolution rows are updated outside the Review 05 resolution log.
