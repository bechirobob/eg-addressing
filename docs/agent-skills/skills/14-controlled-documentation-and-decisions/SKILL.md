# Skill 14 — Controlled Documentation and Decisions

## Use when

Use for work orders, ADRs, RFIs, standards, baselines, risk records, runbooks, user/training documents, API/data dictionaries, release records, review records, or generated formal artifacts.

## Objective

Keep documentation authoritative, versioned, accurate, non-promotional, and traceable to implementation and evidence.

## Procedure

1. Identify the document class and authoritative source.
2. Add required metadata: stable ID, version/commit, status, owner, scope, audience, date, related ADR/work order/risk, and supersession.
3. State whether the document describes current, target, proposed, simulated, or accepted behavior.
4. Use the correct controlled status; do not use “final” without authority/version.
5. Link claims to implementation, tests, decisions, or review records.
6. Keep source and generated artifacts traceable and reproducible.
7. Update affected documentation in the same PR as the change.
8. Preserve accepted history:
   - supersede rather than silently rewrite;
   - do not alter SDA outcome/finding text;
   - agent updates only its designated resolution log.
9. Validate links, references, headings, controlled terminology, and generated artifacts.
10. Check sensitive information, examples, and screenshots.
11. For public/training documents, verify bilingual semantic alignment and accessibility.
12. Use readiness language precisely.

## Required output

- Controlled metadata
- Authority/source statement
- Current versus target boundary
- Related work order/ADR/risk links
- Evidence links
- Supersession/closeout behavior
- Validation result

## Claim rules

- `implemented` requires source.
- `tested` requires named evidence.
- `deployed` requires environment and artifact.
- `accepted` requires SDA record.
- `official/published` requires institutional authority.
- `national-production-ready` requires SDA and Programme Owner decision.

## Stop and escalate when

- A document would reveal secrets, real restricted data, or security-sensitive details.
- A proposal is being presented as current behavior.
- A reviewer decision would be rewritten.
- Spanish/English versions differ in legal or operational meaning.
- A generated artifact cannot be traced to source and commit.

## Anti-patterns

- Updating only generated output.
- Using modification date as proof of freshness.
- Saying “all criteria pass” without criterion-specific evidence.
- Embedding a consequential decision only in a diagram.
- Committing real credentials or personal data as an example.
- Treating a broad handoff note as the executable engineering handbook.
