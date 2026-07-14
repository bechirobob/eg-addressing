# Skill 01 — Task Intake and Routing

## Use when

Use at the beginning of every task, including follow-up requests such as “agent done,” “fix the review,” or “continue.”

## Objective

Convert the request into an explicit, bounded task governed by the correct repository authority and skill set.

## Required inputs

- User request or GitHub issue/PR comment
- Repository and branch context
- Root `AGENTS.md`
- Active SDA work order, if any
- Current PR/review state

## Procedure

1. **Resolve the task object.** Identify the repository, issue, PR, branch, work order, and exact baseline commit.
2. **Restate the requested outcome.** Separate what must change from what must be proven.
3. **Identify authority.** Determine whether the request is already authorized by a work order, requires an RFI, or needs a new work order/maintenance item.
4. **Classify the change.** Assign Class A, B, or C using `docs/agent-skills/README.md`.
5. **Identify affected domains.** Database, API, identity, security, GIS, UI, operations, documentation, release, or programme authority.
6. **Route skills.** Select every applicable skill module and record why.
7. **Set the boundary.** State in-scope, out-of-scope, prohibited, and separately tracked work.
8. **Check readiness to proceed.** Confirm required files, access, branch, and decision authority exist.

## Required output

```text
Task:
Repository:
Exact baseline:
Active work order:
Change class:
Skills invoked:
In scope:
Out of scope:
Authority/RFIs:
First checkpoint:
```

## Evidence standard

The task header must point to the actual work order, branch, issue/PR, and exact baseline—not memory or an older PR body.

## Stop and escalate when

- No active authority permits the requested change.
- The requested outcome conflicts with an accepted ADR or standard.
- The task mixes design-only and runtime implementation without explicit authorization.
- A public, official, identity, retention, security, or data-loss decision is unstated.

## Anti-patterns

- Starting to code because the request sounds straightforward.
- Treating “done” as proof that work exists remotely.
- Reusing the previous task’s branch or acceptance criteria without checking.
- Selecting only the most obvious technical skill and ignoring security, operations, or evidence.
