# S01 — Authority, Intake, and Scope Control

## Invoke when

Every task, including follow-ups, review remediation, documentation, maintenance, and emergency work.

## Required inputs

- root `AGENTS.md`;
- `docs/sda/README.md`;
- active work order and acceptance criteria;
- referenced ADRs and standards;
- current PR/issue and latest SDA review;
- base branch, task branch, and exact SHAs.

## Procedure

### 1. Build the authority header

```text
Programme:
Programme Owner instruction:
Active work order:
Current SDA outcome:
Highest applicable ADR:
Mandatory standards:
Change class: A / B / C
```

### 2. Resolve the task boundary

Record four lists:

```text
IN SCOPE
SUPPORTING EVIDENCE
SEPARATE MAINTENANCE
PROHIBITED
```

Classify anticipated file paths and behavior, not only feature names.

### 3. Resolve the readiness boundary

State what the task may legitimately claim after success:

- design produced;
- implementation produced;
- pilot behavior tested;
- agency behavior tested;
- publication readiness assessed;
- production readiness assessed.

Do not inherit a higher readiness label from another task.

### 4. Check branch and PR state

Verify remotely:

- correct branch exists;
- branch base is correct;
- current PR number and draft state;
- whether branch contains unrelated commits;
- whether review record commits changed the PR head;
- whether local and remote heads match.

### 5. Select skill cards

Use `skill-manifest.yaml`. List every selected skill and trigger.

## Outputs

- completed authority header;
- path/behavior scope matrix;
- readiness boundary;
- selected skill list;
- branch/PR state summary.

## Stop or RFI conditions

Stop before editing when:

- no active work order covers a Class A or B change;
- the user request conflicts with an accepted ADR or standard;
- the requested path is explicitly prohibited;
- the work would change public authority, identifiers, administrative hierarchy, retention, classification, roles, or publication behavior without a decision;
- the active branch contains unrelated runtime changes;
- the requested task is based on a stale or superseded review.

## Evidence gate

Before the first implementation edit, the plan must identify:

- exact work order;
- exact acceptance criteria;
- exact expected changed paths;
- prohibited paths;
- current base and task SHAs;
- PR/draft state;
- selected skills.

## Anti-patterns

- “This is just documentation,” without checking whether it changes authority.
- Fixing an unrelated production bug inside a design-only PR.
- Treating a CI-only path as automatically supporting evidence when the work order prohibits it.
- Assuming the current PR head equals the implementation head after a review record is committed.
- Asking for confirmation on decisions the work order already authorizes.
- Proceeding because the change appears small while its authority effect is large.
