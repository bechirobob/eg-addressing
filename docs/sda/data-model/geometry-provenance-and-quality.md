# Geometry, Provenance, and Quality Model

## Decisions

- Raw/candidate geometry is stored in `geometry_observation` with `observed_geom geometry(Geometry,4326)`, source/evidence/license links, capture method, observed_at, recorded_at, and classification.
- Approved geometry is stored in `geometry_version` with `geom geometry(Geometry,4326)`, `subject_table`, `subject_id`, `geometry_role`, source observation, validation method, quality state, effective/recorded time, supersession link, dispute behavior, and one-current constraint.
- Subject integrity uses constrained `subject_table` values plus future WO-002B validation triggers because PostgreSQL cannot FK to multiple tables from one column. This decision is explicit and must be implemented before deployment.
- Administrative and operational boundaries use the same observation/version quality process; public release can use generalized geometry.

## Validation and licensing

Every approved geometry requires source license, transformation history where applicable, SRID check, geometry validity, role/type check, expected administrative containment or exception, and quality assessment rows. Disputed geometry cannot be published as precise public geometry until resolved or released with explicit warning policy.
