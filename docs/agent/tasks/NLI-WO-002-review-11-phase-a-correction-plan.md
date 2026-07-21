# NLI-WO-002 Review 11 Phase A Correction Plan

## Authority header

| Item | Value |
|---|---|
| Reviewer-owned start head | `2671ee9dfd6fa6312dadbb4033834bd3a2c5900d` |
| Reviewed Phase A implementation | `25de8fb258ee0b45c18eced979e39d6d54df99ac` |
| Assessment record | `docs/sda/reviews/NLI-WO-002-review-11-phase-a-assessment.md` |
| Decision | `PHASE A CORRECTION REQUIRED` |
| Authorized correction | A2 independent fixture authority and A3 authoritative F02 execution only |
| Prohibited | Phase B, F04-F12 implementation, Review 12 request, PR #8 contamination, runtime/app/migration/Docker/data/secrets changes |

## Scope

Correct the Phase A harness so it proves the F02/F14 checkpoint at the Phase A level:

1. Preserve accepted A1 topology: `current_source`, `canonical_target`, `test_control`, controlled migration runner use, non-authoritative CI step.
2. Build a machine-checked 237-field coverage matrix from `current-pg-catalog.json` and `transformation-registry-reviewed.json`.
3. Replace aggregate expected-target evidence with complete typed expected rows.
4. Bind transform groups to explicit implementation units and fail on spec/implementation drift.
5. Correct geotag spatial observation/provenance/quality/authority handling.
6. Correct correction-case identity, crosswalk, archive, unresolved-reference exception, and remove the invalid self-correction relationship.
7. Query evidence from PostgreSQL, including actual rows, FK targets, duplicate checks and typed hashes.
8. Replace duplicate/manual probes with distinct normal-path mutations that rollback and prove unchanged state.
9. Add cleanup/recreate proof.

## Why this approach

The prior Phase A commit proved the skeleton but not complete authority. This correction keeps the accepted topology and makes the harness compare independently maintained reviewed inputs against actual `canonical_target` rows queried from PostgreSQL.

## Files likely touched

- `.github/workflows/api-ci.yml` — preserve non-authoritative Phase A CI step and add cleanup lifecycle proof if needed.
- `docs/sda/data-model/scripts/authoritative_harness.py` — Phase A A2/A3 correction only.
- `docs/sda/data-model/fixtures/current-source/phase-a-complete-source-records.json` — complete table-level source records covering 25 current tables.
- `docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json` — reviewed group declarations bound to implementation units.
- `docs/sda/data-model/fixtures/expected-target/phase-a-expected-target-records.json` — complete typed expected row set.
- `docs/sda/data-model/fixtures/mutations/phase-a-negative-probes.json` — distinct normal-path probes.
- `docs/sda/data-model/phase-a-*.json` — regenerated Phase A evidence reports.
- `docs/sda/data-model/phase-a-legacy-vs-authoritative.md` — preserve legacy-vs-authoritative framing.
- `docs/agent/tasks/NLI-WO-002-review-11-phase-a-s16-self-audit.md` — updated Phase A correction S16.
- `docs/sda/reviews/NLI-WO-002-review-11.md` — update only F02/F14 agent-response cells.

## Expected outcome

- `current pg_catalog fields = 237`
- `reviewed transformation fields = 237`
- `authoritative executed dispositions = 237`
- `missing fields = 0`
- `duplicate field claims = 0`
- `conflicting dispositions = 0`
- `unexecuted transform groups = 0`
- actual and expected target row sets match bidirectionally
- second-run inserts/updates are zero
- duplicate counts are queried, not hard-coded
- cleanup/recreate proof passes
- exact-head CI green
- PR #7 remains open/draft/unmerged

## Risks and mitigation

| Risk | Mitigation |
|---|---|
| Accidentally drifting into F04-F12 | Keep this harness limited to F02/F14 evidence; leave legacy guardrails intact and labelled legacy. |
| Creating a new shadow framework | Use only `current_source`, `canonical_target`, `test_control`; no `r11_*` schemas. |
| Expected rows becoming generated truth | Keep expected fixture as committed JSON input; harness validates and hashes it but does not author/repair it. |
| Semantic overclaim on administrative authority | Use separate conditional government reference authority, `non_official=true`, and open authority RFI links. |
| False-positive negative probes | Mutate one input per probe, run the normal path, assert named gate/reason, rollback, and compare before/after state hash. |

## Verification steps

1. Run Phase A harness locally in a fresh disposable DB.
2. Run legacy guardrails locally.
3. Run `validate_skill_pack.py` and `git diff --check`.
4. Prove prohibited paths absent.
5. Commit and push.
6. Verify local/remote/PR head equality.
7. Wait for exact-head CI: agent skills, API jobs including `sda-design-model`, frontend.
8. Update PR body to Phase A correction/reassessment framing.
9. Request Phase A reassessment only, not SDA Review 12.
