# NLI Agent Master Operating Protocol

**Purpose:** define the agent’s default behavior from task intake through SDA acceptance.

## 1. Start from authority, not from code

At task start, identify and record:

```text
Programme:
Active work order:
Branch:
Change class: A / B / C
Acceptance criteria:
Referenced ADRs:
Referenced standards:
Explicitly prohibited work:
Current SDA outcome, if remediation:
```

Do not edit implementation until this control header is complete.

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

## 3. Classify every affected path

Before editing, place expected paths into:

| Classification | Meaning |
|---|---|
| In scope | Directly authorized by the work order. |
| Supporting evidence | Necessary test, documentation, or CI evidence authorized by the work order. |
| Separate maintenance | Valid defect or improvement outside the task boundary. |
| Prohibited | Explicitly outside the work order or reserved to another authority. |

If a path changes classification during work, update the plan before editing it.

## 4. Decompose acceptance criteria

For every criterion define:

```text
Criterion:
Observable behavior:
Implementation/model change:
Positive test:
Negative test:
Authority or policy check:
Evidence artifact:
Failure condition:
Residual risk:
```

Do not map several criteria to the same generic sentence unless they are genuinely proven by the same specific assertion.

## 5. Separate observed and expected truth

For every comparison, define two independent sources:

- **Observed:** generated or discovered from the current implementation.
- **Expected:** reviewed source data, standard, ADR, work order, or manually authored fixture.

The same function must not produce both observed and expected results.

Examples:

- observed API policies from implementation; expected policies from a reviewed registry;
- observed database catalog from PostgreSQL; expected target model from reviewed metadata;
- observed scenario results from execution; expected outcomes from independently authored fixtures;
- observed changed paths from Git; expected scope from the work order.

## 6. Implement in bounded, reviewable units

A unit should have:

- one purpose;
- known affected domains;
- its own tests;
- a reversible or forward-recoverable boundary;
- no unrelated cleanup;
- a commit message describing the decision or behavior.

When CI exposes an unrelated defect, stop mixing work and invoke S14.

## 7. Prove semantics, not artefact presence

A claim requires an executable assertion wherever practical.

| Weak evidence | Required stronger evidence |
|---|---|
| File exists | File parses and its contents satisfy exact schema/rules. |
| Row count matches | Values, relationships, authority, classification, and exceptions match. |
| Keyword present | Exact method, field, transition, constraint, or policy is validated. |
| SQL text appears valid | SQL executes in disposable PostgreSQL/PostGIS. |
| Negative result string | The invalid action is executed and fails for the expected reason. |
| CI is green | Named jobs prove the named criteria at the exact head. |
| Generated expected file | Independently reviewed expected source compared with observed output. |

## 8. Run the pre-submission self-audit

Use `templates/self-audit.md`. At minimum verify:

- all acceptance criteria have truthful status;
- no out-of-scope paths changed;
- no review outcome or reviewer finding text changed;
- all negative tests actually execute;
- no fallback heuristic silently accepts unknown values;
- generated files are deterministic;
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
7. Wait for or inspect exact-head CI in the active interaction.
8. Record workflow and job IDs in the PR body/comment.
9. Request SDA review against the exact implementation SHA.

A local clean tree is not a submitted task.

## 10. Remediate review findings precisely

For each finding:

1. quote the finding ID and required resolution;
2. identify root cause, not only symptom;
3. define a finding-specific correction;
4. add a regression or semantic test;
5. commit the correction;
6. record exact evidence;
7. update only the authorized resolution-log section;
8. keep the SDA disposition as `OPEN` until the SDA closes it.

Never generate bulk “resolved” rows from a generic template.

## 11. Completion declaration

Use this form:

```text
Implementation/model status: IMPLEMENTED | PARTIAL | NOT STARTED
Verification status: VERIFIED AT <SHA> | LOCAL ONLY | NOT VERIFIED
Submission status: PR #<n> DRAFT/READY | NOT PUSHED
SDA status: NOT REVIEWED | REWORK REQUIRED | ACCEPTED ...
Remaining findings/RFIs:
Readiness boundary:
```

Do not say “done” without these distinctions.

## 12. Permanent stop conditions

Stop and raise an RFI or isolate work when:

- authority, public-code, publication, boundary, identity, retention, or classification decisions are missing;
- a target field or transformation has no reviewed meaning;
- a current value cannot be mapped without loss;
- expected evidence would be generated by the same logic as observed evidence;
- an unrelated runtime fix appears during design-only work;
- CI can only pass by weakening a control;
- a negative test cannot be executed;
- a review record would need to be rewritten outside its resolution log;
- the task requires production data, credentials, or authority not provided.
