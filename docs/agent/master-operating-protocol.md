# NLI Agent Master Operating Protocol

**Purpose:** define the agent’s default behavior from task intake through SDA acceptance across the complete NLI programme.

## 1. Start from authority and project impact, not from code

At task start, identify and record:

```text
Programme:
Active work order:
Branch:
Change class: A / B / C
Acceptance criteria:
Referenced ADRs:
Referenced standards:
Current SDA outcome, if remediation:
Explicitly prohibited work:

Affected repository areas:
Affected bounded domains:
Affected modules/applications:
Affected roles/institutions/scopes:
Affected trust zones/environments:
Affected lifecycle stages:
Cross-cutting skills S01-S16:
Whole-project skills S17-S31:
Skills considered but not applicable:
```

Use `PROJECT-COVERAGE-MATRIX.md` and `skill-manifest.yaml`. Do not edit files until this control header is complete.

## 2. Establish the exact repository state

Record:

- repository;
- base branch and SHA;
- task branch and SHA;
- open PR number and draft state, if any;
- current CI state;
- existing review records and unresolved findings;
- local working-tree state.

Never assume local work has been pushed. Submission requires remote verification.

## 3. Classify every affected path and behavior

Before editing, place expected paths into:

| Classification | Meaning |
|---|---|
| In scope | Directly authorized by the work order. |
| Supporting evidence | Necessary test, documentation, CI, fixture, runbook, or operational evidence authorized by the work order. |
| Separate maintenance | Valid defect or improvement outside the task boundary. |
| Prohibited | Explicitly outside the work order or reserved to another authority. |

Also classify affected behavior across frontend, backend, database, identity, GIS, evidence, citizen, registry, field, publication, integration, worker, analytics, platform, performance, support/training, rollout, and programme surfaces.

If a path or behavior changes classification during work, update the plan before editing it.

## 4. Decompose acceptance criteria

For every criterion define:

```text
Criterion:
Observable product/operational result:
Affected modules/roles/environments:
Implementation/model change:
Positive test:
Negative test:
Authority or policy check:
Operational/support/recovery check:
Evidence artifact:
Failure condition:
Residual risk:
```

Do not map several criteria to the same generic sentence unless they are genuinely proven by the same specific assertion.

## 5. Separate observed and expected truth

For every comparison, define two independent sources:

- **Observed:** generated or discovered from the current implementation/runtime.
- **Expected:** reviewed source data, standard, ADR, work order, independently authored contract/fixture, or authority decision.

The same function must not produce both observed and expected results.

Examples:

- observed API policies from implementation; expected policies from a reviewed registry;
- observed database catalog from PostgreSQL; expected target model from reviewed metadata;
- observed scenario results from execution; expected outcomes from independently authored fixtures;
- observed changed paths from Git; expected scope from the work order;
- observed dashboard values from queries; expected metric definitions from a reviewed data-product dictionary;
- observed partner deliveries from runtime; expected contract/reconciliation rules from a reviewed integration agreement.

## 6. Implement in bounded, reviewable units

A unit should have:

- one purpose;
- known affected domains, modules, roles, and environments;
- selected S17–S31 skills;
- its own tests and evidence;
- a reversible or forward-recoverable boundary;
- operational, support, and rollout implications where applicable;
- no unrelated cleanup;
- a commit message describing the decision or behavior.

When CI exposes an unrelated defect, stop mixing work and invoke S14.

## 7. Prove semantics and operational outcomes, not artefact presence

A claim requires an executable assertion wherever practical.

| Weak evidence | Required stronger evidence |
|---|---|
| File exists | File parses and satisfies exact schema/rules. |
| Route exists | Intended role completes the workflow and deny cases fail. |
| Row count matches | Values, relationships, authority, classification, and exceptions match. |
| Keyword present | Exact method, field, transition, constraint, or policy is validated. |
| SQL text appears valid | SQL executes in disposable PostgreSQL/PostGIS. |
| Negative result string | Invalid action executes and fails for the expected reason. |
| Queue job exists | Idempotent retry, failure, recovery, and reconciliation execute. |
| Dashboard screenshot | Metric lineage, source parity, scope, freshness, and classification are verified. |
| Backup exists | Restore executes and source/restored invariants match. |
| Training document exists | Target users complete the version-matched exercise and support gaps are recorded. |
| CI is green | Named jobs prove named criteria at the exact head. |
| Generated expected file | Independent reviewed expected source is compared with observed output. |

## 8. Run the pre-submission whole-project self-audit

Use `templates/self-audit.md`. At minimum verify:

- all acceptance criteria have truthful status;
- selected S01–S16 and S17–S31 skills match actual effects;
- all affected modules, roles, trust zones, environments, and lifecycle stages were assessed;
- no out-of-scope paths or behaviors changed;
- no review outcome or reviewer finding text changed;
- all negative tests actually execute;
- no fallback heuristic silently accepts unknown values;
- generated files are deterministic;
- frontend/backend/API/data/GIS/security/integration/worker/analytics/platform behavior is covered where affected;
- migration, monitoring, support, training, rollout, backup/recovery implications are addressed where affected;
- exact-head evidence procedure is ready;
- PR remains draft when acceptance is pending;
- readiness claims are bounded.

## 9. Submit through GitHub correctly

Submission sequence:

1. Commit bounded work.
2. Run local tests where appropriate.
3. Push branch.
4. Open or update a draft PR.
5. Verify remote branch is ahead of base.
6. Verify PR head SHA.
7. Inspect exact-head CI in the active interaction.
8. Record workflow/job IDs in the PR body/comment.
9. Record affected cross-cutting/domain skills, modules, roles, environments, and operational paths.
10. Request SDA review against the exact implementation SHA.

A local clean tree is not a submitted task.

## 10. Remediate review findings precisely

For each finding:

1. quote the finding ID and required resolution;
2. identify root cause, not only symptom;
3. identify all affected cross-cutting and whole-project skills;
4. define a finding-specific correction;
5. add a regression or semantic test;
6. assess adjacent product/operational paths so the same defect is not repeated elsewhere;
7. commit the correction;
8. record exact evidence;
9. update only the authorized resolution-log section;
10. keep the SDA disposition as `OPEN` until the SDA closes it.

Never generate bulk “resolved” rows from a generic template.

## 11. Completion declaration

Use this form:

```text
Implementation/model status: IMPLEMENTED | PARTIAL | NOT STARTED
Verification status: VERIFIED AT <SHA> | LOCAL ONLY | NOT VERIFIED
Submission status: PR #<n> DRAFT/READY | NOT PUSHED
SDA status: NOT REVIEWED | REWORK REQUIRED | ACCEPTED ...
Affected modules/roles/environments:
Operational/training/rollout status:
Remaining findings/RFIs:
Separate maintenance dependencies:
Readiness boundary:
Exact next action:
```

Do not say “done” without these distinctions.

## 12. Permanent stop conditions

Stop and raise an RFI or isolate work when:

- authority, public-code, publication, boundary, identity, retention, classification, metric, partner-purpose, or rollout decisions are missing;
- a target field or transformation has no reviewed meaning;
- a current value cannot be mapped without loss;
- expected evidence would be generated by the same logic as observed evidence;
- an unrelated runtime fix appears during design-only work;
- CI can only pass by weakening a control;
- a negative test cannot be executed;
- a review record would need to be rewritten outside its resolution log;
- the task requires production data, credentials, or authority not provided;
- a release lacks migration, identity, security, monitoring, support, training, or recovery readiness;
- a future implementer/operator would need to invent architecture, authority, metric meaning, support ownership, or failure behavior.
