# SDA Pattern Acceptance — Address-Points Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-PATTERN-01-ASSESSMENT`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `2f9373ef0481af498638810d43a8008986c4697b`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `ACCEPTED AS REPLICATION PATTERN WITH RECORDED CONDITIONS`

## 1. Review boundary

Reviewed the final-control delta for the single authorized transform group `WO002-R06-geometry-observation-address_points`, including the explicit callable and registry binding, complete PostgreSQL source-row query, reviewed transform-spec row, coordinate precision, source/evidence lineage, address identity-crosswalk semantics, PostGIS target writes, conditional authority exception, read-only complete-set comparison, idempotency, two-source same-address behavior, oracle-access control, specification drift tests, implementation/source/comparator mutations, same-database rollback evidence, changed paths, oracle hashes and exact-head CI.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- Reviewed implementation head is `2f9373ef0481af498638810d43a8008986c4697b`.
- Parent, correction and final-correction reviewer oracles were unchanged.
- The change remained limited to the one transform-spec row, one-slice harness, one-slice evidence and task record.
- No other transform group, F04–F12, runtime application, executable migration, migration runner, Docker runtime, production/pilot data, secret, `.env*` or PR #8 path changed.
- Exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend workflows completed successfully.

## 2. Accepted implementation pattern

The following pattern is accepted at the exact reviewed commit:

```text
complete current_source source row
→ independently reviewed transform specification
→ explicit per-group callable
→ typed canonical_target rows and real target references
→ committed observed state
→ separate read-only complete-set comparison against reviewer-owned expected truth
→ strict normal-path mutations and same-database rollback proof
```

Accepted controls:

1. `transform_address_points_geometry()` is an explicit callable and is bound to `impl_wo002_r06_geometry_observation_address_points`.
2. The transform does not route through the generic all-groups `transform_group()` function.
3. The transform reads the complete `current_source.address_points` row and consumes reviewed covered/context fields.
4. Context fields and source-method translation are declared by the reviewed transform-spec row.
5. The observed-output producer does not read the reviewer-owned acceptance oracles.
6. The address reference resolves through one shared address-level crosswalk and exactly one registry subject.
7. Source-record and evidence lineage derive from the queried source identity rather than fixed fixture IDs.
8. Coordinate precision is preserved through typed `ST_MakePoint` insertion with SRID 4326.
9. The transform creates one geometry observation and one owned conditional authority exception for each source point.
10. No canonical geometry version, quality approval, CRS transformation or substitute per-field geometry assertion is created.
11. The comparator uses a separate read-only connection and compares all source-attributable geometry observations and migration exceptions in both directions.
12. Unexpected target rows and wrong independently expected geometry fail.
13. Two point observations referencing the same address reuse one address identity crosswalk without duplicate or multiple identity resolution.
14. The second execution produces zero inserts and zero updates.
15. Negative tests use real implementation, source, specification, precondition and expected-result mutations and prove same-database rollback before reset.

## 3. Recorded conditions

Pattern acceptance is governed by:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-geometry-transform-pattern-contract.json
```

Conditions:

- Acceptance is tied to the exact implementation commit, transform-spec row and oracle hashes recorded in that contract.
- Any change to the accepted callable, binding, accepted spec row or reviewer oracles invalidates this pattern acceptance until further SDA review.
- The in-process oracle gate is accepted only as a deterministic design-harness control; it is not a production security or identity boundary.
- Acceptance-oracle access must remain absent from observed-output code.
- The address crosswalk is a prerequisite owned by identity/crosswalk transformation, not an output owned by the geometry transform.
- Each additional transform group requires a group-specific reviewer-owned oracle before implementation.
- Replication must retain explicit group callables and must not collapse into a generic all-groups evidence function.

## 4. Scope of acceptance

Accepted:

- The address-points geometry transformation pattern.
- Reuse of this pattern as the engineering baseline for later SDA-authorized geometry slices.

Not accepted or authorized:

- Any of the other 89 transform groups.
- Broad Phase A reassessment.
- Closure of F02 or F14.
- Phase B.
- F04–F12 remediation.
- SDA Review 12.
- NLI-WO-002B.
- Executable migration or runtime implementation.
- Official geometry promotion, publication, public-code issuance, certificates, signage, partner release, pilot deployment or production deployment.

## 5. Decision

`ACCEPTED AS REPLICATION PATTERN WITH RECORDED CONDITIONS`

The narrow method has produced an independently reviewable and credible vertical slice. The accepted pattern may now be used only for the next bounded geometry-family planning checkpoint. No additional group implementation is authorized until the SDA provides the relevant group-specific expected-result control.

## 6. Next controlled checkpoint

The next task is mapping-only. The implementation agent must prepare a geometry-family replication mapping pack for:

- `WO002-R06-geometry-observation-address_records`
- `WO002-R06-geometry-observation-citizen_geotag_submissions`

The pack must identify complete source records, subject/identity resolution, source/evidence lineage, context and translation rules, exact proposed target rows, conditional exceptions, expected absences and unresolved authority decisions. It must not modify implementation code or activate either transform group.
