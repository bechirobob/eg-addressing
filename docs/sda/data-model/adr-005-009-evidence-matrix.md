# ADR-005 through ADR-009 Review 07 Evidence Matrix

This matrix replaces aggregate `Generated checks` evidence with named assertions. ADR-005 through ADR-009 remain proposed; NLI-WO-002B remains unauthorized until SDA accepts the model and issues a separate implementation work order.

| ADR | Claim/constraint | Finding dependency | Named assertion IDs | Evidence artifact | Status | Unresolved condition |
|---|---|---|---|---|---|---|
| ADR-005 | Internal identifiers, public aliases and legacy crosswalk authority | F02/F09 | F02-source-row-identity-*; F02-reference-final-fk-*; F09-reviewed-convergence-unit-* | transformation-fixture-report.json; schema-convergence-units-reviewed.json | passing | NLI-WO-002B implementation remains unauthorized; unresolved legacy references terminate in migration_exception until owner approval |
| ADR-006 | Administrative geography and operational areas | F05/F09 | F05-admin-boundary-old-new-versions; F09-final-fk-outputs-* | review07-scenario-temporal-assertions.md; schema-convergence-plan.md | passing with RFI boundary | Official publication/territorial rollout still requires SDA acceptance and future implementation order |
| ADR-007 | Subject registry and addressable object cardinality | F04/F10 | F04-cardinality-positive-record-type-*; F04-multi-unit-independent-canonical-records; F10-scenario-* | review07-scenario-temporal-assertions.md; target-schema-catalog.json | passing | Runtime migration/application changes remain out of scope for PR #7 |
| ADR-008 | Temporal versioning and supersession | F05/F07/F10 | F05-corrected-address-two-version-history; F05-admin-boundary-old-new-versions; F07-lifecycle-positive-* | review07-scenario-temporal-assertions.md; lifecycle-transitions.json; target-schema-catalog.json | passing | Dual-read parity and contract/removal authority require future WO-002B |
| ADR-009 | Geometry evidence and provenance | F06 | F06-geometry-authority-negative-suite; F06-invalid-geometry-* | draft-physical-schema.sql; target-schema-catalog.json | passing | Institutional actors/scopes are design evidence only; no runtime role/permission rollout in PR #7 |
