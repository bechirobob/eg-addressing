# NLI-WO-002 Phase A Legacy-vs-Authoritative Harness Distinction

## Boundary

Phase A adds an authoritative checkpoint harness for F02/F14 only. Existing Review 04–10 checks remain legacy guardrails and continue to run in CI, but they are not treated as final SDA acceptance evidence for F02–F12.

## Authoritative Phase A evidence

| Area | Evidence |
|---|---|
| Current-source topology | `phase-a-current-source-catalog-report.json` |
| Canonical-target topology | `phase-a-canonical-target-catalog-report.json` |
| Schema leakage / test-control isolation | `phase-a-topology-schema-leakage-report.json` |
| Complete-source fixture inventory | `phase-a-complete-source-record-fixture-inventory.json` |
| Target transform inventory | `phase-a-target-entity-transform-inventory.json` |
| Real FK / crosswalk evidence | `phase-a-target-fk-crosswalk-evidence.json` |
| Archive / exception evidence | `phase-a-archive-exception-evidence.json` |
| First-run / second-run idempotency | `phase-a-idempotency-evidence.json` |
| Strict negative probes | `phase-a-strict-negative-probe-report.json` |

## Legacy guardrails preserved

| Legacy guardrail | Phase A status |
|---|---|
| `review04_design_pipeline.py` | Still runs as existing design-pack generator/legacy guardrail. |
| `design_consistency_check.py` | Still runs after legacy generator. |
| Review 09/10 F02/F04–F12 scripts | Kept in repository; not removed or treated as Phase A authoritative evidence. |

## Non-claims

- Phase A does not resolve F04–F12.
- Phase A does not retire legacy guardrails.
- Phase A does not switch the SDA acceptance authority to the new harness.
- Phase A does not request SDA Review 12.
