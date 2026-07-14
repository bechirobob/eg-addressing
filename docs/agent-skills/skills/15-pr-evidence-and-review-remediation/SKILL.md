# Skill 15 — Pull-Request Evidence and Review Remediation

## Use when

Use when opening a PR, responding to SDA findings, preparing exact-head review, updating evidence, or closing an accepted work order.

## Objective

Submit a reviewable PR whose scope, claims, tests, and residual risks can be assessed criterion by criterion, then resolve findings without altering reviewer authority.

## Initial PR procedure

1. Confirm branch, base, work order, change class, and PR state.
2. Use `.github/PULL_REQUEST_TEMPLATE.md` and `docs/sda/templates/pull-request-evidence.md`.
3. Include:
   - objective and readiness boundary;
   - acceptance-criterion matrix;
   - file/domain inventory;
   - architecture/ADR/standard alignment;
   - database/API/security/GIS/UI/operations/documentation effects;
   - exact tests and results;
   - migrations/recovery details;
   - screenshots/artifacts;
   - RFIs, deviations, limitations, and residual risks.
4. Keep the PR draft until the work order permits ready-for-review status.
5. Bind evidence to the exact implementation head through CI and PR metadata/comment.

## Review-remediation procedure

1. Read the complete review record, not only the PR summary comment.
2. Preserve the reviewer’s outcome, finding class, observation, required resolution, and disposition.
3. Build a finding matrix:

| Finding | Root cause | Required change | Exact test/evidence | Commit | Residual condition |
|---|---|---|---|---|---|

4. Resolve findings in bounded commits; do not bulk-stamp every finding with the same artifact.
5. Add a regression test for the actual defect, not merely the desired file/string.
6. Update only the designated resolution-log section.
7. Re-run all affected jobs at the new exact head.
8. Update controlled evidence truthfully; use `PARTIAL` or `FAIL` when appropriate.
9. Verify remote head, PR state, changed paths, and clean working tree.
10. Request the next SDA review and name the exact implementation commit.

## Acceptance preparation

Before requesting acceptance:

- every acceptance criterion has specific evidence;
- every finding has a finding-specific commit and test;
- CI is green at the exact implementation head;
- no out-of-scope path remains;
- PR body/evidence are not stale;
- required review record exists;
- no readiness claim exceeds authority;
- branch remains unmerged until acceptance permits merge.

## Required evidence

- Exact head
- Workflow/run/job IDs
- Changed-path proof
- Criterion matrix
- Finding-resolution matrix
- Artifacts/screenshots/reports
- Residual risks/conditions
- PR draft/ready/merged state

## Stop and escalate when

- A finding requires architecture or institutional authority.
- A valid fix is outside the active work order.
- Evidence cannot truthfully show resolution.
- The reviewer record was modified outside the agent resolution section.
- New commits invalidate the previously cited exact-head CI.

## Anti-patterns

- Marking all findings resolved with the same generic report.
- Updating resolution rows before the fix/test exists.
- Saying CI is green using runs from the prior head.
- Making the PR ready or merging before SDA acceptance.
- Rewriting the review outcome or reviewer disposition.
- Treating “agent done” as a review result.
- Leaving a stale PR body that names an older head and old review stage.
