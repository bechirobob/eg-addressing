# S14 — Maintenance-Fix Isolation

## Invoke when

- CI exposes a real defect outside the active work order;
- design-only work reveals a runtime bug;
- a security, migration, packaging, or operational fix is valid but unrelated;
- emergency maintenance is required;
- a scope guard detects an incidental change.

## Required inputs

- active work-order scope and prohibited paths;
- base branch and current task branch;
- defect reproduction and failing test;
- applicable accepted controls and maintenance change class;
- dependency relationship between the defect and active task.

## Procedure

### 1. Classify the defect

Record:

```text
Defect:
Discovered during:
Affected runtime/control:
Severity:
Does active work require it to proceed?
Is it authorized by the active work order?
```

A useful fix is not automatically in scope.

### 2. Preserve evidence before separation

Capture:

- failing test/log;
- exact original head;
- root cause;
- minimal patch;
- regression test;
- affected accepted controls.

### 3. Create a separate maintenance path

- branch from the correct authoritative base;
- apply only the minimal defect fix and regression evidence;
- reference the original discovery context;
- open a separate issue/PR;
- use the applicable work order or Class C maintenance authority;
- request focused review.

### 4. Restore the active PR boundary

- remove the incidental patch from the original PR;
- retain only documentation or references permitted by the active scope;
- rerun changed-path guard and exact-head CI;
- update evidence to state where the separate fix lives.

### 5. Manage dependency safely

If active work truly depends on the maintenance fix:

- document the dependency;
- merge or accept the maintenance fix first where possible;
- rebase/refresh the active branch;
- do not duplicate the fix in both PRs;
- do not claim the active PR is merge-ready while dependency is unresolved.

### 6. Emergency path

For emergency work record:

- incident ID and approver;
- reason normal sequencing is unsafe;
- exact changes/commands;
- before/after evidence;
- recovery steps;
- post-incident permanent PR/work order.

Emergency status does not erase audit or review requirements.

## Outputs

- separate maintenance branch/issue/PR;
- minimal patch and regression test;
- restored scope-safe original PR;
- dependency and sequencing note;
- accurate changed-path evidence.

## Stop conditions

Stop when:

- the correct maintenance authority is unclear;
- the patch changes architecture or public authority beyond maintenance scope;
- the fix cannot be separated without data or compatibility consequences;
- the original PR still contains the runtime change after separation;
- two branches contain divergent versions of the same fix;
- the defect requires production credentials or data not authorized.

## Evidence gate

Isolation is complete only when:

- the separate PR contains the minimal fix and regression proof;
- the active PR no longer contains the out-of-scope path;
- both branch diffs are independently understandable;
- CI is green for the correct heads;
- dependency order is explicit;
- readiness claims reflect any unmerged dependency.

## Anti-patterns

- Keeping a valid runtime fix in a design-only PR because CI found it there.
- Reverting the fix without preserving a separate issue or patch.
- Creating a second PR from the contaminated task branch instead of the authoritative base.
- Duplicating the same patch across two PRs.
- Calling a cross-domain behavior change “cleanup.”
