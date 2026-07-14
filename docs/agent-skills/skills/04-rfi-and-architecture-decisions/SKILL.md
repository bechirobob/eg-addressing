# Skill 04 — RFI and Architecture Decisions

## Use when

Use when implementation encounters ambiguity, multiple viable architectures, institutional authority, new dependencies, data loss, public exposure, identifier semantics, hierarchy, publication, retention, or security exceptions.

## Objective

Prevent consequential national decisions from being hidden in code, SQL, generators, or implementation convenience.

## Decision routing

### Use an ADR when

- the decision is primarily technical and within SDA authority;
- it should govern future work repeatedly;
- alternatives and consequences can be evaluated now.

### Use an RFI when

- government/institutional/legal authority is required;
- source authority is unknown;
- the decision affects official publication, hierarchy, privacy, retention, public-code grammar, land/title, or risk acceptance;
- the work cannot proceed safely without an external answer.

### Use a risk record when

- the decision is understood but intentionally deferred;
- compensating controls, owner, and review date can be named.

## Procedure

1. State one precise decision question.
2. Identify the requirement and implementation checkpoint blocked by the decision.
3. Gather current evidence and constraints.
4. Define real alternatives, including deferral where valid.
5. For each alternative, analyze:
   - behavior and authority;
   - data model and migration;
   - security and privacy;
   - performance and operations;
   - compatibility and failure modes;
   - reversibility and cost.
6. Recommend an option without presenting it as approved.
7. State the consequence of no decision.
8. Identify the exact decision owner.
9. Update plan, risk register, and affected design once decided.
10. Convert durable decisions into ADRs/standards.

## Required output

Use `docs/sda/templates/rfi.md` or the repository ADR pattern. Include explicit status, owner, alternatives, decision, conditions, and follow-up.

## Evidence standard

An ADR acceptance statement must link to a real model assertion, test, constraint, or controlled condition. Do not claim guarantees that the current design/test suite does not demonstrate.

## Stop and escalate when

- The implementation agent would be deciding legal or institutional authority.
- An unresolved RFI is being treated as an approved default.
- A public code or official geometry would be issued.
- Data would be discarded, disclosed, or retained without authority.
- A new technology would create material operational or licensing impact.

## Anti-patterns

- Embedding a decision only in draft SQL.
- Giving every ADR the same generic alternatives and consequences.
- Naming “do what the proposal says” as an architecture alternative.
- Marking an ADR accepted while its defining findings remain open.
- Addressing several unrelated institutional questions in one broad RFI.
