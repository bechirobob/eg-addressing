# Skill 05 — Scope, Git, and Exact-Head Control

## Use when

Use for branch creation, PR preparation, scope review, unrelated defect discovery, evidence closeout, or any claim tied to a commit.

## Objective

Keep work orders auditable, prevent mixed-scope PRs, and ensure evidence belongs to the exact implementation reviewed.

## Procedure

1. Confirm approved base ref and exact SHA.
2. Create or check out the branch named by the work order.
3. Verify local/remote branch alignment before changes.
4. Maintain a scope ledger:
   - authorized paths and behavior;
   - prohibited paths and behavior;
   - discovered unrelated items.
5. Make intentional commits grouped by bounded purpose.
6. When an unrelated defect is found:
   - document it;
   - create a separate maintenance issue/branch/PR;
   - remove it from the active branch;
   - preserve relevant regression evidence.
7. Before review, compare branch to base and inspect every changed path.
8. Push and verify the remote head equals the intended local head.
9. Run required CI at that exact head.
10. Record the implementation SHA and workflow/job IDs in PR metadata/comment.
11. Keep the PR draft/ready state required by the work order.
12. Leave the working tree clean.

## Exact-head evidence rule

Do not attempt a self-referential committed SHA. Use:

```text
implementation commit
→ CI runs against that commit
→ immutable PR comment/metadata records SHA and run IDs
→ later SDA review record identifies the implementation commit
```

## Required output

- Base SHA
- Branch and remote head
- Changed-path inventory
- Scope compliance result
- Exact-head CI runs/jobs
- Working-tree status
- PR state
- Separate issues/PRs for unrelated work

## Stop and escalate when

- A valid fix changes a path prohibited by the active work order.
- Remote and local heads differ.
- CI ran on an older commit.
- PR evidence names a stale head.
- The work order requires draft status but the PR is marked ready or merged.

## Anti-patterns

- Mixing design documents and runtime fixes because the fix is small.
- Claiming exact-head success using CI from the previous commit.
- Updating the PR body with an old SHA and never correcting it.
- Force-updating accepted history without explicit authority.
- Treating a clean local tree as proof that changes were pushed.
