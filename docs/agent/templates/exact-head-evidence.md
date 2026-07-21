# Exact-Head Submission Evidence

**Repository:**  
**Work order:**  
**PR:**  
**Base branch/SHA:**  
**Implementation/model branch:**  
**Implementation/model SHA:**  
**Evidence-stamp SHA, if different:**  
**Current PR head:**  
**PR draft state:**  
**Recorded at:**

## 1. Scope proof

- Changed paths:
- Prohibited-path result:
- Runtime behavior changed:
- Executable migrations changed:
- Production/pilot data changed:
- Separate maintenance dependencies:

## 2. Workflow evidence

| Workflow | Run ID | Job | Job ID | Conclusion | What it proves |
|---|---:|---|---:|---|---|
| | | | | | |

## 3. Criterion-specific evidence

| AC/finding | Exact assertion | Command/job/report | Result | Limitation |
|---|---|---|---|---|
| | | | | |

## 4. Generated artefacts

- Generator command:
- Deterministic rerun:
- Clean-diff result:
- Parser/execution target:
- Report paths:
- Checks not performed:

## 5. Positive and negative proof

| Behavior | Positive evidence | Negative evidence | Expected source independent? |
|---|---|---|---|
| | | | YES/NO |

## 6. Review request binding

```text
Requesting SDA review against implementation/model SHA: <sha>
PR state: <draft/ready>
Open findings/RFIs: <list>
NLI-WO-next-phase authorization: <authorized/not authorized>
Readiness boundary: <statement>
```

## 7. SHA integrity note

A committed file cannot cryptographically contain its own final commit SHA. When the implementation SHA is created after this evidence file:

1. record the final SHA and workflow/job IDs in the PR body or immutable PR comment;
2. ensure the SDA review record later names that exact implementation SHA;
3. do not create another implementation change after the review request without issuing a new exact-head evidence record.

## 8. Declaration

- [ ] Remote head equals the reported implementation head.
- [ ] Required workflows ran against that head.
- [ ] The PR is accessible and in the required draft state.
- [ ] The PR body/comment contains no stale prior-review SHA.
- [ ] Evidence does not claim checks that were not executed.
- [ ] Review status is not confused with implementation completion.
