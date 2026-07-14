# ADR-005 through ADR-009 Review 08 Evidence Matrix

This matrix preserves ADRs as proposed and ties each defining guarantee to named executable Review 08 assertions. It does not authorize NLI-WO-002B or production/runtime migration.

| ADR | Claim/constraint | Finding dependency | Named executable assertions | Evidence artifact | Status | Unresolved condition / RFI |
| --- | --- | --- | --- | --- | --- | --- |
| ADR-005 | identity/public aliases/crosswalk authority | F02/F09 | F02-source-row-identity-*; F02-reference-final-fk-*; F09-review08-convergence-* | transformation-fixture-report.json; review08-f09-f11-reconciliation-report.json | proposed; executable evidence passing | NLI-WO-002B unauthorized; owner approval still required |
| ADR-006 | administrative geography and operational areas | F05/F09 | F05-admin-boundary-old-new-versions; F05-temporal-review08-register; F10-administrative-boundary-change-*; F09-reviewed-convergence-unit-* | review08-f04-f07-integrity-report.json; review08-scenario-query-report.json | proposed; executable evidence passing | official territorial rollout/publication authority remains future SDA decision |
| ADR-007 | subject registry and addressable object cardinality | F04/F10 | F04-cardinality-positive-record-type-*; F04-cardinality-review08-matrix; F10-scenario-*; F10-review08-query-sections-* | review08-f04-f07-integrity-report.json; review08-scenario-query-report.json | proposed; executable evidence passing | runtime migration/application changes remain out of scope |
| ADR-008 | temporal versioning and supersession | F05/F07/F10/F12 | F05-temporal-review08-register; F07-lifecycle-positive-*; F07-lifecycle-review08-graph; F12-* | review08-f04-f07-integrity-report.json; semantic-mutation-test-report.json | proposed; executable evidence passing | dual-read parity and removal authority require future WO-002B |
| ADR-009 | geometry evidence and provenance | F06/F12 | F06-geometry-authority-review08; weakened-geometry-authority mutation | review08-f04-f07-integrity-report.json; semantic-mutation-test-report.json | proposed; executable evidence passing | institutional actors/scopes remain design evidence only |
