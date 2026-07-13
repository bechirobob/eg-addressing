# SDA Standard — Documentation and Controlled Records

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** architecture, APIs, data, operations, user guidance, decisions, work orders, reviews, and generated formal artefacts

## 1. Documentation is part of the system

A feature is incomplete when operators, reviewers, support staff, integrators, or future engineers cannot determine how it works, who may use it, what evidence it creates, and how it fails or recovers.

Documentation MUST describe the accepted implementation, not an aspirational state presented as current fact.

## 2. Controlled document classes

The following classes have distinct purposes and MUST not be conflated:

- **Charter:** authority and governance.
- **Baseline:** evidence-based description of a named current state.
- **Reference architecture:** intended target and transition constraints.
- **Standard:** recurring mandatory engineering rule.
- **ADR:** durable decision, alternatives, and consequences.
- **Work order:** bounded implementation authorization and acceptance criteria.
- **RFI:** decision request needed to proceed safely.
- **Review record:** findings, resolutions, evidence, and acceptance outcome.
- **Runbook:** safe operational procedure with verification and escalation.
- **User/training guide:** task guidance for a defined audience and version.
- **API/data contract:** machine and human-readable interface definition.
- **Release record:** deployed artefact, environment, checks, decisions, and recovery information.

## 3. Required metadata

Controlled documents MUST state, as applicable:

- title and stable identifier;
- version or governing commit;
- status;
- owner/authority;
- scope and audience;
- effective or review date;
- related work orders, ADRs, risks, and systems;
- superseded document or decision;
- production/readiness limitations.

Do not use ambiguous labels such as “final” without a version and status.

## 4. Status vocabulary

Use explicit statuses appropriate to the document class, such as:

- Draft;
- Proposed;
- Issued;
- Accepted;
- Accepted with conditions;
- Active;
- Superseded;
- Withdrawn;
- Archived;
- Rework required.

A draft proposal MUST NOT be cited as an implemented control.

## 5. Source and generated artefacts

- Durable source documents belong in version control.
- Generated PDFs, screenshots, diagrams, exports, and evidence bundles MUST identify their source commit and generation process.
- Where source and generated artefacts coexist, the authoritative source MUST be declared.
- Generated artefacts MUST be reproducible where practical.
- Do not manually edit generated output without updating its source.
- Large or sensitive runtime evidence belongs in approved artefact storage, not necessarily Git.

## 6. Architecture decisions

An ADR MUST include:

- context and decision drivers;
- decision;
- alternatives considered;
- consequences, including operational and migration effects;
- status and supersession links;
- unresolved follow-up work.

Accepted ADRs are not rewritten to hide past rationale. A later decision supersedes them explicitly.

## 7. Work orders and traceability

A work order MUST include:

- stable ID, status, owner, and branch convention;
- objective and risk addressed;
- in-scope and out-of-scope work;
- mandatory constraints and prohibited approaches;
- numbered acceptance criteria;
- required tests and evidence;
- dependencies, RFIs, and acceptance process.

Pull requests and review records MUST reference the work order and address every acceptance criterion individually.

## 8. API and data documentation

- OpenAPI and generated contracts MUST match implementation.
- Data dictionaries MUST define field meaning, type, nullability, controlled vocabulary, classification, source, lifecycle, and public/partner projection.
- Diagrams MUST be accompanied by text explaining authority and data flow; diagrams alone are insufficient.
- Examples MUST use non-sensitive fixtures and identify that they are examples.
- Breaking changes require migration and deprecation documentation.

## 9. Operational documentation

Runbooks MUST include:

- purpose and trigger;
- authority and prerequisites;
- environment and safety warnings;
- exact steps/commands where appropriate;
- expected output;
- verification and abort criteria;
- rollback or forward recovery;
- audit/evidence generated;
- escalation path;
- last tested date and result.

Untested runbooks MUST be marked as unvalidated.

## 10. User and training documentation

- State the intended role, institution/scope assumptions, language, application version, and environment.
- Match actual workflow labels and states.
- Distinguish pilot simulations from official publication.
- Avoid exposing credentials, real personal data, internal object keys, or security-sensitive operational details.
- Provide accessible structure, text alternatives, and readable document navigation.
- Bilingual versions MUST be semantically aligned and controlled together.

## 11. Accuracy and claims

Use evidence-backed language:

- “implemented” requires source;
- “tested” requires named test/evidence;
- “deployed” requires an environment and artefact;
- “pilot-ready,” “agency-ready,” “publication-ready,” and “national-production-ready” require their applicable gate decisions.

Do not use “government-grade,” “secure,” “highly available,” “official,” or “complete” as unqualified promotional claims.

## 12. Sensitive information

Documentation MUST NOT contain:

- secrets, tokens, passwords, keys, or private endpoints;
- real identity-document values or unnecessary personal data;
- production database dumps or unrestricted evidence;
- hidden agent/system prompts;
- operational details whose disclosure materially weakens security, unless stored in an appropriately restricted system.

Safe environment-variable names, redacted examples, and public architecture descriptions are permitted.

## 13. Review and freshness

- Documents affected by a change MUST be updated in the same pull request.
- Baselines and runbooks MUST be reviewed after material architecture or operational change.
- Stale documents MUST be updated, superseded, or explicitly marked historical.
- A recent file modification date is not proof that its content is current.
- Review should verify links, references, generated artefacts, terminology, and readiness claims.

## 14. Required evidence

Documentation-bearing changes require:

- list of controlled records added/changed;
- authority and status check;
- link/reference validation;
- source-to-generated artefact traceability where applicable;
- bilingual/accessibility check for public or training material;
- confirmation that examples contain no sensitive data;
- review of claims against actual implementation and evidence.
