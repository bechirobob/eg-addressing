# S12 — GitHub Delivery and Exact-Head Proof

## Invoke when

- creating or using a branch;
- committing, pushing, or opening/updating a PR;
- requesting SDA review;
- recording CI evidence;
- distinguishing implementation head from review-record head.

## Required inputs

- repository and base branch;
- work-order branch convention;
- local and remote branch state;
- PR template and evidence contract;
- required CI workflows/jobs;
- active SDA review record.

## Procedure

### 1. Verify repository and branch state

Before work:

```text
Repository:
Base branch and SHA:
Task branch and SHA:
Remote branch exists:
PR number/state/draft:
Working tree:
Branch ahead/behind base:
```

### 2. Keep commits bounded

Each commit should identify:

- work order or finding;
- behavior/decision changed;
- tests/evidence included;
- no unrelated cleanup.

A review-record commit is separate from the implementation commit it assesses.

### 3. Push and verify remote submission

After push:

- confirm remote head equals local head;
- confirm branch is ahead of base;
- confirm PR is accessible;
- confirm draft state;
- confirm changed paths remain in scope.

Do not report submission based only on local commits.

### 4. Maintain the PR body accurately

The PR body must state:

- work order;
- implementation/model scope;
- exact current implementation head or reference to an immutable exact-head comment;
- criterion status;
- tests and evidence;
- changed domains and paths;
- RFIs/risks/limitations;
- readiness boundary;
- SDA status.

Remove stale prior-review headings and SHAs.

### 5. Bind exact-head CI

Use this sequence:

1. Push final implementation/evidence commit.
2. Record its SHA.
3. Run/inspect CI for that SHA.
4. Record workflow run IDs, job IDs, conclusions, and artefacts in the PR body or immutable comment.
5. Request SDA review against the implementation SHA.
6. The SDA review record names that SHA and receives a later, separate commit.

A committed evidence file cannot contain its own final SHA. Do not fake one.

### 6. Distinguish heads

Always report:

```text
Implementation/design head reviewed:
Evidence-stamp head, if different:
SDA review-record commit:
Current PR head:
```

When an SDA review record is committed to the task branch, the PR head advances; this does not change the implementation SHA that was reviewed.

### 7. Request review only when reviewable

Before requesting review verify:

- all work is pushed;
- PR exists and is draft/ready as required;
- exact-head jobs completed;
- evidence references exact jobs;
- open finding-resolution rows are updated truthfully;
- no prohibited path changed;
- no stale PR body remains.

## Outputs

- remote branch and draft PR;
- accurate PR body;
- immutable exact-head evidence comment;
- workflow/job evidence;
- review request naming exact implementation SHA.

## Stop conditions

Stop submission when:

- local and remote heads differ;
- branch is not ahead of base;
- no PR exists;
- required CI is pending or failed;
- PR body names a stale head;
- scope guard detects unrelated paths;
- review-resolution rows say resolved without evidence;
- PR was accidentally marked ready or merged before SDA decision.

## Evidence gate

Submission is complete only when GitHub shows:

- pushed commits;
- accessible PR;
- correct draft state;
- exact implementation SHA;
- required workflow/job conclusions;
- changed-path proof;
- review request against that SHA.

## Anti-patterns

- “Agent done” while branch is identical to main.
- Treating a clean local tree as remote submission.
- Recording a final SHA before the final commit.
- Updating an evidence file with a SHA and creating a new unrecorded head.
- Requesting review while exact-head CI is still running.
- Calling the review-record commit the implementation commit.
- Leaving the PR body on Review 03 while requesting Review 06.
