# S13 — SDA Review Remediation

## Invoke when

- the SDA records `REWORK REQUIRED`;
- a PR contains Blocker, Required, Advisory, Accepted Risk, or Architecture Decision Required findings;
- Review 02 or later is requested;
- a resolution log must be updated.

## Required inputs

- full latest SDA review record;
- exact implementation SHA reviewed;
- all open finding IDs and required resolutions;
- current branch/PR state;
- earlier review records and resolved controls to preserve;
- active work order and standards.

## Procedure

### 1. Protect the review record

Treat these sections as reviewer-owned and immutable:

- outcome;
- review boundary;
- acceptance-criterion decisions;
- finding title/class/observation/risk/required resolution;
- reviewer decision and required follow-up.

The agent may update only the explicitly named resolution-log section. Use a section-bounded updater and a guard test.

### 2. Build a finding-resolution matrix

For every open finding record:

| Finding | Root cause | Required behavior | Specific change | Regression test | Commit | Evidence | RFI | Agent status |
|---|---|---|---|---|---|---|---|---|

Do not reuse one generic evidence list for every finding.

### 3. Identify systemic root causes

Determine whether several findings come from one deeper problem, such as:

- heuristic fallback generation;
- observed and expected truth sharing one source;
- incomplete scope analysis;
- path-only route identity;
- file-presence evidence;
- model metadata not rendered into physical constraints;
- scenario templates rather than real cases;
- stale PR/evidence stamping.

Fix the systemic cause and add regression checks, while still resolving every finding individually.

### 4. Preserve accepted controls

List controls from prior reviews that must not regress. Add explicit tests or checks where remediation could affect them.

### 5. Implement findings in bounded commits

Prefer one logical commit per finding or tightly related group. Commit messages should reference finding IDs.

### 6. Prove the required resolution

Each finding needs evidence directly matching the reviewer’s required resolution. Examples:

- if asked for real DB tests, source-string checks do not qualify;
- if asked for an independent expected registry, generating it from observed output does not qualify;
- if asked for scenario-specific records, adding labels to one generic scenario does not qualify;
- if asked to isolate runtime changes, a note explaining the runtime fix does not qualify.

### 7. Update resolution logs safely

Resolution rows should say:

```text
Agent response:
Fixing commit:
Exact test/evidence:
Agent status: READY FOR SDA REVIEW
```

Do not set SDA disposition to resolved. Only the SDA closes findings.

### 8. Run full regression and exact-head proof

- finding-specific tests;
- previously accepted controls;
- complete relevant CI;
- changed-path guard;
- deterministic regeneration;
- exact-head workflow/job evidence.

## Outputs

- finding-resolution matrix;
- bounded corrections and regression tests;
- protected resolution-log update;
- exact-head evidence;
- review request naming the implementation SHA.

## Stop or RFI conditions

Stop when:

- a required resolution needs an institutional decision;
- a finding cannot be reproduced;
- a proposed fix weakens an accepted control;
- the agent would need to edit reviewer-owned text;
- a valid incidental bug is outside work-order scope;
- one generic generator is being used to bulk-close findings;
- exact required evidence cannot be executed.

## Evidence gate

Before requesting the next SDA review:

- every open finding has a unique root cause and correction;
- every finding has a named passing assertion;
- prior accepted controls still pass;
- only the resolution-log section changed in old review records;
- PR body and evidence are current;
- exact-head CI is green;
- agent statuses say ready for review, not SDA-resolved.

## Anti-patterns

- Replacing every resolution row with the same commit and evidence list.
- Changing reviewer disposition tables.
- Adding files/headings to satisfy review language without implementing semantics.
- Marking all findings fixed because the semantic checker says PASS.
- Fixing symptoms while preserving the heuristic that caused them.
- Requesting the next review immediately after push before exact-head CI completes.
