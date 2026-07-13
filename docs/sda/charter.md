# System Design Authority Charter

**Programme:** Equatorial Guinea National Location Infrastructure (NLI)  
**Initial service:** National Digital Addressing Platform  
**Charter version:** 0.1  
**Status:** Established  
**Production authorization:** Not granted

## 1. Purpose

The System Design Authority (SDA) protects the long-term coherence, safety, operability, and public trust of the NLI. It converts programme intent into durable architecture, standards, work orders, review decisions, and evidence gates.

The SDA exists so that implementation speed does not silently create incompatible data, ungoverned authority, fragile operations, or irreversible national dependencies.

## 2. Scope

The SDA governs:

- logical and deployment architecture;
- data models, identifiers, reference data, migrations, and lifecycle states;
- identity, institutional membership, roles, permissions, and territorial scope;
- APIs, partner integration, service accounts, and data exchange;
- GIS, geometry, geocoding, location provenance, and address-code standards;
- security, privacy, audit, evidence, retention, and publication controls;
- user workflows, accessibility, localization, and interface consistency;
- performance, availability, backup, disaster recovery, and incident response;
- testing, release gates, dependency controls, and operational evidence;
- documentation, architecture decisions, risk acceptance, and technical debt.

The SDA does not independently decide legislation, ministerial authority, budget, procurement, or public policy. It records the technical consequences of those decisions and raises unresolved institutional dependencies.

## 3. Roles

### Programme Owner

The Programme Owner:

- sets strategic priorities and delivery sequence;
- confirms institutional and policy assumptions;
- appoints or recognizes the authorities permitted to approve official publication;
- accepts programme-level risk where acceptance is lawful and explicit;
- decides trade-offs involving budget, schedule, government policy, and institutional ownership.

### System Design Authority

The SDA:

- maintains the reference architecture and mandatory standards;
- issues implementation work orders and acceptance criteria;
- accepts, conditions, rejects, or returns implementation work;
- records architecture decisions and open risks;
- prevents unsupported claims of government or national-production readiness;
- escalates decisions requiring policy, legal, data-owner, security, or institutional authority.

### Implementation Agent

The Implementation Agent:

- inspects the current implementation before proposing changes;
- provides an acceptance-criterion-mapped plan;
- implements within approved architectural boundaries;
- writes migrations, tests, technical documentation, and operational evidence;
- raises RFIs rather than making unauthorized national decisions;
- identifies residual risk and does not conceal failed controls.

### Operational and institutional authorities

Future named authorities will include platform operations, security operations, national registry governance, GIS/data stewardship, municipal validation, audit, and publication authority. Until formally assigned, the absence of an authority is a readiness blocker, not permission for the implementation team to assume it.

## 4. Decision classes

### Reserved SDA decisions

The following require an accepted ADR, work-order decision, or written SDA ruling:

- authoritative system-of-record changes;
- new databases, identity providers, external platform dependencies, or deployment paradigms;
- address-code grammar or identifier-semantic changes;
- official geometry rules, administrative hierarchy, or territorial-scope changes;
- publication, retirement, correction, or bulk-export authority changes;
- new sensitive data classes or changes in public exposure;
- changes to audit immutability, evidence custody, retention, or deletion;
- role, permission, institutional scope, or segregation-of-duty changes;
- acceptance of data loss, downtime, unsupported migration, or a security exception.

### Delegated implementation decisions

The agent may choose ordinary implementation details when they:

- remain inside accepted architecture and standards;
- do not alter public contracts or authority;
- do not introduce material operational dependencies;
- are reversible and covered by tests;
- are disclosed in the implementation plan and pull request.

## 5. Controlled records

- **Baseline:** records the system as it exists at a named commit.
- **Reference architecture:** defines the intended target state and transition constraints.
- **Standard:** establishes a recurring mandatory engineering rule.
- **ADR:** records a durable architecture decision, alternatives, and consequences.
- **Work order:** authorizes bounded implementation and defines acceptance evidence.
- **RFI:** requests a decision needed to continue safely.
- **Review record:** records findings and the acceptance outcome.
- **Risk entry:** records exposure, treatment, ownership, and status.

Git history is part of the control record. Do not rewrite accepted architecture records merely to conceal superseded decisions; supersede them explicitly.

## 6. Review findings

SDA findings use these classes:

- **Blocker:** creates unacceptable security, authority, integrity, migration, or operational risk; acceptance is impossible until resolved.
- **Required:** violates a work order, standard, or accepted decision and must be corrected.
- **Advisory:** improvement recommended but not required for the current acceptance boundary.
- **Accepted Risk:** explicitly understood and deferred with an owner, rationale, and review date.
- **Architecture Decision Required:** implementation exposed a decision outside delegated authority.

## 7. Acceptance outcomes

The SDA records one outcome:

- `ACCEPTED`
- `ACCEPTED WITH RECORDED CONDITIONS`
- `REWORK REQUIRED`
- `REJECTED — ARCHITECTURAL REDESIGN REQUIRED`

Acceptance applies only to the named work order, commit, evidence set, and environment boundary. It is not an automatic declaration of whole-system production readiness.

## 8. Risk acceptance

A risk may be accepted only when:

- the risk is clearly described, including affected data, users, services, and environments;
- mitigations and alternatives are recorded;
- an accountable owner and review date are named;
- acceptance does not violate law, binding government policy, or an authority outside the acceptor's remit;
- the acceptance is visible in the risk register and relevant review record.

The Implementation Agent cannot accept national programme risk on behalf of the Programme Owner or SDA.

## 9. Emergency changes

Emergency work must still preserve evidence. A break-glass change requires:

- named incident and accountable approver;
- scope and reason;
- commands or changes performed;
- before/after evidence;
- security and data effects;
- post-incident review and permanent corrective work order.

Emergency status is not a bypass for audit, credentials handling, or institutional publication authority.

## 10. Amendment

Changes to this charter require a dedicated review. Substantive amendments must state why the current governance is insufficient and what authority or control changes as a result.
