# S16 — Self-Audit and Context Handoff

## Invoke when

- before every completion or review-request message;
- after a long-running task or major context shift;
- before handing work to another agent or human;
- before rebasing, splitting a PR, or changing branches;
- when conversational context may differ from repository truth.

## Required inputs

- current task context pack;
- active work order and review;
- branch/PR exact state;
- changed paths and commits;
- tests and CI evidence;
- open RFIs/findings/risks;
- readiness boundary.

## Procedure

### 1. Re-read authoritative records

Before reporting status, re-read:

- root `AGENTS.md`;
- active work order;
- latest SDA review and resolution log;
- PR metadata and exact remote head;
- changed-path diff;
- exact-head workflow runs.

Do not rely on the agent’s remembered state.

### 2. Run the self-audit checklist

Use `templates/self-audit.md` and verify:

- authority and scope;
- criterion status;
- review-record integrity;
- expected/observed independence;
- positive and negative evidence;
- changed-path compliance;
- exact-head submission;
- readiness claims;
- residual risks.

### 3. Detect stale or contradictory artefacts

Search for:

- old review numbers or SHAs in the PR body;
- “pending final head” after CI completed;
- evidence claiming no runtime change while runtime paths changed;
- agent resolution rows that say SDA-resolved;
- generated PASS reports that overstate executed checks;
- stale ADR status or work-order boundary;
- local work not pushed.

### 4. Build the context handoff

A handoff must contain:

```text
Repository and branch:
Base SHA:
Current implementation/model SHA:
Current PR and draft state:
Active work order:
Latest SDA outcome/review record:
Completed work:
Exact tests/workflow IDs:
Open findings/RFIs:
Prohibited next actions:
Exact next step:
```

Include file paths and stable identifiers, not a long narrative.

### 5. Produce truthful completion state

Report:

```text
Implementation/model status:
Verification status:
Remote submission status:
SDA acceptance status:
Open conditions:
Readiness boundary:
```

If any line is unknown, say unknown and identify how it must be verified.

### 6. Preserve reproducibility

Ensure a new agent can continue using only:

- repository records;
- branch/PR state;
- exact commits;
- issue/review identifiers;
- tests and evidence.

No essential decision may exist only in chat.

## Outputs

- completed self-audit;
- compact context handoff;
- corrected stale metadata;
- truthful completion declaration;
- exact next action.

## Stop conditions

Do not report done or request review when:

- PR head is not verified;
- required CI is missing/pending/failed;
- changed paths violate scope;
- evidence is stale;
- findings are bulk-stamped without proof;
- review records were modified outside resolution logs;
- local and remote state differ;
- readiness language exceeds the recorded SDA decision.

## Evidence gate

A handoff is complete only when another agent can identify:

- what authority applies;
- what exact commit to inspect;
- what passed;
- what remains open;
- what may not be changed;
- what action comes next.

## Anti-patterns

- “Everything is done” with no exact SHA or PR.
- Repeating conversational history instead of current repository state.
- Omitting an out-of-scope dependency or separate maintenance PR.
- Reporting green CI without naming the run/job.
- Treating the latest branch head as the implementation head after a review-record commit.
- Ending with an offer instead of a precise next action.
