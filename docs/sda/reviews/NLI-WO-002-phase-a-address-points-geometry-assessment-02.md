# SDA Pattern Assessment 02 — Address-Points Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-01-ASSESSMENT-02`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `64ad44b8553dcd0f18bd7dd41363230fb492862b`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `CORRECTION REQUIRED — FINAL SAME-SLICE CONTROL FIXES`

## 1. Review boundary

Reviewed the exact delta after reviewer-owned assessment head `04110902f655102fc859a884477fd2a373065042`, the corrected explicit transform, source and lineage derivation, transform-spec validation, typed PostGIS insertion, read-only positive comparator, complete attributable row-set queries, precision and second-identity tests, implementation/source/spec/extra-row mutations, same-database rollback evidence, oracle integrity, changed-path boundary and exact-head workflows.

Independent repository verification:

- PR #7 is open, draft, mergeable and unmerged.
- Reviewed head is `64ad44b8553dcd0f18bd7dd41363230fb492862b`.
- Changed paths after the prior reviewer head are limited to the one-slice task record, one-slice report and `authoritative_harness.py`.
- Neither reviewer-owned oracle changed.
- No other transform group, F04–F12, runtime application, migration, migration runner, Docker runtime, production/pilot data, secret, `.env*` or PR #8 path changed.

Independent exact-head verification:

- Agent-skills CI run `29427802869`: success.
- API CI run `29427802986`: success.
  - `sda-design-model` job `87394670483`: success.
  - `api-tests` job `87394670537`: success.
  - `migration-lifecycle` job `87394670583`: success.
  - `api-image-runtime` job `87394670495`: success.
- Frontend CI run `29427802976`, job `87394669635`: success.

## 2. Corrections accepted

The following C01–C07 corrections are accepted and must be preserved:

1. Source coordinate precision is preserved through typed `ST_MakePoint` parameters; the precision case returns `POINT(8.7834567 3.7523456)` with SRID 4326.
2. Source key, source record, evidence object, geometry ID, exception ID and exception source key derive from the queried source identity.
3. A second source identity is handled without changing the transform implementation.
4. The reviewed group, implementation unit, callable, covered fields and target entity are checked before dispatch.
5. Positive comparison uses a separate read-only connection and queries all geometry observations and exceptions attributable to the source key.
6. Unexpected additional target rows fail comparison.
7. The wrong-longitude mutation changes transform calculation after querying an unchanged source row.
8. The invalid-coordinate test updates the actual `current_source.address_points` row.
9. Main mutation cases compare pre-test and post-rollback state in the same database before reset.
10. The explicit slice remains independent from the generic all-groups dispatcher.

## 3. Final corrections required

### C08 — Transformation code still reads the reviewer-owned expected oracle

`transform_address_points_geometry()` calls `load_address_points_oracle(True)` to obtain `source_method_translation`. The parent oracle explicitly forbids transformation code from reading it. Separate files and an unchanged hash are insufficient when the observed-output producer reads expected truth.

**Required correction:** Move `source_method_translation` into the reviewed transform-spec row or another implementation input that is not under `docs/sda/acceptance/`. The transform may read the reviewed spec but must not read either acceptance oracle. Add a runtime/static guard proving the transform succeeds when access to both oracle loaders is denied and fails the checkpoint if transformation code calls them.

### C09 — Required-context-field validation is tautological

`reviewed_address_points_transform_spec()` obtains `required_context_fields` directly from the correction oracle and then compares that list with the same oracle list. The actual transform-spec row does not supply the context-field declaration, so context-field drift cannot be detected. The source-method translation is also outside the actual spec.

**Required correction:** Add `required_context_fields` and `source_method_translation` to the one authorized transform-spec row. Load both from that row. Compare the actual spec values against the immutable correction oracle before dispatch. Add distinct drift tests for context fields and source-method translation, in addition to the existing implementation-unit drift test.

### C10 — Missing-source rollback evidence is asserted rather than measured

The missing-source test follows a separate branch that reports `state_unchanged: true` without recording a same-database pre-test and post-failure row-set/hash comparison. C07 required this proof after every failed test before reset.

**Required correction:** Route the missing-source test through the same same-database rollback-evidence mechanism, or provide equivalent measured pre/post row sets and hashes in the same database before reset. Remove any hard-coded state-unchanged claim without raw hash evidence. Require every negative test in the slice report to contain measured rollback evidence or an explicit comparator-only classification where no database write was attempted.

## 4. Decision

`CORRECTION REQUIRED — FINAL SAME-SLICE CONTROL FIXES`

The domain transform itself is now materially sound. Pattern acceptance is withheld only because the producer still reads expected truth, one binding check is self-referential and one failure-state claim lacks measured evidence. These are narrow acceptance-control defects; no broad redesign is required.

## 5. Authorization boundary

Authorized:

- C08–C10 corrections for `WO002-R06-geometry-observation-address_points` only.
- Updating the one authorized transform-spec row with its context fields and source-method translation.
- Updating the one-slice implementation, tests, evidence, task record and non-authoritative CI step.

Not authorized:

- Implementing or modifying any other transform group.
- Broad Phase A reassessment.
- SDA Review 12.
- F04–F12 remediation.
- Runtime application/frontend code, executable migrations, migration-runner, Docker runtime, production/pilot data, secrets, `.env*` or PR #8 changes.

## 6. Reviewer-owned final correction oracle

The implementation must obey and must not modify:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-final-correction-oracle.json
```

The two existing reviewer-owned oracles remain immutable.

## 7. Next checkpoint

Implement C08–C10 only, push exact-head evidence, stop and request final assessment of this one pattern. Do not replicate the pattern before the SDA records acceptance.
