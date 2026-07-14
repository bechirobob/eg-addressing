# Skill 12 — Testing, CI, and Release Evidence

## Use when

Use for every implementation or design-model task that makes a claim requiring proof.

## Objective

Build a risk-proportionate test and evidence system that exercises real behavior, prevents false-positive PASS reports, and binds results to the exact implementation head.

## Procedure

1. Classify the change and identify the highest-risk affected authority/data/workflow.
2. Map each acceptance criterion to an exact executed assertion.
3. Select required test layers:
   - static/type/schema;
   - unit/domain;
   - database/PostGIS integration;
   - authorization policy;
   - API contract;
   - browser/workflow;
   - accessibility/localization;
   - migration/backup/restore;
   - security/abuse;
   - performance/failure/recovery;
   - deterministic generation and clean-diff.
4. Use real dependencies where behavior depends on them.
5. Define positive, negative, boundary, concurrency, collision, cross-scope, failure, and recovery cases.
6. Maintain independently reviewed expected results where observed results are generated.
7. Ensure every named negative test executes the prohibited operation and verifies the expected reason.
8. Ensure every scenario validates scenario-specific behavior and output.
9. Build and test the actual deployable image/runtime when packaging matters.
10. For generated artifacts:
    - make generation portable and deterministic;
    - prevent self-modification;
    - run it in CI;
    - require clean post-generation diff;
    - report only executed assertions.
11. Run required jobs at the exact remote head.
12. Record workflow/run/job IDs and retained artifacts.
13. Re-run after any evidence or review-record commit that changes executable/generation behavior.

## Required evidence

- Criterion-to-test matrix
- Exact commands/jobs
- Positive and negative results
- Environment/dependency versions
- Exact implementation SHA
- Workflow/run/job IDs
- Artifacts/screenshots/reports
- Skipped checks and reason
- Residual risk

## False-positive checks

CI must fail when:

- expected and observed results are produced from the same unchecked source;
- a mapping target exists but example/type/vocabulary is wrong;
- a scenario name exists but scenario-specific facts are missing;
- a negative result was assigned rather than executed;
- a claimed constraint is absent from the physical catalog;
- a route policy’s method/path/handler/roles disagree;
- the generator changes tracked artifacts unexpectedly;
- evidence references a stale head.

## Stop and escalate when

- Required behavior cannot be tested in the available environment.
- A test would require production data or credentials.
- A failing gate is believed to be wrong but no authority exists to change it.
- The PR contains a valid unrelated runtime fix outside scope.

## Anti-patterns

- Disabling or weakening checks to get green CI.
- Treating source inspection as integration proof.
- Counting constraints/indexes without checking the required ones.
- Reporting “semantic validation” from file/string/count checks.
- Using local results while remote exact-head jobs are red or absent.
- Adding a report that always says PASS unless the script crashes.
