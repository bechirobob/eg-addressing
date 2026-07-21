# SDA Assessment — Addresses Identity Foundation

**Reviewed implementation:** `5bce5707f21f6d5ed3098c1a5a7158557ae7f492`  
**Outcome:** `CORRECTION REQUIRED — INTEGRATION CONTROLS ONLY`

## Accepted implementation behavior

The explicit `transform_addresses_identity_crosswalk` slice is materially credible. It queries the complete normalized `addresses` row, validates the reviewed live specification, derives ID-based lineage, enforces government-internal source/evidence classification, creates exactly one location record, one active registry subject and one addresses-ID crosswalk, preserves absolute crosswalk uniqueness, proves second-run idempotency, excludes prohibited outputs, uses a separate read-only comparator and records same-database rollback evidence.

The implementation delta is one commit and changes only the live addresses transform-spec row, the one-slice report and `authoritative_harness.py`. The parent addresses oracle and accepted geometry controls were not changed.

## Blocking findings

### C18 — Exact-head SDA CI is red

At the exact implementation head, `api-ci` run `29453878093` failed. A rerun confirmed `sda-design-model` fails again in the non-authoritative Phase A harness step. API tests passed on rerun, so the remaining failure is reproducible and confined to the SDA harness checkpoint.

The live addresses row now uses `source_record_key = addresses:phase-a-addresses-id`. The paused broad generic harness still indexes the raw fixture under `addresses:phase-a-addresses-001` and directly dereferences each group source-record key. The broad path therefore consumes a narrow specification it was not designed to execute.

Required correction: freeze the broad generic transform-spec input at reviewer head `b303a85ce55f8d50c43369c983ad5a8d67e5fcc4`; broad commands use the frozen fixture, while narrow slices continue using the live specification. Do not rewrite broad expected-target fixtures or hashes.

### C19 — Complete-set comparison misses surplus orphan identity rows

The comparator discovers location records and subjects only through crosswalk target IDs. A surplus source-derived location record or registry subject with no extra crosswalk is not returned. Add `unexpected-extra-location-record` and `unexpected-extra-registry-subject` mutations and make the read-only comparator reject both. Each failure must prove same-database rollback before reset.

### C20 — The addresses slice is not executed by CI

The existing SDA workflow runs `phase-a-all` and the three geometry slices, but not `addresses-identity-slice`. Add the new slice after a fresh disposable-database reset and retain the final generated-diff check.

## Decision boundary

Only C18–C20 are authorized. Preserve the existing addresses implementation, parent oracle, accepted geometry controls and all current mutation evidence. Do not implement another identity group, update broad expected fixtures, request broad reassessment or Review 12, or touch runtime/deployment scope.

Reviewer correction control:

`docs/sda/acceptance/NLI-WO-002-addresses-identity-ci-correction.json`

After correction, obtain green exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend jobs, then stop for final pattern assessment.
