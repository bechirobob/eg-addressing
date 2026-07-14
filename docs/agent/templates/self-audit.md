# Agent Pre-Submission Self-Audit

**Task/work order:**  
**Branch/PR:**  
**Implementation/model SHA:**  
**Latest SDA review:**

## Authority and scope

- [ ] Active work order and current SDA outcome were re-read.
- [ ] Change class is correct.
- [ ] Every changed path is in scope or approved supporting evidence.
- [ ] No unrelated runtime/maintenance fix remains in the PR.
- [ ] Prohibited paths and behaviors were checked from the actual diff.
- [ ] Readiness claim does not exceed recorded authority.

## Acceptance criteria

- [ ] Every AC has a criterion-specific observable assertion.
- [ ] Every AC has positive evidence.
- [ ] Every material boundary has a negative test.
- [ ] Authority/policy checks are explicit.
- [ ] No AC is marked PASS from file presence, counts, headings, or green CI alone.
- [ ] Open RFIs and conditions are visible.

## Evidence quality

- [ ] Expected evidence is independent from observed generation.
- [ ] Negative cases actually execute and fail for the expected reason.
- [ ] No-loss assertions validate values and relationships, not only counts.
- [ ] Generated artefacts are portable, deterministic, and non-self-modifying.
- [ ] SQL/design artefacts parse or execute in the appropriate disposable environment.
- [ ] Reports name checks actually performed and disclose checks not performed.

## Review remediation

- [ ] Every finding has a unique root cause, correction, commit, and evidence.
- [ ] No bulk “resolved” rows use one generic evidence list.
- [ ] SDA outcome/finding/required-resolution/disposition text is unchanged.
- [ ] Only the designated resolution-log section was updated.
- [ ] Agent status says `READY FOR SDA REVIEW`, not SDA-resolved.
- [ ] Prior accepted controls still pass.

## Database/API/GIS/UI/operations

- [ ] Database effects invoke S07 and include recovery evidence.
- [ ] API/auth/sensitive data effects invoke S08 and include allow/deny tests.
- [ ] GIS/evidence/publication effects invoke S09 and preserve authority separation.
- [ ] User-visible effects invoke S10 with language/accessibility/workflow evidence.
- [ ] Release/DR effects invoke S15 with owners, alerts, restore/failure evidence.

## GitHub and exact-head state

- [ ] Local and remote branch heads match.
- [ ] Branch is ahead of the correct base.
- [ ] PR exists and has the correct draft state.
- [ ] PR body is current and contains no stale review/SHA language.
- [ ] Exact-head workflow and job IDs are recorded.
- [ ] Required CI completed successfully at the reported SHA.
- [ ] Review request names the exact implementation/model SHA.
- [ ] Implementation head is distinguished from later review-record commits.

## Security and records

- [ ] No secrets, production credentials, personal data extracts, or unsafe logs were committed.
- [ ] Sensitive values are classified and purpose-limited.
- [ ] Audit/evidence behavior is tested where affected.
- [ ] ADR/RFI records are accurate and not generated from one generic body.
- [ ] No acceptance or production/publication claim is fabricated.

## Completion declaration

```text
Implementation/model status:
Verification status and exact SHA:
Remote submission status:
SDA status:
Open findings/RFIs:
Separate maintenance dependencies:
Readiness boundary:
Exact next action:
```

## Final gate

Any unchecked item that is applicable blocks the “done” or SDA review-request message.
